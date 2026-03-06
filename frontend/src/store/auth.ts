import { computed, ref } from "vue";
import { defineStore } from "pinia";
import { loginRequest, fetchProfile, type UserProfile } from "@/api/auth";

export const useAuthStore = defineStore("auth", () => {
  const token = ref<string | null>(localStorage.getItem("access_token"));
  const user = ref<UserProfile | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  const isAuthenticated = computed(() => Boolean(token.value));

  async function login(username: string, password: string) {
    loading.value = true;
    error.value = null;
    try {
      const response = await loginRequest({ username, password });
      token.value = response.access_token;
      localStorage.setItem("access_token", response.access_token);
      await loadProfile();
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : "登录失败";
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function loadProfile() {
    if (!token.value) {
      return;
    }
    try {
      user.value = await fetchProfile();
    } catch (err: unknown) {
      logout();
      throw err;
    }
  }

  function logout() {
    token.value = null;
    user.value = null;
    localStorage.removeItem("access_token");
  }

  return {
    token,
    user,
    loading,
    error,
    isAuthenticated,
    login,
    logout,
    loadProfile
  };
});
