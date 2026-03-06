<template>
  <div class="dashboard">
    <section class="hero">
      <div>
        <h2>遗迹之光 · 运维面板</h2>
        <p>快速浏览资源审核进度、互动热度与活动执行情况。</p>
      </div>
      <RouterLink to="/resources/create" class="cta">立即提交素材</RouterLink>
    </section>

    <section class="stats" v-if="summary">
      <article class="stat">
        <h3>资源总量</h3>
        <p class="value">{{ summary.total }}</p>
        <span>汇聚平台全部文化资源</span>
      </article>
      <article class="stat">
        <h3>待审核</h3>
        <p class="value pending">{{ summary.pending }}</p>
        <span>等待管理员审核的条目</span>
      </article>
      <article class="stat">
        <h3>已通过</h3>
        <p class="value approved">{{ summary.approved }}</p>
        <span>已对外发布的内容</span>
      </article>
      <article class="stat">
        <h3>需优化</h3>
        <p class="value rejected">{{ summary.rejected }}</p>
        <span>因资料不全被驳回的资源</span>
      </article>
    </section>

    <section class="latest" v-if="summary">
      <header>
        <h3>最近动态</h3>
        <RouterLink to="/resources">查看全部</RouterLink>
      </header>
      <ul>
        <li v-for="item in summary.latest" :key="item.id">
          <div>
            <p class="title">{{ item.title }}</p>
            <p class="meta">{{ formatTime(item.updated_at) }} · {{ statusMap[item.status] ?? item.status }}</p>
          </div>
          <span :class="['badge', item.status]">{{ statusMap[item.status] ?? item.status }}</span>
        </li>
      </ul>
    </section>

    <section class="two-col">
      <article class="card-block" v-if="question">
        <header class="card-head">
          <div>
            <p class="eyebrow">每日一题</p>
            <h3>{{ question.title }}</h3>
            <p class="muted">答对奖励 {{ question.points_reward }} 积分，今天只可提交一次</p>
          </div>
          <span class="date">{{ formatDate(question.active_date) }}</span>
        </header>
        <ul class="quiz-options">
          <li v-for="opt in question.options" :key="opt">
            <label>
              <input type="radio" name="quiz" :value="opt" v-model="selectedOption" :disabled="Boolean(answerResult)" />
              {{ opt }}
            </label>
          </li>
        </ul>
        <div class="quiz-actions">
          <button class="primary" :disabled="!selectedOption || Boolean(answerResult)" @click="submitAnswer">提交答案</button>
          <span v-if="answerResult" :class="['pill', answerResult.is_correct ? 'ok' : 'warn']">
            {{ answerResult.message }}（+{{ answerResult.points_reward }} 分）
          </span>
        </div>
      </article>

      <article class="card-block">
        <header class="card-head">
          <div>
            <p class="eyebrow">猜你喜欢</p>
            <h3>为你挑选的资源</h3>
            <p class="muted">基于最近点赞/收藏的标签与流派推荐</p>
          </div>
          <RouterLink to="/resources" class="ghost-link">更多</RouterLink>
        </header>
        <div class="recommend-grid">
          <div v-for="item in recommendations" :key="item.id" class="recommend-card">
            <div class="title-line">
              <p class="title">{{ item.title }}</p>
              <span class="badge tiny">{{ item.genre || item.resource_type }}</span>
            </div>
            <p class="muted line-2">{{ item.synopsis || "暂无简介" }}</p>
            <div class="tag-row">
              <span v-for="tag in item.tags" :key="tag" class="tag">{{ tag }}</span>
              <span v-if="!item.tags.length" class="tag muted">未设置</span>
            </div>
            <RouterLink :to="`/resources/${item.id}`" class="view-link">查看详情</RouterLink>
          </div>
          <div v-if="!recommendations.length" class="empty">暂无推荐，可先浏览资源或点赞收藏</div>
        </div>
      </article>
    </section>

    <section class="chart-grid" v-if="dashboardStats">
      <article class="chart-card">
        <h3>近 30 天资源新增趋势</h3>
        <BaseChart :option="trendOption" />
      </article>
      <article class="chart-card">
        <h3>热门话题 TOP10</h3>
        <BaseChart :option="topicOption" />
      </article>
      <article class="chart-card">
        <h3>地区分布占比</h3>
        <BaseChart :option="regionOption" />
      </article>
      <article class="chart-card">
        <h3>活动参与概览</h3>
        <BaseChart :option="activityOption" />
      </article>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import dayjs from "dayjs";
import { RouterLink } from "vue-router";
import BaseChart from "@/components/charts/BaseChart.vue";
import { fetchResourceSummary, type ResourceItem, type ResourceSummary } from "@/api/resource";
import { fetchDashboardStats, type DashboardStats } from "@/api/stats";
import { useAuthStore } from "@/store/auth";
import { fetchRecommendations } from "@/api/recommendation";
import { fetchTodayQuestion, submitQuizAnswer, type QuizAnswerResult, type QuizQuestion } from "@/api/quiz";

const summary = ref<ResourceSummary | null>(null);
const dashboardStats = ref<DashboardStats | null>(null);
const recommendations = ref<ResourceItem[]>([]);
const question = ref<QuizQuestion | null>(null);
const selectedOption = ref<string | null>(null);
const answerResult = ref<QuizAnswerResult | null>(null);
const auth = useAuthStore();

const statusMap: Record<string, string> = {
  draft: "草稿",
  pending: "待审核",
  approved: "已通过",
  rejected: "已驳回"
};

const trendOption = computed(() => {
  if (!dashboardStats.value) {
    return {};
  }
  return {
    tooltip: { trigger: "axis" },
    xAxis: {
      type: "category",
      data: dashboardStats.value.resource_trend.map((item) => dayjs(item.day).format("MM/DD"))
    },
    yAxis: { type: "value" },
    series: [
      {
        name: "新增资源",
        type: "line",
        smooth: true,
        data: dashboardStats.value.resource_trend.map((item) => item.count)
      }
    ]
  };
});

const topicOption = computed(() => {
  if (!dashboardStats.value) {
    return {};
  }
  return {
    tooltip: { trigger: "axis" },
    grid: { left: 60, right: 20, bottom: 30, top: 30 },
    xAxis: {
      type: "value"
    },
    yAxis: {
      type: "category",
      data: dashboardStats.value.topic_hot.map((item) => item.name)
    },
    series: [
      {
        name: "话题热度",
        type: "bar",
        data: dashboardStats.value.topic_hot.map((item) => item.value),
        itemStyle: {
          color: "#6366f1"
        }
      }
    ]
  };
});

const regionOption = computed(() => {
  if (!dashboardStats.value) {
    return {};
  }
  return {
    tooltip: { trigger: "item" },
    legend: { bottom: 0 },
    series: [
      {
        name: "地区分布",
        type: "pie",
        radius: ["35%", "70%"],
        itemStyle: { borderRadius: 8 },
        data: dashboardStats.value.region_distribution.map((item) => ({ value: item.value, name: item.name }))
      }
    ]
  };
});

const activityOption = computed(() => {
  if (!dashboardStats.value) {
    return {};
  }
  return {
    tooltip: { trigger: "axis" },
    legend: { top: 0 },
    grid: { left: 60, right: 20, bottom: 30, top: 40 },
    xAxis: {
      type: "category",
      data: dashboardStats.value.activity_participants.map((item) => item.title)
    },
    yAxis: { type: "value" },
    series: [
      {
        name: "报名人数",
        type: "bar",
        data: dashboardStats.value.activity_participants.map((item) => item.enrolled),
        itemStyle: { color: "#38bdf8" }
      },
      {
        name: "签到人数",
        type: "bar",
        data: dashboardStats.value.activity_participants.map((item) => item.checked_in),
        itemStyle: { color: "#10b981" }
      }
    ]
  };
});

function formatTime(value: string) {
  return dayjs(value).format("YYYY-MM-DD HH:mm");
}

function formatDate(value: string) {
  return dayjs(value).format("YYYY-MM-DD");
}

async function loadRecommendations() {
  recommendations.value = await fetchRecommendations(6);
}

async function loadQuiz() {
  question.value = await fetchTodayQuestion();
}

async function submitAnswer() {
  if (!question.value || !selectedOption.value) return;
  const optionKey = selectedOption.value.split(".")[0];
  answerResult.value = await submitQuizAnswer(question.value.id, optionKey);
}

onMounted(async () => {
  summary.value = await fetchResourceSummary();
  if (auth.user?.role === "admin" || auth.user?.role === "practitioner") {
    dashboardStats.value = await fetchDashboardStats();
  }
  await Promise.all([loadRecommendations(), loadQuiz()]);
});
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.hero {
  background: linear-gradient(135deg, #6366f1, #22d3ee);
  border-radius: 20px;
  padding: 28px 32px;
  color: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.hero h2 {
  margin: 0 0 8px;
}

.hero p {
  margin: 0;
  opacity: 0.85;
}

.cta {
  background: #0f172a;
  color: #fff;
  padding: 12px 20px;
  border-radius: 12px;
  font-weight: 600;
}

.stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.stat {
  background: #fff;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.08);
}

.stat h3 {
  margin: 0;
  font-size: 16px;
  color: #475467;
}

.stat .value {
  margin: 12px 0 6px;
  font-size: 32px;
  font-weight: 700;
  color: #0f172a;
}

.stat .value.pending {
  color: #f59e0b;
}

.stat .value.approved {
  color: #10b981;
}

.stat .value.rejected {
  color: #ef4444;
}

.stat span {
  font-size: 12px;
  color: #94a3b8;
}

.latest {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.08);
  padding: 20px 24px;
}

.latest header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.latest ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.latest li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 12px 16px;
}

.title {
  margin: 0 0 6px;
  font-weight: 600;
}

.meta {
  margin: 0;
  color: #94a3b8;
  font-size: 12px;
}

.badge {
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 12px;
}

.badge.pending {
  background: #fff7ed;
  color: #f97316;
}

.badge.approved {
  background: #dcfce7;
  color: #16a34a;
}

.badge.rejected {
  background: #fee2e2;
  color: #ef4444;
}

.badge.draft {
  background: #e0f2fe;
  color: #0284c7;
}

.chart-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.chart-card {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.08);
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chart-card h3 {
  margin: 0;
  font-size: 16px;
}

.two-col {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.card-block {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.08);
  padding: 18px 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.card-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.eyebrow {
  margin: 0;
  color: #94a3b8;
  font-size: 12px;
}

.muted {
  color: #94a3b8;
  margin: 6px 0 0;
}

.date {
  color: #0f172a;
  font-weight: 600;
}

.quiz-options {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.quiz-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.pill {
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 12px;
}

.pill.ok {
  background: #dcfce7;
  color: #15803d;
}

.pill.warn {
  background: #fef3c7;
  color: #b45309;
}

.recommend-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 12px;
}

.recommend-card {
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.title-line {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  align-items: center;
}

.badge.tiny {
  font-size: 10px;
  background: #eef2ff;
  color: #4338ca;
  padding: 4px 8px;
  border-radius: 999px;
}

.tag-row {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.tag {
  padding: 4px 8px;
  background: #f1f5f9;
  color: #475569;
  border-radius: 8px;
  font-size: 12px;
}

.tag.muted {
  background: #e2e8f0;
}

.view-link {
  color: #2563eb;
  font-weight: 600;
}

.line-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.ghost-link {
  color: #475467;
}
</style>
