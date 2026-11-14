from dotenv import load_dotenv
load_dotenv()

from agent.memory.episodic_store import (
    save_episode, retrieve_similar_episodes,
    format_episodes_for_prompt, memory_stats
)

# Delete the old test states so they do not overlap
from agent.memory.episodic_store import get_collection
get_collection().delete(where={"error_category": {"$eq": "dependency"}})

print("=== EPISODIC MEMORY TEST ===\n")

# 1. Save some example episodes
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

print("💾 Saving 2 example episodes...")
save_episode(state1, "success")
save_episode(state2, "success")

# 2. Memory statistics
stats = memory_stats()
print(f"\n📊 Memory statistics: {stats}")

# 3. Retrieval — look for episodes similar to a new error
print("\n🔍 Looking for episodes similar to 'scipy version not found'...")
similar = retrieve_similar_episodes(
    error_logs="ERROR: scipy==9.9.9 not found, no matching distribution found",
    category="dependency",
    top_k=3
)

print(f"   Found: {len(similar)} similar episodes")
for ep in similar:
    print(f"   [{ep['similarity']:.0%}] {ep['fix_applied']}")

# 4. Format for the LLM prompt
print("\n📝 Format for the LLM prompt:")
print(format_episodes_for_prompt(similar))



# Look for something semantically DISTANT
print("\n🔍 Looking for distant episodes (failed test)...")
distant = retrieve_similar_episodes(
    error_logs="AssertionError: assert add(2,3) == 99, test failed",
    category="dependency",
    top_k=2
)
for ep in distant:
    print(f"   [{ep['similarity']:.0%}] {ep['fix_applied']}")