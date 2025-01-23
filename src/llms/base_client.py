class BaseLLMClient(ABC):
   @abstractmethod
   async def chat(self, messages: list, system: str) -> str:
       """
       Send a chat message to the LLM.
       
       Args:
           messages: List of message dicts with 'role' and 'content'
           system: System prompt string
           
       Returns:
           str: The LLM's response
       """
       pass