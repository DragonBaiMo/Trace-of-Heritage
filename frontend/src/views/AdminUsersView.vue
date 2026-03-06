<template>
  <div class="users-page">
    <header class="header">
      <h3>用户管理</h3>
      <div class="filters">
        <input v-model.trim="q" placeholder="按用户名/昵称筛选" />
        <select v-model="role">
          <option value="">全部角色</option>
          <option value="admin">管理员</option>
          <option value="practitioner">从业者</option>
          <option value="user">普通用户</option>
        </select>
        <select v-model="status">
          <option value="">全部状态</option>
          <option value="active">active</option>
          <option value="frozen">frozen</option>
        </select>
        <button @click="load()">刷新</button>
        <button class="ghost" @click="exportUsers">导出用户</button>
      </div>
    </header>

    <section class="panel">
      <table class="table">
        <thead>
          <tr>
            <th>ID</th>
            <th>用户名</th>
            <th>昵称</th>
            <th>角色</th>
            <th>状态</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in filtered" :key="u.id">
            <td>{{ u.id }}</td>
            <td>{{ u.username }}</td>
            <td>
              <input v-model="u.nickname" placeholder="昵称" />
            </td>
            <td>
              <select v-model="u.role">
                <option value="admin">管理员</option>
                <option value="practitioner">从业者</option>
                <option value="user">普通用户</option>
              </select>
            </td>
            <td>
              <select v-model="u.status">
                <option value="active">active</option>
                <option value="frozen">frozen</option>
              </select>
            </td>
            <td>{{ u.created_at?.slice(0,19).replace('T',' ') }}</td>
            <td class="ops">
              <input v-model="u.__resetPwd" type="password" placeholder="重置密码(可选)" />
              <button @click="save(u)">保存</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="!filtered.length" class="empty">暂无数据</div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { fetchUsers, updateUser, type UserItem, type UserUpdatePayload } from '@/api/admin_users';

const list = ref<(UserItem & { __resetPwd?: string })[]>([]);
const q = ref('');
const role = ref('');
const status = ref('');

const filtered = computed(() => {
  return list.value.filter(u => {
    const keyword = q.value.toLowerCase();
    const matchQ = !keyword || u.username.toLowerCase().includes(keyword) || (u.nickname || '').toLowerCase().includes(keyword);
    const matchRole = !role.value || u.role === role.value;
    const matchStatus = !status.value || u.status === status.value;
    return matchQ && matchRole && matchStatus;
  });
});

async function load() {
  list.value = await fetchUsers();
}

async function save(u: UserItem & { __resetPwd?: string }) {
  const payload: UserUpdatePayload = {
    nickname: u.nickname ?? undefined,
    role: u.role,
    status: u.status,
  };
  if (u.__resetPwd && u.__resetPwd.length >= 8) {
    payload.password = u.__resetPwd;
  }
  const updated = await updateUser(u.id, payload);
  const idx = list.value.findIndex(x => x.id === u.id);
  if (idx >= 0) {
    list.value[idx] = { ...updated };
  }
}

function exportUsers() {
  window.open("/api/admin/export?type=users", "_blank");
}

onMounted(load);
</script>

<style scoped>
.users-page { display:flex; flex-direction:column; gap:16px; }
.header { display:flex; justify-content:space-between; align-items:center; }
.filters { display:flex; gap:8px; }
.panel { background:#fff; border-radius:12px; padding:16px 20px; box-shadow:0 10px 30px rgba(15,23,42,.08); }
.table { width:100%; border-collapse: collapse; }
.table th, .table td { border-bottom:1px solid #e2e8f0; padding:10px 8px; text-align:left; }
.ops { display:flex; gap:8px; align-items:center; }
.empty { text-align:center; color:#94a3b8; padding:16px 0; }
input, select { border:1px solid #d0d5dd; border-radius:8px; padding:8px 10px; }
button { padding:8px 12px; border-radius:8px; border:1px solid #e2e8f0; background:#fff; }
.ghost { background:#f8fafc; }
</style>
