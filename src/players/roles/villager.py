from src.players.base_player import BasePlayer, BaseLLMClient

class Villager(BasePlayer):
    def __init__(self, name: str, llm_client: BaseLLMClient):
        super().__init__(name, llm_client)
        self.role = "villager"