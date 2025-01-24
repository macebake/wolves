from src.llms.base_client import BaseLLMClient

class BasePlayer:
    def __init__(self, name: str, llm_client: BaseLLMClient):
        self.name = name
        self.llm = llm_client
        self.is_alive = True
        self.role = None
        
    async def introduce(self) -> str:
        system = f"You are {self.name}, a player in a game of Werewolf. Introduce yourself briefly."
        return await self.llm.chat([], system)
        
    async def get_message(self, history: list) -> dict:
        system = f"You are {self.name}, a {self.role}. Decide if you want to speak."
        response = await self.llm.chat(history, system)
        return json.loads(response)