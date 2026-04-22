# apps/agents/chronicler.py

from neo4j import GraphDatabase
from app.graph.state import AgentState

# Database Connector
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))

async def chronicler_node(state: AgentState):
    intent = state["logic_results"].get("action_type")
    target = state["logic_results"].get("target_id")
    
    # Complex Query: Find the target and their allegiances
    query = """
    MATCH (t:Entity {id: $target_id})-[:ALLEGIANCE_TO]->(f:Faction)
    MATCH (f)-[:ENEMIES_WITH]->(p_faction:Faction)
    RETURN f.name as faction, p_faction.name as enemy_faction
    """
    
    with driver.session() as session:
        result = session.run(query, target_id=target).single()
    
    context = ""
    if result:
        context = f"The target belongs to {result['faction']}, who are bitter rivals with {result['enemy_faction']}."
        
    return {"world_context": context}