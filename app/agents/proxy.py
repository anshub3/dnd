# app/agents/proxy.py

from app.graph.state import AgentState
from app.clients import llm

def _find_active_proxy(game_state: dict):
    return next(
        (player for player in game_state.get("party", []) if player.get("is_ai_proxy")),
        None
    )


async def proxy_node(state: AgentState):
    narrative_context = state["narrative"]
    active_proxy = _find_active_proxy(state["game_state"])

    if active_proxy:
        name = active_proxy["name"]
        persona = active_proxy.get("persona_profile", {"voice": "neutral", "bias": "balanced"})
    else:
        name = state["game_state"].get("active_proxy_name", "Proxy")
        persona = state["game_state"].get(
            "proxy_persona",
            {"voice": "neutral", "bias": "balanced"}
        )

    prompt = f"""
    You are a player in a D&D game.
    CHARACTER: {name}
    PERSONALITY: {persona.get('voice', 'neutral')}
    TACTICAL BIAS: {persona.get('bias', 'balanced')}

    THE DM JUST SAID: "{narrative_context}"

    TASK: Write a short response in the group chat.
    1. Stay in character.
    2. Decide on one action (speak, move, or attack).
    3. Keep it to 1-2 sentences.
    """

    response = llm.invoke(prompt)

    proxy_msg = f"[{name}]: {response}"
    state["history"].append(proxy_msg)

    return state