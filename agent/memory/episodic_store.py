import os
import uuid
from datetime import datetime
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions

# Path dove ChromaDB persiste i dati sul disco
DB_PATH = str(Path(__file__).parent.parent.parent / "data" / "episodic_memory")


def get_collection():
    """
    Restituisce la collection ChromaDB, creandola se non esiste.
    Usa l'embedding function di default (sentence-transformers locale)
    oppure OpenAI se la key è disponibile.
    """
    os.makedirs(DB_PATH, exist_ok=True)
    client = chromadb.PersistentClient(path=DB_PATH)

    # Usa OpenAI embeddings se disponibile, altrimenti default locale
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print("||||:__ OpenAI Embeddings :__||||")
        ef = embedding_functions.OpenAIEmbeddingFunction(
            api_key=openai_key,
            model_name="text-embedding-3-small"
        )
    else:
        print("||||:__ Default ChromaDB Embeddings :__||||")
        ef = embedding_functions.DefaultEmbeddingFunction()

    return client.get_or_create_collection(
        name="ci_episodes",
        embedding_function=ef, #type: ignore
        metadata={"hnsw:space": "cosine"}  # similarità coseno
    )


def save_episode(state: dict, outcome: str) -> str:
    """
    Salva un episodio in ChromaDB dopo il completamento di un ciclo.
    outcome: "success" | "failed" | "escalated"
    Ritorna l'ID dell'episodio salvato.
    """
    collection = get_collection()

    history   = state.get("attempts_history", [])
    last_fix  = history[-1] if history else {}

    # Il testo che verrà embeddato per la ricerca semantica
    error_signature = f"""
    category: {state.get('error_category', 'unknown')}
    job: {state.get('ci_job_name', '')}
    logs: {state.get('ci_logs', '')[:500]}
    diff: {state.get('git_diff', '')[:200]}
    fix_applied: {last_fix.get('fix_applied', '')}
    fix_diff: {last_fix.get('fix_diff', '')[:200]}
    """.strip()

    episode_id = str(uuid.uuid4())

    collection.add(
        ids=[episode_id],
        documents=[error_signature],
        metadatas=[{
            "error_category":  state.get("error_category", "unknown"),
            "fix_applied":     last_fix.get("fix_applied", ""),
            "fix_diff":        last_fix.get("fix_diff", "")[:500],
            "outcome":         outcome,
            "attempt_number":  str(len(history)),
            "repo_name":       state.get("repo_name", ""),
            "timestamp":       datetime.now().isoformat(),
        }]
    )

    print(f"💾 Episodio salvato in memoria (outcome: {outcome}, id: {episode_id[:8]})")
    return episode_id


def retrieve_similar_episodes(
    error_logs: str,
    category: str,
    top_k: int = 3,
    only_successful: bool = True
) -> list[dict]:
    """
    Recupera gli episodi più simili all'errore corrente.
    only_successful=True filtra solo i fix che hanno funzionato.
    Ritorna lista di dict con fix_applied, fix_diff, similarity score.
    """
    collection = get_collection()

    if collection.count() == 0:
        return []  # memoria vuota

    if only_successful:
        where_filter = {
            "$and": [
                {"error_category": {"$eq": category}},
                {"outcome": {"$eq": "success"}}
            ]
        }
    else:
        where_filter = {"error_category": {"$eq": category}}

    try:
        results = collection.query(
            query_texts=[error_logs[:1000]], # lista di query, ChromaDB è ottimizzato per prenderne N
            n_results=min(top_k, collection.count()),
            where=where_filter, #type: ignore
        )
    except Exception as e:
        print(f" ⚠️ Errore retrieval: {e}")
        return []

    episodes = []
    # Si usa [0] perchè fa riferimento all'indice della query nel query_text. Avendone usata solo una, faccio riferimento idx 0
    if results["metadatas"] and results["metadatas"][0]:
        for i, meta in enumerate(results["metadatas"][0]):
            score = 1 - results["distances"][0][i] #type: ignore  # cosine: distance→similarity
            episodes.append({
                "fix_applied": meta.get("fix_applied", ""),
                "fix_diff":    meta.get("fix_diff", ""),
                "outcome":     meta.get("outcome", ""),
                "similarity":  round(score, 3),
                "timestamp":   meta.get("timestamp", ""),
            })

    return episodes


def format_episodes_for_prompt(episodes: list[dict]) -> str:
    """
    Formatta gli episodi recuperati in testo leggibile dall'LLM.
    Usato come context nel prompt del tentativo 3.
    """
    if not episodes:
        return "Nessun episodio simile trovato in memoria."

    lines = ["Fix simili dal passato (ordinati per similarità):\n"]
    for i, ep in enumerate(episodes, 1):
        lines.append(
            f"{i}. [similarity: {ep['similarity']:.0%}] {ep['fix_applied']}\n"
            f"   Diff: {ep['fix_diff'][:200]}\n"
        )
    return "\n".join(lines)


def memory_stats() -> dict:
    """Statistiche sulla memoria — utile per i grafici della tesi."""
    collection = get_collection()
    total      = collection.count()
    if total == 0:
        return {"total": 0}

    all_items = collection.get(include=["metadatas"])
    outcomes  = [m["outcome"] for m in all_items["metadatas"]] #type: ignore
    categories = [m["error_category"] for m in all_items["metadatas"]] #type: ignore

    return {
        "total":      total,
        "success":    outcomes.count("success"),
        "failed":     outcomes.count("failed"),
        "escalated":  outcomes.count("escalated"),
        "by_category": {
            "dependency": categories.count("dependency"),
            "test":       categories.count("test"),
            "config":     categories.count("config"),
        }
    }