<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

import { useAuthStore } from '../../stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)
const form = reactive({
  username: 'admin',
  password: 'pass123456'
})

async function handleSubmit() {
  loading.value = true
  try {
    await authStore.login(form.username, form.password)
    await router.push('/dashboard')
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-shell">
    <section class="login-hero">
      <div class="login-brand-card">
        <img src="/app-icon.svg" alt="思故桌面小喇叭图标" />
        <p>School Notify Admin</p>
        <h1>思故桌面小喇叭管理后台</h1>
        <span>统一查看设备、用户、通知和官网版本。</span>
      </div>
    </section>

    <section class="login-panel">
      <div class="login-card">
        <p class="login-eyebrow">管理员入口</p>
        <h2>登录运营台</h2>
        <el-form label-position="top" @submit.prevent="handleSubmit">
          <el-form-item label="用户名">
            <el-input v-model="form.username" autocomplete="username" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input v-model="form.password" type="password" show-password autocomplete="current-password" />
          </el-form-item>
          <p class="login-hint">会话失效后会自动返回登录页。</p>
          <button class="primary-button" type="button" :disabled="loading" @click="handleSubmit">
            {{ loading ? '登录中...' : '进入后台' }}
          </button>
        </el-form>
      </div>
    </section>
  </div>
</template>
