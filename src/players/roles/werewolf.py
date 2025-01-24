from src.players.base_player import BaseLLMClient

class Werewolf:
    def __init__(self, name: str, llm_client: BaseLLMClient):
        self.name = name
        self.llm = llm_client
        self.is_alive = True
        self.role = None
    
    def introduce(self) -> str:
        system = f"You are {self.name}, a player in a game of Werewolf. Introduce yourself briefly."
        return self.llm.chat([], system)