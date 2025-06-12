from flask import Flask, jsonify, request
from flask_cors import CORS
from game import ContigGame
import os
import numpy as np

# setup of app
APP = Flask(__name__)
CORS(APP)

# (possible) TODO: change this to True if you want to play in computer mode
computer = True

# initial game
game = ContigGame(computer=computer)

'''Route that saves progress'''
@APP.route("/api/save", methods=["POST"])
def save():
    ### backend data
    backend_path = "user-data/backend"
    if not os.path.exists(backend_path):
        os.mkdir("user-data")
        os.mkdir(backend_path)
    # game.board.num_placement, game.board.num_status
    np.savez(f"{backend_path}/board.npz", placement=game.board.num_placement, status=game.board.num_status)
    with open(f"{backend_path}/game.txt", "w") as gamefile:
        # points1, points2, computer_mode
        gamefile.write(f"{game.points1}|{game.points2}|{game.computer_mode}")
    ### frontend data
    frontend_path = "user-data/frontend"
    if not os.path.exists(frontend_path):
        os.mkdir(frontend_path)
    with open(f"{frontend_path}/ui.txt", "w") as uifile:
        # currentPlayer, keys, used, indices, useCount, invalidExpr, display (as a string delimited by |)
        frontend_data = request.get_data()
        frontend_data = frontend_data.decode()
        uifile.write(frontend_data)
    return ""

'''Route that loads saved game data'''
@APP.route("/api/load", methods=["GET"])
def load():
    global game
    try:
        ### backend data
        backend_path = "user-data/backend"
        board = np.load(f"{backend_path}/board.npz")
        gamestats = None
        with open(f"{backend_path}/game.txt", "r") as gamefile:
            gamestats = gamefile.read().replace("\n","").strip()
            gamestats = gamestats.split("|")
        game.board.num_placement, game.board.num_status = board["placement"], board["status"]
        game.points1, game.points2, game.computer_mode = int(gamestats[0]), int(gamestats[1]), eval(gamestats[2])
        ### frontend data
        frontend_path = "user-data/frontend"
        send = None
        with open(f"{frontend_path}/ui.txt", "r") as uifile:
            send = uifile.read().replace("\n","").strip()
            send = send.replace("true", "True").replace("false", "False")
        send = eval(send)
        send["computerMode"] = game.computer_mode
        send["nums"] = game.board.num_placement.tolist()
        send["status"] = game.board.num_status.tolist()
        send["points1"] = game.points1
        send["points2"] = game.points2
        return jsonify(send)
    except:
        game = ContigGame(computer=computer)
        boardList = game.board.num_placement.tolist()
        send = {"nums": boardList, "computerMode": computer}
        return jsonify(send)

'''Route that starts a new game'''
@APP.route("/api/new", methods=["GET"])
def send_board():
    backend_path = "user-data/backend"
    frontend_path = "user-data/frontend"
    global game
    game = ContigGame(computer=computer)
    boardList = game.board.num_placement.tolist()
    send = {"nums": boardList, "computerMode": computer}
    try:
        os.remove(f"{backend_path}/board.npz")
        os.remove(f"{backend_path}/game.txt")
        os.remove(f"{frontend_path}/ui.txt")
        os.rmdir(f"{frontend_path}")
        os.rmdir(f"{backend_path}")
        os.rmdir("user-data")
    except:
        pass
    return jsonify(send)

'''route that gets the potential candidate, and player number to verify (and allocate if ok)'''
@APP.route("/api/humanturn", methods=["POST"])
def perform_human_turn():
    raw = request.get_data()
    raw = raw.decode()
    psq, pid = raw.split(",")
    psq, pid = int(psq), int(pid)
    val = game.human_turn(square=psq, player_id=pid)
    return val

'''route that gets the potential candidate, and player number to verify (and allocate if ok)'''
@APP.route("/api/machineturn", methods=["POST"])
def perform_machine_turn():
    dice = request.get_data()
    dice = dice.decode()
    [a,b,c] = dice.split(",")
    dice = [int(a),int(b),int(c)]
    val = game.machine_turn(dice=dice)
    return val

if __name__ == "__main__":
    APP.run(debug=True)