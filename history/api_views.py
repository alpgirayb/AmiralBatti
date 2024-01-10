from flask import jsonify, request

from app import app

winner = -1
game_id = ""


@app.route('/game/history/get', methods=["GET"])
def game_history_get():  # put application's code here
    print("uzun işler")
    return jsonify({
        "game_id": game_id,
        "winner": winner
    })


@app.route('/game/history/set', methods=["POST"])
def game_history_set():  # put application's code here
    game_id = request.form.get("game_id")
    winner = request.form.get("winner")

    return jsonify({
        "code": True
    })
