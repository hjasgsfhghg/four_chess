import { createRouter, createWebHistory } from 'vue-router'
import Menu from '../views/Menu.vue'
import GameBoard from '../views/GameBoard.vue'
import BattleStats from '../views/BattleStats.vue'

const routes = [
  { path: '/', name: 'Menu', component: Menu },
  { path: '/game', name: 'GameBoard', component: GameBoard },
  { path: '/battle', name: 'BattleStats', component: BattleStats }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
