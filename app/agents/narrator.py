# apps/agents/narrator.py

from neo4j import GraphDatabase
from app.graph.state import AgentState

async def narrator_node(state: AgentState):
    system_prompt = """
    You are an Expert D&D Dungeon Master. 
    Use the following inputs to write a short, atmospheric group-chat message:
    1. MECHANIC: {logic}
    2. WORLD CONTEXT: {context}
    3. DM PERSONA: Grim, descriptive, focuses on sensory details.
    
    Rule: Never break character. Never mention the word 'JSON' or 'Database'.
    """
    
    formatted_prompt = system_prompt.format(
        logic=state["logic_results"],
        context=state["world_context"]
    )
    
    # Call Llama 3.2 for the creative output
    response = llm.invoke(formatted_prompt + f"\nUser said: {state['user_input']}")
    
    return {"narrative": response}


async def proxy_node(state: AgentState):
    print("--- 🤖 Proxy Player is deciding... ---")
    
    # We find the active proxy player from the game state
    active_player = [p for p in state["game_state"]["party"] if p["is_ai_proxy"]][0]
    
    prompt = f"""
    You are playing a D&D character: {active_player['name']}.
    Your Personality: {active_player['persona_profile']}
    Current Situation: {state['narrative']}
    
    Based on your personality, what do you do? 
    Output in character for the group chat. Keep it short.
    """
    
    response = llm.invoke(prompt)
    
    # We append the proxy's action to the history
    state["history"].append(f"{active_player['name']}: {response}")
    return state