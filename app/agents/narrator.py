# apps/agents/narrator.py

from neo4j import GraphDatabase
from app.graph.state import AgentState

'''async def narrator_node(state: AgentState):
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
    
    return {"narrative": response}'''

async def narrator_node(state: AgentState):
    print("--- 🎙️ Narrator: Weaving Lore and Logic ---")
    logic = state["logic_results"]

    if not logic.get("valid", True):
        prompt = f"""
        The player attempted: {state['user_input']}
        The rules forbid this because: {logic.get('reason')}
        
        TASK: In your DM voice, describe the player's attempt failing. 
        Make it sound like a natural part of the world (e.g., the door is too heavy, the magic fizzles).
        Do not mention 'rules' or 'JSON'.
        """
    else:  
        prompt = f"""
        SYSTEM: You are the Dungeon Master. 
        LORE CONTEXT: {state['world_context']}
        MECHANIC RESULT: {state['logic_results']}
        RECENT CHAT HISTORY: {state['history'][-3:]}
        
        USER ACTION: {state['user_input']}
        
        TASK: Write a response for the group chat that progresses the story. 
        If the Lore Context mentions a secret or a specific smell/vibe, weave it into the description of the player's action.
        Do not repeat descriptions already mentioned in the history.
        """
    
    state["narrative"] = llm.invoke(prompt)
    return state


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