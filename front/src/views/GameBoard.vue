<template>
  <div class="game-wrap">
    <div class="player-turn">
      <span class="turn-dot" :class="currentPlayer === 1 ? 'red' : 'yellow'"></span>
      <p>{{ currentPlayer === 1 ? '红方' : '黄方' }}回合</p>
    </div>
    <div class="board">
      <div class="win-line"
        :class="[
          lineInfo.show ? lineInfo.type : '',
          {
            'line-h': lineInfo.type === 'h',
            'line-v': lineInfo.type === 'v',
            'line-s': lineInfo.type === 's',
            'line-b': lineInfo.type === 'b'
          }
        ]"
        :style="getLineStyle"
      ></div>
      <!-- 棋盘 -->
      <div v-for="r in rowCount" :key="r" class="row">
        <div v-for="c in colCount" :key="c" class="cell" @click="handleClick(r-1, c-1)">
          <div class="cell-slot"></div>
          <div class="piece" 
            :class="{
              cell1: board[r-1][c-1] === 1, 
              cell2: board[r-1][c-1] === 2, 
              'cell-fall': fallRow === r && fallCol === c
            }"
          ></div>
        </div>
      </div>
    </div>
    <div class="btn-group" v-show="winner === 0"> 
      <button @click="resetGame">重新开始</button>
      <button @click="goBack">返回主菜单</button>
    </div>
    <div class="modal" v-if="winner !== 0">
      <h3 class="modal-title" :class="[winner === 1 ? 'win-red' : '', winner === 2 ? 'win-yellow' : '', winner === 3 ? 'win-draw' : '']">{{ modalText }}</h3>
      <button @click="resetGame">再来一局</button>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ref } from 'vue'
import { computed } from 'vue'
const router = useRouter()

const lineInfo = ref({
  show: false,
  type: '',
  startX: 0, startY:0,
  endX: 0, endY:0
})

const goBack = () => {
  router.push('/')
}

const resetGame = () => {
  board.value = Array(rowCount).fill(0).map(() => Array(colCount).fill(0))
  currentPlayer.value = 1
  winner.value = 0
  fallRow.value = 0
  fallCol.value = 0
  isAnimating.value = false
  lineInfo.value = {
    show: false,
    type: '',
    startX: 0, startY:0,
    endX: 0, endY:0
  }
}

const modalText = computed(() => {
  switch(winner.value) {
    case 1: return '红方获胜'
    case 2: return '黄方获胜'
    case 3: return '本局平局'
    default: return ''
  }
})

//计算棋子连线的坐标
const cellSize = 80
const gap = 10
const boardPadding = 10

const rowCount = 6
const colCount = 7
const board = ref(Array(rowCount).fill(0).map(() => Array(colCount).fill(0)))
const currentPlayer = ref(1)
const winner = ref(0) // 0=未分胜负，1=红方胜，2=黄方胜，3=平局
const fallRow = ref(-1)
const fallCol = ref(-1)
const isAnimating = ref(false)

// 判断是否连成四子
const checkWin = (row, col, player) => {
  // 四个方向：水平、垂直、左上→右下、右上→左下
  const dirs = [
    [0, 1, 'h'],
    [1, 0, 'v'],
    [1, 1, 's'],
    [1, -1, 'b']
  ]
  for (let [dr, dc, type] of dirs) {
    let list = [[row, col]]
    // 正方向查找
    let r = row + dr
    let c = col + dc
    while (r >= 0 && r < rowCount && c >=0 && c < colCount && board.value[r][c] === player) {
      list.push([r, c])
      r += dr
      c += dc
    }
    // 反方向查找
    r = row - dr
    c = col - dc
    while (r >= 0 && r < rowCount && c >=0 && c < colCount && board.value[r][c] === player) {
      list.unshift([r, c])
      r -= dr
      c -= dc
    }
    // 连成4个及以上，获胜
    if (list.length >= 4) {
      const first = list[0]
      const last = list[list.length - 1]
      lineInfo.value = {
        show: true,
        type: type,
        startX: first[0],
        startY: first[1],
        endX: last[0],
        endY: last[1]
      }
      return true
    }
  }
  return false
}
const getLineStyle = computed(() => {
  if (!lineInfo.value.show) return {}

  const { type, startX, startY, endX, endY } = lineInfo.value
  // 格子中心坐标
  const startLeft = boardPadding + startY * (cellSize + gap) + cellSize / 2
  const startTop = boardPadding + startX * (cellSize + gap) + cellSize / 2
  const endLeft = boardPadding + endY * (cellSize + gap) + cellSize / 2
  const endTop = boardPadding + endX * (cellSize + gap) + cellSize / 2

  // 水平/垂直 直接算长度
  if (type === 'h') {
    const width = (endY - startY) * (cellSize + gap)
    return {
      left: `${startLeft}px`,
      top: `${startTop}px`,
      width: `${width}px`,
      height: '4px',
      transform: 'translateY(-50%)'
    }
  }
  if (type === 'v') {
    const height = (endX - startX) * (cellSize + gap)
    return {
      left: `${startLeft}px`,
      top: `${startTop}px`,
      width: '4px',
      height: `${height}px`,
      transform: 'translateX(-50%)'
    }
  }

  // 斜线：计算斜边长度 + 旋转角度
  const dx = endLeft - startLeft
  const dy = endTop - startTop
  const len = Math.sqrt(dx * dx + dy * dy)
  const angle = Math.atan2(dy, dx) * 180 / Math.PI

  return {
    left: `${startLeft}px`,
    top: `${startTop}px`,
    width: `${len}px`,
    height: '4px',
    transformOrigin: '0 50%',
    transform: `rotate(${angle}deg)`
  }
})
// 判断棋盘是否已满（平局）
const isBoardFull = () => {
  // 遍历每一列，只要还有空位就不是平局
  for (let c = 0; c < colCount; c++) {
    if (board.value[0][c] === 0) {
      return false
    }
  }
  return true
}

// 点击格子触发落子
const handleClick = (clickRow, clickCol) => {

  if (winner.value !== 0 || isAnimating.value) return

  let targetRow = -1
  for (let r = rowCount - 1; r >= 0; r--) {
    if (board.value[r][clickCol] === 0) {
      targetRow = r
      break
    }
  }
  if (targetRow === -1) return
  isAnimating.value = true
  fallRow.value = targetRow + 1
  fallCol.value = clickCol + 1
  board.value[targetRow][clickCol] = currentPlayer.value
  setTimeout(() => {
    fallRow.value = -1
    fallCol.value = -1
    if (checkWin(targetRow, clickCol, currentPlayer.value)) {
      winner.value = currentPlayer.value
      return
    }
    if (isBoardFull()) {
      winner.value = 3
      return
    }
    currentPlayer.value = currentPlayer.value === 1 ? 2 : 1
    isAnimating.value = false
  }, 500)
}
</script>

<style scoped>
.game-container {
  text-align: center;
  padding-top: 100px;
}
.player-turn {
  display: flex;
  align-items: center;/* 控制子元素垂直方向对齐 */
  justify-content: center;/* 水平居中 */
  gap: 20px; /* 圆点和文字间距 */
  margin: 20px 0;
}
/* 左侧圆形色块 */
.turn-dot {
  width: 50px;
  height: 50px;
  border-radius: 50%; /* 变成正圆 */
}
.turn-dot.red {
  background-color: #e53935;
}
.turn-dot.yellow {
  background-color: #d8e51e;
}
.player-turn:has(.red) p {
  color: #e53935;
}
.player-turn:has(.yellow) p {
  color: #d8e51e;
}
.player-turn p {
  margin: 0;
  font-size: 35px; /* 文字大小 */
  font-weight: bold;
}
.btn-group {
  display: flex;
  justify-content: center;
  gap: 100px;
  margin-top: 50px;
}
button {
  width: 200px;
  height: 100px;
  cursor: pointer;
  font-size: 25px;
  border-radius: 6px;
}
.game-wrap {
  text-align: center;
  padding-top: 40px;
}
.board {
  display: inline-grid;
  gap: 10px;
  background: #333;
  padding: 10px;
  border-radius: 8px;
  margin: 50px auto;
  overflow: hidden;
  position: relative;
}
.win-line {
  position: absolute;
  background: #ffffff;
  z-index: 99;
  pointer-events: none; /* 不影响棋盘点击 */
  display: none;
}
.win-line.line-h,
.win-line.line-v,
.win-line.line-s,
.win-line.line-b {
  display: block;
}
.row {
  display: flex;
  gap: 10px;
}
.cell {
  width: 80px;
  height: 80px;
  position: relative;
  overflow: visible;
}
/* 底层棋槽 */
.cell-slot {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: #ffffff;
}
/* 上层棋子 */
.piece {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  transform: translateY(0);
  background: transparent;
}
/* 下落动画类 */
.cell-fall {
  animation: fall 0.5s ease-out forwards;/* 下降的时间（setTimeout）对应 */
}
@keyframes fall {
  from {
    transform: translateY(-1000px);/* 下降的高度 */
  }
  to {
    transform: translateY(0);
  }
}
/* 玩家1 棋子颜色（红色） */
.cell1 {
  background: #e53935 !important;
}
/* 玩家2 棋子颜色（黄色） */
.cell2 {
  background: #d8e51e !important;
}
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.5);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 999;
}
.modal-title {
  font-size: 150px;
  /* 上下外边距控制垂直位置 */
  margin-top: 250px;
  margin-bottom: 40px;
  font-weight: bold;
}
.modal-title.win-red {
  color: #e53935;
}
.modal-title.win-yellow {
  color: #d8e51e;
}
.modal-title.win-draw {
  color: #fff;
}
.modal button {
  width: 200px;
  height: 100px;
  font-size: 25px;
  cursor: pointer;
  border: none;      /* 去掉默认边框 */
  border-radius: 6px;/* 可选：加圆角 */
  margin-top: 250px;/* 上边距（数值越大，按钮越靠下） */
}
</style>