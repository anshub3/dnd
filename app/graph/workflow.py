# app/graph/workflow.py

from langgraph.graph import StateGraph, END
from app.agents.mechanic import mechanic_node
from app.agents.chronicler import chronicler_node
from app.agents.narrator import narrator_node
from app.graph.state import AgentState


# 1. Initialize the Graph
workflow = StateGraph(AgentState)

# 2. Add our "Invisible" Agent Nodes
workflow.add_node("mechanic", mechanic_node)
workflow.add_node("chronicler", chronicler_node)
workflow.add_node("narrator", narrator_node)

# 3. Define the Flow
# Start -> Validate Rules -> Get Lore -> Write Story -> End
workflow.set_entry_point("mechanic")
workflow.add_edge("mechanic", "chronicler")
workflow.add_edge("chronicler", "narrator")
workflow.add_edge("narrator", END)

# 4. Compile the Graph
dungeon_master_app = workflow.compile()