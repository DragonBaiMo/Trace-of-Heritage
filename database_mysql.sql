-- ============================================================================
-- 遗迹之光（Trace-of-Heritage）MySQL版本数据库DDL脚本
-- ============================================================================
-- 项目名称：遗迹之光 - 非遗/戏曲数字化平台
-- 版本：0.2.0
-- 数据库类型：MySQL 5.7+
-- 字符集：utf8mb4 (支持emoji和特殊字符)
-- 存储引擎：InnoDB (支持事务和外键)
-- ============================================================================

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS heritage_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- 选择数据库
USE heritage_db;

-- ============================================================================
-- 用户模块表
-- ============================================================================

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  nickname VARCHAR(100),
  avatar VARCHAR(255),
  bio VARCHAR(500),
  role VARCHAR(20) DEFAULT 'user' NOT NULL,
  status VARCHAR(20) DEFAULT 'active' NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
  KEY idx_username (username),
  KEY idx_role (role),
  KEY idx_status (status),
  KEY idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';


-- ============================================================================
-- 资源管理模块表
-- ============================================================================

-- 创建资源表
CREATE TABLE IF NOT EXISTS resources (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(120) NOT NULL,
  resource_type VARCHAR(20),
  file_path VARCHAR(255),
  external_url VARCHAR(255),
  synopsis TEXT,
  tags JSON DEFAULT '[]',
  era VARCHAR(100),
  genre VARCHAR(100),
  region_code VARCHAR(32),
  author VARCHAR(120),
  copyright_status VARCHAR(20) DEFAULT 'unknown',
  status VARCHAR(20) DEFAULT 'draft' NOT NULL,
  submitter_id INT NOT NULL,
  reviewer_id INT,
  review_note TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
  KEY idx_submitter_id (submitter_id),
  KEY idx_reviewer_id (reviewer_id),
  KEY idx_status (status),
  KEY idx_genre (genre),
  KEY idx_era (era),
  KEY idx_region_code (region_code),
  KEY idx_created_at (created_at),
  CONSTRAINT fk_resources_submitter FOREIGN KEY (submitter_id) REFERENCES users(id) ON DELETE RESTRICT,
  CONSTRAINT fk_resources_reviewer FOREIGN KEY (reviewer_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='资源表';


-- 创建资源地理轨迹表
CREATE TABLE IF NOT EXISTS resource_geo_trails (
  id INT AUTO_INCREMENT PRIMARY KEY,
  resource_id INT NOT NULL,
  place_name VARCHAR(120) NOT NULL,
  region_code VARCHAR(32),
  longitude DECIMAL(9,6) NOT NULL,
  latitude DECIMAL(8,6) NOT NULL,
  occurred_at DATETIME,
  order_no INT NOT NULL,
  KEY idx_resource_id (resource_id),
  KEY idx_region_code (region_code),
  UNIQUE KEY unique_resource_order (resource_id, order_no),
  CONSTRAINT fk_geo_trails_resource FOREIGN KEY (resource_id) REFERENCES resources(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='资源地理轨迹表';


-- ============================================================================
-- 互动模块表
-- ============================================================================

-- 创建帖子表
CREATE TABLE IF NOT EXISTS posts (
  id INT AUTO_INCREMENT PRIMARY KEY,
  author_id INT NOT NULL,
  title VARCHAR(120) NOT NULL,
  content_md LONGTEXT NOT NULL,
  topic VARCHAR(120),
  status VARCHAR(20) DEFAULT 'pending' NOT NULL,
  reviewer_id INT,
  review_note TEXT,
  like_count INT DEFAULT 0 NOT NULL,
  favorite_count INT DEFAULT 0 NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
  KEY idx_author_id (author_id),
  KEY idx_reviewer_id (reviewer_id),
  KEY idx_status (status),
  KEY idx_topic (topic),
  KEY idx_created_at (created_at),
  CONSTRAINT fk_posts_author FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT fk_posts_reviewer FOREIGN KEY (reviewer_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='帖子表';


-- 创建评论表
CREATE TABLE IF NOT EXISTS comments (
  id INT AUTO_INCREMENT PRIMARY KEY,
  post_id INT NOT NULL,
  author_id INT NOT NULL,
  content TEXT NOT NULL,
  status VARCHAR(20) DEFAULT 'pending' NOT NULL,
  reviewer_id INT,
  review_note TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
  KEY idx_post_id (post_id),
  KEY idx_author_id (author_id),
  KEY idx_reviewer_id (reviewer_id),
  KEY idx_status (status),
  KEY idx_created_at (created_at),
  CONSTRAINT fk_comments_post FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
  CONSTRAINT fk_comments_author FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT fk_comments_reviewer FOREIGN KEY (reviewer_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='评论表';


-- 创建反应表
CREATE TABLE IF NOT EXISTS reactions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  target_type VARCHAR(20) NOT NULL,
  target_id INT NOT NULL,
  reaction_type VARCHAR(20) NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
  KEY idx_user_id (user_id),
  KEY idx_target (target_type, target_id),
  KEY idx_reaction_type (reaction_type),
  UNIQUE KEY unique_reaction (target_type, target_id, user_id, reaction_type),
  CONSTRAINT fk_reactions_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='反应表（点赞、收藏）';


-- ============================================================================
-- 活动管理模块表
-- ============================================================================

-- 创建活动表
CREATE TABLE IF NOT EXISTS activities (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(120) NOT NULL,
  description TEXT NOT NULL,
  location VARCHAR(255) NOT NULL,
  start_time DATETIME NOT NULL,
  end_time DATETIME NOT NULL,
  quota INT,
  status VARCHAR(20) DEFAULT 'pending' NOT NULL,
  creator_id INT NOT NULL,
  reviewer_id INT,
  review_note TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
  KEY idx_creator_id (creator_id),
  KEY idx_reviewer_id (reviewer_id),
  KEY idx_status (status),
  KEY idx_start_time (start_time),
  KEY idx_created_at (created_at),
  CONSTRAINT fk_activities_creator FOREIGN KEY (creator_id) REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT fk_activities_reviewer FOREIGN KEY (reviewer_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='活动表';


-- 创建活动报名表
CREATE TABLE IF NOT EXISTS activity_enrollments (
  id INT AUTO_INCREMENT PRIMARY KEY,
  activity_id INT NOT NULL,
  user_id INT NOT NULL,
  status VARCHAR(20) DEFAULT 'applied' NOT NULL,
  applied_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
  checked_in_at DATETIME,
  KEY idx_activity_id (activity_id),
  KEY idx_user_id (user_id),
  KEY idx_status (status),
  UNIQUE KEY unique_enrollment (activity_id, user_id),
  CONSTRAINT fk_enrollments_activity FOREIGN KEY (activity_id) REFERENCES activities(id) ON DELETE CASCADE,
  CONSTRAINT fk_enrollments_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='活动报名表';


-- ============================================================================
-- 审计日志模块表
-- ============================================================================

-- 创建审计日志表
CREATE TABLE IF NOT EXISTS audit_logs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  actor_id INT NOT NULL,
  action VARCHAR(64) NOT NULL,
  target_type VARCHAR(64) NOT NULL,
  target_id VARCHAR(64) NOT NULL,
  note TEXT,
  ip VARCHAR(45),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
  KEY idx_actor_id (actor_id),
  KEY idx_action (action),
  KEY idx_target (target_type, target_id),
  KEY idx_created_at (created_at),
  CONSTRAINT fk_audits_actor FOREIGN KEY (actor_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='审计日志表';


-- ============================================================================
-- 从业者认证模块表
-- ============================================================================

-- 创建从业者认证申请表
CREATE TABLE IF NOT EXISTS practitioner_applications (
  id INT AUTO_INCREMENT PRIMARY KEY,
  realname VARCHAR(100) NOT NULL,
  title VARCHAR(120) NOT NULL,
  bio VARCHAR(1000),
  attachment VARCHAR(500),
  status VARCHAR(20) DEFAULT 'pending' NOT NULL,
  applicant_id INT NOT NULL,
  reviewer_id INT,
  review_note VARCHAR(500),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
  KEY idx_applicant_id (applicant_id),
  KEY idx_reviewer_id (reviewer_id),
  KEY idx_status (status),
  KEY idx_created_at (created_at),
  CONSTRAINT fk_practitioners_applicant FOREIGN KEY (applicant_id) REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT fk_practitioners_reviewer FOREIGN KEY (reviewer_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='从业者认证申请表';


-- ============================================================================
-- 百科模块表
-- ============================================================================

-- 创建百科词条表
CREATE TABLE IF NOT EXISTS wiki_entries (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(200) NOT NULL,
  content LONGTEXT NOT NULL,
  category VARCHAR(50),
  status VARCHAR(20) DEFAULT 'approved' NOT NULL,
  author_id INT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
  KEY idx_title (title),
  KEY idx_category (category),
  KEY idx_status (status),
  KEY idx_author_id (author_id),
  CONSTRAINT fk_wiki_author FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='百科词条表';


-- ============================================================================
-- 系统公告模块表
-- ============================================================================

-- 创建系统公告表
CREATE TABLE IF NOT EXISTS notices (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(120) NOT NULL,
  content TEXT NOT NULL,
  audience VARCHAR(20) DEFAULT 'all' NOT NULL,
  status VARCHAR(20) DEFAULT 'draft' NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
  published_at DATETIME,
  KEY idx_status (status),
  KEY idx_created_at (created_at),
  KEY idx_published_at (published_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统公告表';


-- ============================================================================
-- 每日问答模块表
-- ============================================================================

-- 创建问卷题目表
CREATE TABLE IF NOT EXISTS quiz_questions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  options VARCHAR(1000) NOT NULL,
  correct_option VARCHAR(10) NOT NULL,
  active_date DATE NOT NULL UNIQUE,
  points_reward INT DEFAULT 5 NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
  KEY idx_active_date (active_date),
  KEY idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='问卷题目表';


-- 创建用户问卷答案表
CREATE TABLE IF NOT EXISTS quiz_user_answers (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  question_id INT NOT NULL,
  selected_option VARCHAR(10) NOT NULL,
  is_correct BOOLEAN DEFAULT FALSE NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
  KEY idx_user_id (user_id),
  KEY idx_question_id (question_id),
  KEY idx_is_correct (is_correct),
  KEY idx_created_at (created_at),
  UNIQUE KEY unique_answer (user_id, question_id),
  CONSTRAINT fk_answers_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT fk_answers_question FOREIGN KEY (question_id) REFERENCES quiz_questions(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户答题记录表';


-- ============================================================================
-- 积分商城模块表
-- ============================================================================

-- 创建商品表
CREATE TABLE IF NOT EXISTS products (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(120) NOT NULL,
  cover VARCHAR(255),
  price DECIMAL(10, 2),
  points_price INT DEFAULT 0 NOT NULL,
  stock INT DEFAULT 0 NOT NULL,
  status VARCHAR(20) DEFAULT 'active' NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
  KEY idx_status (status),
  KEY idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='商品表';


-- 创建订单表
CREATE TABLE IF NOT EXISTS orders (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  product_id INT NOT NULL,
  quantity INT DEFAULT 1 NOT NULL,
  points_cost INT DEFAULT 0 NOT NULL,
  status VARCHAR(20) DEFAULT 'pending' NOT NULL,
  shipping_remark VARCHAR(255),
  shipped_at DATETIME,
  confirmed_at DATETIME,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
  KEY idx_user_id (user_id),
  KEY idx_product_id (product_id),
  KEY idx_status (status),
  KEY idx_created_at (created_at),
  CONSTRAINT fk_orders_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT fk_orders_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='订单表';


-- 创建用户积分表
CREATE TABLE IF NOT EXISTS user_points (
  user_id INT PRIMARY KEY,
  balance INT DEFAULT 0 NOT NULL,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
  KEY idx_updated_at (updated_at),
  CONSTRAINT fk_points_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户积分表';


-- ============================================================================
-- 初始化数据
-- ============================================================================

-- 插入默认管理员账户
INSERT IGNORE INTO users (username, password_hash, nickname, role, status)
VALUES (
  'admin',
  '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5YmMxSUaqzluy',
  '系统管理员',
  'admin',
  'active'
);

-- 插入默认从业者账户
INSERT IGNORE INTO users (username, password_hash, nickname, role, status)
VALUES (
  'opera_practitioner',
  '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5YmMxSUaqzluy',
  '戏曲从业者',
  'practitioner',
  'active'
);

-- 插入默认普通用户账户
INSERT IGNORE INTO users (username, password_hash, nickname, role, status)
VALUES (
  'heritage_user',
  '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5YmMxSUaqzluy',
  '文化爱好者',
  'user',
  'active'
);

-- 为每个默认用户初始化积分账户
INSERT IGNORE INTO user_points (user_id, balance)
SELECT id, 1000 FROM users WHERE username IN ('admin', 'opera_practitioner', 'heritage_user');

-- 插入示例系统公告
INSERT IGNORE INTO notices (title, content, audience, status, published_at)
VALUES (
  '平台上线公告',
  '欢迎使用遗迹之光非遗数字化平台！本平台旨在为非遗文化爱好者提供分享、交流和学习的空间。',
  'all',
  'published',
  NOW()
);

-- 插入示例每日问答题目
INSERT IGNORE INTO quiz_questions (title, options, correct_option, active_date, points_reward)
VALUES (
  '下列哪个是中国传统戏曲？',
  '京剧;芭蕾舞;话剧;舞蹈',
  '京剧',
  CURDATE(),
  5
);


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
-- 1. 此脚本为MySQL 5.7+优化版本
-- 2. 使用InnoDB存储引擎支持事务和外键
-- 3. 使用utf8mb4字符集支持emoji和所有Unicode字符
-- 4. 所有表都设置了适当的索引和约束
-- 5. 默认密码为bcrypt加密的"Password123!"
-- ============================================================================
