<template>
  <div class="card">
    <h3>戏曲百科库</h3>
    <p class="sub">检索词条，查看词条详情</p>

    <div class="toolbar">
      <input v-model.trim="keyword" placeholder="搜索词条" @keyup.enter="load" />
      <select v-model="category">
        <option value="">全部分类</option>
        <option value="genre">流派</option>
        <option value="figure">人物</option>
        <option value="term">术语</option>
      </select>
      <button @click="load">搜索</button>
    </div>

    <section class="panel">
      <ul class="list">
        <li v-for="e in items" :key="e.id" @click="openDetail(e.id)" class="row">
          <div class="title">{{ e.title }}</div>
          <div class="meta">{{ e.category || '未分类' }} · {{ e.updated_at.slice(0,10) }}</div>
        </li>
        <li v-if="!items.length" class="empty">暂无数据</li>
      </ul>
      <div class="pager">
        <button :disabled="page<=1" @click="page--; load()">上一页</button>
        <span>第 {{ page }} / {{ totalPages }} 页（共 {{ meta.total }} 条）</span>
        <button :disabled="page>=totalPages" @click="page++; load()">下一页</button>
      </div>
    </section>

    <div v-if="drawer" class="drawer">
      <div class="drawer-body">
        <h4>{{ current?.title }}</h4>
        <div class="cmeta">分类：{{ current?.category || '未分类' }} · 更新时间：{{ current?.updated_at?.slice(0,19).replace('T',' ') }}</div>
        <article class="content" v-html="md(current?.content||'')"></article>
        <div class="ops"><button class="ghost" @click="drawer=false">关闭</button></div>
      </div>
    </div>
  </div>
  
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { fetchWikiEntries, fetchWikiEntry, type PaginationMeta, type WikiEntry } from '@/api/wiki';

const keyword = ref('');
const category = ref('');
const items = ref<WikiEntry[]>([]);
const meta = ref<PaginationMeta>({ page:1, page_size:10, total:0 });
const page = ref(1); const pageSize = ref(10);
const totalPages = computed(()=> Math.max(1, Math.ceil((meta.value.total||0)/pageSize.value)));

const drawer = ref(false);
const current = ref<WikiEntry | null>(null);

async function load(){
  const res = await fetchWikiEntries({ keyword: keyword.value || undefined, category: category.value || undefined, page: page.value, pageSize: pageSize.value });
  items.value = res.data; meta.value = res.meta;
}

async function openDetail(id:number){
  current.value = await fetchWikiEntry(id); drawer.value = true;
}

function md(s:string){
  // 简洁处理：以换行渲染为段落，避免引入额外库
  return (s||'').replace(/\n/g, '<br/>');
}

onMounted(load);
</script>

<style scoped>
.card { display:flex; flex-direction:column; gap:16px; }
.sub { color:#64748b; margin:0; }
.toolbar { display:flex; gap:8px; align-items:center; }
.panel { background:#fff; border-radius:12px; padding:16px 20px; box-shadow:0 10px 30px rgba(15,23,42,.08); }
.list { list-style:none; margin:0; padding:0; display:flex; flex-direction:column; gap:8px; }
.row { display:flex; justify-content:space-between; align-items:center; border:1px solid #e2e8f0; border-radius:10px; padding:10px 12px; cursor:pointer; }
.title { font-weight:600; }
.meta { color:#94a3b8; font-size:12px; }
.pager { display:flex; gap:12px; align-items:center; justify-content:center; padding-top:12px; }
.empty { text-align:center; color:#94a3b8; padding:8px 0; }

.drawer { position:fixed; inset:0; background:rgba(15,23,42,.45); display:flex; justify-content:flex-end; }
.drawer-body { width:640px; height:100%; background:#fff; padding:16px 20px; overflow:auto; display:flex; flex-direction:column; gap:8px; }
.cmeta { color:#94a3b8; font-size:12px; }
.content { white-space:normal; line-height:1.6; color:#334155; }
.ops { display:flex; gap:8px; }
.ops .ghost { background:transparent; }
</style>
