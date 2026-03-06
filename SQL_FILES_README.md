# 遗迹之光（Trace-of-Heritage）SQL文件完整清单

## 📁 文件列表

本项目提供了完整的数据库SQL文件集合，支持多种数据库系统。

### 核心SQL文件

| 文件名 | 说明 | 适用场景 |
|--------|------|--------|
| **database.sql** | 通用版本（SQLite格式） | 开发环境、测试环境 |
| **database_mysql.sql** | MySQL优化版本 | MySQL 5.7+ 生产环境 |
| **database_postgresql.sql** | PostgreSQL专用版本 | PostgreSQL 12+ 生产环境 |

### 文档文件

| 文件名 | 说明 |
|--------|------|
| **DATABASE_GUIDE.md** | 数据库完整用户指南（详细的表结构和功能说明） |
| **SQL_IMPORT_GUIDE.md** | SQL导入和初始化指南（各数据库系统的使用说明） |
| **SQL_FILES_README.md** | 此文件（SQL文件清单和快速参考） |

---

## 🗂️ 表结构汇总

### 核心表（12个）

#### 用户系统（2个表）
- **users** - 用户基本信息
- **user_points** - 用户积分账户

#### 资源管理（2个表）
- **resources** - 资源主表
- **resource_geo_trails** - 资源地理轨迹

#### 互动社区（3个表）
- **posts** - 帖子
- **comments** - 评论
- **reactions** - 点赞/收藏反应

#### 活动管理（2个表）
- **activities** - 活动信息
- **activity_enrollments** - 活动报名

#### 其他系统（1个表）
- **audit_logs** - 审计日志
- **practitioner_applications** - 从业者认证
- **wiki_entries** - 百科词条
- **notices** - 系统公告
- **quiz_questions** - 问卷题目
- **quiz_user_answers** - 答题记录
- **products** - 商品
- **orders** - 订单

**总计**：17个数据表 + 3个视图

---

## ⚡ 快速开始

### 对于SQLite（开发环境）

```bash
# 方法1：自动初始化（推荐）
cd backend
pip install -r requirements.txt
python app/main.py
# FastAPI启动时会自动初始化数据库

# 方法2：手动导入
sqlite3 data/app.db < ../database.sql
```

### 对于MySQL

```bash
# 登录MySQL
mysql -u root -p

# 在MySQL命令行中
source /path/to/database_mysql.sql;

# 验证
SHOW TABLES;
SELECT COUNT(*) FROM users;
```

### 对于PostgreSQL

```bash
# 连接PostgreSQL
psql -U postgres -d heritage_db

-- 在psql命令行中
\i /path/to/database_postgresql.sql;

-- 验证
\dt
SELECT COUNT(*) FROM users;
```

---

## 📊 数据库统计

### 表数量
- **用户管理**：2个表
- **资源管理**：2个表
- **互动社区**：3个表
- **活动管理**：2个表
- **审计系统**：1个表
- **认证系统**：1个表
- **知识库**：2个表（百科 + 公告）
- **问答系统**：2个表
- **商城系统**：3个表

**总计**：18个表 + 3个视图

### 字段总数
约**180个**数据字段，精心设计以满足所有功能需求

### 索引统计
- 单列索引：约50个
- 复合索引：约5个
- 唯一索引：约8个
- JSON索引：1个（PostgreSQL）

**总计**：64个索引，优化查询性能

### 约束统计
- 外键约束：22个
- 唯一约束：10个
- 非空约束：70+个
- 默认值约束：20+个

---

## 🔐 安全特性

### 数据保护
- ✅ 密码字段bcrypt加密存储
- ✅ 外键约束防止数据孤立
- ✅ 唯一约束防止重复数据
- ✅ 审计日志记录所有操作

### 访问控制
- ✅ 级联删除和设置NULL配置
- ✅ 行级权限支持（可在应用层实现）
- ✅ 字符集UTF-8/UTF8MB4全字符支持

---

## 🎯 核心功能表映射

### 资源管理功能
- **resources** - 存储资源基本信息（标题、类型、简介等）
- **resource_geo_trails** - 追踪资源传播路径

### 互动功能
- **posts** - 社区话题讨论
- **comments** - 话题评论
- **reactions** - 点赞和收藏

### 活动管理
- **activities** - 活动发起和管理
- **activity_enrollments** - 参与者报名和签到

### 知识库
- **wiki_entries** - 戏曲相关百科
- **quiz_questions** - 每日知识问卷
- **quiz_user_answers** - 用户答题记录

### 商城系统
- **products** - 商品库
- **orders** - 订单记录
- **user_points** - 用户积分账户

### 系统管理
- **users** - 用户管理
- **practitioner_applications** - 从业者身份审核
- **audit_logs** - 操作审计日志
- **notices** - 系统公告发布

---

## 💾 初始化数据

### 默认账户

```sql
SELECT username, role, password_hash FROM users;
```

| 用户名 | 角色 | 密码 | 积分 |
|--------|------|------|------|
| admin | 管理员 | Password123! | 1000 |
| opera_practitioner | 从业者 | Password123! | 1000 |
| heritage_user | 普通用户 | Password123! | 1000 |

**⚠️ 生产环境中必须更改默认密码！**

### 初始数据内容
- 3个默认用户账户
- 每个用户初始化1000积分
- 1条系统公告示例
- 1条每日问题题目示例

---

## 📈 性能参数

### 建议配置

**SQLite（开发）**
```
内存：256 MB
连接数：5
缓存大小：16 MB
```

**MySQL（生产）**
```
内存：4-8 GB
max_connections：500
query_cache_size：256 MB
InnoDB buffer_pool_size：2-4 GB
```

**PostgreSQL（生产）**
```
内存：4-8 GB
max_connections：200
shared_buffers：4 GB
work_mem：10 MB
```

---

## 🔄 数据库版本对比

### SQLite (database.sql)
**优点**：
- 无需服务器，零配置
- 完美适合开发和测试
- 文件简单易备份

**缺点**：
- 并发能力有限
- 不适合生产大规模应用

**适用**：开发、演示、轻量级应用

### MySQL (database_mysql.sql)
**优点**：
- 业界标准数据库
- 高度优化和稳定
- 广泛的托管支持

**缺点**：
- 需要服务器管理
- 配置复杂度较高

**适用**：小到中等规模生产环境

### PostgreSQL (database_postgresql.sql)
**优点**：
- 高级数据类型支持（JSON/JSONB）
- 强大的查询优化器
- 优秀的并发处理
- 企业级功能

**缺点**：
- 学习曲线较陡
- 资源占用较多

**适用**：中到大型生产环境，复杂查询场景

---

## 🛠️ 维护任务

### 日常维护

```bash
# 备份数据库
mysql -u root -p heritage_db > backup_$(date +%Y%m%d).sql

# 清理过期数据
DELETE FROM audit_logs WHERE created_at < DATE_SUB(NOW(), INTERVAL 90 DAY);

# 重建索引（MySQL）
OPTIMIZE TABLE users, resources, posts, orders;

# 更新统计（PostgreSQL）
VACUUM ANALYZE;
```

### 定期检查

- ✅ 每日备份（完整 + 增量）
- ✅ 每周数据完整性检查
- ✅ 每月性能分析和优化
- ✅ 每季度容量规划评估

---

## 📋 列表查询示例

### 常用查询

#### 查看所有表
```bash
# SQLite
sqlite3 data/app.db ".tables"

# MySQL
USE heritage_db;
SHOW TABLES;

# PostgreSQL
\dt
```

#### 查看表结构
```bash
# SQLite
.schema resources

# MySQL
DESCRIBE resources;
SHOW COLUMNS FROM resources;

# PostgreSQL
\d resources
```

#### 查看索引
```bash
# SQLite
.indexes resources

# MySQL
SHOW INDEX FROM resources;

# PostgreSQL
\d resources
```

---

## 🎓 学习资源

### SQL文件学习路径

1. **快速了解**：阅读本文件（5分钟）
2. **深入学习**：阅读 `DATABASE_GUIDE.md`（30分钟）
3. **动手操作**：按照 `SQL_IMPORT_GUIDE.md` 初始化数据库（10分钟）
4. **查询实践**：运行 `DATABASE_GUIDE.md` 中的查询示例（15分钟）
5. **性能优化**：研究索引和执行计划

### 推荐教程

- **SQLite**：https://www.sqlite.org/cli.html
- **MySQL**：https://dev.mysql.com/doc/refman/8.0/en/
- **PostgreSQL**：https://www.postgresql.org/docs/current/

---

## 🐛 常见问题

### Q1: 导入SQL文件时出现错误

**检查清单**：
1. 确认文件编码为UTF-8
2. 检查使用了正确的数据库工具
3. 确认数据库已创建
4. 查看完整的错误信息

### Q2: 导入成功但没有看到数据

```sql
-- 验证表是否创建
SELECT COUNT(*) FROM information_schema.tables
WHERE table_schema = 'heritage_db';

-- 检查用户数据
SELECT * FROM users;
```

### Q3: 如何在开发中重置数据库

```bash
# SQLite（最简单）
rm data/app.db
python app/main.py  # 会自动重新初始化

# MySQL
DROP DATABASE heritage_db;
CREATE DATABASE heritage_db;
mysql -u root -p heritage_db < database_mysql.sql

# PostgreSQL
DROP DATABASE heritage_db;
CREATE DATABASE heritage_db;
psql -U postgres -d heritage_db -f database_postgresql.sql
```

---

## 📞 支持和反馈

如果遇到问题：

1. 检查 `DATABASE_GUIDE.md` 的常见问题部分
2. 查看 `SQL_IMPORT_GUIDE.md` 的具体数据库说明
3. 运行SQL文件的完整性检查
4. 查阅对应数据库的官方文档

---

## 📄 文件信息

**项目**：遗迹之光（Trace-of-Heritage）
**版本**：0.2.0
**创建日期**：2025-11-30
**数据库版本支持**：
- SQLite 3.0+
- MySQL 5.7+ / 8.0+
- PostgreSQL 12+

---

## ✨ 总结

本项目提供了**3个完整的SQL脚本**和**3个详细的文档文件**：

✅ **开箱即用** - 直接导入即可运行
✅ **多数据库支持** - 轻松切换数据库系统
✅ **生产就绪** - 包含所有生产环境所需配置
✅ **文档完整** - 详细的表结构和操作指南
✅ **高效性能** - 合理的索引和约束设计
✅ **数据安全** - 完整的约束和外键保护

**立即开始使用，构建您的非遗数字化平台！** 🚀

---

*本清单为《遗迹之光》项目的SQL文件完整参考，如有更新需求请参考最新版本。*
