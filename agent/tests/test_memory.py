from dotenv import load_dotenv
load_dotenv()

from agent.memory.episodic_store import (
    save_episode, retrieve_similar_episodes,
    format_episodes_for_prompt, memory_stats
)

# Elimino i vecchi state di test così non si sovrappone
from agent.memory.episodic_store import get_collection
get_collection().delete(where={"error_category": {"$eq": "dependency"}})

print("=== TEST MEMORIA EPISODICA ===\n")

# 1. Salva alcuni episodi di esempio
state1 = {
    "error_category":  "dependency",
    "ci_job_name":     "Install dependencies",
    "ci_logs":         "ERROR: numpy==99.99.99 not found on PyPI",
    "git_diff":        "+numpy==99.99.99",
    "repo_name":       "test/repo",
    "attempts_history": [{
        "attempt": 1, "agent": "dependency",
        "fix_applied": "pinned numpy==1.26.4",
        "fix_diff": "- numpy==99.99.99\n+ numpy==1.26.4"
    }]
}

state2 = {
    "error_category":  "dependency",
    "ci_job_name":     "Install dependencies",
    "ci_logs":         "ERROR: pandas==99.0.0 not found, no matching distribution",
    "git_diff":        "+pandas==99.0.0",
    "repo_name":       "test/repo",
    "attempts_history": [{
        "attempt": 1, "agent": "dependency",
        "fix_applied": "pinned pandas==2.0.3",
        "fix_diff": "- pandas==99.0.0\n+ pandas==2.0.3"
    }]
}

print("💾 Salvo 2 episodi di esempio...")
save_episode(state1, "success")
save_episode(state2, "success")

# 2. Statistiche memoria
stats = memory_stats()
print(f"\n📊 Statistiche memoria: {stats}")

# 3. Retrieval — cerca episodi simili a un nuovo errore
print("\n🔍 Cerco episodi simili a 'scipy version not found'...")
similar = retrieve_similar_episodes(
    error_logs="ERROR: scipy==9.9.9 not found, no matching distribution found",
    category="dependency",
    top_k=3
)

print(f"   Trovati: {len(similar)} episodi simili")
for ep in similar:
    print(f"   [{ep['similarity']:.0%}] {ep['fix_applied']}")

# 4. Formato per prompt LLM
print("\n📝 Formato per prompt LLM:")
print(format_episodes_for_prompt(similar))



# Cerca qualcosa semanticamente DISTANTE
print("\n🔍 Cerco episodi distanti (test fallito)...")
distanti = retrieve_similar_episodes(
    error_logs="AssertionError: assert add(2,3) == 99, test failed",
    category="dependency",
    top_k=2
)
for ep in distanti:
    print(f"   [{ep['similarity']:.0%}] {ep['fix_applied']}")