-- ============================================================================
-- 遗迹之光（Trace-of-Heritage）完整数据库DDL脚本
-- ============================================================================
-- 项目名称：遗迹之光 - 非遗/戏曲数字化平台
-- 版本：0.2.0
-- 创建时间：2025-11-30
-- 说明：包含所有表结构、索引、约束和初始化数据
-- 数据库类型：兼容SQLite/MySQL/PostgreSQL
-- ============================================================================


-- ============================================================================
-- 第一部分：用户模块表
-- ============================================================================

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    nickname VARCHAR(100),
    avatar VARCHAR(255),
    bio VARCHAR(500),
    role VARCHAR(20) DEFAULT 'user' NOT NULL,
    status VARCHAR(20) DEFAULT 'active' NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 创建用户表索引
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_created_at ON users(created_at);


-- ============================================================================
-- 第二部分：资源管理模块表
-- ============================================================================

-- 创建资源表
CREATE TABLE IF NOT EXISTS resources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(120) NOT NULL,
    resource_type VARCHAR(20),
    file_path VARCHAR(255),
    external_url VARCHAR(255),
    synopsis TEXT,
    tags TEXT DEFAULT '[]',
    era VARCHAR(100),
    genre VARCHAR(100),
    region_code VARCHAR(32),
    author VARCHAR(120),
    copyright_status VARCHAR(20) DEFAULT 'unknown',
    status VARCHAR(20) DEFAULT 'draft' NOT NULL,
    submitter_id INTEGER NOT NULL,
    reviewer_id INTEGER,
    review_note TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (submitter_id) REFERENCES users(id),
    FOREIGN KEY (reviewer_id) REFERENCES users(id)
);

-- 创建资源表索引
CREATE INDEX idx_resources_submitter_id ON resources(submitter_id);
CREATE INDEX idx_resources_reviewer_id ON resources(reviewer_id);
CREATE INDEX idx_resources_status ON resources(status);
CREATE INDEX idx_resources_genre ON resources(genre);
CREATE INDEX idx_resources_era ON resources(era);
CREATE INDEX idx_resources_region_code ON resources(region_code);
CREATE INDEX idx_resources_created_at ON resources(created_at);


-- 创建资源地理轨迹表
CREATE TABLE IF NOT EXISTS resource_geo_trails (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resource_id INTEGER NOT NULL,
    place_name VARCHAR(120) NOT NULL,
    region_code VARCHAR(32),
    longitude REAL NOT NULL,
    latitude REAL NOT NULL,
    occurred_at DATETIME,
    order_no INTEGER NOT NULL,
    FOREIGN KEY (resource_id) REFERENCES resources(id) ON DELETE CASCADE,
    UNIQUE(resource_id, order_no)
);

-- 创建资源地理轨迹索引
CREATE INDEX idx_geo_trails_resource_id ON resource_geo_trails(resource_id);
CREATE INDEX idx_geo_trails_region_code ON resource_geo_trails(region_code);


-- ============================================================================
-- 第三部分：互动模块表（帖子、评论、反应）
-- ============================================================================

-- 创建帖子表
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id INTEGER NOT NULL,
    title VARCHAR(120) NOT NULL,
    content_md TEXT NOT NULL,
    topic VARCHAR(120),
    status VARCHAR(20) DEFAULT 'pending' NOT NULL,
    reviewer_id INTEGER,
    review_note TEXT,
    like_count INTEGER DEFAULT 0 NOT NULL,
    favorite_count INTEGER DEFAULT 0 NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (author_id) REFERENCES users(id),
    FOREIGN KEY (reviewer_id) REFERENCES users(id)
);

-- 创建帖子表索引
CREATE INDEX idx_posts_author_id ON posts(author_id);
CREATE INDEX idx_posts_reviewer_id ON posts(reviewer_id);
CREATE INDEX idx_posts_status ON posts(status);
CREATE INDEX idx_posts_topic ON posts(topic);
CREATE INDEX idx_posts_created_at ON posts(created_at);


-- 创建评论表
CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    author_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' NOT NULL,
    reviewer_id INTEGER,
    review_note TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES users(id),
    FOREIGN KEY (reviewer_id) REFERENCES users(id)
);

-- 创建评论表索引
CREATE INDEX idx_comments_post_id ON comments(post_id);
CREATE INDEX idx_comments_author_id ON comments(author_id);
CREATE INDEX idx_comments_reviewer_id ON comments(reviewer_id);
CREATE INDEX idx_comments_status ON comments(status);
CREATE INDEX idx_comments_created_at ON comments(created_at);


-- 创建反应表（点赞、收藏）
CREATE TABLE IF NOT EXISTS reactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    target_type VARCHAR(20) NOT NULL,
    target_id INTEGER NOT NULL,
    reaction_type VARCHAR(20) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(target_type, target_id, user_id, reaction_type)
);

-- 创建反应表索引
CREATE INDEX idx_reactions_user_id ON reactions(user_id);
CREATE INDEX idx_reactions_target ON reactions(target_type, target_id);
CREATE INDEX idx_reactions_type ON reactions(reaction_type);


-- ============================================================================
-- 第四部分：活动管理模块表
-- ============================================================================

-- 创建活动表
CREATE TABLE IF NOT EXISTS activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(120) NOT NULL,
    description TEXT NOT NULL,
    location VARCHAR(255) NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    quota INTEGER,
    status VARCHAR(20) DEFAULT 'pending' NOT NULL,
    creator_id INTEGER NOT NULL,
    reviewer_id INTEGER,
    review_note TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (creator_id) REFERENCES users(id),
    FOREIGN KEY (reviewer_id) REFERENCES users(id)
);

-- 创建活动表索引
CREATE INDEX idx_activities_creator_id ON activities(creator_id);
CREATE INDEX idx_activities_reviewer_id ON activities(reviewer_id);
CREATE INDEX idx_activities_status ON activities(status);
CREATE INDEX idx_activities_start_time ON activities(start_time);
CREATE INDEX idx_activities_created_at ON activities(created_at);


-- 创建活动报名表
CREATE TABLE IF NOT EXISTS activity_enrollments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    activity_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'applied' NOT NULL,
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    checked_in_at DATETIME,
    FOREIGN KEY (activity_id) REFERENCES activities(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(activity_id, user_id)
);

-- 创建活动报名表索引
CREATE INDEX idx_enrollments_activity_id ON activity_enrollments(activity_id);
CREATE INDEX idx_enrollments_user_id ON activity_enrollments(user_id);
CREATE INDEX idx_enrollments_status ON activity_enrollments(status);


-- ============================================================================
-- 第五部分：审计日志模块表
-- ============================================================================

-- 创建审计日志表
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    actor_id INTEGER NOT NULL,
    action VARCHAR(64) NOT NULL,
    target_type VARCHAR(64) NOT NULL,
    target_id VARCHAR(64) NOT NULL,
    note TEXT,
    ip VARCHAR(45),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (actor_id) REFERENCES users(id)
);

-- 创建审计日志索引
CREATE INDEX idx_audits_actor_id ON audit_logs(actor_id);
CREATE INDEX idx_audits_action ON audit_logs(action);
CREATE INDEX idx_audits_target ON audit_logs(target_type, target_id);
CREATE INDEX idx_audits_created_at ON audit_logs(created_at);


-- ============================================================================
-- 第六部分：从业者认证模块表
-- ============================================================================

-- 创建从业者认证申请表
CREATE TABLE IF NOT EXISTS practitioner_applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    realname VARCHAR(100) NOT NULL,
    title VARCHAR(120) NOT NULL,
    bio VARCHAR(1000),
    attachment VARCHAR(500),
    status VARCHAR(20) DEFAULT 'pending' NOT NULL,
    applicant_id INTEGER NOT NULL,
    reviewer_id INTEGER,
    review_note VARCHAR(500),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (applicant_id) REFERENCES users(id),
    FOREIGN KEY (reviewer_id) REFERENCES users(id)
);

-- 创建从业者认证表索引
CREATE INDEX idx_practitioners_applicant_id ON practitioner_applications(applicant_id);
CREATE INDEX idx_practitioners_reviewer_id ON practitioner_applications(reviewer_id);
CREATE INDEX idx_practitioners_status ON practitioner_applications(status);
CREATE INDEX idx_practitioners_created_at ON practitioner_applications(created_at);


-- ============================================================================
-- 第七部分：百科模块表
-- ============================================================================

-- 创建百科词条表
CREATE TABLE IF NOT EXISTS wiki_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(50),
    status VARCHAR(20) DEFAULT 'approved' NOT NULL,
    author_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (author_id) REFERENCES users(id)
);

-- 创建百科表索引
CREATE INDEX idx_wiki_title ON wiki_entries(title);
CREATE INDEX idx_wiki_category ON wiki_entries(category);
CREATE INDEX idx_wiki_status ON wiki_entries(status);
CREATE INDEX idx_wiki_author_id ON wiki_entries(author_id);


-- ============================================================================
-- 第八部分：系统公告模块表
-- ============================================================================

-- 创建系统公告表
CREATE TABLE IF NOT EXISTS notices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(120) NOT NULL,
    content TEXT NOT NULL,
    audience VARCHAR(20) DEFAULT 'all' NOT NULL,
    status VARCHAR(20) DEFAULT 'draft' NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    published_at DATETIME
);

-- 创建公告表索引
CREATE INDEX idx_notices_status ON notices(status);
CREATE INDEX idx_notices_created_at ON notices(created_at);
CREATE INDEX idx_notices_published_at ON notices(published_at);


-- ============================================================================
-- 第九部分：每日问答模块表
-- ============================================================================

-- 创建问卷题目表
CREATE TABLE IF NOT EXISTS quiz_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(255) NOT NULL,
    options VARCHAR(1000) NOT NULL,
    correct_option VARCHAR(10) NOT NULL,
    active_date DATE NOT NULL UNIQUE,
    points_reward INTEGER DEFAULT 5 NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 创建问卷题目索引
CREATE INDEX idx_quiz_questions_active_date ON quiz_questions(active_date);
CREATE INDEX idx_quiz_questions_created_at ON quiz_questions(created_at);


-- 创建用户问卷答案表
CREATE TABLE IF NOT EXISTS quiz_user_answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    selected_option VARCHAR(10) NOT NULL,
    is_correct BOOLEAN DEFAULT FALSE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (question_id) REFERENCES quiz_questions(id),
    UNIQUE(user_id, question_id)
);

-- 创建用户答案表索引
CREATE INDEX idx_answers_user_id ON quiz_user_answers(user_id);
CREATE INDEX idx_answers_question_id ON quiz_user_answers(question_id);
CREATE INDEX idx_answers_is_correct ON quiz_user_answers(is_correct);
CREATE INDEX idx_answers_created_at ON quiz_user_answers(created_at);


-- ============================================================================
-- 第十部分：积分商城模块表
-- ============================================================================

-- 创建商品表
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(120) NOT NULL,
    cover VARCHAR(255),
    price DECIMAL(10, 2),
    points_price INTEGER DEFAULT 0 NOT NULL,
    stock INTEGER DEFAULT 0 NOT NULL,
    status VARCHAR(20) DEFAULT 'active' NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 创建商品表索引
CREATE INDEX idx_products_status ON products(status);
CREATE INDEX idx_products_created_at ON products(created_at);


-- 创建订单表
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER DEFAULT 1 NOT NULL,
    points_cost INTEGER DEFAULT 0 NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' NOT NULL,
    shipping_remark VARCHAR(255),
    shipped_at DATETIME,
    confirmed_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- 创建订单表索引
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_product_id ON orders(product_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at);


-- 创建用户积分表
CREATE TABLE IF NOT EXISTS user_points (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 0 NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 创建积分表索引
CREATE INDEX idx_points_updated_at ON user_points(updated_at);


-- ============================================================================
-- 第十一部分：初始化数据
-- ============================================================================

-- 插入默认管理员账户
INSERT OR IGNORE INTO users (username, password_hash, nickname, role, status, created_at, updated_at)
VALUES (
    'admin',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5YmMxSUaqzluy',
    '系统管理员',
    'admin',
    'active',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);

-- 插入默认从业者账户
INSERT OR IGNORE INTO users (username, password_hash, nickname, role, status, created_at, updated_at)
VALUES (
    'opera_practitioner',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5YmMxSUaqzluy',
    '戏曲从业者',
    'practitioner',
    'active',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);

-- 插入默认普通用户账户
INSERT OR IGNORE INTO users (username, password_hash, nickname, role, status, created_at, updated_at)
VALUES (
    'heritage_user',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5YmMxSUaqzluy',
    '文化爱好者',
    'user',
    'active',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);

-- 为每个默认用户初始化积分账户
INSERT OR IGNORE INTO user_points (user_id, balance, updated_at)
SELECT id, 1000, CURRENT_TIMESTAMP FROM users WHERE username IN ('admin', 'opera_practitioner', 'heritage_user');

-- 插入示例系统公告
INSERT OR IGNORE INTO notices (title, content, audience, status, published_at)
VALUES (
    '平台上线公告',
    '欢迎使用遗迹之光非遗数字化平台！本平台旨在为非遗文化爱好者提供分享、交流和学习的空间。',
    'all',
    'published',
    CURRENT_TIMESTAMP
);

-- 插入示例每日问答题目（可选）
INSERT OR IGNORE INTO quiz_questions (title, options, correct_option, active_date, points_reward)
VALUES (
    '下列哪个是中国传统戏曲？',
    '京剧;芭蕾舞;话剧;舞蹈',
    '京剧',
    DATE('now'),
    5
);


-- ============================================================================
-- 第十二部分：视图和存储过程（可选扩展）
-- ============================================================================

-- 创建用户统计视图（用户总数、资源总数等）
CREATE VIEW IF NOT EXISTS vw_user_statistics AS
SELECT
    u.id,
    u.username,
    u.nickname,
    COUNT(DISTINCT r.id) AS total_resources,
    COUNT(DISTINCT p.id) AS total_posts,
    COUNT(DISTINCT a.id) AS total_activities,
    COALESCE(up.balance, 0) AS points_balance
FROM users u
LEFT JOIN resources r ON u.id = r.submitter_id AND r.status = 'approved'
LEFT JOIN posts p ON u.id = p.author_id AND p.status = 'approved'
LEFT JOIN activities a ON u.id = a.creator_id AND a.status = 'approved'
LEFT JOIN user_points up ON u.id = up.user_id
GROUP BY u.id, u.username, u.nickname, up.balance;


-- 创建资源统计视图（按流派和年代统计）
CREATE VIEW IF NOT EXISTS vw_resource_statistics AS
SELECT
    genre,
    era,
    COUNT(*) AS resource_count,
    COUNT(DISTINCT submitter_id) AS contributor_count
FROM resources
WHERE status = 'approved'
GROUP BY genre, era;


-- 创建活动参与度视图
CREATE VIEW IF NOT EXISTS vw_activity_participation AS
SELECT
    a.id,
    a.title,
    COUNT(DISTINCT ae.user_id) AS total_participants,
    SUM(CASE WHEN ae.status = 'checked_in' THEN 1 ELSE 0 END) AS checked_in_count,
    a.quota,
    a.start_time
FROM activities a
LEFT JOIN activity_enrollments ae ON a.id = ae.activity_id
WHERE a.status = 'approved'
GROUP BY a.id, a.title, a.quota, a.start_time;


-- ============================================================================
-- 第十三部分：表约束和校验规则
-- ============================================================================

-- 用户角色枚举值：admin, practitioner, user
-- 用户状态枚举值：active, inactive, suspended

-- 资源类型枚举值：图片, 视频, 文档, 音频, 其他
-- 资源状态枚举值：draft, pending, approved, rejected
-- 版权状态枚举值：unknown, public_domain, copyrighted, licensed

-- 帖子状态枚举值：pending, approved, rejected
-- 评论状态枚举值：pending, approved, rejected

-- 活动状态枚举值：pending, approved, rejected
-- 报名状态枚举值：applied, checked_in, canceled

-- 从业者认证状态枚举值：pending, approved, rejected

-- 百科状态枚举值：approved, pending, rejected

-- 公告状态枚举值：draft, published
-- 公告受众枚举值：all, user, practitioner, admin

-- 订单状态枚举值：pending, shipped, completed, canceled
-- 反应类型枚举值：like, favorite
-- 反应目标类型枚举值：post, resource

-- 问卷答题状态：二元值（正确/错误）通过 is_correct 字段表示


-- ============================================================================
-- 第十四部分：数据完整性和性能优化注意事项
-- ============================================================================

/*
性能优化建议：
1. 定期分析表统计信息，帮助查询优化器制定更好的执行计划
2. 考虑分区大型表（如resources、audit_logs），按时间范围分区
3. 为频繁搜索的字段添加全文索引（title、content等）
4. 定期清理过期的审计日志和已完成的订单
5. 考虑为JSON字段（tags）创建生成的列索引

数据备份策略：
1. 每日全备份
2. 每小时增量备份
3. 保留至少30天的备份副本
4. 定期测试备份恢复流程

安全建议：
1. 所有用户输入使用参数化查询防止SQL注入
2. 密码字段永远不应在日志中出现
3. 定期审计日志，监控异常操作
4. 使用最小权限原则设置数据库用户权限
5. 启用行级安全（RLS）来限制用户数据访问范围
*/


-- ============================================================================
-- 脚本结束
-- ============================================================================
-- 说明：
-- 1. 此脚本包含完整的数据库结构定义
-- 2. 所有表都包含必要的索引以优化查询性能
-- 3. 所有外键都设置了适当的级联删除规则
-- 4. 初始化数据包括默认管理员和演示账户
-- 5. 默认密码均为 Hash 后的 "Password123!"（bcrypt处理）
-- 6. 支持SQLite、MySQL和PostgreSQL，某些方言可能需要微调
-- ============================================================================
