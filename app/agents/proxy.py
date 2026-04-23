# app/agent/proxy.py

from app.graph.state import AgentState

async def proxy_node(state: AgentState):
    print(f"--- 🤖 Proxy: Acting as {state['active_proxy_name']} ---")
    
    # We pull the persona and the current situation
    persona = state["game_state"]["active_proxy_persona"]
    narrative_context = state["narrative"]
    
    prompt = f"""
    You are a player in a D&D game. 
    CHARACTER: {state['active_proxy_name']}
    PERSONALITY: {persona['voice_style']}
    TACTICAL BIAS: {persona['bias']}
    
    THE DM JUST SAID: "{narrative_context}"
    
    TASK: Write a short response in the group chat. 
    1. Stay in character.
    2. Decide on one action (speak, move, or attack).
    3. Keep it to 1-2 sentences.
    """
    
    response = llm.invoke(prompt)
    
    # We add this to the "Group Chat" history
    proxy_msg = f"[{state['active_proxy_name']}]: {response}"
    state["history"].append(proxy_msg)
    
    return state