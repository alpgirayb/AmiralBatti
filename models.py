import json

from flask import jsonify
from sqlalchemy import Column, Integer, String, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship

from app import db


# import mysql.connector
#
# connection = mysql.connector.connect(
#     host="localhost",
#     user="username",
#     password="password",
#     database="database_name"
# )
# cursor = connection.cursor()
class Game(db.Model):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player1 = Column(Integer, ForeignKey('players.id', ondelete="SET NULL"), nullable=True)
    player2 = Column(Integer, ForeignKey('players.id', ondelete="SET NULL"), nullable=True)
    active_player = Column(Integer, ForeignKey('players.id', ondelete="SET NULL"), nullable=True)

    coordinates = relationship('Coordinate', back_populates='game')
    choices = relationship('Choice', back_populates='game', primaryjoin="Game.id == Choice.game_id")
    active_player_obj = relationship('Player', foreign_keys=[active_player])
    player1_obj = relationship('Player', foreign_keys=[player1])
    player2_obj = relationship('Player', foreign_keys=[player2])

    def __init__(self):
        self.player1 = None
        self.player2 = None
        self.active_player = self.player1

    def get_player(self, no):
        if no == 1:
            return self.player1
        if no == 2:
            return self.player2
        return None

    def get_player_obj(self, no):
        if no == 1:
            return self.player1_obj
        if no == 2:
            return self.player2_obj
        return None

    def set_player1(self, player):
        self.player1 = player

    def set_player2(self, player):
        self.player2 = player

    def next_turn(self, coordinate):
        hit = self.check_for_hit(coordinate)
        if hit:
            self.non_active_player.print_map(coordinate.game_id)
            return True
        else:
            print("Missed the boat.")
        if self.active_player == self.player1:
            self.active_player = self.player2
        else:
            self.active_player = self.player1
        return hit

    def check_for_finish(self):
        return not self.non_active_player.is_alive(self.id)

    @property
    def non_active_player(self):
        if self.active_player == self.player1:
            return self.player2_obj
        else:
            return self.player1_obj

    def check_for_hit(self, coordinate):
        choice = self.non_active_player.get_choice_at(coordinate)
        if choice and choice.is_alive:
            choice.is_alive = 0
            return True
        return False


class Coordinate(db.Model):
    __tablename__ = "coordinates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(Integer, ForeignKey('games.id', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    x = Column(Integer, nullable=False)
    y = Column(Integer, nullable=False)

    choices = relationship('Choice', back_populates='coordinates')
    game = relationship('Game', back_populates='coordinates')

    def __init__(self, game_id, x, y):
        self.game_id = game_id
        self.x = x
        self.y = y

    def equals(self, coord):
        return self.x == coord.x and self.y == coord.y


class Choice(db.Model):
    __tablename__ = "choices"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    game_id = Column(Integer, ForeignKey('games.id', onupdate="CASCADE", ondelete="CASCADE"),
                     nullable=False)
    player_id = Column(Integer, ForeignKey('players.id', onupdate="CASCADE", ondelete="CASCADE"),
                       nullable=False)
    coordinate_id = Column(Integer, ForeignKey('coordinates.id', onupdate="CASCADE", ondelete="CASCADE"),
                           nullable=False)
    ship_type = Column(Integer, nullable=False)
    is_alive = Column(Integer, default=1, nullable=False)

    coordinates = relationship('Coordinate', back_populates='choices')
    game = relationship('Game', back_populates='choices', primaryjoin="Game.id == Choice.game_id")
    coordinate_obj = relationship('Coordinate', foreign_keys=[coordinate_id])
    player = relationship('Player', foreign_keys=[player_id], backref="choices")

    def __init__(self, game_id, coordinate, ship_type):
        self.coordinate_obj = coordinate
        self.game_id = game_id
        self.ship_type = ship_type
        self.is_alive = 1


BOARD_COLUMN_COUNT = 5
BOARD_ROW_COUNT = 5

# SHIP_TYPES={
#     1: 1
# }
# direction_right = 1
# direction_down = 2

player_choice = db.Table(
    'player_choices',
    db.Column('player_id', db.Integer(), db.ForeignKey('players.id', onupdate="CASCADE", ondelete="CASCADE")),
    db.Column('choice_id', db.Integer(), db.ForeignKey('choices.id', onupdate="CASCADE", ondelete="CASCADE")),
    db.Column('game_id', db.Integer(), db.ForeignKey('players.id', onupdate="CASCADE", ondelete="CASCADE")),
    PrimaryKeyConstraint('player_id', 'choice_id', 'game_id')
)


class Player(db.Model):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # Choices = Column(Integer, nullable=False)
    name = Column(String(255), nullable=False)

    # choices = relationship('Choice', back_populates="player")

    def __init__(self, name):
        self.choices = []
        self.name = name

    def is_coordinate_occupied(self, coordinate):
        for choice in self.choices:
            if choice.coordinate_obj.x == coordinate.x and choice.coordinate_obj.y == coordinate.y:
                return True
        return False

    def add_choice(self, game_id, coordinate, ship_type, direction):
        direction_right = 1

        for i in range(ship_type):
            if direction == direction_right:
                x = coordinate.x + i
                y = coordinate.y
            else:
                x = coordinate.x
                y = coordinate.y + i

            new_coordinate = Coordinate(game_id, x, y)

            if self.is_coordinate_occupied(new_coordinate):
                raise ValueError("ships are colliding. Choose a another place")

            self.choices.append(Choice(game_id, new_coordinate, ship_type))
        db.session.commit()

    def get_choice_at(self, coordinate):
        for item in self.choices:
            if item.coordinate_obj.equals(coordinate) and item.game_id == coordinate.game_id:
                return item
        return None

    def is_alive(self, game_id):
        for choice in self.choices:
            if choice.game_id == game_id:
                if choice.is_alive:
                    return True
        return False

    def print_map(self, game_id):
        print("Player[{}]'s map:\n".format(self.name))
        playernum = self.name
        # if not playernum in ["1", "2"]:
        #            return api_result(success=False, msg="Invalid parameter value")
        for i in range(BOARD_ROW_COUNT):
            line = ""
            for j in range(BOARD_COLUMN_COUNT):
                choice = self.get_choice_at(Coordinate(game_id, j, i))
                if not choice:
                    line += "- \t"
                    continue
                if choice.is_alive:
                    line += "1 \t"
                else:
                    line += "X \t"
            print(line)

    @property
    def dict(self):
        return {"id": self.id, "name": self.name}


def api_result(success: object = True, msg: object = "", data: object = None) -> object:
    print("api result :" + json.dumps({"success": success, "msg": msg, "data": data}))
    return jsonify({"success": success, "msg": msg, "data": data})
