import { createRouter, createWebHistory, RouteRecordRaw } from "vue-router";
import { useAuthStore } from "@/store/auth";

const routes: RouteRecordRaw[] = [
  {
    path: "/login",
    name: "login",
    component: () => import("@/views/LoginView.vue")
  },
  {
    path: "/register",
    name: "register",
    component: () => import("@/views/RegisterView.vue")
  },
  {
    path: "/",
    component: () => import("@/views/LayoutShell.vue"),
    children: [
      {
        path: "",
        name: "dashboard",
        component: () => import("@/views/DashboardView.vue"),
        meta: { requiresAuth: true }
      },
      {
        path: "resources",
        name: "resources",
        component: () => import("@/views/ResourceListView.vue"),
        meta: { requiresAuth: true }
      },
      {
        path: "resources/create",
        name: "resource-create",
        component: () => import("@/views/ResourceSubmitView.vue"),
        meta: { requiresAuth: true }
      },
      {
        path: "resources/:id",
        name: "resource-detail",
        component: () => import("@/views/ResourceDetailView.vue"),
        meta: { requiresAuth: true }
      },
      {
        path: "interaction",
        name: "interaction",
        component: () => import("@/views/InteractionView.vue"),
        meta: { requiresAuth: true }
      },
      {
        path: "activities",
        name: "activities",
        component: () => import("@/views/ActivityCenterView.vue"),
        meta: { requiresAuth: true }
      },
      {
        path: "audits",
        name: "audit",
        component: () => import("@/views/AuditLogView.vue"),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: "admin/review",
        name: "admin-review",
        component: () => import("@/views/AdminReviewView.vue"),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: "admin/analytics",
        name: "admin-analytics",
        component: () => import("@/views/AdminContentAnalyticsView.vue"),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: "admin/practitioners",
        name: "admin-practitioners",
        component: () => import("@/views/AdminPractitionersView.vue"),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: "admin/products",
        name: "admin-products",
        component: () => import("@/views/AdminProductsView.vue"),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: "admin/orders",
        name: "admin-orders",
        component: () => import("@/views/AdminOrdersView.vue"),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: "admin/users",
        name: "admin-users",
        component: () => import("@/views/AdminUsersView.vue"),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: "profile",
        name: "profile",
        component: () => import("@/views/ProfileView.vue"),
        meta: { requiresAuth: true }
      },
      {
        path: "practitioner/verify",
        name: "practitioner-verify",
        component: () => import("@/views/PractitionerVerifyView.vue"),
        meta: { requiresAuth: true }
      },
      {
        path: "my/resources",
        name: "my-resources",
        component: () => import("@/views/MyResourcesView.vue"),
        meta: { requiresAuth: true }
      },
      {
        path: "activities/explore",
        name: "activities-explore",
        component: () => import("@/views/ActivitiesExploreView.vue"),
        meta: { requiresAuth: true }
      },
      {
        path: "activities/me",
        name: "my-enrollments",
        component: () => import("@/views/MyEnrollmentsView.vue"),
        meta: { requiresAuth: true }
      },
      {
        path: "topics/hot",
        name: "hot-topics",
        component: () => import("@/views/HotTopicsView.vue"),
        meta: { requiresAuth: true }
      },
      {
        path: "wiki",
        name: "wiki",
        component: () => import("@/views/WikiView.vue"),
        meta: { requiresAuth: true }
      },
      {
        path: "culture",
        name: "culture-share",
        component: () => import("@/views/CultureShareView.vue"),
        meta: { requiresAuth: true }
      },
      {
        path: "shop",
        name: "shop",
        component: () => import("@/views/ShopView.vue"),
        meta: { requiresAuth: true }
      }
    ]
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach(async (to, _from, next) => {
  const store = useAuthStore();
  if (store.isAuthenticated && !store.user) {
    try {
      await store.loadProfile();
    } catch (error) {
      console.error("加载用户信息失败", error);
    }
  }

  if (to.meta.requiresAuth && !store.isAuthenticated) {
    next({ name: "login", query: { redirect: to.fullPath } });
    return;
  }
  if (to.meta.requiresAdmin && store.user?.role !== "admin") {
    next({ name: "dashboard" });
    return;
  }
  // 非登录页禁止已登录用户访问注册页
  if (to.name === "register" && store.isAuthenticated) {
    next({ name: "dashboard" });
    return;
  }
  if (to.name === "login" && store.isAuthenticated) {
    next({ name: "dashboard" });
    return;
  }
  next();
});

export default router;
