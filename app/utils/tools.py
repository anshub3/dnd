def roll_dice(sides: int = 20):
    import random
    return random.randint(1, sides)

def update_hp(player_id: str, amount: int, game_state: dict):
    # Logic to find player and subtract/add HP
    for p in game_state['party']:
        if p['id'] == player_id:
            p['stats']['hp'] += amount
    return game_state