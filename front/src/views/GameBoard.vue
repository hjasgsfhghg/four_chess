<template>
  <div class="game-wrap" :class="{ 'battle-layout': mode === 'battle' }">
    <!-- ═══ 左侧：棋盘区域 ═══ -->
    <div class="board-section">
      <div class="player-turn">
        <span class="turn-dot" :class="currentPlayer === 1 ? 'red' : 'yellow'"></span>
        <p>{{ currentPlayer === 1 ? '红方' : '黄方' }}回合</p>
      </div>

      <div v-if="mode === 'single' && aiThinking" class="ai-thinking">AI 思考中…</div>

      <div v-if="mode === 'watch'" class="watch-status">
        <span>观战中</span>
        <button class="pause-btn" @click="togglePause">{{ watchPaused ? '继续' : '暂停' }}</button>
      </div>

      <div v-if="mode === 'battle'" class="battle-info-bar">
        <div v-show="battleRunning && !battleRoundEnd" class="battle-status-bar">
          <span>第 {{ currentRound }} / {{ battleRounds }} 局</span>
          <span class="battle-role">
            红={{ currentRound % 2 === 1 ? '策略A' : '策略B' }}
            黄={{ currentRound % 2 === 1 ? '策略B' : '策略A' }}
          </span>
        </div>
        <div v-show="battleRoundEnd" class="battle-round-result">
          {{ roundResultText }}
        </div>
      </div>

      <div class="board">
        <div class="win-line"
          :class="[
            lineInfo.show ? lineInfo.type : '',
            { 'line-h': lineInfo.type === 'h', 'line-v': lineInfo.type === 'v', 'line-s': lineInfo.type === 's', 'line-b': lineInfo.type === 'b' }
          ]"
          :style="getLineStyle"
        ></div>
        <div v-for="r in rowCount" :key="r" class="row">
          <div v-for="c in colCount" :key="c" class="cell" @click="handleClick(r-1, c-1)">
            <div class="cell-slot"></div>
            <div class="piece"
              :class="{ cell1: board[r-1][c-1] === 1, cell2: board[r-1][c-1] === 2 }"
            ></div>
          </div>
        </div>
      </div>

      <div class="btn-group" v-show="winner === 0">
        <button @click="resetGame">重新开始</button>
        <button @click="goBack">返回主菜单</button>
      </div>

      <div class="modal" v-if="winner !== 0 && mode !== 'battle'">
        <h3 class="modal-title" :class="[winner === 1 ? 'win-red' : '', winner === 2 ? 'win-yellow' : '', winner === 3 ? 'win-draw' : '']">{{ modalText }}</h3>
        <button @click="resetGame">再来一局</button>
      </div>
    </div>

    <!-- ═══ 右侧：策略对战面板 ═══ -->
    <div v-if="mode === 'battle'" class="battle-panel">
      <h2>策略对战</h2>

      <div class="battle-config">
        <div class="battle-select-row">
          <label>策略 A</label>
          <select v-model="battleStrategyA" :disabled="battleRunning">
            <option value="random">随机</option>
            <option value="greedy">贪心</option>
            <option value="minimax">Minimax（深度4）</option>
            <option value="enhanced">Alpha-Beta 增强</option>
          </select>
        </div>
        <div class="battle-vs">VS</div>
        <div class="battle-select-row">
          <label>策略 B</label>
          <select v-model="battleStrategyB" :disabled="battleRunning">
            <option value="random">随机</option>
            <option value="greedy">贪心</option>
            <option value="minimax">Minimax（深度4）</option>
            <option value="enhanced">Alpha-Beta 增强</option>
          </select>
        </div>
        <div class="battle-select-row">
          <label>局数</label>
          <select v-model.number="battleRounds" :disabled="battleRunning">
            <option :value="10">10</option>
            <option :value="50">50</option>
            <option :value="100">100</option>
            <option :value="200">200</option>
          </select>
        </div>
        <div class="battle-select-row">
          <label>间隔(ms)</label>
          <input type="number" v-model.number="tgDelay" :disabled="battleRunning" min="0" max="5000" step="100" />
        </div>
        <div class="battle-select-row">
          <label>API 地址</label>
          <select v-model="apiMode" :disabled="battleRunning" @change="onApiModeChange">
            <option value="network">联网</option>
            <option value="local">本地</option>
          </select>
        </div>
        <button class="battle-start-btn" @click="battleRunning ? stopBattle() : startBattle()">
          {{ battleRunning ? '停止对战' : '开始对战' }}
        </button>
      </div>

      <div class="battle-stats" v-if="battleStarted">
        <h3>实时战绩</h3>
        <div class="battle-stat-row">
          <span class="stat-label">策略A 胜</span>
          <span class="stat-value stat-a">{{ battleStatsA }}</span>
        </div>
        <div class="battle-stat-row">
          <span class="stat-label">策略B 胜</span>
          <span class="stat-value stat-b">{{ battleStatsB }}</span>
        </div>
        <div class="battle-stat-row">
          <span class="stat-label">平局</span>
          <span class="stat-value stat-draw">{{ battleStatsDraw }}</span>
        </div>
        <div class="battle-stat-row">
          <span class="stat-label">已完成</span>
          <span class="stat-value">{{ battleStatsA + battleStatsB + battleStatsDraw }} / {{ battleRounds }}</span>
        </div>

        <div class="battle-summary-bar">
          <div class="summary-seg seg-a" :style="{ flex: battleStatsA || 0.1 }" :title="'策略A 胜: ' + battleStatsA"></div>
          <div class="summary-seg seg-draw" :style="{ flex: battleStatsDraw || 0.1 }" :title="'平局: ' + battleStatsDraw"></div>
          <div class="summary-seg seg-b" :style="{ flex: battleStatsB || 0.1 }" :title="'策略B 胜: ' + battleStatsB"></div>
        </div>

        <div class="battle-pct-row">
          <span>{{ pctA }}%</span>
          <span>{{ pctDraw }}%</span>
          <span>{{ pctB }}%</span>
        </div>

        <div class="battle-timing">
          <div class="timing-row"><span class="timing-label">策略A 耗时</span><span class="timing-value stat-a">{{ apiDurationA }}</span></div>
          <div class="timing-sub"><span>最大 {{ statsA.max }}</span><span>最小 {{ statsA.min }}</span><span>平均 {{ statsA.avg }}</span></div>
          <div class="timing-row"><span class="timing-label">策略B 耗时</span><span class="timing-value stat-b">{{ apiDurationB }}</span></div>
          <div class="timing-sub"><span>最大 {{ statsB.max }}</span><span>最小 {{ statsB.min }}</span><span>平均 {{ statsB.avg }}</span></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter, useRoute } from 'vue-router'
import { ref, computed, onMounted, onUnmounted } from 'vue'

const router = useRouter()
const route = useRoute()

const mode = computed(() => route.query.mode || 'double')

const lineInfo = ref({ show: false, type: '', startX: 0, startY: 0, endX: 0, endY: 0 })
const rowCount = 6
const colCount = 7
const board = ref(Array(rowCount).fill(0).map(() => Array(colCount).fill(0)))
const currentPlayer = ref(1)
const winner = ref(0)
const aiThinking = ref(false)
const watchPaused = ref(false)
const watchTimer = ref(null)

const battleStrategyA = ref('enhanced')
const battleStrategyB = ref('random')
const battleRounds = ref(50)
const battleRunning = ref(false)
const battleStarted = ref(false)
const battleRoundEnd = ref(false)
const currentRound = ref(1)
const battleStatsA = ref(0)
const battleStatsB = ref(0)
const battleStatsDraw = ref(0)
const battleWinnerCache = ref(0)

const cellSize = 80
const gap = 10
const boardPadding = 10
const tgDelay = ref(0)
const apiMode = ref('network')
const apiBase = ref('http://223.109.143.156:3014')

const onApiModeChange = () => {
  apiBase.value = apiMode.value === 'local' ? 'http://localhost:3014' : 'http://223.109.143.156:3014'
}

const apiDurationA = ref('-')
const apiDurationB = ref('-')
const timingsA = ref([])
const timingsB = ref([])

const statsA = computed(() => calcStats(timingsA.value))
const statsB = computed(() => calcStats(timingsB.value))
const calcStats = (arr) => {
  if (arr.length === 0) return { max: '-', min: '-', avg: '-' }
  return {
    max: `${Math.max(...arr).toFixed(0)}ms`,
    min: `${Math.min(...arr).toFixed(0)}ms`,
    avg: `${(arr.reduce((a, b) => a + b, 0) / arr.length).toFixed(0)}ms`
  }
}

const goBack = () => {
  stopBattle()
  router.push('/')
}

const resetBoardOnly = () => {
  if (watchTimer.value) { clearTimeout(watchTimer.value); watchTimer.value = null }
  board.value = Array(rowCount).fill(0).map(() => Array(colCount).fill(0))
  currentPlayer.value = 1
  winner.value = 0
  aiThinking.value = false
  battleRoundEnd.value = false
  battleWinnerCache.value = 0
  lineInfo.value = { show: false, type: '', startX: 0, startY: 0, endX: 0, endY: 0 }
}

const resetGame = () => {
  stopBattle()
  battleStarted.value = false
  battleStatsA.value = 0
  battleStatsB.value = 0
  battleStatsDraw.value = 0
  currentRound.value = 1
  resetBoardOnly()
}

const modalText = computed(() => {
  switch (winner.value) {
    case 1: return '红方获胜'
    case 2: return '黄方获胜'
    case 3: return '本局平局'
    default: return ''
  }
})

const roundResultText = computed(() => {
  switch (battleWinnerCache.value) {
    case 1: return `第 ${currentRound.value} 局：红方胜`
    case 2: return `第 ${currentRound.value} 局：黄方胜`
    case 3: return `第 ${currentRound.value} 局：平局`
    default: return ''
  }
})

const pctA = computed(() => {
  const total = battleStatsA.value + battleStatsB.value + battleStatsDraw.value
  if (total === 0) return 0
  return (battleStatsA.value / total * 100).toFixed(1)
})
const pctB = computed(() => {
  const total = battleStatsA.value + battleStatsB.value + battleStatsDraw.value
  if (total === 0) return 0
  return (battleStatsB.value / total * 100).toFixed(1)
})
const pctDraw = computed(() => {
  const total = battleStatsA.value + battleStatsB.value + battleStatsDraw.value
  if (total === 0) return 0
  return (battleStatsDraw.value / total * 100).toFixed(1)
})

const checkWin = (row, col, player) => {
  const dirs = [[0, 1, 'h'], [1, 0, 'v'], [1, 1, 's'], [1, -1, 'b']]
  for (let [dr, dc, type] of dirs) {
    let list = [[row, col]]
    let r = row + dr, c = col + dc
    while (r >= 0 && r < rowCount && c >= 0 && c < colCount && board.value[r][c] === player) {
      list.push([r, c]); r += dr; c += dc
    }
    r = row - dr; c = col - dc
    while (r >= 0 && r < rowCount && c >= 0 && c < colCount && board.value[r][c] === player) {
      list.unshift([r, c]); r -= dr; c -= dc
    }
    if (list.length >= 4) {
      const first = list[0], last = list[list.length - 1]
      lineInfo.value = { show: true, type, startX: first[0], startY: first[1], endX: last[0], endY: last[1] }
      return true
    }
  }
  return false
}

const getLineStyle = computed(() => {
  if (!lineInfo.value.show) return {}
  const { type, startX, startY, endX, endY } = lineInfo.value
  const startLeft = boardPadding + startY * (cellSize + gap) + cellSize / 2
  const startTop = boardPadding + startX * (cellSize + gap) + cellSize / 2
  const endLeft = boardPadding + endY * (cellSize + gap) + cellSize / 2
  const endTop = boardPadding + endX * (cellSize + gap) + cellSize / 2

  if (type === 'h') {
    const width = (endY - startY) * (cellSize + gap)
    return { left: `${startLeft}px`, top: `${startTop}px`, width: `${width}px`, height: '4px', transform: 'translateY(-50%)' }
  }
  if (type === 'v') {
    const height = (endX - startX) * (cellSize + gap)
    return { left: `${startLeft}px`, top: `${startTop}px`, width: '4px', height: `${height}px`, transform: 'translateX(-50%)' }
  }
  const dx = endLeft - startLeft, dy = endTop - startTop
  const len = Math.sqrt(dx * dx + dy * dy)
  const angle = Math.atan2(dy, dx) * 180 / Math.PI
  return { left: `${startLeft}px`, top: `${startTop}px`, width: `${len}px`, height: '4px', transformOrigin: '0 50%', transform: `rotate(${angle}deg)` }
})

const isBoardFull = () => {
  for (let c = 0; c < colCount; c++) { if (board.value[0][c] === 0) return false }
  return true
}

const findDropRow = (col) => {
  for (let r = rowCount - 1; r >= 0; r--) { if (board.value[r][col] === 0) return r }
  return -1
}

const getStrategyForPlayer = (player) => {
  if (currentRound.value % 2 === 1) {
    return player === 1 ? battleStrategyA.value : battleStrategyB.value
  } else {
    return player === 1 ? battleStrategyB.value : battleStrategyA.value
  }
}

const recordBattleResult = () => {
  const w = winner.value
  battleWinnerCache.value = w
  battleRoundEnd.value = true

  if (w === 1) {
    if (currentRound.value % 2 === 1) { battleStatsA.value++ } else { battleStatsB.value++ }
  } else if (w === 2) {
    if (currentRound.value % 2 === 1) { battleStatsB.value++ } else { battleStatsA.value++ }
  } else {
    battleStatsDraw.value++
  }
}

const scheduleNextRound = () => {
  if (!battleRunning.value) return
  if (currentRound.value >= battleRounds.value) {
    battleRunning.value = false
    return
  }
  currentRound.value++
  resetBoardOnly()
  watchTimer.value = setTimeout(() => triggerAI(1), tgDelay.value)
}

const doDrop = (row, col, player) => {
  board.value[row][col] = player

  if (checkWin(row, col, player)) {
    winner.value = player
    if (mode.value === 'battle' && battleRunning.value) {
      recordBattleResult()
      setTimeout(scheduleNextRound, 1000)
    }
    return
  }
  if (isBoardFull()) {
    winner.value = 3
    if (mode.value === 'battle' && battleRunning.value) {
      recordBattleResult()
      setTimeout(scheduleNextRound, 1000)
    }
    return
  }
  const nextPlayer = player === 1 ? 2 : 1
  currentPlayer.value = nextPlayer
  afterTurn()
}

const afterTurn = () => {
  if (mode.value === 'single' && currentPlayer.value === 2) {
    triggerAI(2)
  } else if (mode.value === 'watch' && !watchPaused.value && winner.value === 0) {
    watchTimer.value = setTimeout(() => triggerAI(currentPlayer.value), tgDelay.value)
  } else if (mode.value === 'battle' && battleRunning.value && winner.value === 0) {
    watchTimer.value = setTimeout(() => triggerAI(currentPlayer.value), tgDelay.value)
  }
}

const triggerAI = async (player) => {
  const t0 = performance.now()

  aiThinking.value = true
  try {
    const flippedBoard = board.value.map(r => [...r]).reverse()
    const strategy = mode.value === 'battle' ? getStrategyForPlayer(player) : 'enhanced'
    const resp = await fetch(`${apiBase.value}/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ board: flippedBoard, who: player, strategy })
    })
    const data = await resp.json()
    const durationMs = performance.now() - t0
    const duration = `${durationMs.toFixed(0)}ms`
    if (mode.value === 'battle') {
      const isA = (currentRound.value % 2 === 1) === (player === 1)
      if (isA) {
        apiDurationA.value = duration
        timingsA.value.push(durationMs)
      } else {
        apiDurationB.value = duration
        timingsB.value.push(durationMs)
      }
    }
    if (data.drop === -1 || winner.value !== 0) { aiThinking.value = false; return }
    const targetRow = findDropRow(data.drop)
    if (targetRow === -1) { aiThinking.value = false; return }
    doDrop(targetRow, data.drop, player)
  } catch (e) {
    console.error('AI API 调用失败:', e)
  } finally {
    aiThinking.value = false
  }
}

const handleClick = (clickRow, clickCol) => {
  if (winner.value !== 0) return
  if (aiThinking.value) return
  if (mode.value === 'single' && currentPlayer.value === 2) return
  if (mode.value === 'watch') return
  if (mode.value === 'battle') return

  const targetRow = findDropRow(clickCol)
  if (targetRow === -1) return
  doDrop(targetRow, clickCol, currentPlayer.value)
}

const togglePause = () => {
  if (winner.value !== 0) return
  watchPaused.value = !watchPaused.value
  if (!watchPaused.value) {
    watchTimer.value = setTimeout(() => triggerAI(currentPlayer.value), tgDelay.value)
  } else {
    if (watchTimer.value) { clearTimeout(watchTimer.value); watchTimer.value = null }
  }
}

const startBattle = () => {
  battleStatsA.value = 0
  battleStatsB.value = 0
  battleStatsDraw.value = 0
  currentRound.value = 1
  battleRunning.value = true
  battleStarted.value = true
  apiDurationA.value = '-'
  apiDurationB.value = '-'
  timingsA.value = []
  timingsB.value = []
  resetBoardOnly()
  watchTimer.value = setTimeout(() => triggerAI(1), tgDelay.value)
}

const stopBattle = () => {
  battleRunning.value = false
  if (watchTimer.value) { clearTimeout(watchTimer.value); watchTimer.value = null }
}

onMounted(() => {
  if (mode.value === 'watch') {
    watchTimer.value = setTimeout(() => triggerAI(1), tgDelay.value)
  }
})

onUnmounted(() => {
  if (watchTimer.value) clearTimeout(watchTimer.value)
})
</script>

<style scoped>
.game-wrap {
  text-align: center;
  padding-top: 40px;
}
.battle-layout {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  gap: 60px;
  padding: 40px 40px 0;
  max-width: 1400px;
  margin: 0 auto;
}
.board-section { flex-shrink: 0; }

.player-turn {
  display: flex; align-items: center; justify-content: center; gap: 20px; margin: 20px 0;
}
.turn-dot { width: 50px; height: 50px; border-radius: 50%; }
.turn-dot.red  { background-color: #e53935; }
.turn-dot.yellow { background-color: #d8e51e; }
.player-turn:has(.red) p    { color: #e53935; }
.player-turn:has(.yellow) p { color: #d8e51e; }
.player-turn p { margin: 0; font-size: 35px; font-weight: bold; }

.ai-thinking {
  text-align: center; font-size: 24px; color: #ff9800; margin: 10px 0;
  animation: pulse 1s ease-in-out infinite;
}
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }

.watch-status {
  display: flex; align-items: center; justify-content: center; gap: 20px;
  margin: 10px 0; font-size: 24px; color: #2196f3;
}
.pause-btn { width: 100px; height: 40px; font-size: 18px; cursor: pointer; border-radius: 6px; }

.battle-info-bar { min-height: 48px; margin: 10px 0; }
.battle-status-bar {
  display: flex; align-items: center; justify-content: center; gap: 30px;
  margin: 10px 0; font-size: 22px; color: #333;
}
.battle-role { font-size: 16px; color: #666; }

.battle-round-result {
  font-size: 28px; font-weight: bold; color: #ff5722;
  margin: 10px 0; animation: pulse 0.8s ease-in-out infinite;
}

.btn-group { display: flex; justify-content: center; gap: 100px; margin-top: 50px; min-height: 100px; }
button { width: 200px; height: 100px; cursor: pointer; font-size: 25px; border-radius: 6px; }

.board {
  display: inline-grid; gap: 10px; background: #333; padding: 10px;
  border-radius: 8px; margin: 50px auto; overflow: hidden; position: relative;
}
.win-line { position: absolute; background: #ffffff; z-index: 99; pointer-events: none; display: none; }
.win-line.line-h, .win-line.line-v, .win-line.line-s, .win-line.line-b { display: block; }
.row { display: flex; gap: 10px; }
.cell { width: 80px; height: 80px; position: relative; }
.cell-slot { width: 100%; height: 100%; border-radius: 50%; background: #ffffff; }
.piece { position: absolute; top: 0; left: 0; width: 100%; height: 100%; border-radius: 50%; }
.cell1 { background: #e53935 !important; }
.cell2 { background: #d8e51e !important; }

.modal {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.5); display: flex; flex-direction: column;
  justify-content: center; align-items: center; z-index: 999;
}
.modal-title { font-size: 150px; margin-top: 250px; margin-bottom: 40px; font-weight: bold; }
.modal-title.win-red  { color: #e53935; }
.modal-title.win-yellow { color: #d8e51e; }
.modal-title.win-draw  { color: #fff; }
.modal button { width: 200px; height: 100px; font-size: 25px; cursor: pointer; border: none; border-radius: 6px; margin-top: 250px; }

/* ═══ 右侧对战面板 ═══ */
.battle-panel {
  width: 380px; background: #f5f5f5; border-radius: 12px;
  padding: 30px; text-align: center; flex-shrink: 0;
}
.battle-panel h2 { margin: 0 0 24px 0; font-size: 28px; }
.battle-config { display: flex; flex-direction: column; gap: 14px; }
.battle-select-row { display: flex; align-items: center; gap: 12px; }
.battle-select-row label { width: 70px; text-align: right; font-size: 18px; font-weight: bold; }
.battle-select-row select, .battle-select-row input { flex: 1; height: 38px; font-size: 16px; border-radius: 6px; padding: 0 8px; }
.battle-vs { font-size: 24px; font-weight: bold; color: #888; }
.battle-start-btn { width: 100%; height: 48px; font-size: 20px; cursor: pointer; border-radius: 6px; margin-top: 6px; }

.battle-stats { margin-top: 24px; }
.battle-stats h3 { margin-bottom: 14px; }
.battle-stat-row { display: flex; justify-content: space-between; padding: 6px 0; font-size: 18px; border-bottom: 1px solid #ddd; }
.stat-label { font-weight: bold; }
.stat-a  { color: #e53935; }
.stat-b  { color: #d8b81e; }
.stat-draw { color: #888; }

.battle-summary-bar { display: flex; height: 24px; border-radius: 6px; overflow: hidden; margin-top: 14px; gap: 2px; }
.summary-seg { min-width: 2px; }
.seg-a  { background: #e53935; }
.seg-b  { background: #d8b81e; }
.seg-draw { background: #9e9e9e; }

.battle-pct-row { display: flex; justify-content: space-around; margin-top: 6px; font-size: 14px; color: #666; }

.battle-timing { margin-top: 16px; background: #fff; border-radius: 8px; padding: 12px 16px; }
.timing-row { display: flex; justify-content: space-between; padding: 4px 0; font-size: 15px; }
.timing-label { color: #888; }
.timing-value { color: #333; font-weight: bold; font-variant-numeric: tabular-nums; }
.timing-sub { display: flex; justify-content: space-around; font-size: 13px; color: #999; padding: 2px 0 6px; }
</style>

<style>
html, body {
  scrollbar-width: none;
  -ms-overflow-style: none;
}
html::-webkit-scrollbar, body::-webkit-scrollbar { display: none; }
</style>
