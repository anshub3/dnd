import asyncio
import json
import re
from langchain_ollama import OllamaLLM
from typing import TypedDict

# 1. Modernized Model Class
llm = OllamaLLM(model="llama3.2")

class AgentState(TypedDict):
    user_input: str
    game_state: dict
    logic_results: dict
    narrative: str

def extract_json(text):
    """Finds and extracts JSON from a string even if wrapped in markdown."""
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        return match.group(0)
    return text

async def mechanic_node(state: AgentState):
    print("--- 🔧 Mechanic is calculating... ---")
    prompt = f"""
    Context: {state['game_state']}
    User Input: {state['user_input']}
    Task: Roll a d20 and determine if the action succeeds.
    Return ONLY a JSON object: 
    {{
        "action": "lockpicking",
        "roll": 18,
        "success": true
    }}
    """
    response = llm.invoke(prompt)
    
    try:
        # Extract and parse the JSON safely
        json_str = extract_json(response)
        state["logic_results"] = json.loads(json_str)
    except Exception as e:
        print(f"Error parsing JSON. Raw response: {response}")
        # Fallback logic if LLM fails
        state["logic_results"] = {"action": "error", "roll": 0, "success": False}
        
    return state

async def narrator_node(state: AgentState):
    print("--- 🎙️ Narrator is speaking... ---")
    # We pass the logic results specifically to the narrator
    logic = state["logic_results"]
    prompt = f"You are a D&D DM. Write a short atmospheric response for this result: {logic}"
    state["narrative"] = llm.invoke(prompt)
    return state

async def main():
    initial_state = {
        "user_input": "I try to pick the lock on the iron chest.",
        "game_state": {"player_level": 1, "location": "Dungeon Cell"},
        "logic_results": {},
        "narrative": ""
    }
    
    # Run the flow
    state = await mechanic_node(initial_state)
    state = await narrator_node(state)
    
    print("\n" + "="*30)
    print(f"MECHANIC OUTPUT: {state['logic_results']}")
    print(f"DM RESPONSE: {state['narrative']}")
    print("="*30)

if __name__ == "__main__":
    asyncio.run(main())