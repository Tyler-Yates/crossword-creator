from typing import List, Optional, Tuple, Set

from application.data.word_manager import WordManager


class Board:
    """
    Represents a board for a single player
    """

    def __init__(self, player_id: str, board_size: int, word_manager: WordManager):
        self.player_id = player_id
        self.board_size = board_size
        self.board: List[List[Optional[str]]] = [[None for _ in range(board_size)] for _ in range(board_size)]
        self.word_manager = word_manager

    def _set_board(self, board: List[List[Optional[str]]]):
        self.board_size = len(board)
        self.board = board

    def add_tile(self, tile: str, row: int, col: int) -> Optional[str]:
        """
        Adds a tile to the given position on the board.

        Args:
            tile: The tile
            row: The row
            col: The column

        Returns:
            The tile that was previously at that location. Could be None.
        """
        previous_tile = self.board[row][col]
        self.board[row][col] = tile
        return previous_tile

    def remove_tile(self, row: int, col: int) -> Optional[str]:
        """
        Removes the tile from the given position on the board.

        Args:
            row: The row
            col: The column

        Returns:
            The tile that was removed. Could be None.
        """
        removed_tile = self.board[row][col]
        self.board[row][col] = None
        return removed_tile

    def board_is_valid_crossword(self) -> Set[Tuple[int, int]]:
        """
        Returns whether the board represents a valid crossword.

        Returns:
            A set of invalid points on the board. If empty, the board is a valid crossword.
        """
        invalid_points = set()

        # Check across each row
        for row in range(self.board_size):
            current_word = ""
            for col in range(self.board_size):
                tile = self.board[row][col]
                # If the position is blank, it's time to check
                if tile is None:
                    # If we have a current word of length more than 1, check its validity
                    if len(current_word) > 1:
                        # If the word is not valid, add the points to the list of invalid points
                        if not self.word_manager.is_word(current_word):
                            for i in range(len(current_word)):
                                invalid_points.add((row, col - 1 - i))
                    # Now that we are done with our checks, we clear the current word to continue our search
                    current_word = ""
                else:
                    current_word += tile

            # The current word could go to the end of the board so we need to do an additional check
            if not self.word_manager.is_word(current_word):
                for i in range(len(current_word)):
                    invalid_points.add((row, self.board_size - 1 - i))

        # Check down each column
        for col in range(self.board_size):
            current_word = ""
            for row in range(self.board_size):
                tile = self.board[row][col]
                # If the position is blank, it's time to check
                if tile is None:
                    # If we have a current word of length more than 1, check its validity
                    if len(current_word) > 1:
                        # If the word is not valid, add the points to the list of invalid points
                        if not self.word_manager.is_word(current_word):
                            for i in range(len(current_word)):
                                invalid_points.add((row - 1 - i, col))
                    # Now that we are done with our checks, we clear the current word to continue our search
                    current_word = ""
                else:
                    current_word += tile

            # The current word could go to the end of the board so we need to do an additional check
            if not self.word_manager.is_word(current_word):
                for i in range(len(current_word)):
                    invalid_points.add((self.board_size - 1 - i, col))

        return invalid_points
