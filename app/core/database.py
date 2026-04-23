import json
from sqlalchemy import create_engine, Column, String, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.graph.state import AgentState


DATABASE_URL = "postgresql://dnd_project:password_dnd@localhost/dnd_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class GameStateModel(Base):
    __tablename__ = "game_sessions"
    
    # Using game_id as the primary key to resume sessions
    game_id = Column(String, primary_key=True, index=True)
    # JSONB field to store the entire GameState Pydantic object
    state_data = Column(JSON) 

Base.metadata.create_all(bind=engine)

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