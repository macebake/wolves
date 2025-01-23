import os
from dotenv import load_dotenv
from src.game.orchestrator import GameOrchestrator
from src.game.game_state import GameState
from src.game.narrator import Narrator
from src.players.roles import Villager, Werewolf
from src.utils.logger import GameLogger
from src.llm.factory import LLMFactory

def main():
   load_dotenv()
   
   # Initialize LLM clients
   llm_factory = LLMFactory()
   default_llm = os.getenv("DEFAULT_LLM")
   
   # Initialize logger
   logger = GameLogger()
   game_state = GameState()
   
   # Create players with potentially different LLMs
   players = [
       Villager("Alice", llm_factory.create_client(default_llm)),
       Villager("Bob", llm_factory.create_client(default_llm)), 
       Villager("Charlie", llm_factory.create_client(default_llm)),
       Werewolf("Diana", llm_factory.create_client(default_llm))
   ]
   
   # Create narrator with its own LLM
   narrator = Narrator(llm_factory.create_client(default_llm))
   
   orchestrator = GameOrchestrator(
       game_state=game_state,
       players=players,
       narrator=narrator,
       logger=logger
   )
   
   orchestrator.run()

if __name__ == "__main__":
   main()