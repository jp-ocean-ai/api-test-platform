import { createRouter, createWebHistory } from 'vue-router'
import ProjectsView from '../views/ProjectsView.vue'
import EnvironmentsView from '../views/EnvironmentsView.vue'
import ApisView from '../views/ApisView.vue'
import TestCasesView from '../views/TestCasesView.vue'
import ExecutionsView from '../views/ExecutionsView.vue'

const routes = [
  { path: '/', redirect: '/projects' },
  { path: '/projects', component: ProjectsView },
  { path: '/environments', component: EnvironmentsView },
  { path: '/apis', component: ApisView },
  { path: '/testcases', component: TestCasesView },
  { path: '/executions', component: ExecutionsView },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
