import { createRouter, createWebHistory } from 'vue-router'
import GraphicView from '../views/GraphicView.vue'
import TableView from '../views/TableView.vue'

const routes = [
  { path: '/Graphic', component: GraphicView },
  { path: '/Table', component: TableView }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router