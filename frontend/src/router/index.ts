import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: () => import('@/views/Dashboard.vue'),
    },
    {
      path: '/surveys',
      name: 'surveys',
      component: () => import('@/views/Surveys.vue'),
    },
    {
      path: '/surveys/:id/results',
      name: 'survey-results',
      component: () => import('@/views/SurveyResults.vue'),
    },
    {
      path: '/employees',
      name: 'employees',
      component: () => import('@/views/Employees.vue'),
    },
    {
      path: '/results',
      name: 'results',
      component: () => import('@/views/Results.vue'),
    },
  ],
})

export default router
