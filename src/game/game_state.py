class GameState:
    def __init__(self, players: dict):  # players is dict of name -> role
        self.players = players
        self.living_players = set(players.keys())
        self.dead_players = set()
        self.last_deaths = set()
        
    def kill_player(self, player_name: str):
        if player_name in self.living_players:
            self.living_players.remove(player_name)
            self.dead_players.add(player_name)
            self.last_deaths.add(player_name)
        
    def exile_player(self, player_name: str):
        self.kill_player(player_name)
        
    def is_game_over(self) -> bool:
        werewolves = sum(1 for p in self.living_players 
                        if self.players[p] == "werewolf")
        villagers = len(self.living_players) - werewolves
        return werewolves == 0 or werewolves >= villagers