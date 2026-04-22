import asyncio
import json
import re
from langchain_ollama import OllamaLLM
from typing import TypedDict
from pydantic import BaseModel

# --- SYMBOLIC LAYER (The Math) ---
class MechanicsEngine:
    @staticmethod
    def resolve_action(intent: dict, dc: int = 15):
        # The logic is 100% deterministic here
        roll = intent.get("dice_roll", 0)
        success = roll >= dc
        return {
            "success": success,
            "msg": "Success!" if success else "Failure!",
            "actual_roll": roll
        }

# --- NEURAL LAYER (The AI) ---
llm = OllamaLLM(model="llama3.2")

class AgentState(TypedDict):
    user_input: str
    logic_results: dict
    narrative: str

def extract_json(text):
    match = re.search(r'\{.*\}', text, re.DOTALL)
    return match.group(0) if match else text

async def mechanic_node(state: AgentState):
    print("--- 🔧 Mechanic: Parsing Intent ---")
    prompt = """
    Identify the D&D action. Output ONLY JSON: {"action": "string", "dice_roll": <int 1-20>}
    """
    response = llm.invoke(f"{prompt}\nInput: {state['user_input']}")
    
    # 1. AI interprets intent
    intent = json.loads(extract_json(response))
    
    # 2. Python executes the rule (The Symbolic part)
    engine = MechanicsEngine()
    result = engine.resolve_action(intent, dc=12) # Setting a DC of 12
    
    state["logic_results"] = {**intent, **result}
    return state

async def narrator_node(state: AgentState):
    print("--- 🎙️ Narrator: Generating Prose ---")
    logic = state["logic_results"]
    prompt = f"DM a D&D scene. Result: {logic['action']} was a {logic['msg']} (Roll: {logic['actual_roll']})."
    state["narrative"] = llm.invoke(prompt)
    return state

async def run_test(user_query: str):
    state = {"user_input": user_query, "logic_results": {}, "narrative": ""}
    state = await mechanic_node(state)
    state = await narrator_node(state)
    print(f"\n[USER]: {user_query}")
    print(f"[ENGINE]: {state['logic_results']}")
    print(f"[DM]: {state['narrative']}\n")

if __name__ == "__main__":
    asyncio.run(run_test("I try to kick down the heavy oak door!"))