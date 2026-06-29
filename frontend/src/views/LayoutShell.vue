<template>
  <div class="layout">
    <aside class="sidebar">
      <div class="brand">
        <h1 class="logo">寻戏之旅——经典戏曲文化分享互动管理系统的设计与实现</h1>
        <p class="logo-sub">文化遗产协作工作台</p>
      </div>
      <nav>
        <RouterLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="nav-item"
          exact-active-class="active"
        >
          <span class="nav-dot"></span>
          {{ item.label }}
        </RouterLink>
      </nav>
      <div class="flex-spacer"></div>
      <div class="user-card" v-if="auth.user">
        <p class="user-email">{{ auth.user.email }}</p>
        <p class="user-role">当前角色：{{ roleLabel }}</p>
      </div>
      <div class="sidebar-footer">
        <button class="btn ghost" style="width:100%" @click="handleLogout">退出登录</button>
      </div>
    </aside>
    <main class="content">
      <header class="content-header">
        <div class="headline">
          <h2>{{ pageTitle }}</h2>
          <p class="subtitle">{{ subtitle }}</p>
        </div>
        <div class="quick-info">
          <span class="dot"></span>
          <span>最后刷新时间：{{ now }}</span>
        </div>
      </header>
      <section class="content-body page card">
        <router-view />
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from "vue";
import { useRoute, useRouter, RouterLink } from "vue-router";
import { useAuthStore } from "@/store/auth";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();

const now = ref(new Date().toLocaleString());
let timer: number | undefined;

onMounted(() => {
  timer = window.setInterval(() => {
    now.value = new Date().toLocaleString();
  }, 60000);
});

onUnmounted(() => {
  if (timer) {
    clearInterval(timer);
  }
});

const navItems = computed(() => {
  const items: { to: string; label: string }[] = [];
  if (auth.user?.role === "admin") {
    items.push(
      { to: "/", label: "数据总览" },
      { to: "/resources", label: "资源库" },
      { to: "/culture", label: "文化分享" },
      { to: "/admin/analytics", label: "热门分析" },
      { to: "/admin/practitioners", label: "从业者管理" },
      { to: "/admin/products", label: "商品管理" },
      { to: "/admin/orders", label: "订单管理" },
      { to: "/admin/review", label: "审核中心" },
      { to: "/admin/users", label: "用户管理" },
      { to: "/audits", label: "审计日志" },
    );
  } else if (auth.user?.role === "practitioner") {
    items.push(
      { to: "/practitioner/verify", label: "从业者认证" },
      { to: "/resources/create", label: "提交资源" },
      { to: "/topics/hot", label: "热门话题" },
      { to: "/culture", label: "文化分享" },
      { to: "/activities", label: "活动中心" },
    );
  } else if (auth.user?.role === "user") {
    items.push(
      { to: "/topics/hot", label: "热门话题" },
      { to: "/wiki", label: "戏曲百科库" },
      { to: "/culture", label: "文化分享" },
      { to: "/interaction", label: "互动广场" },
      { to: "/activities/explore", label: "活动参与" },
      { to: "/activities/me", label: "我的报名" },
      { to: "/shop", label: "积分商城" },
    );
  }
  if (auth.user) {
    items.push({ to: "/profile", label: "个人资料" });
  }
  return items;
});

const roleLabel = computed(() => {
  if (!auth.user) {
    return "未登录";
  }
  if (auth.user.role === "admin") {
    return "管理员";
  }
  if (auth.user.role === "practitioner") {
    return "从业者";
  }
  return "普通用户";
});

const pageTitle = computed(() => {
  switch (route.name) {
    case "dashboard":
      return "工作台总览";
    case "resources":
      return "资源管理中心";
    case "resource-create":
      return "提交新资源";
    case "resource-detail":
      return "资源详情";
    case "interaction":
      return "互动广场";
    case "activities-explore":
      return "活动参与";
    case "my-enrollments":
      return "我的报名";
    case "hot-topics":
      return "热门话题";
    case "wiki":
      return "戏曲百科库";
    case "culture-share":
      return "文化分享";
    case "shop":
      return "积分商城";
    case "login":
      return "登录";
    case "register":
      return "注册";
    case "activities":
      return "活动管理";
    case "audit":
      return "审计日志";
    case "admin-review":
      return "审核中心";
    case "admin-analytics":
      return "热门内容分析";
    case "admin-practitioners":
      return "从业者管理";
    case "admin-products":
      return "商品管理";
    case "admin-orders":
      return "订单管理";
    case "admin-users":
      return "用户管理";
    case "profile":
      return "个人资料";
    case "practitioner-verify":
      return "从业者认证";
    case "my-resources":
      return "我的资源";
    default:
      return "寻戏之旅——经典戏曲文化分享互动管理系统的设计与实现";
  }
});

const subtitle = computed(() => {
  switch (route.name) {
    case "dashboard":
      return "掌握资源发展趋势与待办提醒";
    case "resources":
      return "检索与跟踪资源全生命周期";
    case "resource-create":
      return "完善素材信息并提交审核";
    case "resource-detail":
      return "查看资源元数据与轨迹地图";
    case "interaction":
      return "浏览帖子互动与话题热度";
    case "activities-explore":
      return "浏览活动并在线报名";
    case "my-enrollments":
      return "查看我的报名记录与状态";
    case "hot-topics":
      return "参与热门话题，发布与互动";
    case "wiki":
      return "检索戏曲百科词条与分类";
    case "culture-share":
      return "精选视频推荐与每周荐读";
    case "shop":
      return "使用积分兑换商品";
    case "login":
      return "使用已有账号登录系统";
    case "register":
      return "注册一个新账号以便登录系统";
    case "activities":
      return "策划或跟进活动执行进度";
    case "audit":
      return "追溯关键操作留痕，确保安全可控";
    case "admin-review":
      return "统一处理资源/活动/帖子的审核任务";
    case "admin-analytics":
      return "基于资源数据的热门内容洞察";
    case "admin-practitioners":
      return "审核材料并验证身份，维护从业者资格";
    case "admin-products":
      return "维护积分商城商品";
    case "admin-orders":
      return "查看订单并发货";
    case "admin-users":
      return "管理员维护用户信息与权限";
    case "profile":
      return "查看与维护个人基础信息";
    case "practitioner-verify":
      return "提交资质材料，成为认证从业者";
    case "my-resources":
      return "查看与跟进我提交的资源";
    default:
      return "";
  }
});

function handleLogout() {
  auth.logout();
  router.push({ name: "login" });
}
</script>

<style scoped>
.layout { display:grid; grid-template-columns:260px 1fr; min-height:100vh; }
.sidebar { color:#fff; padding:24px; display:flex; flex-direction:column; gap:16px; position:sticky; top:0;
  background: linear-gradient(180deg, rgba(122,156,122,.95), rgba(96,132,96,.95));
  box-shadow: var(--shadow);
}
.brand { display:flex; flex-direction:column; gap:6px; }
.logo { margin:0; font-size:22px; letter-spacing:2px; }
nav { display:flex; flex-direction:column; gap:8px; }
.nav-item { color:#f1f5f9; text-decoration:none; padding:10px 12px; border-radius:10px; display:flex; align-items:center; gap:8px; transition:background .15s }
.nav-item:hover{ background: rgba(255,255,255,.08); }
.nav-item.active { background: rgba(255,255,255,.14); color:#fff; }
.nav-dot { width:6px; height:6px; background:#dbe7db; border-radius:50%; display:inline-block; }
.flex-spacer { flex:1; }
.user-card { background: rgba(255,255,255,.12); border-radius:14px; padding:12px; }
.user-email { color:#e2e8f0; font-size:12px; margin:0 0 6px; }
.user-role { margin:0; }
.sidebar-footer { padding-top:8px; padding-bottom:4px; }
.content { padding:20px 28px; }
.content-header { display:flex; justify-content:space-between; align-items:center; }
.headline h2 { margin:0 0 4px; font-size:28px; color:var(--ink); }
.subtitle { margin:0; color:var(--muted); }
.quick-info { display:flex; gap:8px; align-items:center; color:var(--muted); }
.quick-info .dot { width:8px; height:8px; border-radius:50%; background:var(--success); }
.content-body { margin-top:16px; }
@media (max-width:1080px){
  .layout{ grid-template-columns:220px 1fr; }
  .content-header{ flex-direction:column; align-items:flex-start; gap:16px; }
}
</style>
