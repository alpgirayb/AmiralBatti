from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object("config.LocalBaseConfig")

db = SQLAlchemy(app, session_options={"expire_on_commit": False},
                engine_options={"pool_size": 3000, "max_overflow": 3000})
from models import Game, Player, Coordinate, Choice, api_result
from history.api_views import *

board_game = None

def commit_game_to_db():
    board_game = Game()
    board_game.set_player1(1)
    board_game.set_player2(2)
    board_game.active_player = 1
    db.session.add(board_game)
    db.session.commit()
    print("game id:" + str(board_game.id))

    return True


def commit_choices_to_db():
    tryout_variable = Choice()
    tryout_variable.coordinate = 1
    tryout_variable.ship_type = 1
    db.session.add(tryout_variable)
    db.session.commit()

    return True

def retrieve_game_from_db():
    game_2 = Game.query.filter_by(id=1).first()
    print("game 2 retrieved:" + str(game_2.id))


@app.before_first_request
def initialize_db_and_folders():
    print("creating database tables")
    """Initializes DB tables from models, creates roles and upload directories if they don't exist"""
    db.create_all()
    # commit_game_to_db()
    # retrieve_game_from_db()

    try:
        # create_path_if_not_exists(app.config["SLIDE_DEEPZOOM_DIR"])
        print("")
    except:
        pass


# bu da tamam
@app.route("/api/game/add_player", methods=["POST"])
def add_player():
    # get player name param from request
    # check if player name exists on db
    # if so, return error message with proper text
    # create new player and save to db
    name_param = request.form.get("name")
    if not name_param:
        return api_result(success=False, msg="Player name required")
    on_db = Player.query.filter_by(name=name_param).first()
    if on_db:
        return api_result(success=False, msg="User already registered with:" + name_param)

    player = Player(name_param)
    db.session.add(player)
    db.session.commit()

    return api_result(success=True, msg="User registered with " + str(player.id), data=player.id)
# bu da tamam
@app.route("/api/game/delete_player", methods=["DELETE"])
def delete_player():
    player_id = request.form.get("id")
    player = Player.query.get(player_id)
    if player:
        db.session.delete(player)
        db.session.commit()
        return api_result(success=True, msg="Player deleted successfully")
    else:
        return api_result(success=False, msg="Player not found")
# bu da tamam
@app.route("/api/game/list_all_players", methods=["GET"])
def list_all_players():
    players = Player.query.all()
    player_list = []

    for player in players:
        player_list.append({
            "id": player.id,
            "name": player.name
        })

    return api_result(success=True, data=player_list)
# bu da tamam
@app.route("/api/game/list_players_of_game", methods=["GET"])
def list_players_of_game():
    game_id = request.form.get("id")
    game = Game.query.get(game_id)
    if not game:
        return api_result(success=False, msg="Game not found")

    player_list = []
    if game.player1_obj:
        player_list.append(game.player1_obj.dict)
    if game.player2_obj:
        player_list.append(game.player2_obj.dict)

    return api_result(success=True, data=player_list)
# bu da tamam
@app.route("/api/game/get_game_by_id", methods=["GET"])
def get_game_by_id():
    game_id = request.form.get("id")
    game = Game.query.get(game_id)
    if not game:
        return api_result(success=False, msg="Game not found")

    game_details = {
        "id": game.id,
        "player1": game.player1_obj.dict if game.player1_obj else None,
        "player2": game.player2_obj.dict if game.player2_obj else None,
        "active_player": game.active_player_obj.dict if game.active_player_obj else None,
    }

    return api_result(success=True, msg="Game found succesfully", data=game_details)
# bu da tamam
@app.route("/api/game/add_game", methods=["POST"])
def add_game():
    # iki oyuncuyu aldıktan sonra boş oyun ekranı oluşturulsun playerları ekledikten sonra, gemi eklemeye geçsin
    player1_id = request.form.get("player1")
    if not player1_id:
        return api_result(success=False, msg="Player1 id isn't satisfied", data=None)
    player1 = Player.query.filter_by(id=player1_id)
    if not player1:
        return api_result(success=False, msg="Couldn't find the player1 in database", data=None)
    player2_id = request.form.get("player2")
    if not player2_id:
        return api_result(success=False, msg="Player2 id isn't satisfied", data=None)
    player2 = Player.query.filter_by(id=player2_id)
    if not player2:
        return api_result(success=False, msg="Couldn't find the player2 in database", data=None)
    new_game = Game()
    new_game.player1 = player1_id
    new_game.player2 = player2_id
    new_game.active_player = player1_id
    db.session.add(new_game)
    db.session.commit()

    return api_result(success=True, msg="Game added successfully", data={"game_id": new_game.id})
# bu da tamam
@app.route("/api/game/delete_game", methods=["DELETE"])
def delete_game():
    # get the game_id first
    game_id = request.form.get("id")
    # check game_id param and check on_db existence
    if not game_id:
        return api_result(success=False, msg="There's no game id found", data=None)
    on_db = Game.query.filter(Game.id == game_id).delete()
    if not on_db:
        return api_result(success=False, msg="Couldn't find the game on database", data=None)
    #  deleted_game = Game()
    #  deleted_game.id = game_id
    #  db.session.delete()
    db.session.commit()
    return api_result(success=True, msg="Game deleted successfully", data=None)
# bu da tamam
@app.route('/api/game/list_all_games', methods=["GET"])
def list_all_games():
    games = Game.query.all()
    game_list = []

    for game in games:
        game_list.append({
            "id": game.id,
            "player1": game.player1,
            "player2": game.player2,
            "active_player": game.active_player
        })

    return api_result(success=True, data=game_list)
@app.route("/api/game/check_for_game_finish", methods=["POST"])
def check_for_game_finish():
    board_game = Game.query.get(game_id)
    finish = board_game.check_for_finish()
    return api_result(success=finish)
@app.route('/api/game/join_game', methods=["Post"])
def join_game():
        player_id = request.data.get('player_id')
        game_id = request.data.get('game_id')

        if not player_id or not game_id:
            return api_result(success=False, msg="Player ID and Game ID is required.")

        new_player1 = Player.query.filter_by(id= player_id).first()
        new_player2 = Player.query.filter_by(id= player_id).first()

        # Find the game by game_id
        game = Game.query.get(game_id)
        if not game:
            return api_result(success=False, msg="Game not found.")

        # Assign the player to the game
        if not game.player1:
            game.player1 = new_player1.id
        elif not game.player2:
            game.player2 = new_player2.id
        else:
            return api_result(success=False, msg="The game is already full.")
        
        db.session
        db.session.commit()
        return api_result(success=True, msg="Player joined the game successfully.")
#bu da tamam
@app.route("/api/game/get_player_by_id", methods=["GET"])
def get_player_by_id():
    player_id = request.form.get("player_id")
    player = Player.query.get(player_id)
    if not player:
        return api_result(success=False, msg="Player not found")
    player_details = {
        "id": player.id,
        "name": player.name
    }
    return api_result(success=True, msg="Player found succesfully", data=player_details)

@app.route("/api/game/add_choice", methods=["POST"])
def add_choice():
    # player_no = int(request.form.get("player_no"))
    # if player_no not in ["1", "2"]:
    #     return api_result(success=False, msg="Invalid parameter value")
    try:
        player_no = int(request.form.get("player_no"))
        game_id = int(request.form.get("game_id"))
        coord_x = int(request.form.get("coord_x"))
        coord_y = int(request.form.get("coord_y"))
        direction = int(request.form.get("direction"))
        ship_type = int(request.form.get("ship_type"))
    except ValueError:
        return api_result(success=False, msg="Invalid parameter value")
    # BOARD_ROW_COUNT, BOARD_COL_COUNT
    board_game = Game.query.get(game_id)
    player = board_game.get_player_obj(player_no)
    player.add_choice(game_id, Coordinate(game_id, coord_x, coord_y), ship_type, direction)
    return api_result()

@app.route('/api/game/place_ships', methods=['POST'])
def place_ships():
    try:
        player_id = request.form.get('player_id')
        ship_list = request.form.get('ship_list')
        if not player_id or not ship_list:
            return api_result(success=False, msg="player_id and ship_list are required.")
        player = Player.query.get(player_id)
        if not player:
            return api_result(success=False, msg="Player not found.")
        # Place ships on the board
        for ship_data in ship_list:
            x = ship_data.get('x')
            y = ship_data.get('y')
            ship_type = ship_data.get('ship_type')
            direction = ship_data.get('direction')

            if x is None or y is None or ship_type is None or direction is None:
                return api_result(success=False, msg="Invalid ship data.")

            coordinate = Coordinate.query.filter_by(x=x, y=y).first()
            if not coordinate:
                return api_result(success=False, msg="Coordinate not found.")

            try:
                player.add_choice(coordinate, ship_type, direction)
            except ValueError as e:
                return api_result(success=False, msg=str(e))
        db.session.commit()
        return api_result(success=True, msg="Ships placed successfully.")
    except Exception as e:
        return api_result(success=False, msg=str(e))

@app.route("/api/game/next_turn", methods=["POST"])
def next_turn():
    coord_x = int(request.form.get("coord_x"))
    player_no = int(request.form.get("player_no"))
    coord_y = int(request.form.get("coord_y"))
    game_id = int(request.form.get("game_id"))
    board_game = Game.query.get(game_id)
    player = Player.query.get(player_no)
    if not player.id == board_game.active_player:
        return api_result(success=False,msg="It's not your turn")
    coord = Coordinate(game_id,coord_x, coord_y)
    hit = board_game.next_turn(coord)
    db.session.commit()
    finish = board_game.check_for_finish()
    return api_result(success=hit,data=finish)

@app.route("/api/game/print_map", methods=["POST"])
def print_player_map():
    no = int(request.form.get("player_no"))
    game_id = int(request.form.get("game_id"))
    if not no:
        print("You can only type player 1 or player 2, please do accordingly")
        return api_result(success=False, msg="Player no expected")
    player_no = int(no)
    if not (player_no == 1 or player_no == 2):
        print("You can only type player 1 or player 2, please do accordingly")
        return api_result(success=False, msg="Player no can be 1 or 2")
    #board_game = Game()
    board_game = Game.query.get(game_id)
    player = board_game.get_player_obj(player_no)
    if not player:
        return api_result(success=False, msg="User not found")
    player.print_map(game_id)
    return api_result()

@app.route("/api/game/present_turn", methods=["POST"])
def present_turn():
    #hangi kareyi vuracağını iste,kareyi vurdu,vurduktan sonra karenin dolu olup olmadığını kontrol et
    #kontrol ettikten sonra eğer vurduysa tekrar vurma hakkı ver(burayı front-endini yaparken kontrol ediceksin
    #next_turn sonucu hit geldiyse)
    #eğer tutturamazsa next_turn ile oyun
    #sırasını karşıya ver.
    return api_result()

# todo add_game apisi yaz. game_id=15 (add/delete/get_by_id/list_all_games)+
# todo list games game[]+
# todo player create apisi yaz [player_id=5] (add/delete/get_by_id/list_all_playes/list_players_of_game)+
# todo player update-> login to game[player_id=5,game_id=15]
# todo player -> add choice

# unit test

if __name__ == '__main__':
    app.run()
