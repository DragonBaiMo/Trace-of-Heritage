-- ============================================================================
-- 遗迹之光（Trace-of-Heritage）PostgreSQL版本数据库DDL脚本
-- ============================================================================
-- 项目名称：遗迹之光 - 非遗/戏曲数字化平台
-- 版本：0.2.0
-- 数据库类型：PostgreSQL 12+
-- 说明：包含所有表结构、索引、约束和初始化数据
-- ============================================================================

-- ============================================================================
-- 创建数据库（可选，如果还未创建）
-- ============================================================================
/*
psql -U postgres

CREATE DATABASE heritage_db
  WITH
  ENCODING 'UTF8'
  LOCALE 'en_US.UTF-8';

\c heritage_db
*/


-- ============================================================================
-- 扩展
-- ============================================================================

-- UUID支持（可选）
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


-- ============================================================================
-- 枚举类型定义
-- ============================================================================

CREATE TYPE user_role AS ENUM ('admin', 'practitioner', 'user');
CREATE TYPE user_status AS ENUM ('active', 'inactive', 'suspended');

CREATE TYPE resource_type AS ENUM ('图片', '视频', '文档', '音频', '其他');
CREATE TYPE resource_status AS ENUM ('draft', 'pending', 'approved', 'rejected');
CREATE TYPE copyright_status AS ENUM ('unknown', 'public_domain', 'copyrighted', 'licensed');

CREATE TYPE post_status AS ENUM ('pending', 'approved', 'rejected');
CREATE TYPE comment_status AS ENUM ('pending', 'approved', 'rejected');

CREATE TYPE activity_status AS ENUM ('pending', 'approved', 'rejected');
CREATE TYPE enrollment_status AS ENUM ('applied', 'checked_in', 'canceled');

CREATE TYPE practitioner_status AS ENUM ('pending', 'approved', 'rejected');
CREATE TYPE wiki_status AS ENUM ('approved', 'pending', 'rejected');
CREATE TYPE notice_status AS ENUM ('draft', 'published');
CREATE TYPE notice_audience AS ENUM ('all', 'user', 'practitioner', 'admin');

CREATE TYPE order_status AS ENUM ('pending', 'shipped', 'completed', 'canceled');
CREATE TYPE reaction_type_enum AS ENUM ('like', 'favorite');
CREATE TYPE target_type_enum AS ENUM ('post', 'resource');


-- ============================================================================
-- 用户模块表
-- ============================================================================

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  nickname VARCHAR(100),
  avatar VARCHAR(255),
  bio VARCHAR(500),
  role user_role DEFAULT 'user' NOT NULL,
  status user_status DEFAULT 'active' NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 创建用户表索引
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_created_at ON users(created_at);

-- 用户表评论
COMMENT ON TABLE users IS '用户表';
COMMENT ON COLUMN users.id IS '用户唯一标识';
COMMENT ON COLUMN users.username IS '用户名（唯一）';
COMMENT ON COLUMN users.password_hash IS '密码哈希（bcrypt加密）';
COMMENT ON COLUMN users.role IS '用户角色：admin/practitioner/user';
COMMENT ON COLUMN users.status IS '用户状态：active/inactive/suspended';


-- ============================================================================
-- 资源管理模块表
-- ============================================================================

-- 创建资源表
CREATE TABLE IF NOT EXISTS resources (
  id SERIAL PRIMARY KEY,
  title VARCHAR(120) NOT NULL,
  resource_type resource_type,
  file_path VARCHAR(255),
  external_url VARCHAR(255),
  synopsis TEXT,
  tags JSONB DEFAULT '[]'::JSONB,
  era VARCHAR(100),
  genre VARCHAR(100),
  region_code VARCHAR(32),
  author VARCHAR(120),
  copyright_status copyright_status DEFAULT 'unknown',
  status resource_status DEFAULT 'draft' NOT NULL,
  submitter_id INT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
  reviewer_id INT REFERENCES users(id) ON DELETE SET NULL,
  review_note TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 创建资源表索引
CREATE INDEX idx_resources_submitter_id ON resources(submitter_id);
CREATE INDEX idx_resources_reviewer_id ON resources(reviewer_id);
CREATE INDEX idx_resources_status ON resources(status);
CREATE INDEX idx_resources_genre ON resources(genre);
CREATE INDEX idx_resources_era ON resources(era);
CREATE INDEX idx_resources_region_code ON resources(region_code);
CREATE INDEX idx_resources_created_at ON resources(created_at);
CREATE INDEX idx_resources_tags ON resources USING GIN(tags);  -- JSON索引

COMMENT ON TABLE resources IS '资源表';


-- 创建资源地理轨迹表
CREATE TABLE IF NOT EXISTS resource_geo_trails (
  id SERIAL PRIMARY KEY,
  resource_id INT NOT NULL REFERENCES resources(id) ON DELETE CASCADE,
  place_name VARCHAR(120) NOT NULL,
  region_code VARCHAR(32),
  longitude DECIMAL(9,6) NOT NULL,
  latitude DECIMAL(8,6) NOT NULL,
  occurred_at TIMESTAMP,
  order_no INT NOT NULL,
  UNIQUE(resource_id, order_no)
);

-- 创建资源地理轨迹索引
CREATE INDEX idx_geo_trails_resource_id ON resource_geo_trails(resource_id);
CREATE INDEX idx_geo_trails_region_code ON resource_geo_trails(region_code);

COMMENT ON TABLE resource_geo_trails IS '资源地理轨迹表';


-- ============================================================================
-- 互动模块表
-- ============================================================================

-- 创建帖子表
CREATE TABLE IF NOT EXISTS posts (
  id SERIAL PRIMARY KEY,
  author_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title VARCHAR(120) NOT NULL,
  content_md TEXT NOT NULL,
  topic VARCHAR(120),
  status post_status DEFAULT 'pending' NOT NULL,
  reviewer_id INT REFERENCES users(id) ON DELETE SET NULL,
  review_note TEXT,
  like_count INT DEFAULT 0 NOT NULL,
  favorite_count INT DEFAULT 0 NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 创建帖子表索引
CREATE INDEX idx_posts_author_id ON posts(author_id);
CREATE INDEX idx_posts_reviewer_id ON posts(reviewer_id);
CREATE INDEX idx_posts_status ON posts(status);
CREATE INDEX idx_posts_topic ON posts(topic);
CREATE INDEX idx_posts_created_at ON posts(created_at);

COMMENT ON TABLE posts IS '帖子表';


-- 创建评论表
CREATE TABLE IF NOT EXISTS comments (
  id SERIAL PRIMARY KEY,
  post_id INT NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
  author_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  content TEXT NOT NULL,
  status comment_status DEFAULT 'pending' NOT NULL,
  reviewer_id INT REFERENCES users(id) ON DELETE SET NULL,
  review_note TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 创建评论表索引
CREATE INDEX idx_comments_post_id ON comments(post_id);
CREATE INDEX idx_comments_author_id ON comments(author_id);
CREATE INDEX idx_comments_reviewer_id ON comments(reviewer_id);
CREATE INDEX idx_comments_status ON comments(status);
CREATE INDEX idx_comments_created_at ON comments(created_at);

COMMENT ON TABLE comments IS '评论表';


-- 创建反应表
CREATE TABLE IF NOT EXISTS reactions (
  id SERIAL PRIMARY KEY,
  user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  target_type target_type_enum NOT NULL,
  target_id INT NOT NULL,
  reaction_type reaction_type_enum NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  UNIQUE(target_type, target_id, user_id, reaction_type)
);

-- 创建反应表索引
CREATE INDEX idx_reactions_user_id ON reactions(user_id);
CREATE INDEX idx_reactions_target ON reactions(target_type, target_id);
CREATE INDEX idx_reactions_type ON reactions(reaction_type);

COMMENT ON TABLE reactions IS '反应表（点赞、收藏）';


-- ============================================================================
-- 活动管理模块表
-- ============================================================================

-- 创建活动表
CREATE TABLE IF NOT EXISTS activities (
  id SERIAL PRIMARY KEY,
  title VARCHAR(120) NOT NULL,
  description TEXT NOT NULL,
  location VARCHAR(255) NOT NULL,
  start_time TIMESTAMP NOT NULL,
  end_time TIMESTAMP NOT NULL,
  quota INT,
  status activity_status DEFAULT 'pending' NOT NULL,
  creator_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  reviewer_id INT REFERENCES users(id) ON DELETE SET NULL,
  review_note TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 创建活动表索引
CREATE INDEX idx_activities_creator_id ON activities(creator_id);
CREATE INDEX idx_activities_reviewer_id ON activities(reviewer_id);
CREATE INDEX idx_activities_status ON activities(status);
CREATE INDEX idx_activities_start_time ON activities(start_time);
CREATE INDEX idx_activities_created_at ON activities(created_at);

COMMENT ON TABLE activities IS '活动表';


-- 创建活动报名表
CREATE TABLE IF NOT EXISTS activity_enrollments (
  id SERIAL PRIMARY KEY,
  activity_id INT NOT NULL REFERENCES activities(id) ON DELETE CASCADE,
  user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  status enrollment_status DEFAULT 'applied' NOT NULL,
  applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  checked_in_at TIMESTAMP,
  UNIQUE(activity_id, user_id)
);

-- 创建活动报名表索引
CREATE INDEX idx_enrollments_activity_id ON activity_enrollments(activity_id);
CREATE INDEX idx_enrollments_user_id ON activity_enrollments(user_id);
CREATE INDEX idx_enrollments_status ON activity_enrollments(status);

COMMENT ON TABLE activity_enrollments IS '活动报名表';


-- ============================================================================
-- 审计日志模块表
-- ============================================================================

-- 创建审计日志表
CREATE TABLE IF NOT EXISTS audit_logs (
  id SERIAL PRIMARY KEY,
  actor_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  action VARCHAR(64) NOT NULL,
  target_type VARCHAR(64) NOT NULL,
  target_id VARCHAR(64) NOT NULL,
  note TEXT,
  ip VARCHAR(45),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 创建审计日志索引
CREATE INDEX idx_audits_actor_id ON audit_logs(actor_id);
CREATE INDEX idx_audits_action ON audit_logs(action);
CREATE INDEX idx_audits_target ON audit_logs(target_type, target_id);
CREATE INDEX idx_audits_created_at ON audit_logs(created_at);

COMMENT ON TABLE audit_logs IS '审计日志表';


-- ============================================================================
-- 从业者认证模块表
-- ============================================================================

-- 创建从业者认证申请表
CREATE TABLE IF NOT EXISTS practitioner_applications (
  id SERIAL PRIMARY KEY,
  realname VARCHAR(100) NOT NULL,
  title VARCHAR(120) NOT NULL,
  bio VARCHAR(1000),
  attachment VARCHAR(500),
  status practitioner_status DEFAULT 'pending' NOT NULL,
  applicant_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  reviewer_id INT REFERENCES users(id) ON DELETE SET NULL,
  review_note VARCHAR(500),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 创建从业者认证表索引
CREATE INDEX idx_practitioners_applicant_id ON practitioner_applications(applicant_id);
CREATE INDEX idx_practitioners_reviewer_id ON practitioner_applications(reviewer_id);
CREATE INDEX idx_practitioners_status ON practitioner_applications(status);
CREATE INDEX idx_practitioners_created_at ON practitioner_applications(created_at);

COMMENT ON TABLE practitioner_applications IS '从业者认证申请表';


-- ============================================================================
-- 百科模块表
-- ============================================================================

-- 创建百科词条表
CREATE TABLE IF NOT EXISTS wiki_entries (
  id SERIAL PRIMARY KEY,
  title VARCHAR(200) NOT NULL,
  content TEXT NOT NULL,
  category VARCHAR(50),
  status wiki_status DEFAULT 'approved' NOT NULL,
  author_id INT REFERENCES users(id) ON DELETE SET NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 创建百科表索引
CREATE INDEX idx_wiki_title ON wiki_entries(title);
CREATE INDEX idx_wiki_category ON wiki_entries(category);
CREATE INDEX idx_wiki_status ON wiki_entries(status);
CREATE INDEX idx_wiki_author_id ON wiki_entries(author_id);

COMMENT ON TABLE wiki_entries IS '百科词条表';


-- ============================================================================
-- 系统公告模块表
-- ============================================================================

-- 创建系统公告表
CREATE TABLE IF NOT EXISTS notices (
  id SERIAL PRIMARY KEY,
  title VARCHAR(120) NOT NULL,
  content TEXT NOT NULL,
  audience notice_audience DEFAULT 'all' NOT NULL,
  status notice_status DEFAULT 'draft' NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  published_at TIMESTAMP
);

-- 创建公告表索引
CREATE INDEX idx_notices_status ON notices(status);
CREATE INDEX idx_notices_created_at ON notices(created_at);
CREATE INDEX idx_notices_published_at ON notices(published_at);

COMMENT ON TABLE notices IS '系统公告表';


-- ============================================================================
-- 每日问答模块表
-- ============================================================================

-- 创建问卷题目表
CREATE TABLE IF NOT EXISTS quiz_questions (
  id SERIAL PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  options VARCHAR(1000) NOT NULL,
  correct_option VARCHAR(10) NOT NULL,
  active_date DATE NOT NULL UNIQUE,
  points_reward INT DEFAULT 5 NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 创建问卷题目索引
CREATE INDEX idx_quiz_questions_active_date ON quiz_questions(active_date);
CREATE INDEX idx_quiz_questions_created_at ON quiz_questions(created_at);

COMMENT ON TABLE quiz_questions IS '问卷题目表';


-- 创建用户问卷答案表
CREATE TABLE IF NOT EXISTS quiz_user_answers (
  id SERIAL PRIMARY KEY,
  user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  question_id INT NOT NULL REFERENCES quiz_questions(id) ON DELETE CASCADE,
  selected_option VARCHAR(10) NOT NULL,
  is_correct BOOLEAN DEFAULT FALSE NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  UNIQUE(user_id, question_id)
);

-- 创建用户答案表索引
CREATE INDEX idx_answers_user_id ON quiz_user_answers(user_id);
CREATE INDEX idx_answers_question_id ON quiz_user_answers(question_id);
CREATE INDEX idx_answers_is_correct ON quiz_user_answers(is_correct);
CREATE INDEX idx_answers_created_at ON quiz_user_answers(created_at);

COMMENT ON TABLE quiz_user_answers IS '用户答题记录表';


-- ============================================================================
-- 积分商城模块表
-- ============================================================================

-- 创建商品表
CREATE TABLE IF NOT EXISTS products (
  id SERIAL PRIMARY KEY,
  title VARCHAR(120) NOT NULL,
  cover VARCHAR(255),
  price DECIMAL(10, 2),
  points_price INT DEFAULT 0 NOT NULL,
  stock INT DEFAULT 0 NOT NULL,
  status VARCHAR(20) DEFAULT 'active' NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 创建商品表索引
CREATE INDEX idx_products_status ON products(status);
CREATE INDEX idx_products_created_at ON products(created_at);

COMMENT ON TABLE products IS '商品表';


-- 创建订单表
CREATE TABLE IF NOT EXISTS orders (
  id SERIAL PRIMARY KEY,
  user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  product_id INT NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
  quantity INT DEFAULT 1 NOT NULL,
  points_cost INT DEFAULT 0 NOT NULL,
  status order_status DEFAULT 'pending' NOT NULL,
  shipping_remark VARCHAR(255),
  shipped_at TIMESTAMP,
  confirmed_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 创建订单表索引
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_product_id ON orders(product_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at);

COMMENT ON TABLE orders IS '订单表';


-- 创建用户积分表
CREATE TABLE IF NOT EXISTS user_points (
  user_id INT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  balance INT DEFAULT 0 NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 创建积分表索引
CREATE INDEX idx_points_updated_at ON user_points(updated_at);

COMMENT ON TABLE user_points IS '用户积分表';


-- ============================================================================
-- 初始化数据
-- ============================================================================

-- 插入默认管理员账户
INSERT INTO users (username, password_hash, nickname, role, status)
VALUES (
  'admin',
  '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5YmMxSUaqzluy',
  '系统管理员',
  'admin',
  'active'
) ON CONFLICT (username) DO NOTHING;

-- 插入默认从业者账户
INSERT INTO users (username, password_hash, nickname, role, status)
VALUES (
  'opera_practitioner',
  '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5YmMxSUaqzluy',
  '戏曲从业者',
  'practitioner',
  'active'
) ON CONFLICT (username) DO NOTHING;

-- 插入默认普通用户账户
INSERT INTO users (username, password_hash, nickname, role, status)
VALUES (
  'heritage_user',
  '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5YmMxSUaqzluy',
  '文化爱好者',
  'user',
  'active'
) ON CONFLICT (username) DO NOTHING;

-- 为每个默认用户初始化积分账户
INSERT INTO user_points (user_id, balance)
SELECT id, 1000 FROM users WHERE username IN ('admin', 'opera_practitioner', 'heritage_user')
ON CONFLICT (user_id) DO NOTHING;

-- 插入示例系统公告
INSERT INTO notices (title, content, audience, status, published_at)
VALUES (
  '平台上线公告',
  '欢迎使用遗迹之光非遗数字化平台！本平台旨在为非遗文化爱好者提供分享、交流和学习的空间。',
  'all',
  'published',
  CURRENT_TIMESTAMP
) ON CONFLICT DO NOTHING;

-- 插入示例每日问答题目
INSERT INTO quiz_questions (title, options, correct_option, active_date, points_reward)
VALUES (
  '下列哪个是中国传统戏曲？',
  '京剧;芭蕾舞;话剧;舞蹈',
  '京剧',
  CURRENT_DATE,
  5
) ON CONFLICT (active_date) DO NOTHING;


-- ============================================================================
-- 视图定义
-- ============================================================================

-- 创建用户统计视图
CREATE OR REPLACE VIEW vw_user_statistics AS
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


-- 创建资源统计视图
CREATE OR REPLACE VIEW vw_resource_statistics AS
SELECT
  genre,
  era,
  COUNT(*) AS resource_count,
  COUNT(DISTINCT submitter_id) AS contributor_count
FROM resources
WHERE status = 'approved'
GROUP BY genre, era;


-- 创建活动参与度视图
CREATE OR REPLACE VIEW vw_activity_participation AS
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
-- 脚本结束
-- ============================================================================
-- 说明：
-- 1. 此脚本为PostgreSQL 12+优化版本
-- 2. 使用枚举类型确保数据一致性
-- 3. 使用JSONB用于灵活的标签存储
-- 4. 所有表都设置了适当的索引和约束
-- 5. 默认密码为bcrypt加密的"Password123!"
-- ============================================================================
