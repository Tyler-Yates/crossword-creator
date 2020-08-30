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

    session_id = flask.request.sid
    player_id = _get_player_id()

    game_state = _get_game_manager().get_game_state(room)
    if game_state:
        LOG.info(f"User {player_id} has joined room {room}")
        # Only send the game_state update to the SocketIO session ID as the other players do not need to know
        emit("game_state", game_state.get_game_state(player_id=player_id), to=session_id)
    else:
        LOG.warning(f"User {player_id} has joined invalid room {room}")


@socketio.on("add_tile")
def add_tile_event(message):
    """
    Received when a player guesses a word.
    """

    session_id = flask.request.sid
    player_id = _get_player_id()
    LOG.info(f"Received guess from {player_id}: {message}")

    room = message["room"]
    hand_tile_index = message["hand_tile_index"]
    board_position = message["board_position"]

    game_state = _get_game_manager().get_game_state(room)
    game_state.add_tile(player_id, hand_tile_index, (board_position[0], board_position[1]))

    emit("board_update", game_state.get_game_state(player_id), to=session_id)


@socketio.on("new_game")
def new_game_event(message):
    LOG.debug(f"Received new_game: {message}")

    room = message["room"]

    game_state = _get_game_manager().get_game_state(room)
    if game_state:
        game_state.new_board()
    else:
        game_state = _get_game_manager().create_game_for_name(room)

    emit("game_state", game_state.get_game_state(), room=room)


@socketio.on("timer_expired")
def timer_expired_event(message):
    LOG.debug(f"Received timer_expired: {message}")

    session_id = flask.request.sid
    player_id = _get_player_id()
    room = message["room"]

    game_state = _get_game_manager().get_game_state(room)

    if game_state:
        emit("game_over", game_state.get_score_state(player_id), to=session_id)
    else:
        LOG.warning(f"Received timer_expired message from Player {player_id} for invalid game {room}")


def _get_player_id() -> str:
    return flask.request.remote_addr


def _get_game_manager() -> GameManager:
    return current_app.config[GAME_MANAGER_CONFIG_KEY]
