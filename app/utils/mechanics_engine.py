from app.schema.player import GameState

class MechanicsEngine:
    """The 'Symbolic' engine that handles deterministic game rules."""
    
    @staticmethod
    def apply_damage(state: GameState, target_id: str, amount: int) -> GameState:
        for player in state.party:
            if player.id == target_id:
                player.stats.hp = max(0, player.stats.hp - amount)
                state.log.append(f"{player.name} took {amount} damage. HP: {player.stats.hp}")
        return state

    @staticmethod
    def update_inventory(state: GameState, player_id: str, item: str, action: str = "add") -> GameState:
        for player in state.party:
            if player.id == player_id:
                if action == "add":
                    player.inventory.append(item)
                elif action == "remove" and item in player.inventory:
                    player.inventory.remove(item)
        return state