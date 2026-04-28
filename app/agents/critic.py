import json
from app.graph.state import AgentState
from app.clients import llm

async def critic_node(state: AgentState):
    print("--- 🧐 Critic: Auditing Narrative against Rules ---")
    
    narrative = state["narrative"]
    logic = state["logic_results"]
    
    prompt = f"""
    You are the D&D Consistency Auditor. 
    Compare the DM's Story with the Mechanical Fact.
    
    MECHANICAL FACT: {logic}
    DM'S STORY: "{narrative}"
    
    CRITERIA:
    1. If Logic says 'success: false' but Story says they succeeded, it is an ERROR.
    2. If Logic says 'damage: 10' but Story says they are 'unscathed', it is an ERROR.
    3. If the Story mentions an item/spell not in the Logic results, it is an ERROR.

    Does the story pass? Answer ONLY in JSON:
    {{"pass": boolean, "feedback": "string explaining the error if pass is false"}}
    """
    
    response = llm.invoke(prompt)
    audit_results = json.loads(extract_json(response))
    
    # Store the audit in the state so the Narrator knows what to fix
    state["audit_feedback"] = audit_results.get("feedback", "")
    state["passed_audit"] = audit_results.get("pass", True)
    
    return state