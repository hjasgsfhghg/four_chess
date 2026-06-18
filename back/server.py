from flask import Flask, request, jsonify
from add import get_best_drop

app = Flask(__name__)

@app.route("/", methods=["POST"])
def best_move():
    data = request.get_json()
    board = data["board"]      # 6×7 二维数组
    who = data["who"]          # 当前轮到谁下（1=红, 2=黄）
    drop = get_best_drop(board, who)
    return jsonify({"drop": drop})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3014)
