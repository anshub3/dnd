#app/main.py

import logging
from fastapi import FastAPI, HTTPException, Depends
from app.graph.workflow import dungeon_master_app
from app.schema.player import GameState, Player, Stats
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import save_game_state, SessionLocal, GameStateModel, load_db_state, update_db_state
from pydantic import BaseModel
from typing import List, Optional
import json

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def create_default_game_state(game_id: str, player_name: str) -> dict:
    default_player = Player(
        id="player-1",
        name=player_name,
        is_ai_proxy=False,
        stats=Stats(hp=10, max_hp=10, ac=12, strength=12, dexterity=12, intiative_mod=2),
    )
    return GameState(
        game_id=game_id,
        current_location="The Rusty Tankard",
        player_level=1,
        party=[default_player],
        combat_active=False,
        turn_index=0,
        next_turn_is_proxy=False,
        history=[],
    ).dict()

# --------------------------
# API SETUP
# --------------------------

app = FastAPI(title="Neuro-Symbolic D&D DM")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    game_id: str
    message: str
    player_name: Optional[str] = "Adventurer"

class ChatResponse(BaseModel):
    game_id: str
    dm_response: str
    updated_state: dict
    chat_history: List[str]

@app.get("/")
async def root():
    return {"status": "online", "engine": "Llama-3.2-Neuro-Symbolic"}

@app.post("/chat", response_model=ChatResponse)
async def handle_chat(request: ChatRequest):
    """
    Main entry point for the group chat. 
    Handles Hydration -> Execution -> Persistence.
    """
    logger.info(f"Received message for game {request.game_id}: {request.message}")

    try:
        # 1. HYDRATION (PostgreSQL)
        # Load the saved state and history from your database
        state_data, chat_history = load_db_state(request.game_id)
        
        # Initialize default state for new games
        if not state_data:
            logger.info(f"Creating new session for game_id: {request.game_id}")
            state_data = create_default_game_state(request.game_id, request.player_name)
            chat_history = []

        # 2. LANGGRAPH INPUT PREPARATION
        # We package everything into the AgentState schema we defined
        initial_inputs = {
            "user_input": request.message,
            "game_state": state_data,
            "history": chat_history,
            "logic_results": {},
            "world_context": "",
            "narrative": "",
            "passed_audit": True # Default to True for the first pass
        }

        # 3. AGENTIC EXECUTION (LangGraph)
        # This triggers: Mechanic (RAG) -> Chronicler (Neo4j) -> Narrator -> Critic (Loop)
        # Using .ainvoke for asynchronous processing
        final_output = await dungeon_master_app.ainvoke(initial_inputs)

        # 4. PERSISTENCE (PostgreSQL)
        # Save the evolved state and updated history back to the DB
        # Note: We append the new narrative to the history here if the graph didn't already
        updated_history = final_output.get("history", chat_history)
        if final_output["narrative"]:
            updated_history.append(f"DM: {final_output['narrative']}")

        update_db_state(
            request.game_id, 
            final_output["game_state"], 
            updated_history
        )

        # 5. RETURN TO FRONTEND
        return ChatResponse(
            game_id=request.game_id,
            dm_response=final_output["narrative"],
            updated_state=final_output["game_state"],
            chat_history=updated_history
        )

    except Exception as e:
        logger.error(f"Error processing chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Engine Error: {str(e)}")

# --- STARTUP CHECK ---
@app.on_event("startup")
async def startup_event():
    logger.info("Initializing D&D Engine... Checking DB connections...")
    # You could add a quick 'health check' for Neo4j and Postgres here
    logger.info("Ready for adventure.")

if __name__ == "__main__":
    import uvicorn
    # Run the server on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)