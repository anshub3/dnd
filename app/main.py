#app/main.py

from fastapi import FastAPI
from app.graph.workflow import dungeon_master_app
from app.schema.player import GameState


# --------------------------
# API SETUP
# --------------------------

app = FastAPI(title="Neuro-Symbolic D&D DM")

@app.post("/chat")
async def handle_turn(message: str, current_state: GameState):
    """
    1. Receives user message from the UI.
    2. Runs the LangGraph workflow (Mechanic -> Chronicler -> Narrator).
    3. Returns the updated state and the DM's narrative response.
    """
    inputs = {"user_input": message, "state": current_state}
    
    # LangGraph processes the multi-agent logic
    final_output = await dungeon_master_app.ainvoke(inputs)
    
    return {
        "dm_response": final_output["narrative"],
        "updated_state": final_output["state"]
    }