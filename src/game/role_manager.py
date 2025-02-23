import random
from typing import List, Dict


class RoleManager:
    def __init__(self, players: List[str]):
        print("RoleManager created")
        self.num_players = len(players)
        self.players = players

    def _generate_roles(self) -> List[str]:
        print("Generating roles")
        """Generate role distribution based on player count"""
        if self.num_players < 4:
            raise ValueError("Need at least 4 players")

        num_werewolves = max(1, self.num_players // 4)

        roles = ["werewolf"] * num_werewolves
        roles.extend(["villager"] * (self.num_players - num_werewolves))
        random.shuffle(roles)

        return roles

    def assign_roles(self) -> Dict[str, str]:
        print("Assigning roles")
        """Return map of player names to roles"""
        roles = self._generate_roles()
        if len(roles) != self.num_players:
            raise ValueError(f"Role count mismatch: {len(roles)} roles for {self.num_players} players")

        assignments = {p: r for p, r in zip(self.players, roles)}
        return assignments