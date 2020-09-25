import logging

import flask
from flask import current_app
from flask_socketio import emit, join_room

from application import GameManager, GAME_MANAGER_CONFIG_KEY
from .. import socketio

LOG = logging.getLogger("GameState")


@socketio.on("join")
def joined_event(message):
    """
    Received when a player joins a game.
    """

    room = message["room"]
    join_room(room)

    player_id = _get_player_id()

    game_state = _get_game_manager().get_game_state(room)
    if game_state:
        LOG.info(f"User {player_id} has joined room {room}")
        # All players should update their game status now that a new player has joined
        player_name = game_state.player_ids_to_names.get(player_id)
        update = {"request_update": True, "message": f"Player {player_name} has joined the game"}
        emit("request_update", update, room=room)
    else:
        LOG.warning(f"User {player_id} has joined invalid room {room}")


@socketio.on("add_tile")
def add_tile_event(message):
    """
    Received when a player guesses a word.
    """

    session_id = flask.request.sid
    player_id = _get_player_id()
    LOG.debug(f"Received add_tile from {player_id}: {message}")

    room = message["room"]
    hand_tile_index = message["hand_tile_index"]
    board_position = message["board_position"]

    game_state = _get_game_manager().get_game_state(room)
    game_state.add_tile(player_id, hand_tile_index, (board_position[0], board_position[1]))

    emit("board_update", game_state.get_game_state(player_id), to=session_id)


@socketio.on("remove_tile")
def remove_tile_event(message):
    """
    Received when a player guesses a word.
    """

    session_id = flask.request.sid
    player_id = _get_player_id()
    LOG.debug(f"Received remove_tile from {player_id}: {message}")

    room = message["room"]
    board_position = message["board_position"]

    game_state = _get_game_manager().get_game_state(room)
    game_state.remove_tile(player_id, board_position)

    emit("board_update", game_state.get_game_state(player_id), to=session_id)


@socketio.on("start_game")
def new_game_event(message):
    player_id = _get_player_id()
    room = message["room"]
    LOG.info(f"Received start_game from {player_id} for room {room}: {message}")

    game_state = _get_game_manager().get_game_state(room)
    if game_state:
        game_state.start_game()
        emit("request_update", {"request_update": True}, room=room)


@socketio.on("update_request")
def update_request_event(message):
    session_id = flask.request.sid
    player_id = _get_player_id()
    room = message["room"]
    LOG.info(f"Received update_request from {player_id} for room {room}: {message}")

    game_state = _get_game_manager().get_game_state(room)
    if game_state:
        emit("board_update", game_state.get_game_state(player_id), to=session_id)


@socketio.on("peel")
def peel_event(message):
    session_id = flask.request.sid
    player_id = _get_player_id()
    LOG.info(f"Received peel from {player_id}: {message}")

    room = message["room"]

    game_state = _get_game_manager().get_game_state(room)
    if game_state:
        invalid_positions = game_state.peel(player_id)
        if len(invalid_positions) == 0:
            # If the peel was successful, notify all players.
            if game_state.game_running:
                # Game is still running. Update players.
                emit("peel", {"peeling_player": game_state.player_ids_to_names[player_id]}, room=room)
            else:
                # The game is over. Notify players of who one.
                emit("game_over", {"winning_player": game_state.player_ids_to_names[player_id]}, room=room)
        else:
            # If the peel is not valid, only the player who tried to peel should get a message
            emit("unsuccessful_peel", {"invalid_positions": list(invalid_positions)}, to=session_id)


@socketio.on("exchange")
def exchange_event(message):
    session_id = flask.request.sid
    player_id = _get_player_id()
    hand_tile_index = message["hand_tile_index"]
    LOG.info(f"Received exchange from {player_id}: {message}")

    room = message["room"]

    game_state = _get_game_manager().get_game_state(room)
    if game_state:
        game_state.exchange_tile(player_id, hand_tile_index)
        emit("board_update", game_state.get_game_state(player_id), to=session_id)


@socketio.on("shift_board")
def shift_board_event(message):
    session_id = flask.request.sid
    player_id = _get_player_id()
    LOG.info(f"Received shift_board from {player_id}: {message}")

    room = message["room"]

    game_state = _get_game_manager().get_game_state(room)
    if game_state:
        if not game_state.game_running:
            return

        direction = message.get("direction", None)
        if "up" == direction:
            game_state.player_ids_to_boards[player_id].shift_board_up()
        elif "down" == direction:
            game_state.player_ids_to_boards[player_id].shift_board_down()
        elif "left" == direction:
            game_state.player_ids_to_boards[player_id].shift_board_left()
        elif "right" == direction:
            game_state.player_ids_to_boards[player_id].shift_board_right()
        else:
            raise ValueError(f"Invalid direction specified for board shift: {direction}")

        emit("board_update", game_state.get_game_state(player_id), to=session_id)


def _get_player_id() -> str:
    if "playerId" in flask.request.cookies:
        return flask.request.cookies["playerId"]
    else:
        raise ValueError("No playerId detected!")


def _get_game_manager() -> GameManager:
    return current_app.config[GAME_MANAGER_CONFIG_KEY]
