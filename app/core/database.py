# app/core/database.py

import json
from sqlalchemy import create_engine, Column, String, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.graph.state import AgentState
import json

DATABASE_URL = "postgresql://dnd_project:password_dnd@localhost/dnd_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class GameStateModel(Base):
    __tablename__ = "game_sessions"
    
    game_id = Column(String, primary_key=True, index=True)    # Using game_id as the primary key to resume sessions
    chat_history = Column(Text)   # Stores the raw group chat text
    state_data = Column(JSON)     # JSONB field to store the entire GameState Pydantic object
    

Base.metadata.create_all(bind=engine)

def update_db_state(game_id: str, state: dict, history: list):
    """
    Consolidated save function. 
    Updates existing session or creates a new one.
    """
    db = SessionLocal()
    try:
        db_state = db.query(GameStateModel).filter(GameStateModel.game_id == game_id).first()
        
        if db_state:
            db_state.state_data = state
            db_state.chat_history = history
        else:
            db_state = GameStateModel(
                game_id=game_id, 
                state_data=state, 
                chat_history=history
            )
            db.add(db_state)
        
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error saving to database: {e}")
    finally:
        db.close()

def load_db_state(game_id: str):
    """
    Retrieves the state and history to 'hydrate' the LangGraph.
    """
    db = SessionLocal()
    try:
        record = db.query(GameStateModel).filter(GameStateModel.game_id == game_id).first()
        if record:
            return record.state_data, record.chat_history
        return None, []
    finally:
        db.close()

def save_game_state(game_id: str, state: dict):
    db = SessionLocal()
    db_state = db.query(GameStateModel).filter(GameStateModel.game_id == game_id).first()
    if db_state:
        db_state.state_data = state
    else:
        db_state = GameStateModel(game_id=game_id, state_data=state)
        db.add(db_state)
    db.commit()
    db.close()


def save_session_to_postgres(state: AgentState):
    """Saves the flat JSON state for quick recovery."""
    db = SessionLocal()
    # We update the record where game_id matches
    db_state = db.query(GameStateModel).filter(GameStateModel.game_id == state['game_state']['game_id']).first()
    if db_state:
        db_state.state_data = state['game_state']
        db.commit()
    db.close()