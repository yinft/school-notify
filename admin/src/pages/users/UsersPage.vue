<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, View } from '@element-plus/icons-vue'

import { fetchUserDetail, fetchUsers, type AdminUserDetail, type AdminUserListItem } from '../../services/adminUsers'
import { formatDateTime } from '../../utils/datetime'
import { copyText } from '../../utils/copy'

const users = ref<AdminUserListItem[]>([])
const activeDetail = ref<AdminUserDetail | null>(null)
const drawerVisible = ref(false)
const keyword = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const loading = ref(false)
const errorMessage = ref('')

async function loadUsers() {
  loading.value = true
  errorMessage.value = ''
  try {
    const response = await fetchUsers({ keyword: keyword.value, page: currentPage.value, page_size: pageSize.value })
    users.value = response.items
    total.value = response.total
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '用户列表加载失败'
  } finally {
    loading.value = false
  }
}

function applyFilters() {
  currentPage.value = 1
  void loadUsers()
}

function handlePageChange(page: number) {
  currentPage.value = page
  void loadUsers()
}

async function openDetail(userId: string) {
  activeDetail.value = await fetchUserDetail(userId)
  drawerVisible.value = true
}

async function copyUserId(userId: string) {
  const ok = await copyText(userId)
  if (ok) {
    ElMessage.success('用户 ID 已复制')
  }
}

function avatarFallback(nickname?: string | null) {
  return (nickname || '用户').slice(0, 1)
}

onMounted(loadUsers)
</script>

<template>
  <div class="page-stack">
    <section class="table-card">
      <div v-if="errorMessage" class="feedback-banner error-banner">
        <span>{{ errorMessage }}</span>
        <el-button text type="primary" @click="loadUsers">重试</el-button>
      </div>
      <div class="filter-row compact-filter-row single-filter-row">
        <el-input v-model="keyword" class="filter-field filter-field-wide" placeholder="搜索用户 ID / 昵称" clearable :prefix-icon="Search" />
        <el-button type="primary" @click="applyFilters">筛选</el-button>
      </div>
      <div class="table-scroll">
      <el-table v-loading="loading" :data="users" stripe empty-text="暂无用户数据" class="admin-data-table">
        <el-table-column label="头像" width="88">
          <template #default="scope">
            <el-avatar :size="40" :src="scope.row.avatar_url || ''">{{ avatarFallback(scope.row.nickname) }}</el-avatar>
          </template>
        </el-table-column>
        <el-table-column prop="user_id" label="用户 ID" min-width="220" show-overflow-tooltip class-name="mono-cell" />
        <el-table-column prop="nickname" label="昵称" min-width="170" show-overflow-tooltip />
        <el-table-column prop="bound_devices_count" label="绑定设备数" width="120" />
        <el-table-column label="操作" width="110" fixed="right">
          <template #default="scope">
            <div class="table-actions">
            <el-button link type="primary" :icon="View" @click="openDetail(scope.row.user_id)">详情</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      </div>
      <el-pagination
        class="table-pagination"
        layout="total, prev, pager, next"
        :total="total"
        :page-size="pageSize"
        :current-page="currentPage"
        @current-change="handlePageChange"
      />
    </section>

    <el-drawer v-model="drawerVisible" size="520px" title="用户详情">
      <template v-if="activeDetail">
        <div class="detail-stack">
          <div class="detail-card">
            <div class="user-detail-header">
              <el-avatar :size="56" :src="activeDetail.avatar_url || ''">{{ avatarFallback(activeDetail.nickname) }}</el-avatar>
              <div>
                <h3>{{ activeDetail.nickname || '未授权昵称' }}</h3>
                <small>用户资料</small>
              </div>
            </div>
            <div class="detail-meta-grid single-column-grid">
              <div class="detail-meta-item">
                <span>用户 ID</span>
                <strong>{{ activeDetail.user_id }}</strong>
              </div>
            </div>
            <el-button text type="primary" @click="copyUserId(activeDetail.user_id)">复制用户 ID</el-button>
          </div>

          <div class="detail-card">
            <h3>绑定设备</h3>
            <div v-for="device in activeDetail.devices" :key="device.device_id" class="detail-row muted-row">
              <span>{{ device.device_name }}</span>
              <small>{{ device.location_label || device.device_id }}</small>
            </div>
            <p v-if="activeDetail.devices.length === 0" class="empty-copy">暂无绑定设备</p>
          </div>

          <div class="detail-card">
            <h3>最近通知</h3>
            <div v-for="item in activeDetail.recent_notifications" :key="item.notification_id" class="detail-row muted-row">
              <span>{{ item.title }}</span>
              <small>{{ formatDateTime(item.created_at) }}</small>
            </div>
            <p v-if="activeDetail.recent_notifications.length === 0" class="empty-copy">暂无通知记录</p>
          </div>
        </div>
      </template>
    </el-drawer>
  </div>
</template>
