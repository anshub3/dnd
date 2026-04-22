# app/scema/player.py

from pydantic import BaseModel, Field
from typing import List, Optional

class Stats(BaseModel):
    hp: int
    max_hp: int
    ac: int
    strength: int
    dexterity: int
    # ... add other attributes

class Player(BaseModel):
    id: str
    name: str
    is_ai_proxy: bool = False
    stats: Stats
    inventory: List[str] = []
    persona_profile: str = Field(..., description="Traits for the Proxy Agent to mimic")

class GameState(BaseModel):
    game_id: str
    current_location: str
    party: List[Player]
    combat_active: bool = False
    turn_index: int = 0