# app/graph/state.py

from typing import TypedDict, Annotated, List
from operator import add

class AgentState(TypedDict):
    # The current message from the player
    user_input: str
    # The running game state (HP, Inventory, etc.)
    game_state: dict
    # The "Action" the mechanic decided on
    logic_results: dict
    # Lore retrieved from Chronicler
    world_context: str
    # The final prose to send to the UI
    narrative: str
    # A history of what happened in the group chat
    history: Annotated[List[str], add]