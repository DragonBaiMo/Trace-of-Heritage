<template>
  <div class="profile-card">
    <header class="card-header">
      <div>
        <h2 class="title">个人资料</h2>
        <p class="subtitle">完善个人信息，打造更专业的数字名片。</p>
      </div>
      <button v-if="user" class="btn ghost" @click="logout">退出登录</button>
    </header>

    <div v-if="!user" class="empty-state">
      <p class="empty-title">当前未登录</p>
      <p class="empty-tip">登录后即可管理个人信息与密码安全，享受更完整的体验。</p>
      <div class="empty-actions">
        <button class="btn btn-primary" @click="goLogin">立即登录</button>
        <button class="btn btn-secondary" @click="goRegister">注册新账号</button>
      </div>
    </div>

    <div v-else class="content">
      <aside class="summary">
        <div class="avatar-preview">
          <img v-if="avatarUrl" :src="avatarUrl" alt="用户头像" @error="handleAvatarError" />
          <div v-else class="avatar-fallback">{{ displayInitial }}</div>
        </div>

        <div class="summary-info">
          <h3 class="summary-name">{{ form.nickname || user.username }}</h3>
          <div class="badges">
            <span class="role-chip">{{ roleLabel }}</span>
            <span class="status-pill" :class="statusType">{{ statusLabel }}</span>
          </div>
        </div>

        <ul class="meta-list">
          <li>
            <span class="meta-label">用户名</span>
            <span class="meta-value">{{ user.username }}</span>
          </li>
          <li>
            <span class="meta-label">邮箱</span>
            <span class="meta-value">{{ user.email || '未设置' }}</span>
          </li>
          <li>
            <span class="meta-label">最近更新</span>
            <span class="meta-value">{{ user.updated_at ? formatDate(user.updated_at) : '暂无记录' }}</span>
          </li>
        </ul>
      </aside>

      <section class="form-area">
        <div class="section">
          <div>
            <h3 class="section-title">基础资料</h3>
            <p class="section-desc">这些资料将展示在你的公开页面，请保持真实友好。</p>
          </div>
          <div class="form-grid">
            <div class="field">
              <label for="nickname">昵称</label>
              <input id="nickname" v-model.trim="form.nickname" placeholder="填写一个好记的昵称" />
            </div>
            <div class="field">
              <label for="avatar">头像链接</label>
              <input id="avatar" v-model.trim="form.avatar" placeholder="请输入头像图片的链接地址" />
            </div>
            <div class="field">
              <label for="bio">个人简介</label>
              <textarea id="bio" v-model.trim="form.bio" rows="4" placeholder="介绍一下自己，让别人更了解你"></textarea>
            </div>
          </div>
          <div class="actions-row">
            <button class="btn btn-primary" @click="saveProfile" :disabled="saving">
              {{ saving ? '保存中…' : '保存资料' }}
            </button>
          </div>
        </div>

        <div class="section">
          <div>
            <h3 class="section-title">密码安全</h3>
            <p class="section-desc">定期更新密码，保护账号安全。</p>
          </div>
          <div class="form-grid">
            <div class="field">
              <label for="old-password">原密码</label>
              <input id="old-password" v-model.trim="pwd.old_password" type="password" placeholder="请输入当前密码" />
            </div>
            <div class="field">
              <label for="new-password">新密码</label>
              <input id="new-password" v-model.trim="pwd.new_password" type="password" placeholder="至少 8 位，包含字母与数字" />
            </div>
          </div>
          <div class="actions-row">
            <button class="btn btn-secondary" @click="changePassword" :disabled="changing">
              {{ changing ? '提交中…' : '修改密码' }}
            </button>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/store/auth';
import { httpClient } from '@/api/http';

const store = useAuthStore();
const user = computed(() => store.user);
const router = useRouter();

const roleLabel = computed(() => {
  const r = store.user?.role;
  if (r === 'admin') return '管理员';
  if (r === 'practitioner') return '从业者';
  return '普通用户';
});

const statusLabel = computed(() => {
  const status = store.user?.status;
  if (status === 'active') return '已激活';
  if (status === 'pending') return '待审核';
  if (status === 'disabled') return '已停用';
  return status || '状态未知';
});

const statusType = computed(() => {
  const status = store.user?.status;
  if (status === 'active') return 'success';
  if (status === 'pending') return 'warning';
  if (status === 'disabled') return 'danger';
  return 'default';
});

function goLogin() {
  router.push({ name: 'login' });
}
function goRegister() {
  router.push({ name: 'register' });
}
function logout() {
  store.logout();
  router.push({ name: 'login' });
}

// 资料编辑表单
const form = reactive({ nickname: '', avatar: '', bio: '' });
watch(
  user,
  (u) => {
    if (u) {
      form.nickname = u.nickname || '';
      form.avatar = u.avatar || '';
      form.bio = u.bio || '';
    }
  },
  { immediate: true }
);

const avatarFallback = ref(false);
watch(
  () => form.avatar,
  () => {
    avatarFallback.value = false;
  }
);

const avatarUrl = computed(() => {
  if (avatarFallback.value) return '';
  return (form.avatar || '').trim();
});

const displayInitial = computed(() => {
  const text = (form.nickname || user.value?.username || '用户').trim();
  return text ? text.slice(0, 1) : '用';
});

function handleAvatarError() {
  avatarFallback.value = true;
}

const saving = ref(false);
async function saveProfile() {
  if (!user.value) return;
  try {
    saving.value = true;
    const payload: Record<string, unknown> = {};
    if (form.nickname !== (user.value.nickname || '')) payload.nickname = form.nickname || null;
    if (form.avatar !== (user.value.avatar || '')) payload.avatar = form.avatar || null;
    if (form.bio !== (user.value.bio || '')) payload.bio = form.bio || null;
    await httpClient.patch(`/users/me`, payload);
    await store.fetchProfile?.();
    alert('资料已保存');
  } finally {
    saving.value = false;
  }
}

// 修改密码
const pwd = reactive({ old_password: '', new_password: '' });
const changing = ref(false);
async function changePassword() {
  if (!pwd.old_password || !pwd.new_password) {
    alert('请输入原密码与新密码');
    return;
  }
  try {
    changing.value = true;
    await httpClient.post('/users/me/password', { old_password: pwd.old_password, new_password: pwd.new_password });
    pwd.old_password = '';
    pwd.new_password = '';
    alert('密码修改成功');
  } catch (e: any) {
    alert(e?.response?.data?.detail || '修改失败');
  } finally {
    changing.value = false;
  }
}

function formatDate(value: string) {
  try {
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return value;
    return date.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' });
  } catch (error) {
    return value;
  }
}
</script>

<style scoped>
.profile-card {
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
  border-radius: 28px;
  padding: 28px 32px 36px;
  box-shadow: 0 24px 60px -28px rgba(15, 23, 42, 0.35);
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.title {
  margin: 0;
  font-size: 26px;
  font-weight: 700;
  color: #0f172a;
}

.subtitle {
  margin: 8px 0 0;
  font-size: 14px;
  color: #64748b;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  padding: 10px 20px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.2s ease;
  background: #ffffff;
  color: #334155;
}

.btn:not(:disabled):hover {
  transform: translateY(-1px);
  box-shadow: 0 16px 24px -16px rgba(15, 23, 42, 0.35);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.btn-primary {
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  color: #ffffff;
  box-shadow: 0 18px 28px -20px rgba(79, 70, 229, 0.6);
}

.btn-secondary {
  background: rgba(99, 102, 241, 0.1);
  color: #4338ca;
  border-color: rgba(99, 102, 241, 0.28);
}

.btn.ghost {
  background: rgba(248, 250, 252, 0.9);
  border-color: rgba(148, 163, 184, 0.38);
  color: #334155;
}

.empty-state {
  background: linear-gradient(145deg, rgba(99, 102, 241, 0.08), rgba(14, 165, 233, 0.08));
  border-radius: 24px;
  padding: 32px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  text-align: center;
  border: 1px solid rgba(148, 163, 184, 0.18);
}

.empty-title {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: #0f172a;
}

.empty-tip {
  margin: 0;
  color: #64748b;
}

.empty-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
  flex-wrap: wrap;
}

.content {
  display: grid;
  grid-template-columns: minmax(240px, 280px) 1fr;
  gap: 28px;
  align-items: start;
}

.summary {
  background: #ffffff;
  border-radius: 24px;
  padding: 24px;
  border: 1px solid rgba(99, 102, 241, 0.16);
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.avatar-preview {
  width: 120px;
  height: 120px;
  border-radius: 22px;
  overflow: hidden;
  background: linear-gradient(135deg, #a5b4fc 0%, #6366f1 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.2);
}

.avatar-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-fallback {
  font-size: 42px;
  font-weight: 600;
  color: #ffffff;
}

.summary-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.summary-name {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: #1f2937;
}

.badges {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.role-chip {
  background: rgba(14, 165, 233, 0.1);
  color: #0e7490;
  border-radius: 999px;
  padding: 4px 12px;
  font-size: 12px;
  font-weight: 600;
}

.status-pill {
  border-radius: 999px;
  padding: 4px 12px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.status-pill.success {
  background: rgba(34, 197, 94, 0.12);
  color: #15803d;
  border: 1px solid rgba(34, 197, 94, 0.24);
}

.status-pill.warning {
  background: rgba(250, 204, 21, 0.16);
  color: #a16207;
  border: 1px solid rgba(250, 204, 21, 0.28);
}

.status-pill.danger {
  background: rgba(248, 113, 113, 0.16);
  color: #b91c1c;
  border: 1px solid rgba(248, 113, 113, 0.28);
}

.status-pill.default {
  background: rgba(148, 163, 184, 0.16);
  color: #475569;
  border: 1px solid rgba(148, 163, 184, 0.28);
}

.meta-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.meta-label {
  font-size: 12px;
  font-weight: 600;
  color: #64748b;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.meta-value {
  display: block;
  margin-top: 6px;
  font-size: 16px;
  color: #0f172a;
  font-weight: 600;
}

.form-area {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.section {
  background: #ffffff;
  border-radius: 24px;
  padding: 24px 28px;
  border: 1px solid rgba(226, 232, 240, 0.8);
  display: flex;
  flex-direction: column;
  gap: 24px;
  box-shadow: 0 18px 40px -30px rgba(15, 23, 42, 0.25);
}

.section-title {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #111827;
}

.section-desc {
  margin: 6px 0 0;
  font-size: 13px;
  color: #6b7280;
}

.form-grid {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.field label {
  font-weight: 600;
  color: #1f2937;
}

.field input,
.field textarea {
  width: 100%;
  background: #f9fafb;
  border-radius: 16px;
  border: 1px solid transparent;
  padding: 12px 14px;
  transition: border-color 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
  color: #0f172a;
}

.field input:focus,
.field textarea:focus {
  outline: none;
  border-color: #6366f1;
  background: #ffffff;
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.15);
}

.field textarea {
  resize: vertical;
  min-height: 120px;
}

.actions-row {
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 1024px) {
  .content {
    grid-template-columns: 1fr;
  }

  .actions-row {
    justify-content: flex-start;
  }
}

@media (max-width: 768px) {
  .profile-card {
    padding: 24px;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .summary {
    flex-direction: column;
    align-items: flex-start;
  }

  .avatar-preview {
    width: 96px;
    height: 96px;
    border-radius: 18px;
  }

  .section {
    padding: 20px;
  }
}
</style>
