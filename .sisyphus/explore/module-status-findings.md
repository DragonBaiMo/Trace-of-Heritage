# Trace-of-Heritage 模块现状探索报告

探索时间：2026-04-16

---

## 1. 百科/Encyclopedia/Wiki/文化 相关文件

### 后端

| 文件 | 关键内容 | 行号 |
|------|----------|------|
| `backend/app/models/wiki.py` | `WikiEntry` 模型：id/title/content/category/status/author_id/created_at/updated_at | L1-22 |
| `backend/app/schemas/wiki.py` | `WikiEntryRead`(读取schema)、`WikiEntryQuery`(keyword+category查询) | L1-26 |
| `backend/app/services/wiki_service.py` | `WikiService.list_entries()`(关键词+分类+分页)、`get_entry()` | L1-32 |
| `backend/app/api/routes/wiki.py` | `GET /api/wiki/entries`(分页列表)、`GET /api/wiki/entries/{id}` | L1-32 |
| `backend/app/models/resource.py` | `Resource`(文化资源主表)，含 genre/era/region_code 等戏曲元数据字段 | L1-52 |
| `backend/app/main.py` | `app.include_router(wiki.router, prefix="/api")` 注册路由 | L20,L72 |

### 前端

| 文件 | 关键内容 | 行号 |
|------|----------|------|
| `frontend/src/views/WikiView.vue` | 戏曲百科库页面：关键词+分类(genre/figure/term)搜索、分页列表、词条详情Drawer、markdown渲染 | L1-38 |
| `frontend/src/views/LayoutShell.vue` | 导航菜单含 `{ to: "/wiki", label: "戏曲百科库" }` | L95,L140,L193 |

### SQL

| 文件 | 表名 | 字段 | 行号 |
|------|------|------|------|
| `database.sql` | `wiki_entries` | id/title/content/category/status/author_id/created_at/updated_at；索引：title/category/status/author_id | L272-288 |
| `database_mysql.sql` | `wiki_entries` | 同上，含 `fk_wiki_author` 外键约束，InnoDB utf8mb4 | L259-273 |

**当前状态**：百科模块完整实现，有模型/schema/service/API/前端页面/SQL建表，但**没有写入接口**（无 POST/PUT/DELETE），仅支持查询，词条数据需通过 seed 或直接入库。

---

## 2. 视频/Video/Media 相关文件

| 文件 | 关键内容 | 行号 |
|------|----------|------|
| `backend/app/models/resource.py` | `resource_type` 字段（VARCHAR 20），枚举值包含 "video" | L15 |
| `backend/app/core/config.py` | `media_root = "data/uploads"` 文件存储根目录配置 | L38,L77-81 |
| `backend/seed_demo.py` | 种子数据包含 10 条 resource_type="video" 的戏曲视频记录 | L31-42 |
| `frontend/src/views/ResourceSubmitView.vue` | 资源提交表单中 `<option value="video">视频</option>` | L14 |
| `database.sql` 注释 | `-- 资源类型枚举值：图片, 视频, 文档, 音频, 其他` | L530 |
| `database_postgresql.sql` | `CREATE TYPE resource_type AS ENUM ('图片', '视频', '文档', '音频', '其他')` | L40 |

**当前状态**：**不存在**独立的视频模型、视频播放器组件、HLS/流媒体处理逻辑。视频仅作为 `resources` 表中 `resource_type="video"` 的一种资源类型存在，无专用视频详情页、播放控件或视频流端点。

---

## 3. 戏曲/Opera 相关 model/schema/api

| 文件 | 关键字段 | 行号 |
|------|----------|------|
| `backend/app/models/resource.py` | `genre VARCHAR(100)` 流派字段、`era VARCHAR(100)` 年代字段、`region_code VARCHAR(32)` 地域字段 | L21-23 |
| `backend/app/schemas/resource.py` | `ResourceCreate/ResourceRead/ResourceUpdate` 均含 genre/era/region_code | 待确认具体行号 |
| `frontend/src/api/resource.ts` | `genre?: string` | L36 |
| `frontend/src/views/ResourceSubmitView.vue` | genre 输入框 `placeholder="例如：莆仙戏"` | L45 |
| `frontend/src/views/ResourceDetailView.vue` | `<p><strong>流派：</strong>{{ resource?.genre || "未填写" }}</p>` | L22 |
| `backend/app/services/ai_service.py` | 关键词候选池含 `"京剧","豫剧","昆曲","评弹","皮影","非遗","传承","戏曲","曲艺","文化"` | L96 |

**当前状态**：没有独立的"戏曲类型"实体模型，戏曲通过资源的 `genre` 字段分类。AI 服务有戏曲相关关键词池。

---

## 4. 前端路由（frontend/src/router/index.ts）

完整路由清单：

| 路径 | name | 组件 | 权限 |
|------|------|------|------|
| `/login` | login | LoginView | 无 |
| `/register` | register | RegisterView | 无 |
| `/` (LayoutShell) | — | LayoutShell | — |
| `/ ` (空) | dashboard | DashboardView | requiresAuth |
| `/resources` | resources | ResourceListView | requiresAuth |
| `/resources/create` | resource-create | ResourceSubmitView | requiresAuth |
| `/resources/:id` | resource-detail | ResourceDetailView | requiresAuth |
| `/interaction` | interaction | InteractionView | requiresAuth |
| `/activities` | activities | ActivityCenterView | requiresAuth |
| `/audits` | audit | AuditLogView | requiresAuth + requiresAdmin |
| `/admin/review` | admin-review | AdminReviewView | requiresAuth + requiresAdmin |
| `/admin/analytics` | admin-analytics | AdminContentAnalyticsView | requiresAuth + requiresAdmin |
| `/admin/practitioners` | admin-practitioners | AdminPractitionersView | requiresAuth + requiresAdmin |
| `/admin/products` | admin-products | AdminProductsView | requiresAuth + requiresAdmin |
| `/admin/orders` | admin-orders | AdminOrdersView | requiresAuth + requiresAdmin |
| `/admin/users` | admin-users | AdminUsersView | requiresAuth + requiresAdmin |
| `/profile` | profile | ProfileView | requiresAuth |
| `/practitioner/verify` | practitioner-verify | PractitionerVerifyView | requiresAuth |
| `/my/resources` | my-resources | MyResourcesView | requiresAuth |
| `/activities/explore` | activities-explore | ActivitiesExploreView | requiresAuth |
| `/activities/me` | my-enrollments | MyEnrollmentsView | requiresAuth |
| `/topics/hot` | hot-topics | HotTopicsView | requiresAuth |
| `/wiki` | wiki | WikiView | requiresAuth |
| `/shop` | shop | ShopView | requiresAuth |

共 **24 条路由**（含布局壳）。

---

## 5. 前端 views/ 目录所有视图

| 文件名 | 功能描述 |
|--------|----------|
| `ActivitiesExploreView.vue` | 活动探索浏览（公开列表） |
| `ActivityCenterView.vue` | 活动中心（创建、管理活动，含报名管理） |
| `AdminContentAnalyticsView.vue` | 管理员内容分析看板（统计数据） |
| `AdminOrdersView.vue` | 管理员积分商城订单管理 |
| `AdminPractitionersView.vue` | 管理员从业者认证审核 |
| `AdminProductsView.vue` | 管理员商品管理 |
| `AdminReviewView.vue` | 管理员内容审核（资源/帖子/评论） |
| `AdminUsersView.vue` | 管理员用户管理 |
| `AuditLogView.vue` | 审计日志查看 |
| `DashboardView.vue` | 主仪表盘（含推荐资源、通知等） |
| `HotTopicsView.vue` | 热门话题浏览 |
| `InteractionView.vue` | 社区互动（帖子发布/评论） |
| `LayoutShell.vue` | 应用布局壳（顶部导航、侧边栏、路由出口） |
| `LoginView.vue` | 登录页 |
| `MyEnrollmentsView.vue` | 我的活动报名记录 |
| `MyResourcesView.vue` | 我提交的资源列表 |
| `PractitionerVerifyView.vue` | 从业者认证申请提交 |
| `ProfileView.vue` | 个人资料查看与编辑 |
| `RegisterView.vue` | 注册页 |
| `ResourceDetailView.vue` | 资源详情页（含地理轨迹、流派等元数据） |
| `ResourceListView.vue` | 资源列表浏览与搜索 |
| `ResourceSubmitView.vue` | 资源提交表单（含 video/image/document/audio 类型） |
| `ShopView.vue` | 积分商城（商品列表、兑换） |
| `WikiView.vue` | 戏曲百科库（词条检索、分类筛选、详情展示） |

共 **24 个视图文件**。

---

## 6. 前端 store/ 目录

| 文件 | 内容 |
|------|------|
| `frontend/src/store/auth.ts` | **唯一状态文件**。Pinia store，状态：token/user/loading/error/isAuthenticated；方法：login()/logout()/loadProfile()。token 持久化至 localStorage。 |

---

## 7. 后端 models/ 目录所有数据模型

| 文件 | 模型类 | 表名 |
|------|--------|------|
| `activity.py` | Activity、ActivityEnrollment | activities、activity_enrollments |
| `audit.py` | AuditLog | audit_logs |
| `notice.py` | Notice | notices |
| `post.py` | Post、Comment、Reaction | posts、comments、reactions |
| `practitioner.py` | PractitionerApplication | practitioner_applications |
| `product.py` | Product、Order、UserPoint | products、orders、user_points |
| `quiz.py` | QuizQuestion、QuizUserAnswer | quiz_questions、quiz_user_answers |
| `resource.py` | Resource、ResourceGeoTrail | resources、resource_geo_trails |
| `user.py` | User | users |
| `wiki.py` | WikiEntry | wiki_entries |

共 **10 文件、16 个模型类**。

---

## 8. 后端 api/routes/ 所有端点

| 文件 | prefix | 主要端点 |
|------|--------|----------|
| `activities.py` | /api/activities | 活动 CRUD、报名管理 |
| `ai.py` | /api/ai | POST /synopsis（AI生成简介+标签） |
| `audits.py` | /api/audits | 审计日志查询 |
| `auth.py` | /api/auth | 登录/注册/Token刷新 |
| `export.py` | /api/export | 数据导出（CSV/Excel） |
| `health.py` | /api/health | 健康检查 |
| `posts.py` | /api/posts | 帖子/评论/反应 CRUD |
| `practitioners.py` | /api/practitioners | 从业者认证申请与审核 |
| `quiz.py` | /api/quiz | 每日问答题目与答题 |
| `recommendations.py` | /api/recommendations | GET / 个性化推荐资源 |
| `resources.py` | /api/resources | 资源 CRUD + 摘要统计 |
| `shop.py` | /api/shop | 商品列表、积分兑换、订单管理 |
| `stats.py` | /api/stats | GET /dashboard 统计看板 |
| `users.py` | /api/users | 用户管理（管理员） |
| `wiki.py` | /api/wiki | GET /entries + GET /entries/{id} |

共 **15 个路由文件**，wiki 仅有只读接口。

---

## 9. SQL 中百科/视频/周报相关表结构

### 百科表（wiki_entries）

```sql
-- database.sql L272-288 / database_mysql.sql L259-273
CREATE TABLE IF NOT EXISTS wiki_entries (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    title        VARCHAR(200) NOT NULL,   -- 标题，有索引
    content      TEXT NOT NULL,           -- 词条正文（Markdown）
    category     VARCHAR(50),             -- 分类：genre/figure/term 等，有索引
    status       VARCHAR(20) DEFAULT 'approved' NOT NULL,  -- 状态，有索引
    author_id    INTEGER,                 -- 作者（外键 users.id），有索引
    created_at   DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at   DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
);
```

### 视频 — 不存在独立表

视频作为 `resources.resource_type = 'video'` 存在，无独立表、无视频元数据扩展字段（如时长、分辨率、封面等）。

### 周报/Weekly — **不存在**

全库（database.sql、database_mysql.sql、database_postgresql.sql）搜索 weekly/report/周报/newsletter 均无匹配，推荐机制通过 `GET /api/recommendations` 接口实现（基于行为标签匹配），没有定时推送/周报生成机制。

---

<results>
<files>
- i:\CustomBuild\Client-Orders\Graduation-Project\Trace-of-Heritage\backend\app\models\wiki.py:1 — WikiEntry 百科词条 ORM 模型
- i:\CustomBuild\Client-Orders\Graduation-Project\Trace-of-Heritage\backend\app\schemas\wiki.py:1 — WikiEntryRead + WikiEntryQuery schema
- i:\CustomBuild\Client-Orders\Graduation-Project\Trace-of-Heritage\backend\app\services\wiki_service.py:1 — WikiService 查询服务（list/get）
- i:\CustomBuild\Client-Orders\Graduation-Project\Trace-of-Heritage\backend\app\api\routes\wiki.py:1 — GET /api/wiki/entries、GET /api/wiki/entries/{id}（只读，无写入端点）
- i:\CustomBuild\Client-Orders\Graduation-Project\Trace-of-Heritage\backend\app\models\resource.py:1 — Resource 文化资源模型（含 genre/era/resource_type 字段）
- i:\CustomBuild\Client-Orders\Graduation-Project\Trace-of-Heritage\backend\app\api\routes\resources.py:1 — /api/resources 完整 CRUD
- i:\CustomBuild\Client-Orders\Graduation-Project\Trace-of-Heritage\backend\app\api\routes\recommendations.py:1 — GET /api/recommendations（个性化推荐，无周报机制）
- i:\CustomBuild\Client-Orders\Graduation-Project\Trace-of-Heritage\backend\app\core\config.py:38 — media_root 文件存储配置（无专用视频流处理）
- i:\CustomBuild\Client-Orders\Graduation-Project\Trace-of-Heritage\backend\app\main.py:1 — 所有路由注册入口
- i:\CustomBuild\Client-Orders\Graduation-Project\Trace-of-Heritage\frontend\src\router\index.ts:1 — 全部 24 条前端路由定义
- i:\CustomBuild\Client-Orders\Graduation-Project\Trace-of-Heritage\frontend\src\views\WikiView.vue:1 — 戏曲百科库前端页面
- i:\CustomBuild\Client-Orders\Graduation-Project\Trace-of-Heritage\frontend\src\store\auth.ts:1 — 唯一 Pinia store（认证状态）
- i:\CustomBuild\Client-Orders\Graduation-Project\Trace-of-Heritage\database.sql:272 — wiki_entries 建表语句（SQLite 版）
- i:\CustomBuild\Client-Orders\Graduation-Project\Trace-of-Heritage\database_mysql.sql:259 — wiki_entries 建表语句（MySQL 版）
</files>

<answer>
百科模块：完整实现（model/schema/service/API/前端页面/SQL），但仅有只读端点，无写入/编辑接口，词条需通过 seed 或直接入库。
视频模块：不存在独立视频功能，视频作为资源 resource_type="video" 存在，无播放器/视频流/时长等专用字段。
戏曲/Opera：无独立实体，通过 resources.genre 字段区分，AI服务含戏曲关键词池。
推荐/周报：有实时推荐接口（/api/recommendations），无周报/定时推送/newsletter机制，全库无相关表。
</answer>

<confidence>
high — 所有关键文件均已直接读取验证，SQL全库搜索覆盖 weekly/report/周报/newsletter，无遗漏。
</confidence>
</results>
