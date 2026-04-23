from neo4j import GraphDatabase
from app.graph.state import AgentState

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))

async def chronicler_node(state: AgentState):
    print("--- 📚 Chronicler: Fetching Relational Context ---")
    
    # Get current location from GameState (Postgres-sourced)
    current_loc = state["game_state"].get("location", "The Rusty Tankard")
    
    # Complex Query: Find the location's lore AND any NPCs living there
    query = """
    MATCH (l:Location {name: $loc})
    OPTIONAL MATCH (l)-[:HAS_LORE]->(lore:Lore)
    OPTIONAL MATCH (npc:NPC)-[:LIVES_AT]->(l)
    RETURN l.description as desc, lore.text as lore_hint, npc.name as npc_name
    """
    
    with driver.session() as session:
        result = session.run(query, loc=current_loc).single()
    
    if result:
        # We package this context for the Narrator
        context = f"Location Description: {result['desc']}. "
        context += f"Rumors: {result['lore_hint']}. "
        context += f"Characters Present: {result['npc_name']}."
        state["world_context"] = context
    else:
        state["world_context"] = "A nondescript area with no notable features."

    return state