# apps/agents/chronicler.py

from neo4j import GraphDatabase
from app.graph.state import AgentState

# Database Connector
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))

async def chronicler_node(state: AgentState):
    intent = state["logic_results"].get("action_type")
    target = state["logic_results"].get("target_id")

    logic = state["logic_results"]
    game_state = state["game_state"]
    location = game_state.get("location", "Unknown")
    
    # TASK 1: PUSH - Update the Graph with what just happened
    # We record that a 'Player' performed an 'Action' in a 'Location'
    with driver.session() as session:
        session.run("""
            MATCH (l:Location {name: $loc})
            MERGE (p:Player {id: $pid})
            CREATE (p)-[:PERFORMED {action: $act, roll: $roll, success: $suc}]->(l)
        """, loc=location, pid="player_01", act=logic['action'], 
             roll=logic['actual_roll'], suc=logic['success'])

    # TASK 2: PULL - Retrieve context for the Narrator
    # Let's see if this location has any specific 'Rumors' or 'Threats'
    with driver.session() as session:
        result = session.run("""
            MATCH (l:Location {name: $loc})-[:HAS_LORE]->(lore:Lore)
            RETURN lore.text AS lore_text
        """, loc=location).single()
    
    state["world_context"] = result["lore_text"] if result else "No specific lore found for this area."
    
    return state