# 寻戏之旅——经典戏曲文化分享互动管理系统的设计与实现（Trace-of-Heritage）数据库完整指南

## 📋 目录

1. [项目概述](#项目概述)
2. [数据库架构](#数据库架构)
3. [表结构详解](#表结构详解)
4. [初始化说明](#初始化说明)
5. [使用示例](#使用示例)
6. [维护和优化](#维护和优化)

---

## 项目概述

**项目名称**：寻戏之旅——经典戏曲文化分享互动管理系统的设计与实现（Trace-of-Heritage）
**项目类型**：非遗/戏曲数字化平台
**版本**：0.2.0
**数据库**：SQLite（开发）/ MySQL / PostgreSQL（生产）

### 核心功能

- 🎭 **资源管理**：文化资源上传、审核、地理轨迹追踪
- 💧 **水印保护**：自动给图片资源添加水印
- 🗺️ **轨迹追踪**：记录资源的地理传播路径
- 🏪 **积分商城**：用户积分兑换、商品购买、订单管理
- ❓ **每日问答**：每日戏曲知识问卷，答题得积分
- 👥 **互动社区**：帖子、评论、点赞、收藏
- 🎪 **活动管理**：活动发布、报名、签到
- 🎓 **从业者认证**：戏曲从业者身份认证申请
- 📚 **百科词条**：戏曲知识百科库
- 📊 **审计日志**：记录所有关键操作
- 🤖 **AI助手**：自动生成文化资源简介
- 📈 **统计分析**：平台数据统计和分析

---

## 数据库架构

### 数据库设计原则

- **规范化**：遵循第三范式（3NF），避免数据冗余
- **扩展性**：模块化设计，易于添加新功能
- **性能**：合理的索引设计，优化查询效率
- **完整性**：外键约束、唯一约束、非空约束确保数据质量
- **安全性**：最小权限原则，敏感数据加密存储

### 模块划分

```
用户系统         →  users, user_points
资源管理         →  resources, resource_geo_trails
互动社区         →  posts, comments, reactions
活动管理         →  activities, activity_enrollments
审计系统         →  audit_logs
认证系统         →  practitioner_applications
知识库           →  wiki_entries
公告系统         →  notices
问答系统         →  quiz_questions, quiz_user_answers
商城系统         →  products, orders
```

---

## 表结构详解

### 1. 用户管理表（users）

**用途**：存储所有用户信息

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| id | INTEGER | 用户唯一标识 | PK, AI |
| username | VARCHAR(50) | 用户名 | UNIQUE, NOT NULL |
| password_hash | VARCHAR(255) | 密码哈希（bcrypt） | NOT NULL |
| nickname | VARCHAR(100) | 昵称 | |
| avatar | VARCHAR(255) | 头像URL | |
| bio | VARCHAR(500) | 个人简介 | |
| role | VARCHAR(20) | 用户角色 | DEFAULT='user', NOT NULL |
| status | VARCHAR(20) | 用户状态 | DEFAULT='active', NOT NULL |
| created_at | DATETIME | 创建时间 | DEFAULT=NOW() |
| updated_at | DATETIME | 更新时间 | DEFAULT=NOW() |

**角色类型**：
- `admin` - 管理员，具有平台所有权限
- `practitioner` - 从业者，可发布资源、参与认证
- `user` - 普通用户，可浏览、互动、购买

**用户状态**：
- `active` - 活跃
- `inactive` - 未激活
- `suspended` - 禁用

**索引**：username, role, status, created_at

---

### 2. 资源表（resources）

**用途**：存储文化资源基本信息

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| id | INTEGER | 资源唯一标识 | PK, AI |
| title | VARCHAR(120) | 资源标题 | NOT NULL |
| resource_type | VARCHAR(20) | 资源类型 | |
| file_path | VARCHAR(255) | 本地文件路径 | |
| external_url | VARCHAR(255) | 外部链接 | |
| synopsis | TEXT | 资源简介 | |
| tags | TEXT | JSON格式标签数组 | DEFAULT='[]' |
| era | VARCHAR(100) | 年代（如：明清、民国） | |
| genre | VARCHAR(100) | 流派（如：京剧、越剧） | |
| region_code | VARCHAR(32) | 行政区划代码 | |
| author | VARCHAR(120) | 作者/传承人 | |
| copyright_status | VARCHAR(20) | 版权状态 | DEFAULT='unknown' |
| status | VARCHAR(20) | 审核状态 | DEFAULT='draft', NOT NULL |
| submitter_id | INTEGER | 提交者ID | FK(users), NOT NULL |
| reviewer_id | INTEGER | 审核者ID | FK(users) |
| review_note | TEXT | 审核意见 | |
| created_at | DATETIME | 创建时间 | DEFAULT=NOW() |
| updated_at | DATETIME | 更新时间 | DEFAULT=NOW() |

**资源类型**：图片、视频、文档、音频、其他

**资源状态流**：
```
draft (草稿) → pending (待审核) → approved (已批准) / rejected (已驳回)
```

**版权状态**：
- `unknown` - 未知
- `public_domain` - 公有领域
- `copyrighted` - 受著作权保护
- `licensed` - 许可使用

**索引**：submitter_id, reviewer_id, status, genre, era, region_code, created_at

**级联关系**：删除资源时，级联删除其地理轨迹记录

---

### 3. 资源地理轨迹表（resource_geo_trails）

**用途**：记录资源的地理传播路径

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| id | INTEGER | 轨迹点ID | PK, AI |
| resource_id | INTEGER | 关联的资源ID | FK(resources), NOT NULL |
| place_name | VARCHAR(120) | 地点名称 | NOT NULL |
| region_code | VARCHAR(32) | 行政区划代码 | |
| longitude | REAL | 经度 [-180, 180] | NOT NULL |
| latitude | REAL | 纬度 [-90, 90] | NOT NULL |
| occurred_at | DATETIME | 发生时间 | |
| order_no | INTEGER | 排序序号（保证顺序） | NOT NULL |

**约束**：(resource_id, order_no) 唯一约束，防止重复顺序

**用途示例**：
- 追踪戏曲剧目的演出地点演变历史
- 追踪非遗技艺的传承地理位置
- 形成可视化的地理路线图

---

### 4. 帖子表（posts）

**用途**：存储社区互动帖子

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| id | INTEGER | 帖子ID | PK, AI |
| author_id | INTEGER | 作者ID | FK(users), NOT NULL |
| title | VARCHAR(120) | 帖子标题 | NOT NULL |
| content_md | TEXT | Markdown格式内容 | NOT NULL |
| topic | VARCHAR(120) | 话题分类 | |
| status | VARCHAR(20) | 审核状态 | DEFAULT='pending', NOT NULL |
| reviewer_id | INTEGER | 审核者ID | FK(users) |
| review_note | TEXT | 审核意见 | |
| like_count | INTEGER | 点赞数 | DEFAULT=0, NOT NULL |
| favorite_count | INTEGER | 收藏数 | DEFAULT=0, NOT NULL |
| created_at | DATETIME | 创建时间 | DEFAULT=NOW() |
| updated_at | DATETIME | 更新时间 | DEFAULT=NOW() |

**帖子状态**：pending (待审), approved (已批准), rejected (已驳回)

**级联关系**：删除帖子时，级联删除其所有评论

---

### 5. 评论表（comments）

**用途**：存储帖子评论

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| id | INTEGER | 评论ID | PK, AI |
| post_id | INTEGER | 所属帖子ID | FK(posts), NOT NULL |
| author_id | INTEGER | 评论者ID | FK(users), NOT NULL |
| content | TEXT | 评论内容 | NOT NULL |
| status | VARCHAR(20) | 审核状态 | DEFAULT='pending', NOT NULL |
| reviewer_id | INTEGER | 审核者ID | FK(users) |
| review_note | TEXT | 审核意见 | |
| created_at | DATETIME | 创建时间 | DEFAULT=NOW() |

---

### 6. 反应表（reactions）

**用途**：记录用户对资源和帖子的点赞、收藏操作

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| id | INTEGER | 反应ID | PK, AI |
| user_id | INTEGER | 操作用户ID | FK(users), NOT NULL |
| target_type | VARCHAR(20) | 目标类型 | NOT NULL |
| target_id | INTEGER | 目标ID（资源或帖子的ID） | NOT NULL |
| reaction_type | VARCHAR(20) | 反应类型 | NOT NULL |
| created_at | DATETIME | 创建时间 | DEFAULT=NOW() |

**约束**：(target_type, target_id, user_id, reaction_type) 唯一约束，确保幂等性

**目标类型**：post (帖子), resource (资源)

**反应类型**：like (点赞), favorite (收藏)

**用途**：
- 防止重复点赞/收藏
- 便于取消操作
- 用于推荐算法

---

### 7. 活动表（activities）

**用途**：存储平台活动信息

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| id | INTEGER | 活动ID | PK, AI |
| title | VARCHAR(120) | 活动标题 | NOT NULL |
| description | TEXT | 活动说明 | NOT NULL |
| location | VARCHAR(255) | 活动地点 | NOT NULL |
| start_time | DATETIME | 开始时间 | NOT NULL |
| end_time | DATETIME | 结束时间 | NOT NULL |
| quota | INTEGER | 人数上限 | |
| status | VARCHAR(20) | 审核状态 | DEFAULT='pending', NOT NULL |
| creator_id | INTEGER | 创建者ID | FK(users), NOT NULL |
| reviewer_id | INTEGER | 审核者ID | FK(users) |
| review_note | TEXT | 审核意见 | |
| created_at | DATETIME | 创建时间 | DEFAULT=NOW() |
| updated_at | DATETIME | 更新时间 | DEFAULT=NOW() |

**活动状态流**：pending (待审) → approved (已批准) / rejected (已驳回)

---

### 8. 活动报名表（activity_enrollments）

**用途**：记录用户的活动报名和签到信息

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| id | INTEGER | 报名ID | PK, AI |
| activity_id | INTEGER | 活动ID | FK(activities), NOT NULL |
| user_id | INTEGER | 用户ID | FK(users), NOT NULL |
| status | VARCHAR(20) | 报名状态 | DEFAULT='applied', NOT NULL |
| applied_at | DATETIME | 报名时间 | DEFAULT=NOW() |
| checked_in_at | DATETIME | 签到时间 | |

**约束**：(activity_id, user_id) 唯一约束，防止重复报名

**报名状态**：applied (已报名), checked_in (已签到), canceled (已取消)

---

### 9. 审计日志表（audit_logs）

**用途**：记录所有关键操作，用于合规和问题追踪

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| id | INTEGER | 日志ID | PK, AI |
| actor_id | INTEGER | 操作者ID | FK(users), NOT NULL |
| action | VARCHAR(64) | 动作标识 | NOT NULL |
| target_type | VARCHAR(64) | 目标类型 | NOT NULL |
| target_id | VARCHAR(64) | 目标ID | NOT NULL |
| note | TEXT | 操作备注 | |
| ip | VARCHAR(45) | 客户端IP | |
| created_at | DATETIME | 操作时间 | DEFAULT=NOW() |

**常见动作**：
- `create_resource` - 创建资源
- `approve_resource` - 批准资源
- `reject_resource` - 驳回资源
- `delete_user` - 删除用户
- `change_user_role` - 改变用户角色
- `submit_post` - 发布帖子
- `approve_post` - 批准帖子

---

### 10. 从业者认证表（practitioner_applications）

**用途**：管理戏曲从业者身份认证申请

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| id | INTEGER | 申请ID | PK, AI |
| realname | VARCHAR(100) | 真实姓名 | NOT NULL |
| title | VARCHAR(120) | 职业/头衔 | NOT NULL |
| bio | VARCHAR(1000) | 个人简介 | |
| attachment | VARCHAR(500) | 证明材料链接 | |
| status | VARCHAR(20) | 申请状态 | DEFAULT='pending', NOT NULL |
| applicant_id | INTEGER | 申请者ID | FK(users), NOT NULL |
| reviewer_id | INTEGER | 审核者ID | FK(users) |
| review_note | VARCHAR(500) | 审核意见 | |
| created_at | DATETIME | 申请时间 | DEFAULT=NOW() |
| updated_at | DATETIME | 更新时间 | DEFAULT=NOW() |

**申请状态**：pending (待审), approved (已批准), rejected (已驳回)

---

### 11. 百科词条表（wiki_entries）

**用途**：存储戏曲知识百科词条

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| id | INTEGER | 词条ID | PK, AI |
| title | VARCHAR(200) | 词条标题 | NOT NULL |
| content | TEXT | 词条内容 | NOT NULL |
| category | VARCHAR(50) | 分类 | |
| status | VARCHAR(20) | 状态 | DEFAULT='approved', NOT NULL |
| author_id | INTEGER | 作者ID | FK(users) |
| created_at | DATETIME | 创建时间 | DEFAULT=NOW() |
| updated_at | DATETIME | 更新时间 | DEFAULT=NOW() |

**分类示例**：
- 京剧、越剧、黄梅戏等各剧种
- 历史背景、文化保护等主题

---

### 12. 系统公告表（notices）

**用途**：发布系统公告和重要通知

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| id | INTEGER | 公告ID | PK, AI |
| title | VARCHAR(120) | 公告标题 | NOT NULL |
| content | TEXT | 公告内容 | NOT NULL |
| audience | VARCHAR(20) | 受众群体 | DEFAULT='all', NOT NULL |
| status | VARCHAR(20) | 状态 | DEFAULT='draft', NOT NULL |
| created_at | DATETIME | 创建时间 | DEFAULT=NOW() |
| published_at | DATETIME | 发布时间 | |

**受众**：all (所有用户), user (普通用户), practitioner (从业者), admin (管理员)

**状态**：draft (草稿), published (已发布)

---

### 13. 问卷题目表（quiz_questions）

**用途**：每日戏曲知识问卷题目库

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| id | INTEGER | 题目ID | PK, AI |
| title | VARCHAR(255) | 题目内容 | NOT NULL |
| options | VARCHAR(1000) | 选项（分号分隔） | NOT NULL |
| correct_option | VARCHAR(10) | 正确答案 | NOT NULL |
| active_date | DATE | 激活日期 | UNIQUE, NOT NULL |
| points_reward | INTEGER | 答对奖励积分 | DEFAULT=5, NOT NULL |
| created_at | DATETIME | 创建时间 | DEFAULT=NOW() |

**选项格式**：`选项1;选项2;选项3;选项4`
**正确答案格式**：选项内容（如"京剧"）

---

### 14. 用户答题记录表（quiz_user_answers）

**用途**：记录用户的答题记录

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| id | INTEGER | 记录ID | PK, AI |
| user_id | INTEGER | 用户ID | FK(users), NOT NULL |
| question_id | INTEGER | 题目ID | FK(quiz_questions), NOT NULL |
| selected_option | VARCHAR(10) | 用户选择的答案 | NOT NULL |
| is_correct | BOOLEAN | 是否答对 | DEFAULT=FALSE, NOT NULL |
| created_at | DATETIME | 答题时间 | DEFAULT=NOW() |

**约束**：(user_id, question_id) 唯一约束，防止用户重复答题

---

### 15. 商品表（products）

**用途**：积分商城的商品管理

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| id | INTEGER | 商品ID | PK, AI |
| title | VARCHAR(120) | 商品标题 | NOT NULL |
| cover | VARCHAR(255) | 商品封面图 | |
| price | DECIMAL(10, 2) | 实际金额（RMB） | |
| points_price | INTEGER | 积分价格 | DEFAULT=0, NOT NULL |
| stock | INTEGER | 库存数量 | DEFAULT=0, NOT NULL |
| status | VARCHAR(20) | 状态 | DEFAULT='active', NOT NULL |
| created_at | DATETIME | 创建时间 | DEFAULT=NOW() |
| updated_at | DATETIME | 更新时间 | DEFAULT=NOW() |

**状态**：active (上架), inactive (下架)

---

### 16. 订单表（orders）

**用途**：用户购买记录和订单管理

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| id | INTEGER | 订单ID | PK, AI |
| user_id | INTEGER | 购买用户ID | FK(users), NOT NULL |
| product_id | INTEGER | 商品ID | FK(products), NOT NULL |
| quantity | INTEGER | 购买数量 | DEFAULT=1, NOT NULL |
| points_cost | INTEGER | 消耗积分 | DEFAULT=0, NOT NULL |
| status | VARCHAR(20) | 订单状态 | DEFAULT='pending', NOT NULL |
| shipping_remark | VARCHAR(255) | 发货备注/物流单号 | |
| shipped_at | DATETIME | 发货时间 | |
| confirmed_at | DATETIME | 收货时间 | |
| created_at | DATETIME | 订单时间 | DEFAULT=NOW() |

**订单状态流**：
```
pending (待发货) → shipped (已发货) → completed (已收货)
                  └→ canceled (已取消)
```

---

### 17. 用户积分表（user_points）

**用途**：维护每个用户的积分余额

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| user_id | INTEGER | 用户ID | PK, FK(users), NOT NULL |
| balance | INTEGER | 积分余额 | DEFAULT=0, NOT NULL |
| updated_at | DATETIME | 更新时间 | DEFAULT=NOW() |

**积分来源**：
- 注册时获得初始积分
- 答题成功获得奖励
- 提交资源被批准获得

**积分消耗**：
- 商城购物扣费

---

## 初始化说明

### 默认账户

脚本自动创建以下三个默认账户（用于演示和测试）：

| 用户名 | 密码 | 角色 | 说明 |
|--------|------|------|------|
| admin | Password123! | admin | 系统管理员 |
| opera_practitioner | Password123! | practitioner | 戏曲从业者演示账户 |
| heritage_user | Password123! | user | 普通用户演示账户 |

**安全提示**：生产环境中应更改这些密码！

### 初始化数据

- 3个默认用户账户
- 每个用户1000积分初始额度
- 1条系统公告示例
- 1条每日问答示例题目

---

## 使用示例

### 查询示例

#### 1. 获取用户的所有已批准资源

```sql
SELECT r.*
FROM resources r
WHERE r.submitter_id = 1 AND r.status = 'approved'
ORDER BY r.created_at DESC;
```

#### 2. 获取某个活动的参与人数和签到人数

```sql
SELECT
    a.id,
    a.title,
    COUNT(ae.id) AS total_participants,
    SUM(CASE WHEN ae.status = 'checked_in' THEN 1 ELSE 0 END) AS checked_in
FROM activities a
LEFT JOIN activity_enrollments ae ON a.id = ae.activity_id
WHERE a.id = 1
GROUP BY a.id, a.title;
```

#### 3. 获取用户的积分消费历史

```sql
SELECT
    o.id,
    p.title,
    o.quantity,
    o.points_cost,
    o.status,
    o.created_at
FROM orders o
JOIN products p ON o.product_id = p.id
WHERE o.user_id = 1
ORDER BY o.created_at DESC;
```

#### 4. 查询用户的答题记录和正确率

```sql
SELECT
    u.id,
    u.username,
    COUNT(qua.id) AS total_answers,
    SUM(CASE WHEN qua.is_correct THEN 1 ELSE 0 END) AS correct_count,
    ROUND(100.0 * SUM(CASE WHEN qua.is_correct THEN 1 ELSE 0 END) / COUNT(qua.id), 2) AS accuracy_percent
FROM users u
LEFT JOIN quiz_user_answers qua ON u.id = qua.user_id
WHERE u.id = 1
GROUP BY u.id, u.username;
```

#### 5. 获取某个资源的地理轨迹路线

```sql
SELECT
    rgt.order_no,
    rgt.place_name,
    rgt.longitude,
    rgt.latitude,
    rgt.occurred_at
FROM resource_geo_trails rgt
WHERE rgt.resource_id = 1
ORDER BY rgt.order_no ASC;
```

#### 6. 查询待审核的资源列表（按提交时间倒序）

```sql
SELECT
    r.id,
    r.title,
    u.nickname AS submitter,
    r.synopsis,
    r.genre,
    r.era,
    r.created_at
FROM resources r
JOIN users u ON r.submitter_id = u.id
WHERE r.status = 'pending'
ORDER BY r.created_at DESC;
```

#### 7. 查询用户的互动统计（发帖、评论、点赞）

```sql
SELECT
    u.id,
    u.username,
    u.nickname,
    COUNT(DISTINCT p.id) AS post_count,
    COUNT(DISTINCT c.id) AS comment_count,
    COUNT(DISTINCT r.id) AS reaction_count
FROM users u
LEFT JOIN posts p ON u.id = p.author_id
LEFT JOIN comments c ON u.id = c.author_id
LEFT JOIN reactions r ON u.id = r.user_id
GROUP BY u.id, u.username, u.nickname;
```

#### 8. 查询平台的按流派分类的资源统计

```sql
SELECT
    genre,
    COUNT(*) AS resource_count,
    COUNT(DISTINCT submitter_id) AS contributor_count
FROM resources
WHERE status = 'approved'
GROUP BY genre
ORDER BY resource_count DESC;
```

### 更新示例

#### 1. 审核通过资源

```sql
UPDATE resources
SET status = 'approved',
    reviewer_id = 1,
    review_note = '资源完整，质量良好',
    updated_at = CURRENT_TIMESTAMP
WHERE id = 1;
```

#### 2. 发货

```sql
UPDATE orders
SET status = 'shipped',
    shipping_remark = '圆通快递，单号：123456789',
    shipped_at = CURRENT_TIMESTAMP
WHERE id = 1;
```

#### 3. 更新用户积分

```sql
UPDATE user_points
SET balance = balance - 100,
    updated_at = CURRENT_TIMESTAMP
WHERE user_id = 1;
```

#### 4. 禁用用户账户

```sql
UPDATE users
SET status = 'suspended',
    updated_at = CURRENT_TIMESTAMP
WHERE id = 5;
```

---

## 维护和优化

### 定期维护任务

#### 1. 备份数据库

```bash
# SQLite备份
cp data/app.db data/app.db.backup.$(date +%Y%m%d_%H%M%S)

# MySQL备份
mysqldump -u root -p heritage_db > heritage_db.sql

# PostgreSQL备份
pg_dump heritage_db > heritage_db.sql
```

#### 2. 清理过期数据

```sql
-- 删除7天前已取消的订单
DELETE FROM orders
WHERE status = 'canceled'
  AND created_at < datetime('now', '-7 days');

-- 删除90天前的日志（可选，根据合规要求）
DELETE FROM audit_logs
WHERE created_at < datetime('now', '-90 days');
```

#### 3. 更新表统计（MySQL/PostgreSQL）

```sql
-- MySQL
ANALYZE TABLE users;
ANALYZE TABLE resources;
ANALYZE TABLE posts;

-- PostgreSQL
VACUUM ANALYZE users;
VACUUM ANALYZE resources;
VACUUM ANALYZE posts;
```

### 性能优化建议

#### 1. 查询优化

- 对频繁搜索的字段添加索引
- 使用EXPLAIN分析慢查询
- 避免在WHERE子句中使用函数

#### 2. 索引策略

```sql
-- 添加复合索引优化常见查询
CREATE INDEX idx_resources_status_created ON resources(status, created_at);
CREATE INDEX idx_posts_status_created ON posts(status, created_at);
CREATE INDEX idx_orders_user_status ON orders(user_id, status);
```

#### 3. 分页查询最佳实践

```sql
-- 使用LIMIT和OFFSET分页
SELECT * FROM resources
WHERE status = 'approved'
ORDER BY created_at DESC
LIMIT 20 OFFSET 0;
```

#### 4. 缓存策略

- 缓存热点数据（排行榜、推荐、流派列表）
- 设置合理的缓存过期时间（5-30分钟）
- 使用Redis或内存缓存

### 数据完整性检查

```sql
-- 检查孤立记录（资源表中引用的用户不存在）
SELECT r.id FROM resources r
LEFT JOIN users u ON r.submitter_id = u.id
WHERE u.id IS NULL;

-- 检查订单中的商品是否存在
SELECT o.id FROM orders o
LEFT JOIN products p ON o.product_id = p.id
WHERE p.id IS NULL;

-- 检查重复的用户答题记录
SELECT user_id, question_id, COUNT(*)
FROM quiz_user_answers
GROUP BY user_id, question_id
HAVING COUNT(*) > 1;
```

### 监控指标

定期监控以下关键指标：

1. **数据库大小**：监控数据库文件增长速度
2. **表大小**：identify最大的表，评估分区需求
3. **查询性能**：记录慢查询日志
4. **并发连接数**：确保连接池足够
5. **数据一致性**：定期验证外键和约束

---

## 常见问题

### Q1: 如何在生产环境中更改默认密码？

```sql
-- 使用Python bcrypt库生成新哈希
-- 然后执行更新
UPDATE users
SET password_hash = '[新的bcrypt哈希]'
WHERE username = 'admin';
```

### Q2: 如何处理大量数据导入？

- 使用批量插入而不是逐行插入
- 禁用外键约束临时加快导入速度
- 使用事务提高效率

### Q3: 积分如何管理？

- 建议为积分操作创建审计日志
- 使用事务保证一致性
- 定期对账验证余额正确性

### Q4: 如何导出数据进行分析？

```sql
-- 导出为CSV（支持大多数数据库）
.mode csv
.output resources.csv
SELECT * FROM resources WHERE status = 'approved';
```

---

## 安全建议

1. **SQL注入防护**：始终使用参数化查询
2. **访问控制**：使用最小权限原则设置数据库用户
3. **数据加密**：敏感信息（密码）使用加密存储
4. **审计日志**：记录所有关键操作
5. **定期备份**：每日备份，保留多个版本
6. **监控日志**：定期审查异常操作

---

## 参考资源

- **SQLite文档**：https://www.sqlite.org/docs.html
- **MySQL文档**：https://dev.mysql.com/doc/
- **PostgreSQL文档**：https://www.postgresql.org/docs/

---

*此文档为《寻戏之旅——经典戏曲文化分享互动管理系统的设计与实现》项目的数据库完整指南，如有疑问请联系开发团队。*
