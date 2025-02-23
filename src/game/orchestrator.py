from src.game.game_state import GameState
from src.game.narrator import Narrator
from src.game.logger import GameLogger
from src.game.conversation import GameMessage
from src.game.conversation import ConversationManager
from src.game.role_manager import RoleManager
from typing import List
from src.game.roles import BasePlayer, Villager, Werewolf


class GameOrchestrator:
    def __init__(self, players: List[BasePlayer], narrator: Narrator, logger: GameLogger):
        self.players = players
        self.narrator = narrator
        self.logger = logger
        self.conversation = ConversationManager()
        self.role_manager = None  # Will be initialized after introductions
        self.game_state = None

    def run(self):
        self.logger.log({"event": "game_start"})
        self.introduction_phase()
        self.role_assignment_phase()
        
        while not self.game_state.is_game_over():
            self.logger.log({"event": "night_phase_start"})
            self.night_phase()
            if self.game_state.is_game_over():
                break
            
            self.logger.log({"event": "day_phase_start"})
            self.day_phase()
            
        self.end_game()

    def introduction_phase(self):
        self.logger.log({"event": "introduction_phase_start"})
        for player in self.players:
            intro = player.introduce(existing_names=[p.name for p in self.players if p.name])
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
        # Initialize role manager after all players have introduced themselves
        self.role_manager = RoleManager([p.name for p in self.players])
        self.logger.log({"event": "introduction_phase_end"})

    def role_assignment_phase(self):
        print("Starting role assignment phase")
        if not self.role_manager:
            raise ValueError("Role manager not initialized - introduction phase must be completed first")
            
        roles = self.role_manager.assign_roles()
        for player in self.players:
            role = roles[player.name]
            # Create new player instance of correct type
            if role == "werewolf":
                new_player = Werewolf(player.llm)
            else:
                new_player = Villager(player.llm)
            
            # Transfer existing player state
            new_player.name = player.name
            new_player.is_alive = player.is_alive
            
            # Replace player in list
            self.players[self.players.index(player)] = new_player
            
            # Assign role and log
            self.conversation.assign_role(player.name, role)
            self.logger.log({
                "event": "role_assigned",
                "data": {"player": player.name, "role": role}
            })
        
        self.game_state = GameState(roles)

    def get_message(self, history: List[GameMessage]) -> dict:
        print("Getting message")
        system = f"You are {self.name}, a {self.role}. Given the game state, share your thoughts about who might be a werewolf and why."
        messages = [{"content": msg.content} for msg in history]
        messages.append({"content": system})
        response = self.llm.get_response(messages)
        return {"wants_to_speak": True, "message": response}

    def night_phase(self):
        print("Starting night phase")
        # Announce night falling
        night_start = self.narrator.announce_night()
        self.conversation.add_message(GameMessage(
            phase="night",
            player="narrator",
            content=night_start,
            visibility="public"
        ))
        self.logger.log({
            "event": "night_start",
            "data": {"message": night_start}
        })

        # Werewolves choose victim
        werewolves = [p for p in self.players if p.role == "werewolf" and p.is_alive]
        if werewolves:
            # Let werewolves deliberate
            for wolf in werewolves:
                decision = wolf.get_message(self.conversation.get_player_history(wolf.name))
                self.conversation.add_message(GameMessage(
                    phase="night",
                    player=wolf.name,
                    content=decision,
                    visibility="private"  # Only other werewolves can see
                ))
                self.logger.log({
                    "event": "werewolf_deliberation",
                    "data": {
                        "player": wolf.name,
                        "message": decision
                    }
                })

            victim = self._conduct_werewolf_vote(werewolves)
            self.game_state.kill_player(victim)
            self.logger.log({
                "event": "werewolf_kill",
                "data": {"victim": victim}
            })

        # Announce night ending
        night_end = self.narrator.announce_dawn()
        self.conversation.add_message(GameMessage(
            phase="night",
            player="narrator",
            content=night_end,
            visibility="public"
        ))

    def _conduct_werewolf_vote(self, werewolves: List[BasePlayer]) -> str:
        print("Conducting werewolf vote")
        # For now, just pick first living non-werewolf
        living_villagers = [
            p.name for p in self.players 
            if p.role != "werewolf"
            and p.is_alive
        ]
        return living_villagers[0] if living_villagers else None

    def _conduct_vote(self) -> str:
        print("Conducting vote")
        # For now, just pick first living player
        living = list(self.players)
        return living[0] if living else None

    def day_phase(self):
        print("Starting day phase")
        # Announce deaths
        deaths = self.narrator.announce_deaths(self.game_state.last_deaths)
        message = GameMessage(phase="day", player="narrator", content=deaths)
        self.conversation.add_message(message)
        self.logger.log({
            "event": "day_start",
            "data": {"deaths": list(self.game_state.last_deaths), "message": deaths}
        })

        for player in deaths:
            self.game_state.kill_player(player)
        
        discussion_ended = False
        while not discussion_ended:
            alive_players = [p for p in self.game_state.living_players]
            for player in alive_players:
                response = player.get_message(self.conversation.get_player_history(player.name))
                message = GameMessage(
                    phase="discussion",
                    player=player.name,
                    content=response,
                    visibility="public"
                )
                self.conversation.add_message(message)
                self.logger.log({
                    "event": "player_discussion",
                    "data": {"player": player.name, "message": response}
                })
            
            discussion_ended = self.narrator.should_start_vote(
                self.conversation.get_player_history("narrator")
            )
        
        vote_announcement = self.narrator.announce_vote()
        self.conversation.add_message(GameMessage(
            phase="voting",
            player="narrator",
            content=vote_announcement
        ))
        self.logger.log({
            "event": "voting_start",
            "data": {"message": vote_announcement}
        })

        exile = self._conduct_vote()
        self.game_state.kill_player(exile)
        self.logger.log({
            "event": "player_exiled",
            "data": {"player": exile}
        })
           
    def _conduct_discussion(self):
        print("Conducting discussion")
        alive_players = [p for p in self.game_state.living_players]
        for player in alive_players:
            response = player.get_message(self.conversation.get_player_history(player.name))
            message = GameMessage(
                phase="discussion",
                player=player.name,
                content=response,
                visibility="public"
            )
            self.conversation.add_message(message)
            self.logger.log({
                "event": "player_discussion",
                "data": {"player": player.name, "message": response}
            })

    def end_game(self):
        print("Ending game")
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
