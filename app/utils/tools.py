def roll_dice(sides: int = 20):
    import random
    return random.randint(1, sides)


def extract_json(text: str) -> str:
    """Find and extract JSON from a string, even if wrapped in markdown."""
    import re
    match = re.search(r'\{.*\}', text, re.DOTALL)
    return match.group(0) if match else text

def update_hp(player_id: str, amount: int, game_state: dict):
    # Logic to find player and subtract/add HP
    for p in game_state['party']:
        if p['id'] == player_id:
            p['stats']['hp'] += amount
    return game_state