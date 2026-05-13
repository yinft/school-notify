<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'

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
  await recommendVersion(item.id)
  ElMessage.success('已设为推荐版本')
  await loadVersions()
}

async function handleDelete(item: AdminVersion) {
  await deleteVersion(item.id)
  ElMessage.success('版本已删除')
  await loadVersions()
}

onMounted(loadVersions)
</script>

<template>
  <div class="page-stack">
    <section class="hero-panel">
      <div>
        <p class="section-eyebrow">Versions</p>
        <h2>官网版本管理</h2>
        <span>维护官网展示的客户端版本、推荐版和下载地址。</span>
      </div>
      <button class="primary-button narrow" type="button" @click="openCreate">新建版本</button>
    </section>

    <section class="table-card">
      <div v-if="errorMessage" class="feedback-banner error-banner">
        <span>{{ errorMessage }}</span>
        <el-button text type="primary" @click="loadVersions">重试</el-button>
      </div>
      <div class="filter-row versions-filter-row">
        <el-input v-model="keyword" placeholder="搜索版本号 / Build / 更新说明" clearable />
        <el-button type="primary" @click="applyFilters">筛选</el-button>
      </div>
      <el-table v-loading="loading" :data="versions" stripe empty-text="暂无版本数据">
        <el-table-column prop="version" label="版本号" min-width="120" />
        <el-table-column prop="build_number" label="Build" min-width="100" />
        <el-table-column prop="platform" label="平台" width="100" />
        <el-table-column label="状态" width="180">
          <template #default="scope">
            <div class="inline-tags">
              <span class="state-tag" :class="scope.row.is_published ? 'published' : 'draft'">
                {{ scope.row.is_published ? '已发布' : '草稿' }}
              </span>
              <span v-if="scope.row.is_recommended" class="state-tag recommended">推荐版</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="发布时间" min-width="180">
          <template #default="scope">
            {{ formatDateTime(scope.row.published_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" min-width="320">
          <template #default="scope">
            <el-button text type="primary" @click="openEdit(scope.row)">编辑</el-button>
            <el-button v-if="!scope.row.is_published" text @click="handlePublish(scope.row)">发布</el-button>
            <el-button v-else text @click="handleUnpublish(scope.row)">下线</el-button>
            <el-button v-if="scope.row.is_published" text @click="handleRecommend(scope.row)">设为推荐</el-button>
            <el-button v-if="!scope.row.is_published" text type="danger" @click="handleDelete(scope.row)">删除</el-button>
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

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="560px">
      <el-form label-position="top">
        <el-form-item label="平台">
          <el-input v-model="form.platform" :disabled="Boolean(editingId)" />
        </el-form-item>
        <el-form-item label="版本号">
          <el-input v-model="form.version" :disabled="Boolean(editingId)" />
        </el-form-item>
        <el-form-item label="Build 号">
          <el-input v-model="form.build_number" :disabled="Boolean(editingId)" />
        </el-form-item>
        <el-form-item label="下载地址">
          <el-input v-model="form.download_url" />
        </el-form-item>
        <el-form-item label="文件大小（字节）">
          <el-input v-model.number="form.file_size" />
        </el-form-item>
        <el-form-item label="更新说明">
          <el-input v-model="form.release_notes" type="textarea" :rows="4" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
