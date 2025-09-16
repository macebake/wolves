import os
from dotenv import load_dotenv
from src.game.orchestrator import GameOrchestrator
from src.game.game_state import GameState
from src.game.narrator import Narrator
from src.game.roles import BasePlayer, Villager, Werewolf
from src.game.logger import GameLogger
from src.llms.factory import LLMFactory


def main():
    load_dotenv()

    llm = LLMFactory().create_client()
    logger = GameLogger()
    narrator = Narrator(llm)

    # Create players
    players = [
        BasePlayer(LLMFactory().create_client()) for i in range(7)
    ]

    orchestrator = GameOrchestrator(players, narrator, logger)

    # the run method
    orchestrator.run()

if __name__ == "__main__":
    for i in range(100):
        main()