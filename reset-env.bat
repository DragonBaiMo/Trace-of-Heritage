@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo 遗迹之光 - 虚拟环境重置脚本
echo ========================================
echo.

:: 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python,请先安装 Python 3.8+
    pause
    exit /b 1
)

:: 检查 Node.js 是否安装
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Node.js,请先安装 Node.js 18+
    pause
    exit /b 1
)

echo [提示] 检测到 Python 和 Node.js 环境正常
echo.

:: 询问用户是否继续
set /p confirm="是否继续重置虚拟环境? 这将删除现有的所有依赖 (Y/N): "
if /i not "%confirm%"=="Y" (
    echo [取消] 用户取消操作
    pause
    exit /b 0
)

echo.
echo ========================================
echo 第一步: 清理现有虚拟环境
echo ========================================
echo.

:: 删除后端虚拟环境
if exist "backend\.venv" (
    echo [清理] 正在删除后端虚拟环境...
    rmdir /s /q "backend\.venv"
    echo [完成] 后端虚拟环境已删除
) else (
    echo [跳过] 后端虚拟环境不存在
)

:: 删除前端依赖
if exist "frontend\node_modules" (
    echo [清理] 正在删除前端依赖...
    rmdir /s /q "frontend\node_modules"
    echo [完成] 前端依赖已删除
) else (
    echo [跳过] 前端依赖不存在
)

:: 删除前端可能误创建的虚拟环境
if exist "frontend\.venv" (
    echo [清理] 正在删除前端误创建的虚拟环境...
    rmdir /s /q "frontend\.venv"
    echo [完成] 前端 .venv 已删除
)

echo.
echo ========================================
echo 第二步: 创建后端虚拟环境
echo ========================================
echo.

cd backend
echo [创建] 正在创建 Python 虚拟环境...
python -m venv .venv
if errorlevel 1 (
    echo [错误] 创建虚拟环境失败
    cd ..
    pause
    exit /b 1
)
echo [完成] Python 虚拟环境创建成功

echo [升级] 正在升级 pip...
.venv\Scripts\python.exe -m pip install --upgrade pip
if errorlevel 1 (
    echo [警告] pip 升级失败,但将继续安装依赖
)

echo [安装] 正在安装后端依赖...
.venv\Scripts\pip.exe install -r requirements.txt
if errorlevel 1 (
    echo [错误] 后端依赖安装失败
    cd ..
    pause
    exit /b 1
)
echo [完成] 后端依赖安装成功
cd ..

echo.
echo ========================================
echo 第三步: 安装前端依赖
echo ========================================
echo.

cd frontend
echo [安装] 正在安装前端依赖...
call npm install
if errorlevel 1 (
    echo [错误] 前端依赖安装失败
    cd ..
    pause
    exit /b 1
)
echo [完成] 前端依赖安装成功
cd ..

echo.
echo ========================================
echo 重置完成!
echo ========================================
echo.
echo [成功] 虚拟环境已重置完成,可以开始使用
echo.
echo 后续操作:
echo   1. 运行 start-dev.bat 启动开发服务器
echo   2. 或手动启动:
echo      - 后端: cd backend ^&^& .venv\Scripts\uvicorn.exe app.main:app --reload
echo      - 前端: cd frontend ^&^& npm run dev
echo.
echo 访问地址:
echo   - 前端: http://localhost:5173/
echo   - 后端: http://127.0.0.1:8000
echo   - API文档: http://127.0.0.1:8000/docs
echo.

pause
