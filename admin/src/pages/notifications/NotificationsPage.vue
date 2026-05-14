<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, View } from '@element-plus/icons-vue'

import { fetchNotificationDetail, fetchNotifications, type AdminNotificationDetail, type AdminNotificationListItem } from '../../services/adminNotifications'
import { formatDateTime } from '../../utils/datetime'
import { copyText } from '../../utils/copy'

const notifications = ref<AdminNotificationListItem[]>([])
const activeDetail = ref<AdminNotificationDetail | null>(null)
const drawerVisible = ref(false)
const keyword = ref('')
const senderUserId = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const loading = ref(false)
const errorMessage = ref('')

async function loadNotifications() {
  loading.value = true
  errorMessage.value = ''
  try {
    const response = await fetchNotifications({
      keyword: keyword.value,
      sender_user_id: senderUserId.value,
      page: currentPage.value,
      page_size: pageSize.value
    })
    notifications.value = response.items
    total.value = response.total
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '通知列表加载失败'
  } finally {
    loading.value = false
  }
}

function applyFilters() {
  currentPage.value = 1
  void loadNotifications()
}

function handlePageChange(page: number) {
  currentPage.value = page
  void loadNotifications()
}

async function openDetail(notificationId: string) {
  activeDetail.value = await fetchNotificationDetail(notificationId)
  drawerVisible.value = true
}

async function copyNotificationId(notificationId: string) {
  const ok = await copyText(notificationId)
  if (ok) {
    ElMessage.success('通知 ID 已复制')
  }
}

onMounted(loadNotifications)
</script>

<template>
  <div class="page-stack">
    <section class="table-card">
      <div v-if="errorMessage" class="feedback-banner error-banner">
        <span>{{ errorMessage }}</span>
        <el-button text type="primary" @click="loadNotifications">重试</el-button>
      </div>
      <div class="filter-row">
        <el-input v-model="keyword" placeholder="搜索标题 / 内容" clearable :prefix-icon="Search" />
        <el-input v-model="senderUserId" placeholder="发送人 user_id" clearable />
        <el-button type="primary" @click="applyFilters">筛选</el-button>
      </div>
      <el-table v-loading="loading" :data="notifications" stripe empty-text="暂无通知数据">
        <el-table-column prop="notification_id" label="通知 ID" min-width="180" />
        <el-table-column prop="title" label="标题" min-width="180" />
        <el-table-column prop="sender_user_id" label="发送人" min-width="120" />
        <el-table-column label="发送时间" min-width="180">
          <template #default="scope">
            {{ formatDateTime(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="投递" width="130">
          <template #default="scope">
            <span class="delivery-summary">
              <span class="delivery-ok">{{ scope.row.success_count }}</span>
              <span class="delivery-divider">/</span>
              <span class="delivery-fail">{{ scope.row.failed_count }}</span>
            </span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="scope">
            <el-button text type="primary" :icon="View" @click="openDetail(scope.row.notification_id)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        class="table-pagination"
        layout="total, prev, pager, next"
        :total="total"
        :page-size="pageSize"
        :current-page="currentPage"
        @current-change="handlePageChange"
      />
    </section>

    <el-drawer v-model="drawerVisible" size="560px" title="通知详情">
      <template v-if="activeDetail">
        <div class="detail-stack">
          <div class="detail-card">
            <h3>{{ activeDetail.title }}</h3>
            <p>{{ activeDetail.content }}</p>
            <div class="detail-meta-grid">
              <div class="detail-meta-item">
                <span>通知 ID</span>
                <strong>{{ activeDetail.notification_id }}</strong>
              </div>
              <div class="detail-meta-item">
                <span>发送人</span>
                <strong>{{ activeDetail.sender_user_id }}</strong>
              </div>
              <div class="detail-meta-item full-span-item">
                <span>发送时间</span>
                <strong>{{ formatDateTime(activeDetail.created_at) }}</strong>
              </div>
            </div>
            <el-button text type="primary" @click="copyNotificationId(activeDetail.notification_id)">复制通知 ID</el-button>
          </div>

          <div class="detail-card">
            <h3>投递明细</h3>
            <div v-for="item in activeDetail.deliveries" :key="item.device_id" class="delivery-row">
              <div>
                <strong>{{ item.device_name || item.device_id }}</strong>
                <small>{{ item.device_id }}</small>
              </div>
              <span :class="['delivery-state', item.failed ? 'failed' : 'ok']">
                {{ item.failed ? '失败' : '成功' }}
              </span>
            </div>
            <p v-if="activeDetail.deliveries.length === 0" class="empty-copy">暂无投递明细</p>
          </div>
        </div>
      </template>
    </el-drawer>
  </div>
</template>
