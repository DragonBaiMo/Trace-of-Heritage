# 寻戏之旅——经典戏曲文化分享互动管理系统的设计与实现 - 快速部署脚本说明

本项目提供了一套完整的 Windows 批处理脚本,方便在不同电脑间快速部署和启动项目。

## 脚本清单

### 1. reset-env.bat - 虚拟环境重置脚本
**用途**: 一键清理并重建前后端虚拟环境,安装所有依赖

**使用场景**:
- 首次部署到新电脑
- 依赖出现问题需要重置
- 迁移项目到其他环境

**执行步骤**:
1. 删除旧的虚拟环境和依赖
2. 创建 Python 虚拟环境
3. 升级 pip 并安装后端依赖
4. 安装前端 npm 依赖

**运行方式**:
```bash
双击运行 reset-env.bat
```

### 2. start-dev.bat - 开发服务器启动脚本
**用途**: 同时启动前后端开发服务器(在独立窗口中)

**前置条件**: 需要先运行 `reset-env.bat` 初始化环境

**运行方式**:
```bash
双击运行 start-dev.bat
```

启动后会打开两个窗口:
- 寻戏之旅——经典戏曲文化分享互动管理系统的设计与实现-后端服务 (http://127.0.0.1:8000)
- 寻戏之旅——经典戏曲文化分享互动管理系统的设计与实现-前端服务 (http://localhost:5173)

关闭对应窗口即可停止服务。

### 3. start-backend.bat - 仅启动后端
**用途**: 只启动后端 FastAPI 服务

**运行方式**:
```bash
双击运行 start-backend.bat
```

按 Ctrl+C 停止服务。

### 4. start-frontend.bat - 仅启动前端
**用途**: 只启动前端 Vite 开发服务器

**运行方式**:
```bash
双击运行 start-frontend.bat
```

按 Ctrl+C 停止服务。

### 5. check-env.bat - 环境检查工具
**用途**: 检查系统环境和项目依赖是否完整

**检查项目**:
- Python 是否安装
- Node.js 和 npm 是否安装
- 后端虚拟环境是否存在
- 后端依赖是否安装
- 前端依赖是否安装
- 配置文件是否存在

**运行方式**:
```bash
双击运行 check-env.bat
```

## 快速开始 - 迁移到新电脑

### 步骤 1: 复制项目文件
将整个项目文件夹复制到新电脑,**不需要**复制以下目录:
- `backend\.venv` (虚拟环境)
- `frontend\node_modules` (依赖)
- `backend\__pycache__` (缓存)
- `.git` (可选,如果不需要版本历史)

### 步骤 2: 安装必要环境
确保新电脑已安装:
- **Python 3.8+** ([下载地址](https://www.python.org/downloads/))
- **Node.js 18+** ([下载地址](https://nodejs.org/))

### 步骤 3: 检查环境
```bash
双击运行 check-env.bat
```
查看系统环境是否满足要求。

### 步骤 4: 重置虚拟环境
```bash
双击运行 reset-env.bat
```
等待自动安装完成所有依赖(首次运行需要几分钟)。

### 步骤 5: 启动项目
```bash
双击运行 start-dev.bat
```

### 步骤 6: 访问应用
- **前端页面**: http://localhost:5173/
- **后端 API**: http://127.0.0.1:8000
- **API 文档**: http://127.0.0.1:8000/docs

## 测试账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | `admin` | `Admin123!` |
| 戏曲从业者 | `opera_practitioner` | `Practitioner123!` |
| 普通用户 | `heritage_user` | `Heritage123!` |

## 常见问题

### 1. "Python 未安装"或"Node.js 未安装"
- 确保已正确安装 Python 和 Node.js
- 确保已将它们添加到系统 PATH 环境变量
- 重新打开命令提示符窗口

### 2. "虚拟环境不存在"
- 运行 `reset-env.bat` 重新创建环境

### 3. 依赖安装失败
- 检查网络连接
- 如果是 pip 安装失败,可以尝试使用国内镜像:
  ```bash
  cd backend
  .venv\Scripts\pip.exe install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
  ```
- 如果是 npm 安装失败,可以尝试:
  ```bash
  cd frontend
  npm install --registry=https://registry.npmmirror.com
  ```

### 4. 端口被占用
- 后端默认端口 8000,前端默认端口 5173
- 如果提示端口被占用,请关闭占用端口的程序或修改配置

### 5. 数据库初始化问题
- 数据库文件位于 `backend\data\app.db`
- 首次启动会自动创建并初始化
- 如需重置数据库,删除该文件后重启后端服务

## 配置文件

### 后端配置 (backend/.env)
```env
# 数据库配置
DATABASE_URL=sqlite:///./data/app.db

# JWT 配置
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS 配置
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

### 前端配置 (frontend/.env)
```env
VITE_API_BASE=http://127.0.0.1:8000
```

## 手动操作(高级)

如果需要手动操作,可以参考以下命令:

### 后端手动部署
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 前端手动部署
```bash
cd frontend
npm install
npm run dev
```

## 打包和分发

### 迁移到其他电脑需要复制的文件
```
Trace-of-Heritage/
├── backend/
│   ├── app/          # 源代码
│   ├── data/         # 数据库文件(可选)
│   ├── tests/        # 测试
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
├── frontend/
│   ├── src/          # 源代码
│   ├── index.html
│   ├── package.json
│   ├── .env.example
│   └── README.md
├── reset-env.bat     # 环境重置脚本
├── start-dev.bat     # 启动脚本
├── start-backend.bat # 后端启动脚本
├── start-frontend.bat# 前端启动脚本
└── check-env.bat     # 环境检查脚本
```

**不需要复制**:
- `backend\.venv\` (会重新创建)
- `frontend\node_modules\` (会重新安装)
- `backend\__pycache__\` (运行时缓存)
- `frontend\dist\` (构建产物)

## 技术支持

如遇问题,请检查:
1. 运行 `check-env.bat` 查看环境状态
2. 查看后端日志窗口的错误信息
3. 查看前端浏览器控制台的错误信息
4. 确认防火墙没有阻止端口 8000 和 5173

---

**祝使用愉快!**
