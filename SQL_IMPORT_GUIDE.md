# SQL导入和数据库初始化指南

本文档说明如何在不同的数据库系统中使用提供的SQL文件。

---

## 快速开始

### 对于开发环境（SQLite）

最简单的方法——项目已集成自动初始化：

```bash
# 启动后端时会自动初始化数据库
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
python app/main.py
```

SQLAlchemy ORM会自动：
1. 创建 `data/app.db` SQLite数据库文件
2. 创建所有数据表
3. 初始化默认账户

**无需手动执行SQL脚本！**

---

## 如果需要手动初始化或重置

### 方案1: 使用SQLite命令行

#### 步骤1：打开SQLite命令行

```bash
# 进入项目backend目录
cd backend

# 打开SQLite命令行（会自动创建app.db）
sqlite3 data/app.db
```

#### 步骤2：执行SQL脚本

```sql
-- 方案A: 直接读取SQL文件（推荐）
.read ../database.sql

-- 方案B: 逐行手动复制粘贴SQL语句
-- （建议用于生产环境备份恢复）
```

#### 步骤3：验证初始化成功

```sql
-- 列出所有表
.tables

-- 查看用户表
SELECT id, username, role FROM users;

-- 查看初始积分
SELECT * FROM user_points;

-- 退出SQLite
.quit
```

---

### 方案2: 使用Python脚本初始化（推荐）

#### 创建初始化脚本 `backend/init_db.py`

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库初始化脚本
用于从SQL文件初始化数据库或重置数据库
"""

import os
import sqlite3
from pathlib import Path

def init_database_from_sql():
    """
    从SQL文件初始化数据库
    """
    # 数据库路径
    db_path = Path("data/app.db")
    sql_file = Path("../database.sql")

    # 确保data目录存在
    db_path.parent.mkdir(exist_ok=True)

    # 连接数据库（如果不存在则创建）
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    try:
        # 读取并执行SQL文件
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_script = f.read()

        # 执行所有SQL语句
        cursor.executescript(sql_script)
        conn.commit()

        print("✅ 数据库初始化成功！")
        print(f"📁 数据库文件: {db_path.absolute()}")

        # 打印初始化统计
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"👤 用户总数: {user_count}")

        cursor.execute("SELECT username, role FROM users")
        for username, role in cursor.fetchall():
            print(f"   - {username} ({role})")

    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def reset_database():
    """
    重置数据库（删除并重新创建）
    """
    db_path = Path("data/app.db")

    if db_path.exists():
        confirm = input("⚠️  确定要删除现有数据库吗？(yes/no): ")
        if confirm.lower() == 'yes':
            os.remove(db_path)
            print(f"🗑️  已删除: {db_path}")
        else:
            print("❌ 操作取消")
            return

    init_database_from_sql()

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--reset':
        reset_database()
    else:
        init_database_from_sql()
```

#### 运行初始化脚本

```bash
# 从backend目录运行
cd backend

# 第一次初始化
python init_db.py

# 重置数据库（删除并重新创建）
python init_db.py --reset
```

---

## MySQL 初始化

### 前置条件

```bash
# 安装MySQL（如果未安装）
# Windows: 下载并安装MySQL Installer
# Mac: brew install mysql
# Linux: sudo apt-get install mysql-server
```

### 步骤1：创建数据库

```bash
# 登录MySQL
mysql -u root -p

# 或带密码
mysql -u root -pYourPassword
```

### 步骤2：在MySQL命令行中执行

```sql
-- 创建数据库
CREATE DATABASE heritage_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 选择数据库
USE heritage_db;

-- 导入SQL文件
-- 注意：需要将database.sql中的SQLite特定语法改为MySQL兼容版本
SOURCE /path/to/database.sql;

-- 验证
SHOW TABLES;
SELECT COUNT(*) FROM users;
```

### 步骤3：创建数据库用户（生产环境）

```sql
-- 创建新用户
CREATE USER 'heritage_user'@'localhost' IDENTIFIED BY 'StrongPassword123!';

-- 授予权限
GRANT ALL PRIVILEGES ON heritage_db.* TO 'heritage_user'@'localhost';

-- 刷新权限
FLUSH PRIVILEGES;
```

### 步骤4：更新后端配置

编辑 `backend/app/core/config.py`：

```python
# 改为MySQL数据库URL
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://heritage_user:StrongPassword123!@localhost/heritage_db"
```

---

## PostgreSQL 初始化

### 前置条件

```bash
# 安装PostgreSQL
# Windows: 下载PostgreSQL安装程序
# Mac: brew install postgresql
# Linux: sudo apt-get install postgresql
```

### 步骤1：创建数据库

```bash
# 使用psql命令行工具
psql -U postgres -h localhost

# 或一步到位（Windows PowerShell）
psql -U postgres -h localhost -c "CREATE DATABASE heritage_db;"
```

### 步骤2：在PostgreSQL命令行中执行

```sql
-- 连接到数据库
\c heritage_db

-- 导入SQL文件
\i '/path/to/database.sql'

-- 验证
\dt  -- 列出所有表
SELECT COUNT(*) FROM users;
```

### 步骤3：创建数据库用户（生产环境）

```sql
-- 创建新用户
CREATE USER heritage_user WITH PASSWORD 'StrongPassword123!';

-- 授予权限
ALTER ROLE heritage_user WITH LOGIN;
GRANT CONNECT ON DATABASE heritage_db TO heritage_user;
GRANT USAGE ON SCHEMA public TO heritage_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO heritage_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO heritage_user;
```

### 步骤4：更新后端配置

编辑 `backend/app/core/config.py`：

```python
# 改为PostgreSQL数据库URL
SQLALCHEMY_DATABASE_URL = "postgresql://heritage_user:StrongPassword123!@localhost/heritage_db"
```

---

## 命令行快速导入方式

### SQLite 一行命令

```bash
sqlite3 data/app.db < ../database.sql
```

### MySQL 一行命令

```bash
# 前提：已创建数据库
mysql -u root -p heritage_db < ../database.sql

# 或
mysql -u root -pYourPassword heritage_db < ../database.sql
```

### PostgreSQL 一行命令

```bash
psql -U postgres -d heritage_db -f ../database.sql
```

---

## 数据库迁移脚本（用于已有数据库）

如果已经有旧版数据库需要迁移：

### 创建迁移脚本 `backend/migrate_db.py`

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库迁移脚本
用于从旧版本迁移到新版本
"""

import sqlite3
from pathlib import Path

def migrate_to_latest():
    """
    执行数据库迁移
    """
    db_path = Path("data/app.db")

    if not db_path.exists():
        print("❌ 数据库不存在，请先初始化")
        return

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    try:
        # 迁移1: 添加新表（如果不存在）
        # 示例：添加新的user_settings表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                notifications_enabled BOOLEAN DEFAULT TRUE,
                theme VARCHAR(20) DEFAULT 'light',
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
        """)

        # 迁移2: 添加新列（如果不存在）
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN last_login DATETIME;")
        except sqlite3.OperationalError:
            # 列已存在，跳过
            pass

        # 迁移3: 更新现有数据
        # 示例：为没有的用户初始化积分
        cursor.execute("""
            INSERT OR IGNORE INTO user_points (user_id, balance)
            SELECT id, 0 FROM users
        """)

        conn.commit()
        print("✅ 数据库迁移完成！")

    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_to_latest()
```

运行迁移：

```bash
cd backend
python migrate_db.py
```

---

## 备份和恢复

### SQLite 备份

```bash
# 备份整个数据库
cp data/app.db data/app.db.backup.$(date +%Y%m%d_%H%M%S)

# 或使用SQLite命令
sqlite3 data/app.db ".backup data/app.db.backup"
```

### SQLite 恢复

```bash
# 恢复备份
cp data/app.db.backup data/app.db

# 或使用SQLite命令
sqlite3 data/app.db ".restore data/app.db.backup"
```

### MySQL 备份

```bash
# 备份整个数据库
mysqldump -u root -p heritage_db > heritage_db_backup.sql

# 带时间戳的备份
mysqldump -u root -p heritage_db > heritage_db_$(date +%Y%m%d_%H%M%S).sql
```

### MySQL 恢复

```bash
# 恢复备份
mysql -u root -p heritage_db < heritage_db_backup.sql
```

### PostgreSQL 备份

```bash
# 备份整个数据库
pg_dump -U postgres heritage_db > heritage_db_backup.sql

# 自定义格式备份（可恢复部分）
pg_dump -U postgres -Fc heritage_db > heritage_db_backup.dump
```

### PostgreSQL 恢复

```bash
# 恢复备份（SQL格式）
psql -U postgres heritage_db < heritage_db_backup.sql

# 恢复备份（自定义格式）
pg_restore -U postgres -d heritage_db heritage_db_backup.dump
```

---

## 常见问题

### Q: 导入时出现"错误的SQL语法"

**原因**：可能是SQLite特定语法与其他数据库不兼容

**解决**：
1. SQLite使用 `AUTOINCREMENT`，MySQL/PostgreSQL使用 `AUTO_INCREMENT`
2. 确保使用正确的数据库命令行工具
3. 检查文件编码（应为UTF-8）

### Q: 如何在production重置数据库？

**不推荐直接删除！** 建议：

```sql
-- 备份旧数据
CREATE TABLE users_backup AS SELECT * FROM users;

-- 清空表（保留结构）
TRUNCATE TABLE quiz_user_answers;
TRUNCATE TABLE reactions;
TRUNCATE TABLE comments;
DELETE FROM posts;
DELETE FROM resources;
DELETE FROM users;

-- 重新初始化默认用户
INSERT INTO users (...) VALUES (...);
```

### Q: 导入成功但看不到数据

```bash
# 检查数据是否真的导入
sqlite3 data/app.db "SELECT COUNT(*) FROM users;"

# 如果是0，说明INSERT语句没有执行
# 检查是否有PRAGMA integrity_check错误
sqlite3 data/app.db "PRAGMA integrity_check;"
```

### Q: 如何验证数据库完整性？

```bash
# SQLite
sqlite3 data/app.db
> PRAGMA integrity_check;
> PRAGMA foreign_key_check;

# MySQL
SHOW ENGINE INNODB STATUS;
CHECK TABLE users, resources, posts, ...;

# PostgreSQL
\x on
SELECT pg_catalog.pg_stat_file('base/' || oid)
FROM pg_database WHERE datname = current_database();
```

---

## 自动化初始化脚本

### Windows Batch 脚本

创建 `init-database.bat`：

```batch
@echo off
REM 遗迹之光数据库初始化脚本

echo.
echo ===================================
echo 遗迹之光数据库初始化脚本
echo ===================================
echo.

cd /d "%~dp0backend"

REM 检查Python环境
if not exist ".venv\Scripts\python.exe" (
    echo 创建虚拟环境...
    python -m venv .venv
)

REM 激活虚拟环境
call .venv\Scripts\activate.bat

REM 安装依赖
echo 安装依赖...
pip install -r requirements.txt

REM 初始化数据库
echo.
echo 初始化数据库...
python init_db.py

REM 检查结果
if %errorlevel% equ 0 (
    echo.
    echo ✅ 数据库初始化成功！
    echo.
    echo 默认账户：
    echo   用户名: admin / opera_practitioner / heritage_user
    echo   密码: Password123!
    echo.
) else (
    echo.
    echo ❌ 数据库初始化失败！
    echo.
)

pause
```

### PowerShell 脚本

创建 `init-database.ps1`：

```powershell
# 遗迹之光数据库初始化脚本（PowerShell版本）

Write-Host "===================================" -ForegroundColor Cyan
Write-Host "遗迹之光数据库初始化脚本" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""

# 进入backend目录
Set-Location "$PSScriptRoot\backend"

# 创建虚拟环境
if (-not (Test-Path ".venv")) {
    Write-Host "创建虚拟环境..." -ForegroundColor Yellow
    python -m venv .venv
}

# 激活虚拟环境
& ".\.venv\Scripts\Activate.ps1"

# 安装依赖
Write-Host "安装依赖..." -ForegroundColor Yellow
pip install -r requirements.txt

# 初始化数据库
Write-Host ""
Write-Host "初始化数据库..." -ForegroundColor Yellow
python init_db.py

Write-Host ""
Write-Host "✅ 数据库初始化完成！" -ForegroundColor Green
Write-Host ""
Write-Host "默认账户：" -ForegroundColor Green
Write-Host "  用户名: admin / opera_practitioner / heritage_user"
Write-Host "  密码: Password123!"
Write-Host ""
```

运行脚本：

```bash
# Windows命令行
init-database.bat

# PowerShell
.\init-database.ps1
```

---

## 最佳实践

1. **开发环境**：自动初始化，无需手动操作
2. **测试环境**：使用 `init_db.py --reset` 快速重置
3. **生产环境**：仅用于备份/恢复，避免直接修改
4. **定期备份**：每天1次完整备份 + 每小时1次增量备份
5. **迁移计划**：总是先在测试环境验证，再应用到生产

---

*此指南帮助您快速初始化和管理《遗迹之光》项目的数据库。*
