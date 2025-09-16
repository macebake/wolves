class GameState:
    def __init__(self, players: dict):  # players is dict of name -> role
        self.players = players
        self.living_players = set(players.keys())
        self.dead_players = set()
        self.last_deaths = set()
        
    def kill_player(self, player):
        if player.name in self.living_players:
            player.is_alive = False
            self.living_players.remove(player.name)
            self.dead_players.add(player.name)
            self.last_deaths.add(player.name)
        else:
            raise ValueError(f"Cannot kill player '{player.name}' - player is not alive")

    def is_game_over(self) -> bool:
        werewolves = sum(
            1 for p in self.living_players 
            if self.players[p] == "werewolf"
        )
        villagers = len(self.living_players) - werewolves
        return werewolves == 0 or werewolves >= villagers