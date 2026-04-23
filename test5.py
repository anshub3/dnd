import asyncio
from app.core.database import update_db_state, load_db_state

async def test_persistence():
    GID = "college_project_test_1"
    
    # 1. Mock Data
    initial_state = {"location": "The Rusty Tankard", "party": [{"name": "Valerius", "hp": 10}]}
    initial_history = ["DM: Welcome to the tavern."]
    
    print("--- 💾 Saving initial state ---")
    update_db_state(GID, initial_state, initial_history)
    
    # 2. Simulate loading it back
    print("--- 🔄 Loading state back ---")
    recovered_state, recovered_history = load_db_state(GID)
    
    print(f"Recovered Location: {recovered_state['location']}")
    print(f"Recovered HP: {recovered_state['party'][0]['hp']}")
    
    if recovered_state['location'] == "The Rusty Tankard":
        print("\n✅ DB Persistence check passed!")
    else:
        print("\n❌ DB Persistence check failed.")

if __name__ == "__main__":
    asyncio.run(test_persistence())