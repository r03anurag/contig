from flask import Flask, jsonify, request
from flask_cors import CORS
from game import ContigGame

# setup of app
APP = Flask(__name__)
CORS(APP)

# (possible) TODO: change this to True if you want to play in computer mode
computer = True

# data
#game = ContigGame(computer=computer)

'''Route that fetches the gameboard'''
@APP.route("/api/new", methods=["GET"])
def send_board():
    global game
    game = ContigGame(computer=computer)
    boardList = game.board.num_placement.tolist()
    send = {"board": boardList, "computerMode": computer}
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