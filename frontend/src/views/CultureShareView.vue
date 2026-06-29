<template>
  <div class="card">
    <h3>文化分享</h3>
    <p class="sub">戏曲视频精选推荐 · 每周荐读</p>

    <!-- Tab 切换 -->
    <div class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        :class="['tab-btn', { active: activeTab === tab.key }]"
        @click="activeTab = tab.key"
      >{{ tab.label }}</button>
    </div>

    <!-- ===== 视频推荐 ===== -->
    <section v-if="activeTab === 'video'">
      <div class="toolbar">
        <select v-model="genreFilter" @change="loadVideos">
          <option value="">全部剧种</option>
          <option v-for="g in genreOptions" :key="g" :value="g">{{ g }}</option>
        </select>
        <span class="total-hint">共 {{ videoMeta.total }} 条推荐</span>
      </div>

      <div v-if="videoLoading" class="loading">加载中…</div>
      <div v-else class="video-grid">
        <a
          v-for="v in videos"
          :key="v.id"
          :href="v.url"
          target="_blank"
          rel="noopener noreferrer"
          class="video-card"
        >
          <div class="vc-header">
            <span :class="['platform-badge', v.platform]">
              {{ platformLabel(v.platform) }}
            </span>
            <span v-if="v.opera_genre" class="genre-tag">{{ v.opera_genre }}</span>
            <span v-if="v.duration_display" class="duration">{{ v.duration_display }}</span>
          </div>
          <p class="vc-title">{{ v.title }}</p>
          <p class="vc-desc">{{ v.description }}</p>
          <div class="vc-footer">
            <span class="link-hint">点击前往观看 →</span>
          </div>
        </a>
        <p v-if="!videos.length" class="empty">暂无视频推荐</p>
      </div>

      <div class="pager" v-if="videoMeta.total > videoPageSize">
        <button :disabled="videoPage <= 1" @click="videoPage--; loadVideos()">上一页</button>
        <span>第 {{ videoPage }} / {{ videoTotalPages }} 页</span>
        <button :disabled="videoPage >= videoTotalPages" @click="videoPage++; loadVideos()">下一页</button>
      </div>
    </section>

    <!-- ===== 每周荐读 ===== -->
    <section v-if="activeTab === 'weekly'">
      <div v-if="digestLoading" class="loading">加载中…</div>
      <div v-else>
        <!-- 最新一期置顶卡片 -->
        <div v-if="latestDigest" class="digest-latest">
          <div class="digest-header">
            <div class="digest-week-badge">第 {{ latestDigest.week_number }} 周</div>
            <div>
              <h4 class="digest-title">{{ latestDigest.title }}</h4>
              <p class="digest-date">发布于 {{ formatDate(latestDigest.published_at) }}</p>
            </div>
          </div>
          <p class="digest-summary">{{ latestDigest.summary }}</p>
          <ul class="digest-items">
            <li v-for="(item, idx) in latestDigest.items" :key="idx" class="digest-item">
              <span :class="['item-type-badge', item.type]">{{ item.type === 'video' ? '视频' : '文章' }}</span>
              <div class="item-body">
                <a :href="item.url" target="_blank" rel="noopener noreferrer" class="item-title">
                  {{ item.title }}
                </a>
                <p v-if="item.desc" class="item-desc">{{ item.desc }}</p>
              </div>
            </li>
          </ul>
        </div>

        <!-- 历史期刊列表 -->
        <div v-if="digests.length > 1" class="digest-history">
          <h4 class="history-heading">往期荐读</h4>
          <div
            v-for="d in digests.slice(1)"
            :key="d.id"
            class="history-card"
            @click="expandedDigest = expandedDigest === d.id ? null : d.id"
          >
            <div class="history-card-head">
              <span class="digest-week-badge sm">第 {{ d.week_number }} 周</span>
              <span class="history-title">{{ d.title }}</span>
              <span class="history-date">{{ formatDate(d.published_at) }}</span>
              <span class="toggle-icon">{{ expandedDigest === d.id ? '▲' : '▼' }}</span>
            </div>
            <template v-if="expandedDigest === d.id">
              <p class="digest-summary" style="margin-top:8px">{{ d.summary }}</p>
              <ul class="digest-items">
                <li v-for="(item, idx) in d.items" :key="idx" class="digest-item">
                  <span :class="['item-type-badge', item.type]">{{ item.type === 'video' ? '视频' : '文章' }}</span>
                  <div class="item-body">
                    <a :href="item.url" target="_blank" rel="noopener noreferrer" class="item-title">
                      {{ item.title }}
                    </a>
                    <p v-if="item.desc" class="item-desc">{{ item.desc }}</p>
                  </div>
                </li>
              </ul>
            </template>
          </div>
        </div>

        <p v-if="!digests.length" class="empty">暂无荐读内容</p>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import {
  fetchVideoRecommendations,
  fetchWeeklyDigests,
  fetchLatestDigest,
  type VideoRecommendation,
  type WeeklyDigest,
  type PaginationMeta,
} from '@/api/cultural';

const tabs = [
  { key: 'video', label: '🎬 视频推荐' },
  { key: 'weekly', label: '📖 每周荐读' },
];
const activeTab = ref<'video' | 'weekly'>('video');

// ---------- 视频推荐 ----------
const genreOptions = ['京剧', '昆曲', '越剧', '粤剧', '黄梅戏', '豫剧', '秦腔', '川剧', '评剧', '徽剧'];
const genreFilter = ref('');
const videos = ref<VideoRecommendation[]>([]);
const videoMeta = ref<PaginationMeta>({ page: 1, page_size: 20, total: 0 });
const videoPage = ref(1);
const videoPageSize = ref(20);
const videoLoading = ref(false);
const videoTotalPages = computed(() => Math.max(1, Math.ceil(videoMeta.value.total / videoPageSize.value)));

async function loadVideos() {
  videoLoading.value = true;
  try {
    const res = await fetchVideoRecommendations({
      genre: genreFilter.value || undefined,
      page: videoPage.value,
      pageSize: videoPageSize.value,
    });
    videos.value = res.data;
    videoMeta.value = res.meta;
  } finally {
    videoLoading.value = false;
  }
}

function platformLabel(platform: string): string {
  if (platform === 'bilibili') return 'B 站';
  if (platform === 'youtube') return 'YouTube';
  return platform;
}

// ---------- 每周荐读 ----------
const digests = ref<WeeklyDigest[]>([]);
const latestDigest = ref<WeeklyDigest | null>(null);
const digestLoading = ref(false);
const expandedDigest = ref<number | null>(null);

async function loadDigests() {
  digestLoading.value = true;
  try {
    const [latestRes, listRes] = await Promise.all([
      fetchLatestDigest(),
      fetchWeeklyDigests({ page: 1, pageSize: 20 }),
    ]);
    latestDigest.value = latestRes;
    digests.value = listRes.data;
  } finally {
    digestLoading.value = false;
  }
}

function formatDate(dt?: string | null): string {
  if (!dt) return '';
  return dt.slice(0, 10);
}

onMounted(() => {
  loadVideos();
  loadDigests();
});
</script>

<style scoped>
.card { display: flex; flex-direction: column; gap: 16px; }
.sub { color: #64748b; margin: 0; }

/* Tabs */
.tabs { display: flex; gap: 8px; }
.tab-btn {
  padding: 8px 20px;
  border: 1.5px solid #e2e8f0;
  border-radius: 24px;
  background: transparent;
  cursor: pointer;
  font-size: 14px;
  color: #64748b;
  transition: all 0.2s;
}
.tab-btn.active {
  background: #c0392b;
  border-color: #c0392b;
  color: #fff;
  font-weight: 600;
}

/* Toolbar */
.toolbar { display: flex; gap: 12px; align-items: center; }
.total-hint { color: #94a3b8; font-size: 13px; }

/* Video Grid */
.video-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
  margin-top: 4px;
}
.video-card {
  display: flex;
  flex-direction: column;
  gap: 8px;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 14px 16px;
  text-decoration: none;
  color: inherit;
  transition: box-shadow 0.2s, border-color 0.2s;
  cursor: pointer;
}
.video-card:hover {
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.1);
  border-color: #c0392b;
}
.vc-header { display: flex; gap: 6px; align-items: center; flex-wrap: wrap; }
.platform-badge {
  font-size: 11px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 20px;
  background: #f1f5f9;
  color: #475569;
}
.platform-badge.bilibili { background: #e8f4fd; color: #00a1d6; }
.platform-badge.youtube  { background: #fff0f0; color: #ff0000; }
.genre-tag {
  font-size: 11px;
  padding: 2px 8px;
  background: #fef3c7;
  color: #92400e;
  border-radius: 20px;
}
.duration { font-size: 11px; color: #94a3b8; margin-left: auto; }
.vc-title { margin: 0; font-weight: 600; font-size: 14px; color: #1e293b; line-height: 1.4; }
.vc-desc { margin: 0; font-size: 12px; color: #64748b; line-height: 1.5; flex: 1; }
.vc-footer { display: flex; justify-content: flex-end; }
.link-hint { font-size: 12px; color: #c0392b; font-weight: 500; }

/* Weekly Digest */
.digest-latest {
  background: linear-gradient(135deg, #fff7f7 0%, #fff 60%);
  border: 1.5px solid #fca5a5;
  border-radius: 16px;
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.digest-header { display: flex; gap: 16px; align-items: flex-start; }
.digest-week-badge {
  background: #c0392b;
  color: #fff;
  font-size: 12px;
  font-weight: 700;
  padding: 4px 12px;
  border-radius: 20px;
  white-space: nowrap;
  flex-shrink: 0;
}
.digest-week-badge.sm { padding: 2px 10px; font-size: 11px; }
.digest-title { margin: 0; font-size: 16px; font-weight: 700; color: #1e293b; }
.digest-date { margin: 4px 0 0; font-size: 12px; color: #94a3b8; }
.digest-summary { margin: 0; color: #475569; font-size: 13px; line-height: 1.6; }

.digest-items { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 10px; }
.digest-item { display: flex; gap: 10px; align-items: flex-start; }
.item-type-badge {
  font-size: 11px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 20px;
  flex-shrink: 0;
  margin-top: 2px;
}
.item-type-badge.video { background: #dbeafe; color: #1d4ed8; }
.item-type-badge.article { background: #d1fae5; color: #065f46; }
.item-body { display: flex; flex-direction: column; gap: 2px; }
.item-title {
  color: #c0392b;
  text-decoration: none;
  font-size: 14px;
  font-weight: 600;
  line-height: 1.4;
}
.item-title:hover { text-decoration: underline; }
.item-desc { margin: 0; font-size: 12px; color: #64748b; }

/* History */
.digest-history { display: flex; flex-direction: column; gap: 8px; margin-top: 16px; }
.history-heading { margin: 0 0 8px; font-size: 14px; color: #64748b; font-weight: 600; }
.history-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 12px 16px;
  cursor: pointer;
}
.history-card:hover { border-color: #fca5a5; }
.history-card-head { display: flex; gap: 10px; align-items: center; }
.history-title { font-weight: 600; font-size: 14px; flex: 1; color: #1e293b; }
.history-date { font-size: 12px; color: #94a3b8; }
.toggle-icon { color: #94a3b8; font-size: 11px; }

/* Misc */
.pager { display: flex; gap: 12px; align-items: center; justify-content: center; padding-top: 12px; }
.loading { text-align: center; color: #94a3b8; padding: 32px 0; }
.empty { text-align: center; color: #94a3b8; padding: 32px 0; }
</style>
