<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const menuItems = [
  { label: '仪表盘', path: '/dashboard' },
  { label: '设备管理', path: '/devices' },
  { label: '用户管理', path: '/users' },
  { label: '通知记录', path: '/notifications' },
  { label: '版本管理', path: '/versions' }
]

const pageTitle = computed(() => menuItems.find((item) => item.path === route.path)?.label || '管理后台')

async function handleLogout() {
  await authStore.logout()
  await router.push('/login')
}
</script>

<template>
  <div class="admin-shell">
    <aside class="admin-sidebar">
      <div class="brand-block">
        <img src="/app-icon.svg" alt="思故桌面小喇叭图标" />
        <div>
          <strong>思故桌面小喇叭</strong>
          <span>设备与版本运营台</span>
        </div>
      </div>
      <nav class="sidebar-nav">
        <RouterLink
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          class="nav-link"
          :class="{ active: route.path === item.path }"
        >
          {{ item.label }}
        </RouterLink>
      </nav>
    </aside>

    <main class="admin-main">
      <header class="admin-topbar">
        <div>
          <p class="topbar-eyebrow">School Notify Admin</p>
          <h1>{{ pageTitle }}</h1>
        </div>
        <div class="topbar-actions">
          <div class="admin-chip">
            <span>{{ authStore.profile?.display_name || '管理员' }}</span>
          </div>
          <button class="ghost-button" type="button" @click="handleLogout">退出登录</button>
        </div>
      </header>

      <section class="admin-content">
        <RouterView />
      </section>
    </main>
  </div>
</template>
