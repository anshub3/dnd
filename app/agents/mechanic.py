# apps/agents/mechanic.py

import json
import os
import re
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage
from app.utils.mechanics_engine import MechanicsEngine
from app.graph.state import AgentState
# Assuming you're using Ollama or LangChain's Llama interface
from langchain_ollama import OllamaLLM

load_dotenv()

llm = OllamaLLM(model=os.environ.get("OLLAMA_MODEL", "llama3.2"), format="json")

LEVEL_REQUIREMENTS = {
    "world_altering": 17,  # Wish, Reality Warping
    "teleportation": 7,    # Dimension Door, Teleport
    "resurrection": 5,     # Revivify
    "area_destruction": 5  # Fireball, Lightning Bolt
}

async def mechanic_node(state: AgentState):
    # 1. AI prompt
    prompt = """
    You are the D&D 5e Mechanic Parser. 
    Current Player Level: {state['game_state'].get('player_level', 1)}
    User Input: {state['user_input']}
    Analyze the input and output ONLY a JSON object. 
    Do not calculate HP changes yourself.
    
    Task:
    1. Determine if the action is physically/magically possible for their level.
    2. If impossible, set "valid": false and provide a "reason".
    3. If possible, set "valid": true and provide "dice_roll".

    Categorize this action into one of: [melee, social, exploration, teleportation, world_altering, area_destruction].

    Output ONLY JSON:
    {{
        "action": "string",
        "valid": boolean,
        "reason": "string",
        "dice_roll": int,
        "category": "string",
        "intensity": int
    }}
    """
    
    player_level = state['game_state'].get('player_level', 1)
    action_cat = logic_results.get("category")
    response = llm.invoke(prompt)
    logic_results = json.loads(re.search(r'\{.*\}', response, re.DOTALL).group(0))



    '''
    # 2. Extraction 
    try:
        json_str = re.search(r'\{.*\}', response, re.DOTALL).group(0)
        intent_data = json.loads(json_str)
    except Exception as e:
        print(f"Mechanic failed to parse JSON: {e}")
        return state # Or handle error
    '''

    # 3. Symbolic Execution (The "Symbolic" part of Neuro-Symbolic)
    # We use our Python engine to update the actual numbers
    engine = MechanicsEngine()
    game_state_obj = state["game_state"] # This should be the Pydantic object
    
    if action_cat in LEVEL_REQUIREMENTS:
        required = LEVEL_REQUIREMENTS[action_cat]
        if player_level < required:
            logic_results["valid"] = False
            logic_results["reason"] = f"Action category '{action_cat}' requires Level {required}. You are only Level {player_level}."

    # 4. Store results for the Narrator to read
    state["logic_results"] = logic_results
    return state
    