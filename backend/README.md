# 后端服务启动说明

## 环境准备
1. 创建虚拟环境并安装依赖：
   ```bash
   cd backend
   python -m venv .venv
   .venv\\Scripts\\activate
   pip install -r requirements.txt
   ```
2. 按需复制环境变量示例：
   ```bash
   cp .env.example .env
   ```

## 初始化数据库
项目启动时会自动创建 SQLite 表结构，并确保存在默认管理员账号。数据文件默认位于 `data/app.db`，可通过 `.env` 调整。

### 默认账号

为方便联调，系统会在启动时自动初始化三类账号（如需修改请在 `.env` 中覆盖对应配置）：

| 角色       | 用户名                | 密码               |
|------------|-----------------------|--------------------|
| 管理员     | `admin`               | `Admin123!`        |
| 戏曲从业者 | `opera_practitioner`  | `Practitioner123!` |
| 普通用户   | `heritage_user`       | `Heritage123!`     |

请务必在生产环境修改这些默认凭据。

如需彻底清空并重建数据库（移除旧有以问号表示的可选字段约定），可执行：

```bash
python -m backend.scripts.reset_database
```

若要跳过交互确认，请附加 `--force` 参数。

## 启动服务
```bash
uvicorn app.main:app --reload
```

## 关键接口速览
- `GET /api/resources`（Query：`status,keyword,page,page_size`）：资源列表筛选及分页查询，返回分页元信息。
- `GET /api/resources/summary`：获取资源数量统计与最近动态。
- `GET /api/audits`（Query：`limit`）：管理员查看审计日志，追踪关键操作。

## 运行测试
```bash
pytest
```
