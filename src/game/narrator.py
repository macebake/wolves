from src.llms.base_client import BaseLLMClient

class Narrator:
    def __init__(self, llm_client: BaseLLMClient):
        self.llm = llm_client
        
    async def announce_deaths(self, deaths: set) -> str:
        system = "You are the narrator. Announce the deaths dramatically but briefly."
        return await self.llm.chat([{"content": str(deaths)}], system)