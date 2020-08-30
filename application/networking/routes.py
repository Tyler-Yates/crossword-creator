import logging

import flask
from flask import current_app, redirect, render_template, request

from application import GAME_MANAGER_CONFIG_KEY
from application.data.game_manager import GameManager
from . import main

LOG = logging.getLogger("Routes")


@main.route("/")
def index():
    return render_template("index.html")


@main.route("/games/<game_name>")
def game_page(game_name: str):
    game_state = _get_game_manager().get_game_state(game_name)

    if game_state:
        player_id = _get_player_id()
        player_name = game_state.player_ids_to_names[player_id]
        return render_template("game.html", game_state=game_state, player_id=player_id, player_name=player_name)
    return "Could not find game!", 404


@main.route("/create_game", methods=["POST"])
def create_game():
    player_id = _get_player_id()
    LOG.info(f"Creating game for {player_id}")

    player_name = player_id
    if request.form:
        player_name = request.form.get("player_name", player_id)

    game_state = _get_game_manager().create_game()
    game_state.new_player(player_id, player_name)
    game_state.start_game()  # TODO do not do this as soon as game starts
    return redirect(f"/games/{game_state.game_name}", code=302)


def _get_game_manager() -> GameManager:
    return current_app.config[GAME_MANAGER_CONFIG_KEY]


def _get_player_id() -> str:
    return flask.request.remote_addr
