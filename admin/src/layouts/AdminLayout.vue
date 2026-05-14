<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  SwitchButton,
  DataAnalysis,
  Monitor,
  User,
  Bell,
  Upload,
  Fold,
  Expand,
  HomeFilled,
  ArrowRight
} from '@element-plus/icons-vue'

import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const sidebarCollapsed = ref(false)

const menuItems = [
  { label: '仪表盘', path: '/dashboard', icon: DataAnalysis },
  { label: '设备管理', path: '/devices', icon: Monitor },
  { label: '用户管理', path: '/users', icon: User },
  { label: '通知记录', path: '/notifications', icon: Bell },
  { label: '版本管理', path: '/versions', icon: Upload }
]

const pageTitle = computed(() => {
  if (route.meta?.title) return route.meta.title as string
  return menuItems.find((item) => item.path === route.path)?.label || '管理后台'
})

const breadcrumbs = computed(() => {
  const items = [{ label: '首页', path: '/dashboard', icon: HomeFilled }]
  if (route.path !== '/dashboard' && route.meta?.title) {
    items.push({ label: route.meta.title as string, path: route.path })
  }
  return items
})

function toggleSidebar() {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

async function handleLogout() {
  await authStore.logout()
  await router.push('/login')
}
</script>

<template>
  <div class="admin-shell" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
    <aside class="admin-sidebar card-box">
      <div class="brand-block">
        <img src="/app-icon.png" alt="思故桌面小喇叭图标" />
        <div v-if="!sidebarCollapsed" class="brand-text">
          <strong>思故桌面小喇叭</strong>
          <span>School Notify Admin</span>
        </div>
      </div>
      <nav class="sidebar-nav">
        <el-tooltip v-for="item in menuItems" :key="item.path" :content="item.label" placement="right" :disabled="!sidebarCollapsed">
          <RouterLink
            :to="item.path"
            class="nav-link"
            :class="{ active: route.path === item.path }"
          >
            <el-icon><component :is="item.icon" /></el-icon>
            <span v-if="!sidebarCollapsed" class="nav-label">{{ item.label }}</span>
          </RouterLink>
        </el-tooltip>
      </nav>
      <div class="sidebar-collapse-btn" @click="toggleSidebar">
        <el-icon><Fold v-if="!sidebarCollapsed" /><Expand v-else /></el-icon>
      </div>
    </aside>

    <main class="admin-main">
      <header class="admin-topbar card-box">
        <div class="topbar-left">
          <nav class="breadcrumb">
            <template v-for="(crumb, idx) in breadcrumbs" :key="crumb.path">
              <RouterLink v-if="idx < breadcrumbs.length - 1" :to="crumb.path" class="breadcrumb-item">
                <el-icon v-if="crumb.icon"><component :is="crumb.icon" /></el-icon>
                <span>{{ crumb.label }}</span>
              </RouterLink>
              <span v-else class="breadcrumb-item current">
                <span>{{ crumb.label }}</span>
              </span>
              <el-icon v-if="idx < breadcrumbs.length - 1" class="breadcrumb-sep"><ArrowRight /></el-icon>
            </template>
          </nav>
        </div>
        <div class="topbar-actions">
          <div class="admin-chip">
            <el-icon><User /></el-icon>
            <span>{{ authStore.profile?.display_name || '管理员' }}</span>
          </div>
          <el-button plain @click="handleLogout">
            <el-icon><SwitchButton /></el-icon>
            <span>退出登录</span>
          </el-button>
        </div>
      </header>

      <section class="admin-content">
        <RouterView />
      </section>
    </main>
  </div>
</template>
