<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus, Edit, Upload, Download, Delete, Star } from '@element-plus/icons-vue'

import { createVersion, deleteVersion, fetchVersions, publishVersion, recommendVersion, unpublishVersion, updateVersion, type AdminVersion } from '../../services/adminVersions'
import { formatDateTime } from '../../utils/datetime'

const versions = ref<AdminVersion[]>([])
const dialogVisible = ref(false)
const editingId = ref<number | null>(null)
const keyword = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const loading = ref(false)
const errorMessage = ref('')
const form = reactive({
  platform: 'windows',
  version: '',
  build_number: '',
  release_notes: '',
  download_url: '',
  file_size: null as number | null
})

const dialogTitle = computed(() => (editingId.value ? '编辑版本' : '新建版本'))
const recommendedVersionId = computed(() => versions.value.find((item) => item.is_recommended)?.id ?? null)
const recommendedVersion = computed(() => versions.value.find((item) => item.is_recommended) ?? null)
const latestPublishedVersion = computed(() => versions.value.find((item) => item.is_published) ?? null)
const websiteTargetVersion = computed(() => recommendedVersion.value || latestPublishedVersion.value)

function resetForm() {
  editingId.value = null
  form.platform = 'windows'
  form.version = ''
  form.build_number = ''
  form.release_notes = ''
  form.download_url = ''
  form.file_size = null
}

async function loadVersions() {
  loading.value = true
  errorMessage.value = ''
  try {
    const response = await fetchVersions({ keyword: keyword.value, page: currentPage.value, page_size: pageSize.value })
    versions.value = response.items
    total.value = response.total
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '版本列表加载失败'
  } finally {
    loading.value = false
  }
}

function applyFilters() {
  currentPage.value = 1
  void loadVersions()
}

function handlePageChange(page: number) {
  currentPage.value = page
  void loadVersions()
}

function openCreate() {
  resetForm()
  dialogVisible.value = true
}

function openEdit(item: AdminVersion) {
  editingId.value = item.id
  form.platform = item.platform
  form.version = item.version
  form.build_number = item.build_number
  form.release_notes = item.release_notes
  form.download_url = item.download_url
  form.file_size = item.file_size
  dialogVisible.value = true
}

async function submitForm() {
  if (editingId.value) {
    await updateVersion(editingId.value, {
      release_notes: form.release_notes,
      download_url: form.download_url,
      file_size: form.file_size
    })
    ElMessage.success('版本已更新')
  } else {
    await createVersion({
      platform: form.platform,
      version: form.version,
      build_number: form.build_number,
      release_notes: form.release_notes,
      download_url: form.download_url,
      file_size: form.file_size
    })
    ElMessage.success('版本已创建')
  }
  dialogVisible.value = false
  await loadVersions()
}

async function handlePublish(item: AdminVersion) {
  await publishVersion(item.id)
  ElMessage.success('版本已发布')
  await loadVersions()
}

async function handleUnpublish(item: AdminVersion) {
  await unpublishVersion(item.id)
  ElMessage.success('版本已下线')
  await loadVersions()
}

async function handleRecommend(item: AdminVersion) {
  await ElMessageBox.confirm(
    `确认将 ${item.version} 设为推荐版本吗？设置后官网默认下载和客户端心跳升级目标都会切换到这个版本。`,
    '设为推荐版本',
    {
      type: 'warning',
      confirmButtonText: '确认切换',
      cancelButtonText: '取消'
    }
  )
  await recommendVersion(item.id)
  ElMessage.success('已设为推荐版本')
  await loadVersions()
}

async function handleDelete(item: AdminVersion) {
  await ElMessageBox.confirm(`确认删除版本 ${item.version} 吗？未发布版本删除后无法恢复。`, '删除版本', {
    type: 'warning',
    confirmButtonText: '确认删除',
    cancelButtonText: '取消'
  })
  await deleteVersion(item.id)
  ElMessage.success('版本已删除')
  await loadVersions()
}

function resolveVersionStatusType(item: AdminVersion) {
  if (item.is_recommended) {
    return 'warning'
  }

  if (item.is_published) {
    return 'success'
  }

  return 'info'
}

function versionStatusText(item: AdminVersion) {
  if (item.is_recommended) {
    return '推荐版本'
  }

  if (item.is_published) {
    return '已发布'
  }

  return '草稿'
}

function websiteVisibilityText(item: AdminVersion) {
  return item.is_published ? '官网可见' : '官网隐藏'
}

function heartbeatTargetText(item: AdminVersion) {
  return item.is_recommended ? '自动升级' : '不推送'
}

function releaseAvailabilityText(item: AdminVersion) {
  if (item.is_recommended) {
    return '默认下载'
  }

  if (item.is_published) {
    return '已发布未推荐'
  }

  return '仅后台可见'
}

function versionRowClassName({ row }: { row: AdminVersion }) {
  if (row.is_recommended) {
    return 'version-row-recommended'
  }

  if (row.is_published) {
    return 'version-row-published'
  }

  return 'version-row-draft'
}

onMounted(loadVersions)
</script>

<template>
  <div class="page-stack">
    <section class="table-card">
      <div class="table-card-header">
        <div class="card-header-copy">
          <p class="section-eyebrow">Version Control</p>
          <h2>版本管理</h2>
          <p class="section-subcopy">推荐版本会作为官网默认下载入口和客户端心跳升级目标。没有推荐版本时，官网会回退到最新发布版本。</p>
        </div>
        <el-button type="primary" :icon="Plus" @click="openCreate">新建版本</el-button>
      </div>
      <div class="version-guide-panel">
        <div class="version-guide-item">
          <span class="guide-dot guide-dot-warning"></span>
          <div>
            <strong>推荐版本</strong>
            <p>默认下载入口和客户端升级目标，同平台仅保留一个。</p>
          </div>
        </div>
        <div class="version-guide-item">
          <span class="guide-dot guide-dot-success"></span>
          <div>
            <strong>已发布</strong>
            <p>已进入官网更新记录，可用于对外试用和定向验证。</p>
          </div>
        </div>
        <div class="version-guide-item">
          <span class="guide-dot guide-dot-muted"></span>
          <div>
            <strong>草稿</strong>
            <p>仅后台可见，可继续补充下载地址和更新说明。</p>
          </div>
        </div>
      </div>
      <div class="version-target-strip">
        <article class="version-target-card primary-target">
          <div class="target-card-head">
            <span class="target-kicker">Current Download Target</span>
            <el-tag v-if="recommendedVersion" type="warning" effect="dark" round>推荐优先</el-tag>
            <el-tag v-else-if="latestPublishedVersion" type="success" effect="dark" round>发布回退</el-tag>
            <el-tag v-else type="info" effect="dark" round>暂未配置</el-tag>
          </div>
          <strong>
            {{ websiteTargetVersion ? `v${websiteTargetVersion.version}` : '暂无可下载版本' }}
          </strong>
          <p>
            {{
              recommendedVersion
                ? '官网默认下载和客户端自动升级都会优先指向这个推荐版本。'
                : latestPublishedVersion
                  ? '当前没有推荐版本，官网会回退到最新发布版本；客户端不会自动升级。'
                  : '当前还没有发布版本，官网和客户端都不会暴露下载目标。'
            }}
          </p>
        </article>
        <article class="version-target-card secondary-target">
          <div class="target-card-head">
            <span class="target-kicker">Client Heartbeat</span>
            <el-tag type="info" effect="plain" round>保守策略</el-tag>
          </div>
          <strong>
            {{ recommendedVersion ? `升级到 v${recommendedVersion.version}` : '未触发自动升级' }}
          </strong>
          <p>
            {{
              recommendedVersion
                ? '只有推荐版本会通过设备心跳下发升级信息，便于先发布观察、再正式切换。'
                : '没有推荐版本时，客户端继续正常工作，不会因为最新发布版本而自动收到升级提示。'
            }}
          </p>
        </article>
      </div>
      <div v-if="errorMessage" class="feedback-banner error-banner">
        <span>{{ errorMessage }}</span>
        <el-button text type="primary" @click="loadVersions">重试</el-button>
      </div>
      <div class="filter-row compact-filter-row versions-filter-row">
        <el-input v-model="keyword" class="filter-field filter-field-wide" placeholder="搜索版本号 / Build / 更新说明" clearable :prefix-icon="Search" />
        <el-button type="primary" @click="applyFilters">筛选</el-button>
      </div>
      <el-table v-loading="loading" :data="versions" stripe empty-text="暂无版本数据" :row-class-name="versionRowClassName">
        <el-table-column prop="version" label="版本号" min-width="120" />
        <el-table-column prop="build_number" label="Build" min-width="100" />
        <el-table-column prop="platform" label="平台" width="100" />
        <el-table-column label="版本状态" min-width="220">
          <template #default="scope">
            <div class="inline-tags version-tag-cluster">
              <el-tag :type="resolveVersionStatusType(scope.row)" effect="light" round>
                {{ versionStatusText(scope.row) }}
              </el-tag>
              <el-tag v-if="scope.row.is_published && scope.row.id !== recommendedVersionId" type="info" effect="plain" round>
                已发布未推荐
              </el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="下载角色" width="132">
          <template #default="scope">
            <el-tag :type="scope.row.is_recommended ? 'warning' : scope.row.is_published ? 'success' : 'info'" effect="plain" round>
              {{ releaseAvailabilityText(scope.row) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="推荐标识" width="132">
          <template #default="scope">
            <span v-if="scope.row.is_recommended" class="featured-version-badge">
              <i></i>
              <span>当前推荐</span>
            </span>
            <span v-else class="featured-version-placeholder">-</span>
          </template>
        </el-table-column>
        <el-table-column label="官网展示" width="124">
          <template #default="scope">
            <el-tag :type="scope.row.is_published ? 'success' : 'info'" effect="plain" round>
              {{ websiteVisibilityText(scope.row) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="客户端升级" width="124">
          <template #default="scope">
            <el-tag :type="scope.row.is_recommended ? 'warning' : 'info'" effect="plain" round>
              {{ heartbeatTargetText(scope.row) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="更新说明" min-width="280" show-overflow-tooltip>
          <template #default="scope">
            <span>{{ scope.row.release_notes || '未填写更新说明' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="发布时间" min-width="180">
          <template #default="scope">
            {{ formatDateTime(scope.row.published_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" min-width="280">
          <template #default="scope">
            <el-button text type="primary" :icon="Edit" @click="openEdit(scope.row)">编辑</el-button>
            <el-button v-if="!scope.row.is_published" text :icon="Upload" @click="handlePublish(scope.row)">发布</el-button>
            <el-button v-else text :icon="Download" @click="handleUnpublish(scope.row)">下线</el-button>
            <el-button v-if="scope.row.is_recommended" text type="warning" :icon="Star" disabled>当前推荐</el-button>
            <el-button v-else-if="scope.row.is_published" text :icon="Star" @click="handleRecommend(scope.row)">设为推荐</el-button>
            <el-button v-if="!scope.row.is_published" text type="danger" :icon="Delete" @click="handleDelete(scope.row)">删除</el-button>
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

      <el-dialog v-model="dialogVisible" :title="dialogTitle" width="680px" class="app-form-dialog">
        <el-form label-position="top" class="dialog-form-grid">
          <div class="form-grid two-columns">
            <el-form-item label="平台">
              <el-input v-model="form.platform" :disabled="Boolean(editingId)" />
            </el-form-item>
            <el-form-item label="Build 号">
              <el-input v-model="form.build_number" :disabled="Boolean(editingId)" placeholder="例如 20260517.1" />
            </el-form-item>
          </div>
          <div class="form-grid two-columns">
            <el-form-item label="版本号">
              <el-input v-model="form.version" :disabled="Boolean(editingId)" placeholder="建议使用 x.y.z" />
            </el-form-item>
            <el-form-item label="文件大小（字节）">
              <el-input v-model.number="form.file_size" placeholder="可选" />
            </el-form-item>
          </div>
          <el-form-item label="下载地址">
            <el-input v-model="form.download_url" placeholder="https://.../desktop-speaker.zip" />
          </el-form-item>
          <el-form-item label="更新说明">
            <el-input v-model="form.release_notes" type="textarea" :rows="5" resize="vertical" placeholder="填写本次版本的主要变更、修复内容和适用说明。" />
          </el-form-item>
        </el-form>
       <template #footer>
         <el-button @click="dialogVisible = false">取消</el-button>
         <el-button type="primary" @click="submitForm">保存</el-button>
       </template>
      </el-dialog>
  </div>
</template>
