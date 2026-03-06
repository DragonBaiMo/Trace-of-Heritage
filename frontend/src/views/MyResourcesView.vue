<template>
  <div class="card">
    <h3>我的资源</h3>
    <div class="toolbar">
      <input v-model.trim="keyword" placeholder="按标题/简介搜索" />
      <select v-model="status">
        <option value="">全部状态</option>
        <option value="draft">草稿</option>
        <option value="pending">待审</option>
        <option value="approved">已通过</option>
        <option value="rejected">已驳回</option>
      </select>
      <button @click="load()">查询</button>
      <RouterLink v-if="canSubmit" class="btn" to="/resources/create">提交新资源</RouterLink>
    </div>

    <section class="panel">
      <ul class="list">
        <li v-for="item in mine" :key="item.id" class="row">
          <div class="main">
            <h4>{{ item.title }}</h4>
            <p class="meta">状态：{{ item.status }} · 提交时间：{{ fmt(item.created_at) }}</p>
            <p class="desc">{{ item.synopsis || '（无简介）' }}</p>
          </div>
        </li>
        <li v-if="!mine.length" class="empty">暂无数据</li>
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
import { computed, onMounted, ref } from 'vue';
import { useAuthStore } from '@/store/auth';
import { fetchResources, type ResourceItem, type PaginationMeta } from '@/api/resource';
import { RouterLink } from 'vue-router';

const auth = useAuthStore();
const canSubmit = computed(() => auth.user?.role === 'practitioner' || auth.user?.role === 'admin');

const page = ref(1);
const pageSize = ref(10);
const meta = ref<PaginationMeta>({ page: 1, page_size: 10, total: 0 });
const list = ref<ResourceItem[]>([]);
const keyword = ref('');
const status = ref('');

const mine = computed(() => list.value.filter(x => x.submitter_id === auth.user?.id));
const totalPages = computed(() => Math.max(1, Math.ceil((meta.value.total || 0) / pageSize.value)));

function fmt(v: string) {
  const d = new Date(v); const p = (n:number)=>String(n).padStart(2,'0');
  return `${d.getFullYear()}-${p(d.getMonth()+1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`;
}

async function load() {
  const { items, meta: m } = await fetchResources({ status: status.value || undefined, keyword: keyword.value || undefined, page: page.value, pageSize: pageSize.value });
  list.value = items;
  meta.value = m;
}

onMounted(load);
</script>

<style scoped>
.card { display:flex; flex-direction:column; gap:16px; }
.toolbar { display:flex; gap:8px; align-items:center; }
.panel { background:#fff; border-radius:12px; padding:16px 20px; box-shadow:0 10px 30px rgba(15,23,42,.08); }
.list { list-style:none; margin:0; padding:0; display:flex; flex-direction:column; gap:12px; }
.row { border:1px solid #e2e8f0; border-radius:12px; padding:12px; }
.meta { color:#94a3b8; font-size:12px; margin:6px 0 0; }
.desc { color:#475467; margin:6px 0 0; }
.pager { display:flex; gap:12px; align-items:center; justify-content:center; padding-top:12px; }
.btn { padding:8px 12px; border-radius:8px; background:#6366f1; color:#fff; }
.empty { text-align:center; color:#94a3b8; padding:8px 0; }
</style>
