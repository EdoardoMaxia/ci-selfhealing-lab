from langgraph.graph import StateGraph, END
from agent.state import AgentState
from agent.agents.router import router_node
from agent.agents.dependency_agent import dependency_agent_node
from agent.agents.test_agent import test_agent_node
from agent.agents.config_agent import config_agent_node
from agent.pipeline.fix_executor import fix_executor_node
from agent.memory.episodic_store import save_episode


# ──────────────────────────────────────────
#  EPISODIC MEMORY SAVING
# ──────────────────────────────────────────
def save_episode_node(state: AgentState) -> dict:
    print(f"DEBUG skip_memory = {state.get('skip_memory')}")
    if state.get("skip_memory") or state.get("skip_memory_save"):
        return {}
    save_episode(state, outcome="success") #type: ignore
    return {}


def save_escalation_node(state: AgentState) -> dict:
    if state.get("skip_memory") or state.get("skip_memory_save"):
        print(f"escalation...")
        return {"final_status": "escalated"}
    save_episode(state, outcome="escalated") #type: ignore
    print(f"🚨 Escalation after {len(state.get('attempts_history', []))} attempt(s)")
    return {"final_status": "escalated"}

# ──────────────────────────────────────────
#  ROUTING FUNCTIONS
# ──────────────────────────────────────────

def route_to_specialist(state: AgentState) -> str:
    """
    Conditional edge: decides which specialized agent to call
    based on the Router's classification.
    """
    category = state.get("error_category", "unknown")
    confidence = state.get("error_confidence", 0.0)

    # If confidence is too low → direct escalation
    if confidence < 0.5: #type: ignore
        print(f"⚠️  Low confidence ({confidence:.0%}) → escalation")
        return "escalate"

    routing_map = {
        "dependency": "dependency_agent",
        "test":       "test_agent",
        "config":     "config_agent",
        "unknown":    "escalate",
    }
    destination = routing_map.get(category, "escalate") #type: ignore
    print(f"→ Routing to: {destination}")
    return destination


def should_retry_or_escalate(state: AgentState) -> str:
    ci_ok   = state.get("ci_fixed", False)
    history = state.get("attempts_history", [])

    if ci_ok:
        print("✅ CI green! → creating PR")
        return "create_pr"

    if len(history) >= 3:
        print("🚨 3 attempts exhausted → escalation")
        return "escalate"

    # Reads the agent of the last attempt to route back to the right one
    last_agent = history[-1]["agent"] if history else "dependency"
    retry_map  = {
        "dependency": "retry_dep",
        "test":       "retry_test",
        "config":     "retry_conf",
    }
    destination = retry_map.get(last_agent, "retry_dep")
    print(f"🔄 CI still red → retry on {last_agent}_agent")
    return destination

# ──────────────────────────────────────────

# ──────────────────────────────────────────

def create_pr_node(state: AgentState) -> dict:
    from agent.github.client import get_repo, create_pull_request
    from agent.pipeline.fix_executor import build_pr_body

    repo      = get_repo(state["repo_name"])
    branch    = state.get("fix_branch", "fix/ai-unknown")
    category  = state.get("error_category", "unknown")
    sha_short = state.get("commit_sha", "xxxxx")[:7]

    pr_url = create_pull_request(
        repo   = repo,
        branch = branch, #type: ignore
        base   = "main",
        title  = f"🤖 [AI Fix] {category} error — commit {sha_short}",
        body   = build_pr_body(state) #type: ignore  # ← full state
    )
    return {"final_status": "fixed", "pr_url": pr_url}


# ──────────────────────────────────────────
#  GRAPH CONSTRUCTION
# ──────────────────────────────────────────


def build_graph():
    """Builds and compiles the LangGraph graph."""
    graph = StateGraph(AgentState)

    # Add the nodes
    graph.add_node("router",           router_node) #type: ignore
    graph.add_node("dependency_agent", dependency_agent_node) #type: ignore
    graph.add_node("test_agent",       test_agent_node) #type: ignore
    graph.add_node("config_agent",     config_agent_node) #type: ignore
    graph.add_node("fix_executor",     fix_executor_node) #type: ignore
    graph.add_node("create_pr",        create_pr_node)
    graph.add_node("save_episode",     save_episode_node)
    graph.add_node("escalate",         save_escalation_node)

    # Entry point: always start from the router
    graph.set_entry_point("router")

    # Conditional edge: the router decides where to go
    graph.add_conditional_edges(
        "router",
        route_to_specialist,
        {
            "dependency_agent": "dependency_agent",
            "test_agent":       "test_agent",
            "config_agent":     "config_agent",
            "escalate":         "escalate",
        }
    )


    # Fixed edges: every agent → fix_executor
    graph.add_edge("dependency_agent", "fix_executor")
    graph.add_edge("test_agent",       "fix_executor")
    graph.add_edge("config_agent",     "fix_executor")

    # Fix Executor → smart retry loop
    graph.add_conditional_edges(
        "fix_executor",
        should_retry_or_escalate,
        {
            "retry_dep":  "dependency_agent",
            "retry_test": "test_agent",
            "retry_conf": "config_agent",
            "create_pr":  "save_episode",
            "escalate":   "escalate",
        }
    )

    # Terminal nodes
    graph.add_edge("save_episode", "create_pr")
    graph.add_edge("create_pr",    END)
    graph.add_edge("escalate",     END)

    return graph.compile()


# Global instance of the compiled graph
app = build_graph()