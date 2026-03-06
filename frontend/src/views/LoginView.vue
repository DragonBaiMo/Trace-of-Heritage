<template>
  <div class="login-wrapper">
    <form class="login-card" @submit.prevent="handleSubmit">
      <h1>遗迹之光 · 登录</h1>
      <p class="hint">使用用户名与密码进入管理空间。</p>
      <label>
        用户名
        <input v-model="username" type="text" required minlength="4" placeholder="请输入用户名" />
      </label>
      <label>
        密码
        <input v-model="password" type="password" required minlength="8" placeholder="请输入密码" />
      </label>
      <button type="submit" :disabled="auth.loading">{{ auth.loading ? "正在登录" : "登录" }}</button>
      <p v-if="auth.error" class="error">{{ auth.error }}</p>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "@/store/auth";

const auth = useAuthStore();
const route = useRoute();
const router = useRouter();

const username = ref("");
const password = ref("");

onMounted(async () => {
  if (auth.isAuthenticated && !auth.user) {
    await auth.loadProfile();
    router.push({ name: "dashboard" });
  }
});

async function handleSubmit() {
  try {
    await auth.login(username.value, password.value);
    const redirect = (route.query.redirect as string) || "/";
    router.replace(redirect);
  } catch (error) {
    console.error("登录失败", error);
  }
}
</script>

<style scoped>
.login-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #6366f1, #22d3ee);
}

.login-card {
  width: 360px;
  background: #fff;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 20px 40px rgba(15, 23, 42, 0.2);
  display: flex;
  flex-direction: column;
  gap: 16px;
}

label {
  display: flex;
  flex-direction: column;
  font-size: 14px;
  color: #475467;
}

input {
  margin-top: 8px;
  padding: 12px;
  border-radius: 10px;
  border: 1px solid #d0d5dd;
}

button {
  padding: 12px;
  border: none;
  border-radius: 10px;
  background: #6366f1;
  color: #fff;
  font-weight: 600;
}

button:disabled {
  opacity: 0.7;
}

.hint {
  margin-top: -12px;
  color: #667085;
}

.error {
  color: #b91c1c;
  margin: 0;
}
</style>
