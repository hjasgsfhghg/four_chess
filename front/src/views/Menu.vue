<template>
  <div class="menu-container">
    <h1 class="menu-title">四子棋</h1>
    <div class="button-group">
      <button class="menu-btn" @click="goToGame('single')">单人挑战</button>
      <button class="menu-btn" @click="goToGame('double')">双人对战</button>
      <button class="menu-btn" @click="goToGame('watch')">观战模式</button>
      <button class="menu-btn" @click="showRules = true">游戏规则</button>
    </div>

    <div v-if="showRules" class="modal-overlay" @click.self="showRules = false">
      <div class="modal-content">
        <h2 class="rule-title">游戏规则</h2>
        <div class="rule-item">
          <h3>1 游戏目标</h3>
          <p>率先将四个棋子连成一线获胜</p>
        </div>
        <div class="rule-item">
          <h3>2 游戏规则</h3>
          <p>两名玩家轮流放置棋子，棋子从顶部落下</p>
        </div>
        <div class="rule-item">
          <h3>3 获胜条件</h3>
          <p>横向、纵向或斜向连成四子</p>
        </div>
        <div class="rule-item">
          <h3>4 平局</h3>
          <p>棋盘填满仍无人获胜则为平局</p>
        </div>
        <button class="close-btn" @click="showRules = false">关闭</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()
const showRules = ref(false)

const goToGame = (mode) => {
  router.push({ path: '/game', query: { mode } })
}
</script>

<style scoped>
.menu-title {
  text-align: center;
  font-size: 100px;
}
.menu-btn{
  display: block;
  margin: 20px auto 0;
  margin-top: 50px;
  width: 200px;
  height: 100px;
  font-size: 25px;
  cursor: pointer;
  border-radius: 6px;/* 可选：加圆角 */
}
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}
.modal-content {
  background: #fff;
  padding: 30px;
  border-radius: 12px;
  width: 400px;
}
.rule-title {
  text-align: center;
}
.rule-item {
  margin: 15px 0;
  text-align: left;
  margin-left: 50px;
}
.close-btn {
  width: 75px;
  height: 50px;
  cursor: pointer;
  display: block;
  margin: 20px auto 0;
  border-radius: 6px;/* 可选：加圆角 */
}
</style>