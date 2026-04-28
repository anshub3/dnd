# app/graph/workflow.py

from langgraph.graph import StateGraph, END
from app.agents.mechanic import mechanic_node
from app.agents.chronicler import chronicler_node
from app.agents.narrator import narrator_node
from app.agents.proxy import proxy_node
from app.agents.critic import critic_node
from app.graph.state import AgentState


def should_proxy_act(state: AgentState):
    # Check if the next turn in our state belongs to an AI
    if state["game_state"].get("next_turn_is_proxy", False):
        return "proxy"
    return END

def check_narrative_logic(state: AgentState):
    """
    The Critic Node:
    Checks if the Narrator's prose matches the Mechanic's logic.
    """
    narrative = state["narrative"]
    logic = state["logic_results"]
    
    # If the mechanic said 'Fail' but the narrator described a 'Success'
    if logic["success"] == False and "success" in narrative.lower():
        return "rewrite" # Send back to Narrator
    return "finalize"

# 1. Initialize the Graph
workflow = StateGraph(AgentState)

# 2. Add our "Invisible" Agent Nodes
workflow.add_node("mechanic", mechanic_node)
workflow.add_node("chronicler", chronicler_node)
workflow.add_node("narrator", narrator_node)
workflow.add_node("proxy", proxy_node)
workflow.add_node("critic", critic_node)

# 3. Define the Flow
# Start -> Validate Rules -> Get Lore -> Write Story -> End
workflow.set_entry_point("mechanic")
workflow.add_edge("mechanic", "chronicler")
workflow.add_edge("chronicler", "narrator")
workflow.add_edge("mechanic", "narrator")
workflow.add_edge("narrator", "critic")

# The Conditional Edge: Does an AI player speak now?
workflow.add_conditional_edges(
    "narrator",
    should_proxy_act
)
workflow.add_conditional_edges(
    "critic",
    check_narrative_logic,
    {
        "rewrite": "narrator", # Loop back for a fix
        "finalize": END        # Good to go
    }
)
workflow.add_edge("proxy", END)



# 4. Compile the Graph
dungeon_master_app = workflow.compile()