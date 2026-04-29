import json
from app.graph.state import AgentState
from app.clients import llm, get_neo4j_session
from app.utils.tools import extract_json


async def chronicler_node(state: AgentState):
    print("--- 📚 Chronicler: Fetching Relational Context ---")
    
    # Get current location from GameState (Postgres-sourced)
    current_loc = state["game_state"].get(
        "current_location",
        state["game_state"].get("location", "The Rusty Tankard")
    )
    
    # Complex Query: Find the location's lore AND any NPCs living there
    query = """
    MATCH (l:Location {name: $loc})
    OPTIONAL MATCH (l)-[:HAS_LORE]->(lore:Lore)
    OPTIONAL MATCH (npc:NPC)-[:LIVES_AT]->(l)
    RETURN l.description as desc, lore.text as lore_hint, npc.name as npc_name
    """
    
    with get_neo4j_session() as session:
        result = session.run(query, loc=current_loc).single()
    
    '''
    if result:
        # We package this context for the Narrator
        context = f"Location Description: {result['desc']}. "
        context += f"Rumors: {result['lore_hint']}. "
        context += f"Characters Present: {result['npc_name']}."
        state["world_context"] = context
    else:
        state["world_context"] = "A nondescript area with no notable features."
    '''
    if not result:        
        # Ask Llama to generate lore based on the context of the journey
        discovery_prompt = f"""
        The players have just arrived at a new location: {current_loc}.
        Based on the current journey, describe this place in 2 sentences. 
        Assign it a 'Vibe' (e.g. Creepy, Majestic, Ruined).
        Return JSON: {{"description": "...", "vibe": "..."}}
        """
        
        response = llm.invoke(discovery_prompt)
        # Use our regex extraction logic here
        discovery_data = json.loads(extract_json(response))
        
        # 3. Commit to the Graph (Write-Back)
        with get_neo4j_session() as session:
            session.run("""
                CREATE (l:Location {name: $name, description: $desc, vibe: $vibe})
            """, name=current_loc, desc=discovery_data['description'], vibe=discovery_data['vibe'])
        
        state["world_context"] = discovery_data['description']
    else:
        # We package this context for the Narrator
        context = f"Location Description: {result['desc']}. "
        context += f"Rumors: {result['lore_hint']}. "
        context += f"Characters Present: {result['npc_name']}."
        state["world_context"] = context

    return state