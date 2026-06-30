"""
四子棋 策略对战全矩阵测试
===========================
测试 4 种策略两两之间的胜率（含自对弈），共 4×4 = 16 种组合。
通过调用后端 /battle 接口完成，每组对战先手/后手各半。

用法:
    python test_battle.py              # 使用默认 100 轮
    python test_battle.py --rounds 50  # 自定义每组的对战轮数
"""

import json
import sys
import time
import urllib.request
from typing import Optional

BASE_URL = "http://localhost:3014"
STRATEGIES = ["random", "greedy", "minimax", "enhanced"]
STRATEGY_NAMES = {
    "random": "随机",
    "greedy": "贪心",
    "minimax": "Minimax",
    "enhanced": "增强版",
}


def call_battle(strategy_a: str, strategy_b: str, rounds: int) -> Optional[dict]:
    """调用 POST /battle，返回 {a_win, b_win, draw, rounds} 或 None"""
    payload = json.dumps({
        "strategy_a": strategy_a,
        "strategy_b": strategy_b,
        "rounds": rounds,
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{BASE_URL}/battle",
        data=payload,
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req, timeout=600) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"  ✗ 请求失败: {strategy_a} vs {strategy_b} — {e}")
        return None


def format_pct(wins: int, total: int) -> str:
    if total == 0:
        return "   -   "
    return f"{wins / total * 100:6.2f}%"


# ── 辅助：用索引序号比较两个策略，避免字符串比较的字典序陷阱 ──
def idx(s: str) -> int:
    return STRATEGIES.index(s)


def get_battle_result(results: dict, sa: str, sb: str) -> Optional[dict]:
    """从 results 中取回 sa vs sb 的对战结果。
    results 以上三角存储（即只存 idx(sa) <= idx(sb) 的条目），
    本函数自动处理上下三角的对称查找。"""
    ia, ib = idx(sa), idx(sb)
    if ia <= ib:
        return results.get(sa, {}).get(sb)
    else:
        return results.get(sb, {}).get(sa)


def main():
    # 解析命令行参数
    rounds = 100
    args = sys.argv[1:]
    if len(args) >= 2 and args[0] == "--rounds":
        rounds = int(args[1])

    print("=" * 75)
    print("  四子棋策略对战全矩阵测试")
    print(f"  每组 {rounds} 轮（先/后手各 {rounds // 2} 轮），共 10 组，预计耗时数分钟")
    print("=" * 75)

    # ── 只测试上三角（含对角线），下三角由对称推导 ──
    # results[si][sj] = /battle 返回的 dict（仅存储 idx(si) <= idx(sj) 的结果）
    results: dict = {}
    # 记录每次对战的耗时，用于统计
    timings: dict = {}  # timings[(sa, sb)] = elapsed_seconds

    total_start = time.time()
    test_count = 0

    for i, sa in enumerate(STRATEGIES):
        for j, sb in enumerate(STRATEGIES):
            if j < i:
                continue  # 下三角跳过，后面从对称位置推导

            test_count += 1
            label_a = STRATEGY_NAMES[sa]
            label_b = STRATEGY_NAMES[sb]

            print(f"\n[{test_count}/10] {label_a}  vs  {label_b} ...", end=" ", flush=True)
            t0 = time.time()

            res = call_battle(sa, sb, rounds)
            if res is None:
                print("失败，跳过")
                continue

            elapsed = time.time() - t0
            # setdefault 确保 results[sa] 存在，然后存入 results[sa][sb]
            results.setdefault(sa, {})[sb] = res
            timings[(sa, sb)] = elapsed

            print(f"✓ {elapsed:.1f}s  "
                  f"| {label_a}胜:{res['a_win']}  "
                  f"{label_b}胜:{res['b_win']}  "
                  f"平:{res['draw']}")

    total_elapsed = time.time() - total_start
    print(f"\n{'=' * 75}")
    print(f"  全部测试完成，总耗时 {total_elapsed:.0f} 秒")
    print(f"{'=' * 75}")

    # ── 胜率矩阵 ──
    # 行 = 策略 A（我们关注它的胜率），列 = 策略 B（对手）
    # 单元格 = 行策略对列策略的胜率
    print(f"\n{' 胜率矩阵 (行策略 vs 列策略)':^75}")
    print(f"{'行 \\ 列':>10}", end="")
    for sb in STRATEGIES:
        print(f"{STRATEGY_NAMES[sb]:>10}", end="")
    print()

    for sa in STRATEGIES:
        print(f"{STRATEGY_NAMES[sa]:>10}", end="")
        for sb in STRATEGIES:
            r = get_battle_result(results, sa, sb)

            if r is None:
                print(f"{'  N/A  ':>10}", end="")
                continue

            if sa == sb:
                # 自对弈：不适用胜率概念，显示 —
                print(f"{'  —   ':>10}", end="")
            else:
                # sa 作为 strategy_a（先手红方）时的胜场
                ia, ib = idx(sa), idx(sb)
                if ia < ib:
                    wins = r["a_win"]
                else:
                    wins = r["b_win"]
                print(f"{format_pct(wins, r['rounds']):>10}", end="")
        print()

    # ── 综合统计 ──
    print(f"\n{' 综合排名 (按总胜率排序)':^75}")
    print("-" * 75)
    print(f"{'排名':<5}{'策略':<10}{'总胜场':<8}{'总对局':<8}{'胜率':<10}{'对平局':<8}")
    print("-" * 48)

    totals = {s: {"wins": 0, "games": 0, "draws": 0} for s in STRATEGIES}

    for sa in STRATEGIES:
        for sb in STRATEGIES:
            if sa == sb:
                continue
            r = get_battle_result(results, sa, sb)
            if r is None:
                continue

            totals[sa]["games"] += r["rounds"]
            totals[sa]["draws"] += r["draw"]

            ia, ib = idx(sa), idx(sb)
            if ia < ib:
                totals[sa]["wins"] += r["a_win"]
            else:
                totals[sa]["wins"] += r["b_win"]

    ranked = sorted(
        STRATEGIES,
        key=lambda s: totals[s]["wins"] / max(totals[s]["games"], 1),
        reverse=True,
    )

    for rank, s in enumerate(ranked, 1):
        t = totals[s]
        rate = t["wins"] / max(t["games"], 1) * 100
        print(f"{rank:<5}{STRATEGY_NAMES[s]:<10}{t['wins']:<8}{t['games']:<8}{rate:5.2f}%     {t['draws']:<8}")

    # ── 对局详情汇总 ──
    print(f"\n{' 全部对局详情':^75}")
    print("-" * 75)
    print(f"{'红方 (先手)':<14}{'黄方 (后手)':<14}{'红胜':<8}{'黄胜':<8}{'平局':<8}{'轮数':<8}{'耗时':<10}")
    print("-" * 68)

    for sa in STRATEGIES:
        for sb in STRATEGIES:
            if idx(sa) > idx(sb):
                continue
            r = results.get(sa, {}).get(sb)
            if r is None:
                continue
            elapsed = timings.get((sa, sb), 0)
            print(f"{STRATEGY_NAMES[sa]:<14}{STRATEGY_NAMES[sb]:<14}"
                  f"{r['a_win']:<8}{r['b_win']:<8}{r['draw']:<8}{r['rounds']:<8}{elapsed:.1f}s")

    # ── 算法耗时评估 ──
    print(f"\n{' 算法耗时评估':^75}")
    print("=" * 75)

    # 按策略统计耗时：该策略参与的所有对局
    # 注意：自对弈 (sa==sb) 只计一次，避免重复
    strategy_timings = {s: [] for s in STRATEGIES}

    for (sa, sb), elapsed in timings.items():
        if sa == sb:
            strategy_timings[sa].append(elapsed)
        else:
            strategy_timings[sa].append(elapsed)
            strategy_timings[sb].append(elapsed)

    print(f"{'策略':<10}{'参与对局':<10}{'平均耗时':<12}{'最大耗时':<12}{'最小耗时':<12}{'总耗时':<12}")
    print("-" * 68)

    for s in STRATEGIES:
        times = strategy_timings[s]
        if times:
            avg_t = sum(times) / len(times)
            max_t = max(times)
            min_t = min(times)
            sum_t = sum(times)
            print(f"{STRATEGY_NAMES[s]:<10}{len(times):<10}{avg_t:6.1f}s     {max_t:6.1f}s     {min_t:6.1f}s     {sum_t:6.1f}s")
        else:
            print(f"{STRATEGY_NAMES[s]:<10}{'无数据':<10}")

    # 全部对局耗时统计
    all_times = list(timings.values())
    if all_times:
        avg_all = sum(all_times) / len(all_times)
        max_all = max(all_times)
        min_all = min(all_times)
        print("-" * 68)
        print(f"{'全部对局':<10}{len(all_times):<10}{avg_all:6.1f}s     {max_all:6.1f}s     {min_all:6.1f}s     {total_elapsed:6.0f}s")

    print()


if __name__ == "__main__":
    main()
