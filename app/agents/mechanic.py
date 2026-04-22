# apps/agents/mechanic.py

import json
import re
from langchain_core.messages import SystemMessage, HumanMessage
from app.utils.mechanics_engine import MechanicsEngine
from app.graph.state import AgentState
# Assuming you're using Ollama or LangChain's Llama interface
from langchain_community.llms import Ollama 

llm = Ollama(model="llama3.2", format="json")

async def mechanic_node(state: AgentState):
    # 1. AI prompt
    prompt = """
    You are the D&D 5e Mechanic Parser. 
    Analyze the input and output ONLY a JSON object. 
    Do not calculate HP changes yourself.
    
    Fields:
    - "action_type": (attack, heal, skill_check, or movement)
    - "target_id": (The ID of the player or NPC targeted)
    - "dice_roll": (Roll a 1d20)
    - "value": (The raw damage or healing amount based on 5e rules)
    """
    
    response = llm.invoke([
        SystemMessage(content=prompt),
        HumanMessage(content=f"Current State: {state['game_state']}\nPlayer Input: {state['user_input']}")
    ])

    # 2. Extraction 
    try:
        json_str = re.search(r'\{.*\}', response, re.DOTALL).group(0)
        intent_data = json.loads(json_str)
    except Exception as e:
        print(f"Mechanic failed to parse JSON: {e}")
        return state # Or handle error
    
    # 3. Symbolic Execution (The "Symbolic" part of Neuro-Symbolic)
    # We use our Python engine to update the actual numbers
    engine = MechanicsEngine()
    game_state_obj = state["game_state"] # This should be your Pydantic object
    
    if intent_data["action_type"] == "attack":
        # Check success vs AC (Logic moved to Python for 100% accuracy)
        # Assuming we fetch target AC from the state
        updated_state = engine.apply_damage(
            game_state_obj, 
            intent_data["target_id"], 
            intent_data["value"]
        )
        state["game_state"] = updated_state

    # 4. Store results for the Narrator to read
    state["logic_results"] = intent_data
    return state
    