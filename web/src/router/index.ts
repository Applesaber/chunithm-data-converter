import { createRouter, createWebHashHistory } from 'vue-router'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: '/',
      name: 'converter',
      component: () => import('../views/ConverterView.vue'),
    },
    {
      path: '/visualizer',
      name: 'visualizer',
      component: () => import('../views/VisualizerView.vue'),
    },
  ],
})

export default router
