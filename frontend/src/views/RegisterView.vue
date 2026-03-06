<template>
  <div class="auth-card">
    <h2>注册</h2>
    <form @submit.prevent="onSubmit">
      <label>用户名</label>
      <input v-model.trim="form.username" required minlength="4" maxlength="20" />

      <label>密码</label>
      <input v-model="form.password" type="password" required minlength="8" />
      <small>需包含字母与数字</small>

      <label>昵称（可选）</label>
      <input v-model.trim="form.nickname" maxlength="50" />

      <button type="submit" :disabled="loading">{{ loading ? '提交中...' : '注册' }}</button>
      <p v-if="error" class="error">{{ error }}</p>
    </form>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import { register } from '@/api/auth';
import { useAuthStore } from '@/store/auth';

const router = useRouter();
const store = useAuthStore();
const loading = ref(false);
const error = ref<string | null>(null);

const form = reactive({ username: '', password: '', nickname: '' });

async function onSubmit() {
  loading.value = true;
  error.value = null;
  try {
    await register({ username: form.username, password: form.password, nickname: form.nickname || undefined });
    // 注册成功后自动跳转登录
    await store.login(form.username, form.password);
    router.push({ name: 'dashboard' });
  } catch (e: any) {
    error.value = e?.message || String(e) || '注册失败';
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.auth-card { max-width: 420px; margin: 80px auto; background: #fff; padding: 24px; border-radius: 12px; box-shadow: 0 10px 30px rgba(15,23,42,.08); }
label { display:block; margin-top: 12px; font-size: 12px; color:#64748b; }
input { width: 100%; padding: 10px 12px; border:1px solid #d0d5dd; border-radius: 8px; margin-top: 6px; }
button { margin-top: 16px; width: 100%; padding: 10px; border-radius: 8px; border: none; background:#6366f1; color:#fff; }
.error { color: #dc2626; margin-top: 12px; }
small { color:#94a3b8; }
</style>
