<template>
  <div class="resource-page">
    <section class="overview" v-if="summary">
      <article class="stat-card primary">
        <div class="stat-label">资源总量</div>
        <div class="stat-value">{{ summary.total }}</div>
        <p class="stat-desc">平台累计收录的文化资源数量</p>
      </article>
      <article class="stat-card">
        <div class="stat-label">待审核</div>
        <div class="stat-value">{{ summary.pending }}</div>
        <p class="stat-desc">等待管理员审核的提交</p>
      </article>
      <article class="stat-card">
        <div class="stat-label">已通过</div>
        <div class="stat-value">{{ summary.approved }}</div>
        <p class="stat-desc">已对外展示的内容</p>
      </article>
      <article class="stat-card">
        <div class="stat-label">已驳回</div>
        <div class="stat-value">{{ summary.rejected }}</div>
        <p class="stat-desc">需要补充资料的提交</p>
      </article>
    </section>

    <section class="panel">
      <div class="panel-main">
        <header class="toolbar">
          <div class="filters">
            <div class="status-tabs">
              <button
                v-for="item in statusOptions"
                :key="item.value"
                type="button"
                :class="['tab', { active: status === item.value }]"
                @click="applyStatus(item.value)"
              >
                {{ item.label }}
              </button>
            </div>
            <div class="search">
              <input
                v-model="keyword"
                type="search"
                placeholder="按标题或描述关键字检索"
                @keyup.enter="handleSearch"
              />
              <button type="button" class="search-btn" @click="handleSearch">搜索</button>
            </div>
          </div>
          <div class="actions">
            <button v-if="isAdmin" type="button" class="ghost" @click="exportResources">导出资源</button>
            <RouterLink to="/resources/create" class="primary">+ 新建资源</RouterLink>
          </div>
        </header>

        <table>
          <thead>
            <tr>
              <th>标题</th>
              <th>资源类型</th>
              <th>简介</th>
              <th>标签</th>
              <th>状态</th>
              <th>更新时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in resources" :key="item.id">
              <td>
                <p class="title"><RouterLink :to="`/resources/${item.id}`">{{ item.title }}</RouterLink></p>
                <p class="file" v-if="item.file_path">本地文件：{{ item.file_path }}</p>
                <p class="file" v-else-if="item.external_url">外链：{{ item.external_url }}</p>
              </td>
              <td>
                <span class="type">{{ item.resource_type }}</span>
              </td>
              <td>
                <p class="synopsis">{{ item.synopsis || "暂无简介" }}</p>
                <p class="trail" v-if="item.trails.length">轨迹点：{{ item.trails.length }}</p>
              </td>
              <td>
                <div class="tag-list">
                  <span v-for="tag in item.tags" :key="tag" class="tag">{{ tag }}</span>
                  <span v-if="!item.tags.length" class="tag muted">未设置</span>
                </div>
              </td>
              <td>
                <span :class="['badge', item.status]">{{ statusMap[item.status] ?? item.status }}</span>
              </td>
              <td>{{ formatTime(item.updated_at) }}</td>
            </tr>
            <tr v-if="!resources.length">
              <td colspan="6" class="empty">暂无符合条件的数据</td>
            </tr>
          </tbody>
        </table>

        <footer class="pagination" v-if="meta.total > meta.page_size">
          <button type="button" :disabled="meta.page === 1" @click="changePage(meta.page - 1)">
            上一页
          </button>
          <span>第 {{ meta.page }} / {{ totalPages }} 页 · 共 {{ meta.total }} 条</span>
          <button type="button" :disabled="meta.page >= totalPages" @click="changePage(meta.page + 1)">
            下一页
          </button>
        </footer>
      </div>

      <aside class="panel-aside" v-if="summary">
        <h4>最新动态</h4>
        <ul>
          <li v-for="item in summary.latest" :key="item.id">
            <div class="timeline-point"></div>
            <div>
              <p class="timeline-title">{{ item.title }}</p>
              <p class="timeline-meta">{{ formatTime(item.created_at) }} · {{ statusMap[item.status] ?? item.status }}</p>
            </div>
          </li>
        </ul>
      </aside>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import { RouterLink } from "vue-router";
import dayjs from "dayjs";
import {
  fetchResources,
  fetchResourceSummary,
  type PaginationMeta,
  type ResourceItem,
  type ResourceListResult,
  type ResourceQuery,
  type ResourceSummary
} from "@/api/resource";
import { useAuthStore } from "@/store/auth";

const resources = ref<ResourceItem[]>([]);
const summary = ref<ResourceSummary | null>(null);
const meta = reactive<PaginationMeta>({ page: 1, page_size: 10, total: 0 });
const keyword = ref("");
const status = ref<string | undefined>(undefined);
const auth = useAuthStore();

const statusOptions = [
  { label: "全部", value: undefined },
  { label: "草稿", value: "draft" },
  { label: "待审核", value: "pending" },
  { label: "已通过", value: "approved" },
  { label: "已驳回", value: "rejected" }
];

const statusMap: Record<string, string> = {
  draft: "草稿",
  pending: "待审核",
  approved: "已通过",
  rejected: "已驳回"
};

const totalPages = computed(() => Math.max(1, Math.ceil(meta.total / meta.page_size)));

async function loadResources(params: ResourceQuery = {}) {
  const merged: ResourceQuery = {
    status: status.value,
    keyword: keyword.value || undefined,
    page: meta.page,
    pageSize: meta.page_size,
    ...params
  };
  const response: ResourceListResult = await fetchResources(merged);
  resources.value = response.items;
  Object.assign(meta, response.meta);
}

async function loadSummary() {
  summary.value = await fetchResourceSummary();
}

function applyStatus(value: string | undefined) {
  status.value = value;
  meta.page = 1;
  loadResources({ page: 1 });
}

function handleSearch() {
  meta.page = 1;
  loadResources({ page: 1 });
}

function changePage(page: number) {
  meta.page = page;
  loadResources({ page });
}

function formatTime(value: string) {
  return dayjs(value).format("YYYY-MM-DD HH:mm");
}

onMounted(async () => {
  await Promise.all([loadSummary(), loadResources()]);
});

const isAdmin = computed(() => auth.user?.role === "admin");
function exportResources() {
  window.open("/api/admin/export?type=resources", "_blank");
}
</script>

<style scoped>
.resource-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
}

.stat-card {
  background: #fff;
  border-radius: 16px;
  padding: 18px 20px;
  box-shadow: 0 18px 30px rgba(15, 23, 42, 0.08);
  position: relative;
  overflow: hidden;
}

.stat-card.primary {
  background: linear-gradient(135deg, #22d3ee, #3b82f6);
  color: #0b1120;
}

.stat-label {
  font-size: 14px;
  opacity: 0.8;
}

.stat-value {
  font-size: 34px;
  font-weight: 700;
  margin: 12px 0;
}

.stat-desc {
  margin: 0;
  font-size: 12px;
  opacity: 0.7;
}

.panel {
  display: grid;
  grid-template-columns: 2fr minmax(240px, 1fr);
  gap: 24px;
}

.panel-main {
  background: #fff;
  border-radius: 16px;
  padding: 20px 24px 24px;
  box-shadow: 0 18px 30px rgba(15, 23, 42, 0.08);
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.filters {
  display: flex;
  align-items: center;
  gap: 16px;
}

.status-tabs {
  display: inline-flex;
  background: #f1f5f9;
  padding: 4px;
  border-radius: 999px;
  gap: 4px;
}

.tab {
  border: none;
  padding: 8px 16px;
  border-radius: 999px;
  background: transparent;
  color: #475467;
  transition: all 0.2s ease;
}

.tab.active {
  background: #fff;
  color: #0f172a;
  box-shadow: 0 6px 16px rgba(15, 23, 42, 0.12);
}

.search {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #f8fafc;
  padding: 6px 8px 6px 16px;
  border-radius: 12px;
}

.search input {
  border: none;
  background: transparent;
  outline: none;
  min-width: 200px;
}

.search-btn {
  border: none;
  background: #3b82f6;
  color: #fff;
  padding: 8px 16px;
  border-radius: 10px;
  font-weight: 600;
}

.primary {
  padding: 10px 18px;
  background: linear-gradient(135deg, #3b82f6, #6366f1);
  color: #fff;
  border-radius: 12px;
  font-weight: 600;
}
.actions {
  display: flex;
  gap: 8px;
  align-items: center;
}
.ghost {
  padding: 10px 14px;
  border-radius: 12px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  color: #0f172a;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background: #f8fafc;
}

th,
td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
  vertical-align: top;
}

.title {
  margin: 0 0 6px;
  font-weight: 600;
}

.file {
  margin: 0;
  font-size: 12px;
  color: #64748b;
}

.type {
  display: inline-block;
  padding: 6px 12px;
  background: #e0f2fe;
  color: #0369a1;
  border-radius: 999px;
  font-size: 12px;
}

.synopsis {
  margin: 0 0 6px;
  color: #475467;
  font-size: 14px;
}

.trail {
  margin: 0;
  font-size: 12px;
  color: #94a3b8;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag {
  padding: 4px 10px;
  border-radius: 999px;
  background: #f3f4ff;
  color: #4f46e5;
  font-size: 12px;
}

.tag.muted {
  background: #e2e8f0;
  color: #64748b;
}

.badge {
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 12px;
  display: inline-block;
}

.badge.pending {
  background: rgba(234, 179, 8, 0.16);
  color: #b45309;
}

.badge.approved {
  background: rgba(34, 197, 94, 0.16);
  color: #047857;
}

.badge.rejected {
  background: rgba(239, 68, 68, 0.16);
  color: #b91c1c;
}

.badge.draft {
  background: rgba(14, 165, 233, 0.16);
  color: #0c4a6e;
}

.empty {
  text-align: center;
  color: #64748b;
  padding: 32px 0;
}

.pagination {
  margin-top: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
}

.pagination button {
  border: none;
  background: #e2e8f0;
  color: #0f172a;
  padding: 8px 16px;
  border-radius: 10px;
}

.pagination button:disabled {
  opacity: 0.5;
}

.panel-aside {
  background: #fff;
  border-radius: 16px;
  padding: 20px 24px;
  box-shadow: 0 18px 30px rgba(15, 23, 42, 0.08);
}

.panel-aside h4 {
  margin: 0 0 12px;
}

.panel-aside ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.panel-aside li {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.timeline-point {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #6366f1;
  margin-top: 6px;
}

.timeline-title {
  margin: 0;
  font-weight: 600;
}

.timeline-meta {
  margin: 4px 0 0;
  font-size: 12px;
  color: #64748b;
}

@media (max-width: 1024px) {
  .panel {
    grid-template-columns: 1fr;
  }
}
</style>
