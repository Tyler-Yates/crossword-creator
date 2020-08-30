from application.data.board import Board
from tests.data.test_word_manager import TestWordManager


class TestBoard:
    def setup_method(self):
        # Create a word manager that accepts any word
        self.word_manager = TestWordManager()

    def test_valid_board(self):
        tiles = [
            ["d", None, "b", "a", "d"],
            ["a", None, "a", "s", None],
            ["d", "a", "d", None, None],
            ["s", None, None, None, None],
            [None, None, None, None, None],
        ]

        board = Board("test", 5, TestWordManager({"dads", "dad", "bad", "as"}))
        board._set_board(tiles)

        invalid_points = board.board_is_valid_crossword()
        assert [] == invalid_points

    def test_invalid_board(self):
        tiles = [
            ["d", None, "b", "a", "d"],
            ["a", None, "a", "z", None],
            ["d", "a", "d", None, None],
            ["s", None, None, None, None],
            [None, None, None, None, None],
        ]

        board = Board("test", 5, TestWordManager({"dads", "dad", "bad", "as"}))
        board._set_board(tiles)

        invalid_points = board.board_is_valid_crossword()
        assert {(0, 3), (1, 2), (1, 3)} == invalid_points
