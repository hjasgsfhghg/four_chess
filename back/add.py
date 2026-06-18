# 常量
ROWS, COLS = 6, 7
EMPTY = 0
RED = 1
YELLOW = 2

# 评估权重
THREE_SCORE = 1000  # 活三的分数
TWO_SCORE = 10
ONE_SCORE = 1
POSITION_BONUS = 2   # 中间列加成
LOW_ROW_BONUS = 1    # 低行加成

# order_moves 中间列优先级映射（O(1) 查找）
CENTER_RANK = {3: 0, 2: 1, 4: 2, 1: 3, 5: 4, 0: 5, 6: 6}


def get_lowest_empty_row(board: list[list[int]], col: int) -> int:
    """返回该列最低空行的行号，若列已满返回 -1"""
    for r in range(ROWS):
        if board[r][col] == EMPTY:
            return r
    return -1


def try_drop(board: list[list[int]], col: int, player: int) -> tuple[list[list[int]], int] | tuple[None, None]:
    """在指定列落子，返回新棋盘（深拷贝）和落子行号，若列已满返回 (None, None)"""
    row = get_lowest_empty_row(board, col)
    if row == -1:
        return None, None
    new_board = [r[:] for r in board]
    new_board[row][col] = player
    return new_board, row


def check_win_at(board: list[list[int]], r: int, c: int, player: int) -> bool:
    """仅检查从 (r,c) 出发的四个方向是否形成四连（增量检查，O(4)）"""
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

    # 正斜线（右下-左上）
    count = 1
    i = 1
    while r - i >= 0 and c - i >= 0 and board[r - i][c - i] == player:
        count += 1; i += 1
    i = 1
    while r + i < ROWS and c + i < COLS and board[r + i][c + i] == player:
        count += 1; i += 1
    if count >= 4:
        return True

    # 反斜线（右上-左下）
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
    """全盘检查 player 是否四连（仅用于需要全盘扫描的罕见场景）"""
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c] == player and check_win_at(board, r, c, player):
                return True
    return False


def score_window(player_cnt: int, opponent_cnt: int) -> int:
    """根据窗口内双方棋子数评分（player_cnt + opponent_cnt + empty_cnt == 4）"""
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
    """评估整个棋盘相对于 player 的分数，遍历所有四格窗口"""
    score = 0
    opponent = 3 - player

    # 水平窗口
    for r in range(ROWS):
        for c in range(COLS - 3):
            pc = oc = 0
            for i in range(4):
                v = board[r][c + i]
                if v == player: pc += 1
                elif v == opponent: oc += 1
            score += score_window(pc, oc)

    # 垂直窗口
    for r in range(ROWS - 3):
        for c in range(COLS):
            pc = oc = 0
            for i in range(4):
                v = board[r + i][c]
                if v == player: pc += 1
                elif v == opponent: oc += 1
            score += score_window(pc, oc)

    # 正斜线（右下）
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            pc = oc = 0
            for i in range(4):
                v = board[r + i][c + i]
                if v == player: pc += 1
                elif v == opponent: oc += 1
            score += score_window(pc, oc)

    # 反斜线（右上）
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            pc = oc = 0
            for i in range(4):
                v = board[r - i][c + i]
                if v == player: pc += 1
                elif v == opponent: oc += 1
            score += score_window(pc, oc)

    # 位置加成（中间列和低行）
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
    """返回所有非满列的索引列表"""
    moves = []
    for c in range(COLS):
        if board[ROWS - 1][c] == EMPTY:
            moves.append(c)
    return moves


def is_board_full(board: list[list[int]]) -> bool:
    """棋盘是否已满"""
    return all(board[ROWS - 1][c] != EMPTY for c in range(COLS))


def order_moves(moves: list[int], last_move_col: int | None = None) -> list[int]:
    """走法排序：优先中间列，其次靠近 last_move_col 的列"""
    def key(col: int) -> tuple[int, int]:
        center_score = CENTER_RANK.get(col, 10)
        dist = abs(col - last_move_col) if last_move_col is not None else 0
        return (center_score, dist)
    return sorted(moves, key=key)


def alpha_beta(board: list[list[int]], depth: int, alpha: float, beta: float,
               is_maximizing: bool, player: int,
               last_move_col: int | None = None) -> int | float:
    """Alpha-Beta 搜索（落子后的胜负由父层在递归前检查，本层不再重复扫描）"""
    if depth == 0 or is_board_full(board):
        return eva_board(board, player)

    legal_moves = get_not_full_list(board)
    if not legal_moves:
        return eva_board(board, player)

    legal_moves = order_moves(legal_moves, last_move_col)
    opponent = 3 - player

    if is_maximizing:
        value = -float('inf')
        for col in legal_moves:
            new_board, row = try_drop(board, col, player)
            if new_board is None or row is None:
                continue
            if check_win_at(new_board, row, col, player):
                return 1000000
            score = alpha_beta(new_board, depth - 1, alpha, beta, False, opponent, col)
            if score > value:
                value = score
            if value > alpha:
                alpha = value
            if alpha >= beta:
                break
        return value
    else:
        value = float('inf')
        for col in legal_moves:
            new_board, row = try_drop(board, col, player)
            if new_board is None or row is None:
                continue
            if check_win_at(new_board, row, col, player):
                return -1000000
            score = alpha_beta(new_board, depth - 1, alpha, beta, True, opponent, col)
            if score < value:
                value = score
            if value < beta:
                beta = value
            if alpha >= beta:
                break
        return value


def find_immediate_win(board: list[list[int]], player: int) -> int:
    """检查玩家是否有一列可以立即获胜，返回该列索引，若无返回 -1"""
    for col in get_not_full_list(board):
        new_board, row = try_drop(board, col, player)
        if new_board is not None and row is not None and check_win_at(new_board, row, col, player):
            return col
    return -1


def find_immediate_block(board: list[list[int]], player: int) -> int:
    """检查对手是否有一列可以立即获胜，返回需要堵的列索引，若无返回 -1"""
    return find_immediate_win(board, 3 - player)


def get_best_drop(board: list[list[int]], current_player: int) -> int:
    """主函数：给定棋盘和当前玩家，返回最佳落子列"""
    # 1. 检查是否有立即获胜走法
    win_col = find_immediate_win(board, current_player)
    if win_col != -1:
        return win_col

    # 2. 检查是否需要防守
    block_col = find_immediate_block(board, current_player)
    if block_col != -1:
        return block_col

    # 3. Alpha-Beta 搜索决策
    legal = get_not_full_list(board)
    if not legal:
        return -1

    # 动态深度
    empty_count = sum(1 for r in range(ROWS) for c in range(COLS) if board[r][c] == EMPTY)
    if empty_count > 30:
        depth = 6
    elif empty_count > 20:
        depth = 8
    else:
        depth = 10

    legal_ordered = order_moves(legal)
    best_score = -float('inf')
    best_col = legal[0]
    alpha = -float('inf')
    beta = float('inf')
    opponent = 3 - current_player

    for col in legal_ordered:
        new_board, row = try_drop(board, col, current_player)
        if new_board is None or row is None:
            continue
        if check_win_at(new_board, row, col, current_player):
            return col
        score = alpha_beta(new_board, depth - 1, alpha, beta, False, opponent, col)
        if score > best_score:
            best_score = score
            best_col = col
        if best_score > alpha:
            alpha = best_score
        if best_score >= 1000000:
            break

    return best_col
