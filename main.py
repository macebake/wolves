import os
from dotenv import load_dotenv
from src.game.orchestrator import GameOrchestrator
from src.game.game_state import GameState
from src.game.narrator import Narrator
from src.players.base_player import BasePlayer
from src.players.roles.villager import Villager
from src.players.roles.werewolf import Werewolf
from src.utils.logger import GameLogger
from src.llms.factory import LLMFactory
import asyncio

async def main():
    load_dotenv()
    
    llm = LLMFactory().create_client()
    logger = GameLogger()
    narrator = Narrator(llm)
    
    # Create players
    players = [
        BasePlayer(f"Player{i}", llm) for i in range(4)
    ]
    
    orchestrator = GameOrchestrator(players, narrator, logger)

    # Await the run method
    await orchestrator.run()

if __name__ == "__main__":
    asyncio.run(main())