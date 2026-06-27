import time
import logging
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from add import get_best_drop, STRATEGY_MAP, run_battle

app = Flask(__name__)
CORS(app)

# 关闭 Werkzeug 默认日志，避免重复输出
log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)


@app.before_request
def start_timer():
    g.start = time.perf_counter()


@app.after_request
def log_latency(response):
    elapsed = (time.perf_counter() - g.get("start", 0)) * 1000
    print(f"[{time.strftime('%H:%M:%S')}] {request.method} {request.path} → {response.status_code}  {elapsed:.1f}ms")
    return response


@app.route("/", methods=["POST"])
def best_move():
    data = request.get_json()
    board = data["board"]
    who = data["who"]
    strategy = data.get("strategy", "enhanced")
    drop_fn = STRATEGY_MAP.get(strategy, get_best_drop)
    drop = drop_fn(board, who)
    return jsonify({"drop": drop})


@app.route("/battle", methods=["POST"])
def battle():
    data = request.get_json()
    strategy_a = data["strategy_a"]
    strategy_b = data["strategy_b"]
    rounds = data["rounds"]
    result = run_battle(strategy_a, strategy_b, rounds)
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3014,threaded = True)
