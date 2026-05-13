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
        { path: 'dashboard', name: 'dashboard', component: DashboardPage },
        { path: 'devices', name: 'devices', component: DevicesPage },
        { path: 'users', name: 'users', component: UsersPage },
        { path: 'notifications', name: 'notifications', component: NotificationsPage },
        { path: 'versions', name: 'versions', component: VersionsPage }
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
