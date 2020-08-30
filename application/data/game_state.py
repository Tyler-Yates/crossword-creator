import logging
from typing import Dict

from application.data.board import Board
from application.data.word_manager import WordManager

TILES_PER_PLAYER = 40
BOARD_SIZE = 25

LOG = logging.getLogger("GameState")


class GameState:
    """
    Class representing the state of a game.
    """

    def __init__(self, game_name: str, word_manager: WordManager):
        """
        Generates a new game state.
        """
        self.game_name = game_name
        self.word_manager = word_manager

        self.player_ids_to_names = {}
        self.player_ids_to_boards: Dict[str, Board] = {}

        self.game_running = False

    def new_player(self, player_id: str, player_name: str) -> bool:
        """
        Method to call when a new player joins the game.
        Players can only join games that are not in progress.

        Args:
            player_id: The ID of the player
            player_name: The display name of the player

        Returns:
            True if the player successfully joined the game, False otherwise.
        """

        if self.game_running:
            self._log_info(f"Player {player_id}/{player_name} attempted to join a game that has already started.")
            return False
        else:
            self._log_info(f"Player {player_id}/{player_name} has joined game.")
            self.player_ids_to_names[player_id] = player_name
            return True

    def start_game(self):
        self.game_running = True
        self._log_info("Game started")

    def end_game(self):
        self.game_running = False
        self._log_info("Game ended")

    def get_game_state(self, player_id: str = None) -> Dict[str, object]:
        """
        Returns the state of the game when a player joins or reloads the game.

        Args:
            player_id: the ID of the player joining or reloading the game

        Returns:
            the game state
        """
        game_state = {"num_players": len(self.player_ids_to_names)}
        if player_id:
            # Set is not serializable so turn it into a set
            game_state["player_guesses"] = list(self.valid_guesses.get(player_id, {}))
            game_state["player_total_score"] = self.scores.get(player_id, 0)
        else:
            # No player_id indicates a reset of the game so send empty guesses list
            game_state["player_guesses"] = []
        return game_state

    def _log_info(self, log_message: str):
        LOG.info("[%s] %s", self.game_name, log_message)
