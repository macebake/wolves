class GameState:
    def __init__(self, players: dict):  # players is dict of name -> role
        print("GameState created")
        self.players = players
        self.living_players = set(players.keys())
        self.dead_players = set()
        self.last_deaths = set()
        
    def kill_player(self, player_name: str):
        # Validate that this is actually a player in the game
        if player_name not in self.players:
            raise ValueError(f"Cannot kill player '{player_name}' - not a valid player name")
            
        # Only kill if they're actually alive
        if player_name in self.living_players:
            print(f"Killing player: {player_name}")
            self.living_players.remove(player_name)
            self.dead_players.add(player_name)
            self.last_deaths.add(player_name)
        else:
            print(f"Player {player_name} is already dead or not in game")

    def is_game_over(self) -> bool:
        print("Checking if game is over")
        werewolves = sum(
            1 for p in self.living_players 
            if self.players[p] == "werewolf"
        )
        villagers = len(self.living_players) - werewolves
        return werewolves == 0 or werewolves >= villagers