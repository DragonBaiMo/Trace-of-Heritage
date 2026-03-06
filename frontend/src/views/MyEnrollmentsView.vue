<template>
  <div class="card">
    <h3>我的报名</h3>
    <p class="sub">展示我已报名的活动</p>

    <section class="panel">
      <ul class="list">
        <li v-for="a in items" :key="a.id" class="row">
          <div class="main">
            <h4>{{ a.title }}</h4>
            <p class="meta">状态：{{ a.status }} · {{ a.updated_at?.slice(0,19).replace('T',' ') }}</p>
          </div>
        </li>
        <li v-if="!items.length" class="empty">暂无报名记录，前往“活动参与”报名后再来查看</li>
      </ul>
    </section>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { fetchMyEnrollments, type ActivityItem } from '@/api/activities_user';

const items = ref<ActivityItem[]>([]);

async function load(){
  const res = await fetchMyEnrollments();
  items.value = res.data ?? [];
}

onMounted(load);
</script>

<style scoped>
.card { display:flex; flex-direction:column; gap:16px; }
.sub { color:#64748b; margin:0; }
.panel { background:#fff; border-radius:12px; padding:16px 20px; box-shadow:0 10px 30px rgba(15,23,42,.08); }
.list { list-style:none; margin:0; padding:0; display:flex; flex-direction:column; gap:12px; }
.row { border:1px solid #e2e8f0; border-radius:12px; padding:12px; }
.meta { color:#94a3b8; font-size:12px; margin:6px 0 0; }
.empty { text-align:center; color:#94a3b8; padding:8px 0; }
</style>
