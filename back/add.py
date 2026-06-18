import sys
import copy

# 常量
ROWS = 6
COLS = 7
EMPTY = 0
RED = 1
YELLOW = 2

# 评估权重
THREE_SCORE = 100000  # 活三的分数（远大于普通累计）
TWO_SCORE = 10
ONE_SCORE = 1
POSITION_BONUS = 2   # 中间列加成
LOW_ROW_BONUS = 1    # 低行加成

def get_lowest_empty_row(board, col):
    """返回该列最低空行的行号，若列已满返回-1"""
    for r in range(ROWS):
        if board[r][col] == EMPTY:
            return r
    return -1

def drop_piece(board, col, player):
    """在指定列落子，返回新棋盘（深拷贝）和落子行号，若列已满返回None"""
    row = get_lowest_empty_row(board, col)
    if row == -1:
        return None, None
    new_board = [row[:] for row in board]  # 深拷贝
    new_board[row][col] = player
    return new_board, row

def check_win(board, player):
    """检查当前棋盘上player是否已经四子连线"""
    # 检查所有可能的起点
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c] != player:
                continue
            # 水平方向
            if c <= COLS-4 and all(board[r][c+i] == player for i in range(4)):
                return True
            # 垂直方向
            if r <= ROWS-4 and all(board[r+i][c] == player for i in range(4)):
                return True
            # 正斜线 (右下)
            if r <= ROWS-4 and c <= COLS-4 and all(board[r+i][c+i] == player for i in range(4)):
                return True
            # 反斜线 (右上)
            if r >= 3 and c <= COLS-4 and all(board[r-i][c+i] == player for i in range(4)):
                return True
    return False

def evaluate_window(window, player):
    """
    对一个四格窗口进行评分（相对于player）
    返回正分表示对player有利，负分表示对对手有利
    """
    opponent = 3 - player  # 若player=1, opponent=2；若player=2, opponent=1
    player_cnt = window.count(player)
    opponent_cnt = window.count(opponent)
    empty_cnt = window.count(EMPTY)
    
    # 若窗口内有双方棋子，则该窗口不可能形成四子，潜力降低，但仍计分（但通常双方混杂时分数低）
    if player_cnt == 4:
        return THREE_SCORE * 10  # 已经赢了，但通常不会在评估中触发，因为检测获胜会提前返回
    if opponent_cnt == 4:
        return -THREE_SCORE * 10
    
    # 活三：三子+一空，且无对方棋子
    if player_cnt == 3 and empty_cnt == 1:
        return THREE_SCORE
    if opponent_cnt == 3 and empty_cnt == 1:
        return -THREE_SCORE
    
    # 普通计数
    score = 0
    score += player_cnt * (TWO_SCORE if player_cnt >= 2 else ONE_SCORE)  # 简化，实际可线性
    score -= opponent_cnt * (TWO_SCORE if opponent_cnt >= 2 else ONE_SCORE)
    
    # 对双子的额外奖励（如果两个棋子相邻或间隔？这里简化为数量累计）
    # 更精细：若为两个连续棋子，加成更高，但为保持简单，不额外处理。
    return score

def evaluate_board(board, player):
    """
    评估整个棋盘相对于player的分数
    遍历所有四格窗口
    """
    score = 0
    opponent = 3 - player
    
    # 水平窗口
    for r in range(ROWS):
        for c in range(COLS - 3):
            window = [board[r][c+i] for i in range(4)]
            score += evaluate_window(window, player)
    
    # 垂直窗口
    for r in range(ROWS - 3):
        for c in range(COLS):
            window = [board[r+i][c] for i in range(4)]
            score += evaluate_window(window, player)
    
    # 正斜线（右下）
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            window = [board[r+i][c+i] for i in range(4)]
            score += evaluate_window(window, player)
    
    # 反斜线（右上）
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            window = [board[r-i][c+i] for i in range(4)]
            score += evaluate_window(window, player)
    
    # 位置加成（中间列和低行）
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c] == player:
                if c in [3, 4]:
                    score += POSITION_BONUS
                if r <= 1:
                    score += LOW_ROW_BONUS
            elif board[r][c] == opponent:
                if c in [3, 4]:
                    score -= POSITION_BONUS
                if r <= 1:
                    score -= LOW_ROW_BONUS
    
    return score

def get_legal_moves(board):
    """返回所有非满列的索引列表"""
    moves = []
    for c in range(COLS):
        if board[ROWS-1][c] == EMPTY:  # 顶部为空表示可落
            moves.append(c)
    return moves

def order_moves(board, moves, last_move_col=None):
    """
    走法排序：优先中间列，其次靠近last_move_col的列
    """
    # 定义中间列优先级
    center_priority = [3, 2, 4, 1, 5, 0, 6]  # 0列最远
    # 根据中心优先级和与上一列的接近程度排序
    def key(col):
        center_score = center_priority.index(col) if col in center_priority else 10
        if last_move_col is not None:
            dist = abs(col - last_move_col)
        else:
            dist = 0
        return (center_score, dist)
    return sorted(moves, key=key)

def is_board_full(board):
    return all(board[ROWS-1][c] != EMPTY for c in range(COLS))

def alpha_beta(board, depth, alpha, beta, is_maximizing, player, last_move_col=None):
    """
    Alpha-Beta搜索
    player: 当前落子方（1或2）
    is_maximizing: True表示当前层为AI（最大化），False为对手（最小化）
    注意：搜索根节点时player = current_player, is_maximizing = True
    """
    # 检查是否有人获胜（在落子后调用前会检查，此处做安全）
    # 但棋盘状态可能已经存在获胜，则立即返回极值
    if check_win(board, player):
        # 若当前player获胜，则根据最大化/最小化返回不同符号
        # 通常我们认为获胜分数无穷大
        return 1000000 if is_maximizing else -1000000
    # 检查对手获胜
    opponent = 3 - player
    if check_win(board, opponent):
        return -1000000 if is_maximizing else 1000000
    
    if depth == 0 or is_board_full(board):
        return evaluate_board(board, player)
    
    legal_moves = get_legal_moves(board)
    if not legal_moves:
        return evaluate_board(board, player)
    
    # 走法排序
    legal_moves = order_moves(board, legal_moves, last_move_col)
    
    if is_maximizing:
        value = -float('inf')
        for col in legal_moves:
            new_board, row = drop_piece(board, col, player)
            if new_board is None:
                continue
            # 检查这一步是否立即获胜（若获胜则直接返回极大值）
            if check_win(new_board, player):
                return 1000000  # 剪枝，直接返回
            # 递归，下一层是对方回合，对方的最小化
            score = alpha_beta(new_board, depth-1, alpha, beta, False, opponent, col)
            value = max(value, score)
            alpha = max(alpha, value)
            if alpha >= beta:
                break  # beta剪枝
        return value
    else:
        value = float('inf')
        for col in legal_moves:
            new_board, row = drop_piece(board, col, player)
            if new_board is None:
                continue
            # 检查对手是否立刻获胜，若是则返回极小值
            if check_win(new_board, player):
                return -1000000
            score = alpha_beta(new_board, depth-1, alpha, beta, True, opponent, col)
            value = min(value, score)
            beta = min(beta, value)
            if alpha >= beta:
                break  # alpha剪枝
        return value

def find_immediate_win(board, player):
    """检查玩家是否有一列可以立即获胜，返回该列索引，若无返回-1"""
    legal = get_legal_moves(board)
    for col in legal:
        new_board, _ = drop_piece(board, col, player)
        if new_board and check_win(new_board, player):
            return col
    return -1

def find_immediate_block(board, player):
    """检查对手是否有一列可以立即获胜，返回需要堵的列索引，若无返回-1"""
    opponent = 3 - player
    return find_immediate_win(board, opponent)

def get_best_move(board, current_player):
    """
    主函数：给定棋盘和当前玩家，返回最佳落子列
    """
    # 1. 检查是否有立即获胜走法
    win_col = find_immediate_win(board, current_player)
    if win_col != -1:
        return win_col
    
    # 2. 检查是否需要防守
    block_col = find_immediate_block(board, current_player)
    if block_col != -1:
        return block_col
    
    # 3. 搜索决策
    legal = get_legal_moves(board)
    if not legal:
        return -1  # 棋盘已满，无走法
    
    best_score = -float('inf')
    best_col = legal[0]
    
    # 动态深度：根据剩余空位数调整，空位多时深度小，空位少时深度大
    empty_count = sum(1 for r in range(ROWS) for c in range(COLS) if board[r][c] == EMPTY)
    if empty_count > 30:
        depth = 6
    elif empty_count > 20:
        depth = 8
    else:
        depth = 10  # 残局可以更深
    
    # 走法排序
    legal_ordered = order_moves(board, legal, None)
    
    alpha = -float('inf')
    beta = float('inf')
    opponent = 3 - current_player
    
    for col in legal_ordered:
        new_board, row = drop_piece(board, col, current_player)
        if new_board is None:
            continue
        # 检查立即获胜已在前面处理，但再次检查以防漏
        if check_win(new_board, current_player):
            return col  # 强制获胜
        # 搜索，下一层是对手最小化
        score = alpha_beta(new_board, depth-1, alpha, beta, False, opponent, col)
        if score > best_score:
            best_score = score
            best_col = col
        alpha = max(alpha, best_score)
        # 若已找到必胜，可提前终止
        if best_score >= 1000000:
            break
    
    return best_col

# ===================== 测试与输入输出 =====================
def parse_input():
    """从标准输入读取棋盘数据，格式为7列6行，每行6个数字用空格分隔"""
    board = []
    for _ in range(ROWS):
        line = sys.stdin.readline().strip()
        # 允许一行内用空格或逗号分隔
        if ',' in line:
            row = [int(x.strip()) for x in line.split(',')]
        else:
            row = [int(x) for x in line.split()]
        if len(row) != COLS:
            raise ValueError(f"每行必须有{COLS}个数字")
        board.append(row)
    # 读取当前玩家
    player_line = sys.stdin.readline().strip()
    current_player = int(player_line)
    return board, current_player

if __name__ == "__main__":
    # 示例输入：
    # 0 0 0 0 0 0 0
    # 0 0 0 0 0 0 0
    # 0 0 0 0 0 0 0
    # 0 0 0 0 0 0 0
    # 0 0 0 0 0 0 0
    # 0 0 0 0 0 0 0
    # 1
    # 上述表示空棋盘，红方先手
    
    board, current_player = parse_input()
    best_col = get_best_move(board, current_player)
    print(best_col)  # 输出最佳列号（0-6）