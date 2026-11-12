import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional
import chromadb
from chromadb.utils import embedding_functions

# Path where ChromaDB persists its data on disk
DB_PATH = str(Path(__file__).parent.parent.parent / "data" / "episodic_memory")


def get_collection():
    """
    Returns the ChromaDB collection, creating it if it does not exist.
    Uses the default embedding function (local sentence-transformers)
    or OpenAI if the key is available.
    """
    os.makedirs(DB_PATH, exist_ok=True)
    client = chromadb.PersistentClient(path=DB_PATH)

    # Use OpenAI embeddings if available, otherwise the local default
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
        metadata={"hnsw:space": "cosine"}  # cosine similarity
    )


def save_episode(state: dict, outcome: str, case_id: Optional[str] = None) -> str:
    """
    Saves an episode in ChromaDB after a cycle completes.
    outcome: "success" | "failed" | "escalated"
    Returns the ID of the saved episode.
    """
    collection = get_collection()

    # case_id identifies the benchmark case that produced this episode; it lets
    # retrieve_similar_episodes() exclude an episode of the very same case.
    resolved_case_id = case_id if case_id is not None else (state.get("case_id") or "")

    history   = state.get("attempts_history", [])
    last_fix  = history[-1] if history else {}

    # The text that will be embedded for semantic search
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
            "case_id":         resolved_case_id,
            "fix_applied":     last_fix.get("fix_applied", ""),
            "fix_diff":        last_fix.get("fix_diff", "")[:500],
            "outcome":         outcome,
            "attempt_number":  str(len(history)),
            "repo_name":       state.get("repo_name", ""),
            "timestamp":       datetime.now().isoformat(),
        }]
    )

    print(f"💾 Episode saved to memory (outcome: {outcome}, id: {episode_id[:8]})")
    return episode_id


def retrieve_similar_episodes(
    error_logs: str,
    category: str,
    top_k: int = 3,
    only_successful: bool = True,
    current_case_id: Optional[str] = None
) -> list[dict]:
    """
    Retrieves the episodes most similar to the current error.
    only_successful=True keeps only the fixes that worked.
    Returns a list of dicts with fix_applied, fix_diff, similarity score.
    """
    collection = get_collection()

    if collection.count() == 0:
        return []  # empty memory

    clauses = [{"error_category": {"$eq": category}}]
    if only_successful:
        clauses.append({"outcome": {"$eq": "success"}})
    if current_case_id:
        # exclude the episode of the very same case (no self-retrieval)
        clauses.append({"case_id": {"$ne": current_case_id}})
    where_filter = clauses[0] if len(clauses) == 1 else {"$and": clauses}

    try:
        results = collection.query(
            query_texts=[error_logs[:1000]], # list of queries, ChromaDB is optimized to accept N of them
            n_results=min(top_k, collection.count()),
            where=where_filter, #type: ignore
        )
    except Exception as e:
        print(f" ⚠️ Retrieval error: {e}")
        return []

    episodes = []
    # [0] refers to the index of the query in query_texts. Since only one query is used, index 0 is referenced
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
    Formats the retrieved episodes as text readable by the LLM.
    Used as context in the attempt-3 prompt.
    """
    if not episodes:
        return "No similar episode found in memory."

    lines = ["Similar past fixes (sorted by similarity):\n"]
    for i, ep in enumerate(episodes, 1):
        lines.append(
            f"{i}. [similarity: {ep['similarity']:.0%}] {ep['fix_applied']}\n"
            f"   Diff: {ep['fix_diff'][:200]}\n"
        )
    return "\n".join(lines)


def memory_stats() -> dict:
    """Memory statistics — useful for the paper figures."""
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