<template>
  <div class="card">
    <h3>热门内容分析</h3>
    <p class="sub">基于资源概览与统计接口的基础分析视图</p>

    <section class="panel">
      <div class="grid">
        <div class="tile">
          <h4>资源总量</h4>
          <p class="num">{{ summary?.total ?? '-' }}</p>
        </div>
        <div class="tile">
          <h4>待审核</h4>
          <p class="num warn">{{ summary?.pending ?? '-' }}</p>
        </div>
        <div class="tile">
          <h4>已通过</h4>
          <p class="num ok">{{ summary?.approved ?? '-' }}</p>
        </div>
        <div class="tile">
          <h4>已驳回</h4>
          <p class="num bad">{{ summary?.rejected ?? '-' }}</p>
        </div>
      </div>
    </section>

    <section class="panel">
      <h4>最近更新的资源</h4>
      <ul class="list">
        <li v-for="item in summary?.latest || []" :key="item.id">
          <span class="title">{{ item.title }}</span>
          <span class="status">{{ item.status }}</span>
          <span class="time">{{ item.updated_at?.slice(0,19).replace('T',' ') }}</span>
        </li>
        <li v-if="!summary || summary.latest.length===0" class="empty">暂无数据</li>
      </ul>
    </section>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { fetchResourceSummary, type ResourceSummary } from '@/api/resource';

const summary = ref<ResourceSummary | null>(null);

async function load() {
  summary.value = await fetchResourceSummary();
}

onMounted(load);
</script>

<style scoped>
.card { display:flex; flex-direction:column; gap:16px; }
.sub { color:#64748b; margin:0; }
.panel { background:#fff; border-radius:12px; padding:16px 20px; box-shadow:0 10px 30px rgba(15,23,42,.08); }
.grid { display:grid; grid-template-columns: repeat(4, 1fr); gap:12px; }
.tile { background:#f8fafc; border-radius:12px; padding:16px; }
.num { font-size:24px; font-weight:700; margin:6px 0 0; }
.num.ok { color:#16a34a; }
.num.warn { color:#eab308; }
.num.bad { color:#ef4444; }
.list { list-style:none; padding:0; margin:0; display:grid; gap:8px; }
.list li { display:grid; grid-template-columns: 1fr 100px 200px; gap:8px; padding:10px 12px; border:1px solid #e2e8f0; border-radius:8px; }
.title { font-weight:600; }
.status { text-transform: capitalize; color:#475467; }
.time { color:#94a3b8; }
.empty { text-align:center; color:#94a3b8; padding:8px 0; }
</style>
