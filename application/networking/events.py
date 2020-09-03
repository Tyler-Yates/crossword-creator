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
        game_state.player_ids_to_session_ids[player_id] = session_id
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


@socketio.on("new_game")
def new_game_event(message):
    # TODO
    pass


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
            for player_id in game_state.player_ids_to_session_ids.keys():
                if game_state.game_running:
                    # Game is still running. Update players.
                    data_to_send = {
                        "peeling_player": game_state.player_ids_to_names[player_id],
                        **game_state.get_game_state(player_id),
                    }
                    player_session_id = game_state.player_ids_to_session_ids[player_id]
                    emit("peel", data_to_send, to=player_session_id)
                else:
                    # The game is over. Notify players of who one.
                    data_to_send = {
                        "winning_player": game_state.player_ids_to_names[player_id],
                        **game_state.get_game_state(player_id),
                    }
                    player_session_id = game_state.player_ids_to_session_ids[player_id]
                    emit("game_over", data_to_send, to=player_session_id)
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


def _get_player_id() -> str:
    if flask.request.headers.getlist("X-Forwarded-For"):
        return flask.request.headers.getlist("X-Forwarded-For")[0]
    else:
        return flask.request.remote_addr


def _get_game_manager() -> GameManager:
    return current_app.config[GAME_MANAGER_CONFIG_KEY]
