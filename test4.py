import asyncio
import json
import re
from langchain_ollama import OllamaLLM
from typing import TypedDict, List

llm = OllamaLLM(model="llama3.2")

class AgentState(TypedDict):
    user_input: str
    game_state: dict
    logic_results: dict
    narrative: str
    history: List[str] # To simulate the group chat thread

def extract_json(text):
    match = re.search(r'\{.*\}', text, re.DOTALL)
    return match.group(0) if match else text

# --- NODE 1: THE DM (Logic + Story) ---
async def dm_node(state: AgentState):
    print("--- 🎙️ DM: Processing and Narrating ---")
    # Simulate Mechanic + Narrator in one step for brevity in this test
    prompt = f"DM a D&D scene. Action: {state['user_input']}. Result: Success. Roll: 18. Include the mention of a dark, shadowy corner."
    response = llm.invoke(prompt)
    state["narrative"] = response
    state["history"].append(f"DM: {response}")
    return state

# --- NODE 2: THE PROXY (The AI Teammate) ---
async def proxy_node(state: AgentState):
    print("--- 🤖 PROXY: Kaelen the Rogue is reacting ---")
    persona = state["game_state"]["proxy_persona"]
    
    prompt = f"""
    You are Kaelen, a D&D player character.
    Persona: {persona}
    The DM just said: {state['narrative']}
    
    Respond to the DM in the group chat. Stay in character!
    """
    response = llm.invoke(prompt)
    state["history"].append(f"Kaelen: {response}")
    return state

async def main():
    initial_state = {
        "user_input": "I check the tavern door for traps.",
        "game_state": {
            "location": "The Rusty Tankard",
            "proxy_persona": "Sarcastic, paranoid about shadows, loves gold."
        },
        "logic_results": {},
        "narrative": "",
        "history": []
    }

    # Simulate the Graph: DM speaks, then Proxy speaks
    state = await dm_node(initial_state)
    state = await proxy_node(state)

    print("\n--- GROUP CHAT LOG ---")
    for msg in state["history"]:
        print(f"\n{msg}")
    print("\n" + "="*30)

if __name__ == "__main__":
    asyncio.run(main())