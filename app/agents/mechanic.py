# apps/agents/mechanic.py

import json
import re
from langchain_core.messages import SystemMessage, HumanMessage
from app.utils.mechanics_engine import MechanicsEngine
from app.graph.state import AgentState
from app.core.rag_setup import get_retriever
from app.clients import llm

LEVEL_REQUIREMENTS = {
    "world_altering": 17,  # Wish, Reality Warping
    "teleportation": 7,    # Dimension Door, Teleport
    "resurrection": 5,     # Revivify
    "area_destruction": 5  # Fireball, Lightning Bolt
}

async def mechanic_node(state: AgentState):
    #print("--- 🔧 Mechanic: Consulting RAG & Validating Logic ---")
    
    # --- STEP 1: RETRIEVAL ---
    retriever = get_retriever()
    relevant_rules = retriever.invoke(state["user_input"])
    context_str = "\n".join([doc.page_content for doc in relevant_rules])
    
    # --- STEP 2: HYBRID PROMPT (Rules + Intent) ---
    # We combine the RAG context and the categorization task into ONE call to save time/tokens.
    prompt = f"""
    OFFICIAL RULES:
    {context_str}

    CURRENT GAME STATE:
    Player Level: {state['game_state'].get('player_level', 1)}
    User Input: {state['user_input']}

    TASK:
    1. Check if the action is valid based on the OFFICIAL RULES.
    2. Categorize the action: [melee, social, exploration, teleportation, world_altering, area_destruction].
    3. Simulate a 1d20 dice roll.

    Output ONLY JSON:
    {{
        "action": "string",
        "valid": boolean,
        "reason": "string",
        "dice_roll": int,
        "category": "string",
        "intensity": int,
        "is_lore_query": boolean
    }}
    """
    
    response = llm.invoke(prompt)
    
    # --- STEP 3: ROBUST EXTRACTION ---
    try:
        json_str = re.search(r'\{.*\}', response, re.DOTALL).group(0)
        logic_results = json.loads(json_str)
    except Exception as e:
        print(f"Error parsing Mechanic JSON: {e}")
        # Fallback to a safe failure state
        logic_results = {"valid": False, "reason": "System error parsing rules.", "is_lore_query": False}

    # --- STEP 4: SYMBOLIC LEVEL GATE (Deterministic) ---
    # This overrides the LLM if it tries to let a low-level player do high-level magic.
    player_level = state['game_state'].get('player_level', 1)
    action_cat = logic_results.get("category")
    
    LEVEL_REQUIREMENTS = {
        "teleportation": 7,
        "world_altering": 17,
        "area_destruction": 5
    }

    if action_cat in LEVEL_REQUIREMENTS:
        required = LEVEL_REQUIREMENTS[action_cat]
        if player_level < required:
            logic_results["valid"] = False
            logic_results["reason"] = f"Action category '{action_cat}' requires Level {required}. You are only Level {player_level}."

    # --- STEP 5: DYNAMIC ROUTING ---
    # We decide the next path based on the LLM's classification
    if logic_results.get("is_lore_query"):
        state["next_node"] = "chronicler"
    else:
        state["next_node"] = "narrator"

    # Store results
    state["logic_results"] = logic_results
    return state