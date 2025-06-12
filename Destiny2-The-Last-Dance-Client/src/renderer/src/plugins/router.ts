import { createRouter, createWebHashHistory } from 'vue-router'
import IndexView from '@renderer/views/index/IndexView.vue'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: '/',
      name: 'index',
      component: IndexView
    },
    {
      path: '/home',
      name: 'home',
      component: () => import('@renderer/views/home/IndexView.vue')
    },
    {
      path: '/info/:page?',
      name: 'info',
      component: () => import('@renderer/views/info/IndexView.vue')
    },
    {
      path: '/gamepanel',
      name: 'gamepanel',
      component: () => import('@renderer/views/gamepanel/IndexView.vue'),
      redirect: '/room',
      children: [
        {
          path: '/room',
          name: 'room',
          props: true,
          component: () => import('@renderer/views/gamepanel/room/IndexView.vue')
        },
        {
          path: '/map',
          name: 'map',
          props: true,
          component: () => import('@renderer/views/gamepanel/map/IndexView.vue')
        },
        {
          path: '/options',
          name: 'options',
          props: true,
          component: () => import('@renderer/views/gamepanel/options/IndexView.vue')
        },
        {
          path: '/drawcards',
          name: 'drawcards',
          props: true,
          component: () => import('@renderer/views/gamepanel/drawcards/IndexView.vue')
        },
        {
          path: '/decklist',
          name: 'decklist',
          props: true,
          component: () => import('@renderer/views/gamepanel/decklist/IndexView.vue')
        },
        {
          path: '/playerevent',
          name: 'playerevent',
          props: true,
          component: () => import('@renderer/views/gamepanel/playerevent/IndexView.vue')
        },
        {
          path: '/globalevent',
          name: 'globalevent',
          props: true,
          component: () => import('@renderer/views/gamepanel/globalevent/IndexView.vue')
        },
        {
          path: '/shop',
          name: 'shop',
          props: true,
          component: () => import('@renderer/views/gamepanel/shop/IndexView.vue')
        }
      ]
    }
  ]
})

export default router
