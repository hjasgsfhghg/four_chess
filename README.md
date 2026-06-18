# 四子棋（Connect Four）

计算思维与程序实践课程大作业 —— 游戏最优策略分析系统。

## 项目结构

```
four_chess-main/
├── back/
│   ├── server.py      # Flask 后端入口（localhost:3014）
│   └── add.py         # AI 引擎：随机 / 贪心 / Minimax / Alpha-Beta增强
└── front/
    └── src/
        ├── views/
        │   ├── Menu.vue         # 主菜单
        │   ├── GameBoard.vue    # 游戏棋盘（单人/双人/观战/策略对战）
        │   └── BattleStats.vue  # 独立策略统计页
        └── router/index.js
```

## 快速启动

### 1. 后端

```bash
cd back
pip install flask flask-cors
python server.py
```

服务运行在 **http://localhost:3014**

### 2. 前端

```bash
cd front
npm install
npm run dev
```

服务运行在 **http://localhost:5173**，浏览器打开即可。

## 四种 AI 策略

| 策略 | 说明 |
|---|---|
| 随机 | 从合法列中随机选择 |
| 贪心 | 优先获胜 → 封堵对手 → 随机 |
| Minimax | Alpha-Beta 剪枝，固定深度 4 |
| Alpha-Beta 增强 | 动态深度 6/8/10 + 置换表缓存 |

## 玩法模式

- **单人挑战**：玩家执红 vs AI执黄
- **双人对战**：两名玩家本地轮流落子
- **观战模式**：棋盘上实时观看两种策略自动对战，右侧可调参并查看实时战绩
