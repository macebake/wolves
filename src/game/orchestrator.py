from src.game.game_state import GameState
from src.game.narrator import Narrator
from src.utils.logger import GameLogger
from src.conversation.message import GameMessage
from src.conversation.history import ConversationManager
from src.players.roles.role_manager import RoleManager
from typing import List
from src.players.base_player import BasePlayer

class GameOrchestrator:
    def __init__(self, players: List[BasePlayer], narrator: Narrator, logger: GameLogger):
        self.players = players
        self.narrator = narrator
        self.logger = logger
        self.conversation = ConversationManager()
        self.role_manager = RoleManager([p.name for p in players])
        self.game_state = None

    async def run(self):
        self.logger.log({"event": "game_start"})
        await self.introduction_phase()
        await self.role_assignment_phase()
        
        while not self.game_state.is_game_over():
            self.logger.log({"event": "night_phase_start"})
            await self.night_phase()
            if self.game_state.is_game_over():
                break
            
            self.logger.log({"event": "day_phase_start"})
            await self.day_phase()
            
        await self.end_game()

    async def introduction_phase(self):
        self.logger.log({"event": "introduction_phase_start"})
        for player in self.players:
            intro = await player.introduce()
            message = {
                "phase": "intro",
                "player": player.name,
                "content": intro
            }
            self.conversation.add_message(GameMessage(**message))
            self.logger.log({
                "event": "player_introduction",
                "data": message
            })
        self.logger.log({"event": "introduction_phase_end"})

    async def role_assignment_phase(self):
        roles = self.role_manager.assign_roles()
        for player in self.players:
            role = roles[player.name]
            player.role = role
            self.conversation.assign_role(player.name, role)
            self.logger.log({
                "event": "role_assigned",
                "data": {"player": player.name, "role": role}
            })
        
        self.game_state = GameState(roles)

    async def get_message(self, player: BasePlayer):
        history = self.conversation.get_player_history(player.name)
        return await player.get_message(history)

    async def night_phase(self):
       # Werewolves choose victim
       werewolves = [p for p in self.players if p.role == "werewolf" and p.is_alive]
       if werewolves:
           victim = await self._conduct_werewolf_vote(werewolves)
           self.game_state.kill_player(victim)

    async def _conduct_werewolf_vote(self, werewolves: List[BasePlayer]) -> str:
        # For now, just pick first living non-werewolf
        living_villagers = [p.name for p in self.players 
                        if p.name in self.game_state.living_players 
                        and p.role != "werewolf"]
        return living_villagers[0] if living_villagers else None

    async def _conduct_vote(self) -> str:
        # For now, just pick first living player
        living = list(self.game_state.living_players)
        return living[0] if living else None
           
    async def day_phase(self):
        deaths = await self.narrator.announce_deaths(self.game_state.last_deaths)
        message = {
            "phase": "day",
            "player": "narrator",
            "content": deaths
        }
        self.conversation.add_message(GameMessage(**message))
        self.logger.log({
            "event": "deaths_announced",
            "data": message
        })
        
        await self._conduct_discussion()
        
        if self.game_state.living_players():
            exile = await self._conduct_vote()
            self.game_state.exile_player(exile)
            self.logger.log({
                "event": "player_exiled",
                "data": {"player": exile}
            })
           
    async def _conduct_discussion(self):
        alive_players = [p for p in self.players if p.is_alive]
        for player in alive_players:
            response = await player.get_message(self.conversation.get_player_history(player.name))
            if isinstance(response, str) or response.get("wants_to_speak"):
                message = GameMessage(
                    phase="discussion",
                    player=player.name,
                    content=response if isinstance(response, str) else response["message"],
                    visibility="public"
                )
                self.conversation.add_message(message)

    async def end_game(self):
        """End the game and log final state."""
        game_over_msg = "Game Over!"
        final_message = GameMessage(
            phase="end",
            player="narrator",
            content=game_over_msg,
            visibility="public"
        )
        self.conversation.add_message(final_message)
        self.logger.log({
            "event": "game_end",
            "data": {"message": game_over_msg}
        })
