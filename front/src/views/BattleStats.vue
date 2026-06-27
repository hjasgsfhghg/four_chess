<template>
  <div class="battle-container">
    <h1 class="battle-title">策略对战统计</h1>

    <div class="config-panel">
      <div class="config-row">
        <label>策略 A（红方先手）</label>
        <select v-model="strategyA">
          <option value="random">随机</option>
          <option value="greedy">贪心</option>
          <option value="minimax">Minimax（深度4）</option>
          <option value="enhanced">Alpha-Beta 增强</option>
        </select>
      </div>

      <div class="vs-text">VS</div>

      <div class="config-row">
        <label>策略 B（黄方后手）</label>
        <select v-model="strategyB">
          <option value="random">随机</option>
          <option value="greedy">贪心</option>
          <option value="minimax">Minimax（深度4）</option>
          <option value="enhanced">Alpha-Beta 增强</option>
        </select>
      </div>

      <div class="config-row">
        <label>对战局数</label>
        <select v-model.number="rounds">
          <option :value="10">10</option>
          <option :value="50">50</option>
          <option :value="100">100</option>
          <option :value="200">200</option>
        </select>
      </div>

      <button class="start-btn" :disabled="loading" @click="startBattle">
        {{ loading ? '对战中…' : '开始模拟' }}
      </button>
    </div>

    <div v-if="loading" class="loading-spinner"></div>

    <div v-if="result" class="result-panel">
      <h2>对战结果</h2>
      <div class="result-bars">
        <div class="bar-group">
          <span class="bar-label">策略A 胜</span>
          <div class="bar-track">
            <div class="bar-fill bar-a" :style="{ width: pctA + '%' }"></div>
          </div>
          <span class="bar-value">{{ pctA }}%（{{ result.a_win }} 局）</span>
        </div>
        <div class="bar-group">
          <span class="bar-label">平局</span>
          <div class="bar-track">
            <div class="bar-fill bar-draw" :style="{ width: pctDraw + '%' }"></div>
          </div>
          <span class="bar-value">{{ pctDraw }}%（{{ result.draw }} 局）</span>
        </div>
        <div class="bar-group">
          <span class="bar-label">策略B 胜</span>
          <div class="bar-track">
            <div class="bar-fill bar-b" :style="{ width: pctB + '%' }"></div>
          </div>
          <span class="bar-value">{{ pctB }}%（{{ result.b_win }} 局）</span>
        </div>
      </div>
      <div class="summary-bar">
        <div class="summary-seg seg-a" :style="{ flex: result.a_win }" :title="'策略A 胜: ' + result.a_win"></div>
        <div class="summary-seg seg-draw" :style="{ flex: result.draw }" :title="'平局: ' + result.draw"></div>
        <div class="summary-seg seg-b" :style="{ flex: result.b_win }" :title="'策略B 胜: ' + result.b_win"></div>
      </div>
    </div>

    <button class="back-btn" @click="$router.push('/')">返回主菜单</button>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const strategyA = ref('enhanced')
const strategyB = ref('random')
const rounds = ref(50)
const loading = ref(false)
const result = ref(null)

const pctA = computed(() => {
  if (!result.value) return 0
  return (result.value.a_win / result.value.rounds * 100).toFixed(1)
})
const pctB = computed(() => {
  if (!result.value) return 0
  return (result.value.b_win / result.value.rounds * 100).toFixed(1)
})
const pctDraw = computed(() => {
  if (!result.value) return 0
  return (result.value.draw / result.value.rounds * 100).toFixed(1)
})

const startBattle = async () => {
  loading.value = true
  result.value = null
  try {
    const resp = await fetch('http://localhost:3014/battle', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ strategy_a: strategyA.value, strategy_b: strategyB.value, rounds: rounds.value })
    })
    const data = await resp.json()
    result.value = data
  } catch (e) {
    console.error('对战请求失败:', e)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.battle-container { text-align: center; padding-top: 60px; }
.battle-title { font-size: 48px; margin-bottom: 40px; }
.config-panel { display: flex; flex-direction: column; align-items: center; gap: 20px; margin-bottom: 40px; }
.config-row { display: flex; align-items: center; gap: 16px; }
.config-row label { font-size: 20px; width: 200px; text-align: right; }
.config-row select { width: 220px; height: 40px; font-size: 18px; border-radius: 6px; padding: 0 8px; }
.vs-text { font-size: 28px; font-weight: bold; color: #666; }
.start-btn { width: 200px; height: 60px; font-size: 22px; cursor: pointer; border-radius: 6px; margin-top: 10px; }
.start-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.loading-spinner { width: 40px; height: 40px; border: 4px solid #ddd; border-top-color: #2196f3; border-radius: 50%; animation: spin 0.8s linear infinite; margin: 20px auto; }
@keyframes spin { to { transform: rotate(360deg); } }
.result-panel { max-width: 700px; margin: 0 auto 40px; padding: 30px; background: #f5f5f5; border-radius: 12px; }
.result-panel h2 { margin-bottom: 24px; }
.result-bars { display: flex; flex-direction: column; gap: 16px; }
.bar-group { display: flex; align-items: center; gap: 12px; }
.bar-label { width: 90px; text-align: right; font-size: 18px; font-weight: bold; }
.bar-track { flex: 1; height: 28px; background: #e0e0e0; border-radius: 6px; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 6px; transition: width 0.6s ease; }
.bar-a { background: #e53935; }
.bar-b { background: #d8e51e; }
.bar-draw { background: #9e9e9e; }
.bar-value { width: 130px; font-size: 16px; text-align: left; }
.summary-bar { display: flex; height: 32px; border-radius: 6px; overflow: hidden; margin-top: 24px; gap: 2px; }
.summary-seg { min-width: 2px; transition: flex 0.6s ease; }
.seg-a { background: #e53935; }
.seg-b { background: #d8e51e; }
.seg-draw { background: #9e9e9e; }
.back-btn { width: 160px; height: 50px; font-size: 20px; cursor: pointer; border-radius: 6px; }
</style>
