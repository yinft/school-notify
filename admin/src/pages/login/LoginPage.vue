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
    <div class="login-logo-row">
      <img src="/app-icon.png" alt="思故桌面小喇叭图标" />
      <p>思故桌面小喇叭</p>
    </div>

    <section class="login-intro-panel">
      <div class="login-background"></div>
      <div class="login-slogan-card enter-x">
        <img src="/app-icon.png" alt="思故桌面小喇叭图标" />
        <h1>思故桌面小喇叭管理后台</h1>
        <p>统一查看设备、用户、通知和官网版本。</p>
      </div>
    </section>

    <section class="login-form-panel">
      <div class="login-card auth-form-view" @keydown.enter.prevent="handleSubmit">
        <div class="auth-title">
          <h2>欢迎回来 👋🏻</h2>
          <span>请输入管理员账号登录运营后台</span>
        </div>
        <el-form label-position="top" @submit.prevent="handleSubmit">
          <el-form-item label="用户名">
            <el-input v-model="form.username" autocomplete="username" size="large" placeholder="请输入用户名" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input
              v-model="form.password"
              type="password"
              show-password
              autocomplete="current-password"
              size="large"
              placeholder="请输入密码"
            />
          </el-form-item>
          <div class="auth-extra-row">
            <span>会话失效后会自动返回登录页</span>
            <span class="vben-link">管理员登录</span>
          </div>
          <el-button class="auth-submit-button" type="primary" size="large" :loading="loading" @click="handleSubmit">
            登录
          </el-button>
        </el-form>
      </div>
    </section>
  </div>
</template>
