#app/main.py

from fastapi import FastAPI
from app.graph.workflow import dungeon_master_app
from app.schema.player import GameState
from app.core.database import save_game_state, SessionLocal, GameStateModel
import json

# --------------------------
# API SETUP
# --------------------------

app = FastAPI(title="Neuro-Symbolic D&D DM")

@app.post("/chat/{game_id}")
async def handle_chat(game_id: str, message: str):
    # 1. Load state from DB
    db = SessionLocal()
    record = db.query(GameStateModel).filter(GameStateModel.game_id == game_id).first()
    current_state = record.state_data if record else {}
    
    # 2. Run the Multi-Agent Graph
    inputs = {
        "user_input": message, 
        "game_state": current_state,
        "history": []
    }
    
    final_output = await dungeon_master_app.ainvoke(inputs)
    
    # 3. Save the new state back to Postgres
    save_game_state(game_id, final_output["game_state"])
    
    return {
        "dm_response": final_output["narrative"],
        "chat_history": final_output["history"]
    }


def load_db_state(game_id: str):
    db = SessionLocal()
    session = db.query(GameStateModel).filter(GameStateModel.game_id == game_id).first()
    db.close()
    
    if session:
        return session.current_state, json.loads(session.chat_history)
    return None, []