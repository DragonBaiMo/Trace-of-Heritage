<template>
  <div class="card">
    <h3>活动参与</h3>
    <div class="toolbar">
      <select v-model="status">
        <option value="">全部状态</option>
        <option value="approved">已通过</option>
        <option value="pending">待审核</option>
      </select>
      <button @click="load()">查询</button>
    </div>

    <section class="panel">
      <ul class="list">
        <li v-for="a in items" :key="a.id" class="row">
          <div class="main">
            <h4>{{ a.title }}</h4>
            <p class="meta">{{ a.start_time?.slice(0,16).replace('T',' ') }} ~ {{ a.end_time?.slice(0,16).replace('T',' ') }} · 状态：{{ a.status }}</p>
            <p class="desc">{{ a.description || '（无简介）' }}</p>
          </div>
          <div class="ops">
            <button @click="enroll(a.id)">报名</button>
          </div>
        </li>
        <li v-if="!items.length" class="empty">暂无活动</li>
      </ul>

      <div class="pager">
        <button :disabled="page<=1" @click="page--; load()">上一页</button>
        <span>第 {{ page }} / {{ totalPages }} 页（共 {{ meta.total }} 条）</span>
        <button :disabled="page>=totalPages" @click="page++; load()">下一页</button>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from 'vue';
import { fetchActivities, enrollActivity, type ActivityItem, type PaginationMeta } from '@/api/activities_user';

const items = ref<ActivityItem[]>([]);
const meta = ref<PaginationMeta>({ page:1, page_size:10, total:0 });
const page = ref(1); const pageSize = ref(10); const status = ref('approved');

const totalPages = computed(()=> Math.max(1, Math.ceil((meta.value.total||0)/pageSize.value)));

async function load(){
  const res = await fetchActivities({ status: status.value || undefined, page: page.value, pageSize: pageSize.value });
  items.value = res.data ?? [];
  meta.value = res.meta ?? { page: page.value, page_size: pageSize.value, total: res.data?.length ?? 0 };
}

async function enroll(id:number){
  await enrollActivity(id);
  alert('报名成功');
}

onMounted(load);
</script>

<style scoped>
.card { display:flex; flex-direction:column; gap:16px; }
.toolbar { display:flex; gap:8px; align-items:center; }
.panel { background:#fff; border-radius:12px; padding:16px 20px; box-shadow:0 10px 30px rgba(15,23,42,.08); }
.list { list-style:none; margin:0; padding:0; display:flex; flex-direction:column; gap:12px; }
.row { display:flex; justify-content:space-between; align-items:flex-start; border:1px solid #e2e8f0; border-radius:12px; padding:12px; }
.meta { color:#94a3b8; font-size:12px; margin:6px 0 0; }
.desc { color:#475467; margin:6px 0 0; }
.ops button { padding:8px 12px; border-radius:8px; border:1px solid #e2e8f0; background:#fff; }
.pager { display:flex; gap:12px; align-items:center; justify-content:center; padding-top:12px; }
.empty { text-align:center; color:#94a3b8; padding:8px 0; }
</style>
