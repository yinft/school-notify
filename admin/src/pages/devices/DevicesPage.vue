<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, View, Edit } from '@element-plus/icons-vue'

import { fetchDeviceDetail, fetchDevices, unbindDeviceUser, updateDevice, type AdminDeviceDetail, type AdminDeviceListItem } from '../../services/adminDevices'
import { copyText } from '../../utils/copy'

const devices = ref<AdminDeviceListItem[]>([])
const activeDetail = ref<AdminDeviceDetail | null>(null)
const drawerVisible = ref(false)
const keyword = ref('')
const status = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const loading = ref(false)
const errorMessage = ref('')
const renameDialogVisible = ref(false)
const renamingDeviceId = ref('')
const renameForm = reactive({
  device_name: ''
})

async function loadDevices() {
  loading.value = true
  errorMessage.value = ''
  try {
    const response = await fetchDevices({
      keyword: keyword.value,
      status: status.value || undefined,
      page: currentPage.value,
      page_size: pageSize.value
    })
    devices.value = response.items
    total.value = response.total
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '设备列表加载失败'
  } finally {
    loading.value = false
  }
}

function applyFilters() {
  currentPage.value = 1
  void loadDevices()
}

function handlePageChange(page: number) {
  currentPage.value = page
  void loadDevices()
}

async function openDetail(deviceId: string) {
  activeDetail.value = await fetchDeviceDetail(deviceId)
  drawerVisible.value = true
}

async function renameDevice(item: AdminDeviceListItem) {
  renamingDeviceId.value = item.device_id
  renameForm.device_name = item.device_name
  renameDialogVisible.value = true
}

async function submitRename() {
  if (!renameForm.device_name.trim()) {
    ElMessage.warning('请输入设备名称')
    return
  }

  await updateDevice(renamingDeviceId.value, { device_name: renameForm.device_name.trim() })
  ElMessage.success('设备名称已更新')
  renameDialogVisible.value = false
  await loadDevices()
  if (activeDetail.value?.device_id === renamingDeviceId.value) {
    await openDetail(renamingDeviceId.value)
  }
}

async function unbindUser(deviceId: string, userId: string) {
  await unbindDeviceUser(deviceId, userId)
  ElMessage.success('绑定关系已解除')
  await loadDevices()
  await openDetail(deviceId)
}

async function copyDeviceId(deviceId: string) {
  const ok = await copyText(deviceId)
  if (ok) {
    ElMessage.success('设备 ID 已复制')
  }
}

onMounted(loadDevices)
</script>

<template>
  <div class="page-stack">
    <section class="table-card">
      <div v-if="errorMessage" class="feedback-banner error-banner">
        <span>{{ errorMessage }}</span>
        <el-button text type="primary" @click="loadDevices">重试</el-button>
      </div>
      <div class="filter-row compact-filter-row">
        <el-input v-model="keyword" class="filter-field filter-field-wide" placeholder="搜索设备 ID / 名称 / 位置" clearable :prefix-icon="Search" />
        <el-select v-model="status" class="filter-field" placeholder="设备状态" clearable>
          <el-option label="在线" value="online" />
          <el-option label="离线" value="offline" />
        </el-select>
        <el-button type="primary" @click="applyFilters">筛选</el-button>
      </div>
      <el-table v-loading="loading" :data="devices" stripe empty-text="暂无设备数据">
        <el-table-column prop="device_id" label="设备 ID" min-width="160" />
        <el-table-column prop="device_name" label="设备名称" min-width="160" />
        <el-table-column prop="location_label" label="位置" min-width="120" />
        <el-table-column prop="client_version" label="客户端版本" min-width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <span :class="['status-badge', scope.row.status === 'online' ? 'status-online' : 'status-offline']">
              {{ scope.row.status === 'online' ? '在线' : '离线' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="bound_users_count" label="绑定人数" width="100" />
        <el-table-column label="操作" width="180">
          <template #default="scope">
            <el-button text type="primary" :icon="View" @click="openDetail(scope.row.device_id)">详情</el-button>
            <el-button text :icon="Edit" @click="renameDevice(scope.row)">改名</el-button>
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

    <el-drawer v-model="drawerVisible" size="520px" title="设备详情">
      <template v-if="activeDetail">
        <div class="detail-stack">
          <div class="detail-card">
            <h3>{{ activeDetail.device_name }}</h3>
            <div class="detail-meta-grid">
              <div class="detail-meta-item">
                <span>设备 ID</span>
                <strong>{{ activeDetail.device_id }}</strong>
              </div>
              <div class="detail-meta-item">
                <span>设备状态</span>
                <strong class="status-badge" :class="activeDetail.status === 'online' ? 'status-online' : 'status-offline'">
                  {{ activeDetail.status === 'online' ? '在线' : '离线' }}
                </strong>
              </div>
              <div class="detail-meta-item">
                <span>位置</span>
                <strong>{{ activeDetail.location_label || '未设置位置' }}</strong>
              </div>
              <div class="detail-meta-item">
                <span>客户端版本</span>
                <strong>{{ activeDetail.client_version }}</strong>
              </div>
            </div>
            <el-button text type="primary" @click="copyDeviceId(activeDetail.device_id)">复制设备 ID</el-button>
          </div>

          <div class="detail-card">
            <h3>绑定用户</h3>
            <div v-for="user in activeDetail.bound_users" :key="user.user_id" class="detail-row">
              <span>{{ user.nickname || user.user_id }}</span>
              <el-button text type="danger" @click="unbindUser(activeDetail.device_id, user.user_id)">解绑</el-button>
            </div>
            <p v-if="activeDetail.bound_users.length === 0" class="empty-copy">暂无绑定用户</p>
          </div>

          <div class="detail-card">
            <h3>最近通知</h3>
            <div v-for="item in activeDetail.recent_notifications" :key="item.notification_id" class="detail-row muted-row">
              <span>{{ item.title }}</span>
              <small>{{ item.sender_user_id }}</small>
            </div>
            <p v-if="activeDetail.recent_notifications.length === 0" class="empty-copy">暂无通知记录</p>
          </div>
        </div>
      </template>
    </el-drawer>

    <el-dialog v-model="renameDialogVisible" title="修改设备名称" width="460px" class="app-form-dialog">
      <el-form label-position="top" class="dialog-form-grid">
        <el-form-item label="设备名称">
          <el-input v-model="renameForm.device_name" maxlength="128" show-word-limit placeholder="例如：值班室电脑" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="renameDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitRename">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
