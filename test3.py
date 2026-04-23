import asyncio
import json
import re
from langchain_ollama import OllamaLLM
from neo4j import GraphDatabase
from typing import TypedDict

# --- CONFIGURATION ---
llm = OllamaLLM(model="llama3.2")
# Update these with your Neo4j Desktop credentials
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password" 

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

class AgentState(TypedDict):
    user_input: str
    game_state: dict
    logic_results: dict
    world_context: str
    narrative: str

def extract_json(text):
    match = re.search(r'\{.*\}', text, re.DOTALL)
    return match.group(0) if match else text

# --- NODE 1: THE MECHANIC (Neural Intent + Symbolic Rules) ---
async def mechanic_node(state: AgentState):
    print("--- 🔧 Mechanic: Processing Action ---")
    prompt = f"""
    Context: {state['game_state']}
    User Input: {state['user_input']}
    Task: Roll 1d20. Return ONLY JSON: {{"action": "string", "roll": int, "success": bool}}
    """
    response = llm.invoke(prompt)
    state["logic_results"] = json.loads(extract_json(response))
    return state

# --- NODE 2: THE CHRONICLER (GraphRAG) ---
async def chronicler_node(state: AgentState):
    print("--- 📚 Chronicler: Querying Neo4j ---")
    current_loc = state["game_state"].get("location", "The Rusty Tankard")
    
    query = """
    MATCH (l:Location {name: $loc})
    OPTIONAL MATCH (l)-[:HAS_LORE]->(lore:Lore)
    RETURN l.description as desc, lore.text as lore_hint
    """
    
    with driver.session() as session:
        result = session.run(query, loc=current_loc).single()
    
    if result:
        state["world_context"] = f"Desc: {result['desc']} | Lore: {result['lore_hint']}"
    else:
        state["world_context"] = "A generic forest path."
    return state

# --- NODE 3: THE NARRATOR (The DM Voice) ---
async def narrator_node(state: AgentState):
    print("--- 🎙️ Narrator: Composing DM Response ---")
    prompt = f"""
    You are a D&D Dungeon Master. 
    LORE: {state['world_context']}
    LOGIC: {state['logic_results']}
    USER SAYS: {state['user_input']}
    
    Write a short, moody response for the group chat. Mention lore details if relevant.
    """
    state["narrative"] = llm.invoke(prompt)
    return state

# --- EXECUTION ---
async def main():
    # Simulate a player entering the tavern we seeded in Neo4j
    initial_state = {
        "user_input": "I walk inside and ask the barkeep for their strongest drink.",
        "game_state": {"location": "The Rusty Tankard", "player_hp": 20},
        "logic_results": {},
        "world_context": "",
        "narrative": ""
    }

    print("\n🚀 STARTING INTEGRATED TEST...\n")
    
    state = await mechanic_node(initial_state)
    state = await chronicler_node(state)
    state = await narrator_node(state)

    print("\n" + "="*50)
    print(f"SYMBOLIC LOGIC: {state['logic_results']}")
    print(f"GRAPH CONTEXT: {state['world_context']}")
    print("-" * 50)
    print(f"FINAL DM MESSAGE: \n{state['narrative']}")
    print("="*50 + "\n")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        driver.close()