import logging
from typing import Dict, List, Tuple, Optional

from application.data.board import Board
from application.data.tiles import Tiles
from application.data.word_manager import WordManager

STARTING_TILES_PER_PLAYER = 20
TILES_PER_PLAYER = STARTING_TILES_PER_PLAYER * 2
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
        self.player_ids_to_tiles: Dict[str, List[str]] = {}
        self.player_ids_to_boards: Dict[str, Board] = {}

        self.tiles_left = -1
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
            self.player_ids_to_boards[player_id] = Board(player_id, BOARD_SIZE, self.word_manager)
            self.player_ids_to_tiles[player_id] = []
            return True

    def start_game(self):
        self.tiles_left = TILES_PER_PLAYER * len(self.player_ids_to_names.keys())
        self._generate_player_tiles()
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
            # Add the board data to the response
            game_state["hand_tiles"] = self.player_ids_to_tiles[player_id]
            game_state = {**game_state, **self.player_ids_to_boards[player_id].get_json()}
        return game_state

    def add_tile(self, player_id: str, hand_tile_index: int, board_position: Tuple[int, int]) -> None:
        """
        Adds the tile with the given index in the player's hand to their board at the given position.

        Args:
            player_id: The ID of the player
            hand_tile_index: The index of the tile in the player's hand
            board_position: The position on the board
        """
        # Remove the tile from the player's hand
        tile = self.player_ids_to_tiles[player_id].pop(hand_tile_index)

        # Add the tile we are replacing if the position on the board already has a tile
        replaced_tile = self.player_ids_to_boards[player_id].add_tile(tile, board_position[0], board_position[1])
        if replaced_tile:
            self.player_ids_to_tiles[player_id].append(replaced_tile)

    def _generate_player_tiles(self):
        for player_id in self.player_ids_to_tiles.keys():
            self.player_ids_to_tiles[player_id] = Tiles.generate_tiles(STARTING_TILES_PER_PLAYER)
            self.tiles_left -= STARTING_TILES_PER_PLAYER

    def _log_info(self, log_message: str):
        LOG.info("[%s] %s", self.game_name, log_message)
