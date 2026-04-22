# apps/agents/mechanic.py

import json
from langchain_core.messages import SystemMessage, HumanMessage
# Assuming you're using Ollama or LangChain's Llama interface
from langchain_community.llms import Ollama 

llm = Ollama(model="llama3.2", format="json")

async def mechanic_node(state: AgentState):
    prompt = """
    You are the D&D 5e Mechanic. Analyze the user's input against the current game state.
    Output ONLY a JSON object with:
    1. 'action_type': (e.g., 'attack', 'move', 'skill_check')
    2. 'dice_roll': (Simulate a 1d20 roll)
    3. 'success': (boolean based on D&D 5e logic)
    4. 'state_updates': (e.g., {"enemy_hp": 10})
    """
    
    response = llm.invoke([
        SystemMessage(content=prompt),
        HumanMessage(content=f"State: {state['game_state']}\nInput: {state['user_input']}")
    ])
    
    # Parse the Llama 3.2 JSON output
    logic_data = json.loads(response)
    
    return {"logic_results": logic_data}