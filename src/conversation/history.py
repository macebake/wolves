from dataclasses import dataclass
from typing import List, Dict

@dataclass
class GameMessage:
    phase: str
    player: str
    content: str
    visibility: str = "public"  # public, private, or narrator
    
class ConversationManager:
    def __init__(self):
        self.messages: List[GameMessage] = []
        self.player_roles: Dict[str, str] = {}
        
    def add_message(self, message: GameMessage):
        self.messages.append(message)
        
    def assign_role(self, player_name: str, role: str):
        self.player_roles[player_name] = role
        self.add_message(GameMessage(
            phase="role_assignment",
            player=player_name,
            content=f"You are a {role}",
            visibility="private"
        ))
        
    def get_player_history(self, player_name: str) -> List[GameMessage]:
        return [
            msg for msg in self.messages 
            if msg.visibility == "public" or 
               (msg.visibility == "private" and msg.player == player_name)
        ]