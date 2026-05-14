import { createRouter, createWebHistory } from 'vue-router'

import AdminLayout from '../layouts/AdminLayout.vue'
import { useAuthStore } from '../stores/auth'

const LoginPage = () => import('../pages/login/LoginPage.vue')
const DashboardPage = () => import('../pages/dashboard/DashboardPage.vue')
const DevicesPage = () => import('../pages/devices/DevicesPage.vue')
const UsersPage = () => import('../pages/users/UsersPage.vue')
const NotificationsPage = () => import('../pages/notifications/NotificationsPage.vue')
const VersionsPage = () => import('../pages/versions/VersionsPage.vue')

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginPage,
      meta: { public: true }
    },
    {
      path: '/',
      component: AdminLayout,
      children: [
        { path: '', redirect: '/dashboard' },
        { path: 'dashboard', name: 'dashboard', component: DashboardPage, meta: { title: '仪表盘' } },
        { path: 'devices', name: 'devices', component: DevicesPage, meta: { title: '设备管理' } },
        { path: 'users', name: 'users', component: UsersPage, meta: { title: '用户管理' } },
        { path: 'notifications', name: 'notifications', component: NotificationsPage, meta: { title: '通知记录' } },
        { path: 'versions', name: 'versions', component: VersionsPage, meta: { title: '版本管理' } }
      ]
    }
  ]
})

router.beforeEach((to) => {
  const authStore = useAuthStore()
  if (to.meta.public) {
    if (to.path === '/login' && authStore.isAuthenticated) {
      return '/dashboard'
    }
    return true
  }
  if (!authStore.isAuthenticated) {
    return '/login'
  }
  return true
})

export default router
