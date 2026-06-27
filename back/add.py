import random

# 常量
ROWS, COLS = 6, 7
EMPTY = 0
RED = 1
YELLOW = 2

# 评估权重
THREE_SCORE = 1000
TWO_SCORE = 10
ONE_SCORE = 1
POSITION_BONUS = 2
LOW_ROW_BONUS = 1

CENTER_RANK = {3: 0, 2: 1, 4: 2, 1: 3, 5: 4, 0: 5, 6: 6}


def get_lowest_empty_row(board: list[list[int]], col: int) -> int:
    for r in range(ROWS):
        if board[r][col] == EMPTY:
            return r
    return -1


def try_drop(board: list[list[int]], col: int, player: int) -> tuple[list[list[int]], int] | tuple[None, None]:
    row = get_lowest_empty_row(board, col)
    if row == -1:
        return None, None
    new_board = [r[:] for r in board]
    new_board[row][col] = player
    return new_board, row


def check_win_at(board: list[list[int]], r: int, c: int, player: int) -> bool:
    # 水平
    count = 1
    i = 1
    while c - i >= 0 and board[r][c - i] == player:
        count += 1; i += 1
    i = 1
    while c + i < COLS and board[r][c + i] == player:
        count += 1; i += 1
    if count >= 4:
        return True

    # 垂直
    count = 1
    i = 1
    while r - i >= 0 and board[r - i][c] == player:
        count += 1; i += 1
    i = 1
    while r + i < ROWS and board[r + i][c] == player:
        count += 1; i += 1
    if count >= 4:
        return True

    # 正斜线
    count = 1
    i = 1
    while r - i >= 0 and c - i >= 0 and board[r - i][c - i] == player:
        count += 1; i += 1
    i = 1
    while r + i < ROWS and c + i < COLS and board[r + i][c + i] == player:
        count += 1; i += 1
    if count >= 4:
        return True

    # 反斜线
    count = 1
    i = 1
    while r + i < ROWS and c - i >= 0 and board[r + i][c - i] == player:
        count += 1; i += 1
    i = 1
    while r - i >= 0 and c + i < COLS and board[r - i][c + i] == player:
        count += 1; i += 1
    if count >= 4:
        return True

    return False


def check_win(board: list[list[int]], player: int) -> bool:
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c] == player and check_win_at(board, r, c, player):
                return True
    return False


def score_window(player_cnt: int, opponent_cnt: int) -> int:
    empty_cnt = 4 - player_cnt - opponent_cnt

    if player_cnt == 4:
        return THREE_SCORE * 10
    if opponent_cnt == 4:
        return -THREE_SCORE * 10

    if player_cnt == 3 and empty_cnt == 1:
        return THREE_SCORE
    if opponent_cnt == 3 and empty_cnt == 1:
        return -THREE_SCORE

    score = player_cnt * (TWO_SCORE if player_cnt >= 2 else ONE_SCORE)
    score -= opponent_cnt * (TWO_SCORE if opponent_cnt >= 2 else ONE_SCORE)
    return score


def eva_board(board: list[list[int]], player: int) -> int:
    score = 0
    opponent = 3 - player

    for r in range(ROWS):
        for c in range(COLS - 3):
            pc = oc = 0
            for i in range(4):
                v = board[r][c + i]
                if v == player: pc += 1
                elif v == opponent: oc += 1
            score += score_window(pc, oc)

    for r in range(ROWS - 3):
        for c in range(COLS):
            pc = oc = 0
            for i in range(4):
                v = board[r + i][c]
                if v == player: pc += 1
                elif v == opponent: oc += 1
            score += score_window(pc, oc)

    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            pc = oc = 0
            for i in range(4):
                v = board[r + i][c + i]
                if v == player: pc += 1
                elif v == opponent: oc += 1
            score += score_window(pc, oc)

    for r in range(3, ROWS):
        for c in range(COLS - 3):
            pc = oc = 0
            for i in range(4):
                v = board[r - i][c + i]
                if v == player: pc += 1
                elif v == opponent: oc += 1
            score += score_window(pc, oc)

    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c] == player:
                if c in (3, 4):
                    score += POSITION_BONUS
                if r <= 1:
                    score += LOW_ROW_BONUS
            elif board[r][c] == opponent:
                if c in (3, 4):
                    score -= POSITION_BONUS
                if r <= 1:
                    score -= LOW_ROW_BONUS

    return score


def get_not_full_list(board: list[list[int]]) -> list[int]:
    moves = []
    for c in range(COLS):
        if board[ROWS - 1][c] == EMPTY:
            moves.append(c)
    return moves


def is_board_full(board: list[list[int]]) -> bool:
    return all(board[ROWS - 1][c] != EMPTY for c in range(COLS))


def order_moves(moves: list[int], last_move_col: int | None = None) -> list[int]:
    def key(col: int) -> tuple[int, int]:
        center_score = CENTER_RANK.get(col, 10)
        dist = abs(col - last_move_col) if last_move_col is not None else 0
        return (center_score, dist)
    return sorted(moves, key=key)


def alpha_beta(board: list[list[int]], depth: int, alpha: float, beta: float,
               is_maximizing: bool, player: int,
               last_move_col: int | None = None,
               tt: dict | None = None) -> int | float:
    key = None
    if tt is not None:
        key = (tuple(tuple(r) for r in board), is_maximizing)
        if key in tt:
            cached_score, cached_depth = tt[key]
            if cached_depth >= depth:
                return cached_score

    if depth == 0 or is_board_full(board):
        value = eva_board(board, player)
        if tt is not None:
            tt[key] = (value, depth)
        return value

    legal_moves = get_not_full_list(board)
    if not legal_moves:
        value = eva_board(board, player)
        if tt is not None:
            tt[key] = (value, depth)
        return value

    legal_moves = order_moves(legal_moves, last_move_col)
    opponent = 3 - player

    if is_maximizing:
        value = -float('inf')
        for col in legal_moves:
            new_board, row = try_drop(board, col, player)
            if new_board is None or row is None:
                continue
            if check_win_at(new_board, row, col, player):
                value = 1000000
                break
            score = alpha_beta(new_board, depth - 1, alpha, beta, False, opponent, col, tt)
            if score > value:
                value = score
            if value > alpha:
                alpha = value
            if alpha >= beta:
                break
        if tt is not None:
            tt[key] = (value, depth)
        return value
    else:
        value = float('inf')
        for col in legal_moves:
            new_board, row = try_drop(board, col, player)
            if new_board is None or row is None:
                continue
            if check_win_at(new_board, row, col, player):
                value = -1000000
                break
            score = alpha_beta(new_board, depth - 1, alpha, beta, True, opponent, col, tt)
            if score < value:
                value = score
            if value < beta:
                beta = value
            if alpha >= beta:
                break
        if tt is not None:
            tt[key] = (value, depth)
        return value


def find_immediate_win(board: list[list[int]], player: int) -> int:
    for col in get_not_full_list(board):
        new_board, row = try_drop(board, col, player)
        if new_board is not None and row is not None and check_win_at(new_board, row, col, player):
            return col
    return -1


def find_immediate_block(board: list[list[int]], player: int) -> int:
    return find_immediate_win(board, 3 - player)


# ─── 策略 1：随机 ───
def random_drop(board: list[list[int]], player: int) -> int:
    legal = get_not_full_list(board)
    if not legal:
        return -1
    return random.choice(legal)


# ─── 策略 2：贪心 ───
def greedy_drop(board: list[list[int]], player: int) -> int:
    win_col = find_immediate_win(board, player)
    if win_col != -1:
        return win_col
    block_col = find_immediate_block(board, player)
    if block_col != -1:
        return block_col
    return random_drop(board, player)


# ─── 策略 3：Minimax（固定深度 4） ───
def minimax_drop(board: list[list[int]], player: int) -> int:
    win_col = find_immediate_win(board, player)
    if win_col != -1:
        return win_col
    block_col = find_immediate_block(board, player)
    if block_col != -1:
        return block_col

    legal = get_not_full_list(board)
    if not legal:
        return -1

    depth = 4
    legal_ordered = order_moves(legal)
    best_score = -float('inf')
    best_cols = [legal[0]]
    alpha = -float('inf')
    beta = float('inf')
    opponent = 3 - player

    for col in legal_ordered:
        new_board, row = try_drop(board, col, player)
        if new_board is None or row is None:
            continue
        if check_win_at(new_board, row, col, player):
            return col
        score = alpha_beta(new_board, depth - 1, alpha, beta, False, opponent, col)
        if score > best_score:
            best_score = score
            best_cols = [col]
        elif score == best_score:
            best_cols.append(col)
        if best_score > alpha:
            alpha = best_score

    return random.choice(best_cols)


# ─── 策略 4：增强版（置换表 + 动态深度） ───
def get_best_drop(board: list[list[int]], current_player: int) -> int:
    win_col = find_immediate_win(board, current_player)
    if win_col != -1:
        return win_col

    block_col = find_immediate_block(board, current_player)
    if block_col != -1:
        return block_col

    legal = get_not_full_list(board)
    if not legal:
        return -1

    empty_count = sum(1 for r in range(ROWS) for c in range(COLS) if board[r][c] == EMPTY)
    if empty_count > 30:
        depth = 6
    elif empty_count > 20:
        depth = 8
    else:
        depth = 10

    tt: dict = {}
    legal_ordered = order_moves(legal)
    best_score = -float('inf')
    best_cols = [legal[0]]
    alpha = -float('inf')
    beta = float('inf')
    opponent = 3 - current_player

    for col in legal_ordered:
        new_board, row = try_drop(board, col, current_player)
        if new_board is None or row is None:
            continue
        if check_win_at(new_board, row, col, current_player):
            return col
        score = alpha_beta(new_board, depth - 1, alpha, beta, False, opponent, col, tt)
        if score > best_score:
            best_score = score
            best_cols = [col]
        elif score == best_score:
            best_cols.append(col)
        if best_score > alpha:
            alpha = best_score

    return random.choice(best_cols)


# ─── 策略分发字典 ───
STRATEGY_MAP: dict = {
    "random": random_drop,
    "greedy": greedy_drop,
    "minimax": minimax_drop,
    "enhanced": get_best_drop,
}


# ─── 批量对战 ───
def simulate_one_game(strategy_a: str, strategy_b: str) -> int:
    board: list[list[int]] = [[EMPTY] * COLS for _ in range(ROWS)]
    current: int = RED

    while True:
        strat = strategy_a if current == RED else strategy_b
        col = STRATEGY_MAP[strat](board, current)
        if col == -1:
            return 3

        new_board, row = try_drop(board, col, current)
        if new_board is None:
            return 3

        if check_win_at(new_board, row, col, current):
            return current

        if is_board_full(new_board):
            return 3

        board = new_board
        current = YELLOW if current == RED else RED


def run_battle(strategy_a: str, strategy_b: str, rounds: int) -> dict[str, int]:
    a_win: int = 0
    b_win: int = 0
    draw: int = 0

    for i in range(rounds):
        if i % 2 == 0:
            winner = simulate_one_game(strategy_a, strategy_b)
            if winner == RED:
                a_win += 1
            elif winner == YELLOW:
                b_win += 1
            else:
                draw += 1
        else:
            winner = simulate_one_game(strategy_b, strategy_a)
            if winner == RED:
                b_win += 1
            elif winner == YELLOW:
                a_win += 1
            else:
                draw += 1

    return {"a_win": a_win, "b_win": b_win, "draw": draw, "rounds": rounds}
