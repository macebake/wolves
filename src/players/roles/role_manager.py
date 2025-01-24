import random
from typing import List, Dict

class RoleManager:
    def __init__(self, num_players: int):
        self.num_players = num_players
        self.roles = self._generate_roles()
        
    def _generate_roles(self) -> List[str]:
        """Generate role distribution based on player count"""
        if self.num_players < 4:
            raise ValueError("Need at least 4 players")
            
        num_werewolves = max(1, self.num_players // 4)
        roles = ["werewolf"] * num_werewolves
        roles.extend(["villager"] * (self.num_players - num_werewolves))
        random.shuffle(roles)
        return roles
        
    def assign_roles(self) -> Dict[str, str]:
        """Return map of player names to roles"""
        if len(self.roles) != self.num_players:
            raise ValueError("Role count mismatch")
        return {p: r for p, r in zip(self.players, self.roles)}