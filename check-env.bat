@echo off
chcp 65001 >nul

echo ========================================
echo 遗迹之光 - 环境检查工具
echo ========================================
echo.

set error_count=0

:: 检查 Python
echo [检查] Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [×] Python 未安装
    set /a error_count+=1
) else (
    for /f "tokens=*" %%i in ('python --version 2^>^&1') do echo [√] %%i
)

:: 检查 Node.js
echo [检查] Node.js 环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo [×] Node.js 未安装
    set /a error_count+=1
) else (
    for /f "tokens=*" %%i in ('node --version') do echo [√] Node.js %%i
)

:: 检查 npm
echo [检查] npm 环境...
npm --version >nul 2>&1
if errorlevel 1 (
    echo [×] npm 未安装
    set /a error_count+=1
) else (
    for /f "tokens=*" %%i in ('npm --version') do echo [√] npm %%i
)

echo.
echo ----------------------------------------
echo 项目环境检查
echo ----------------------------------------

:: 检查后端虚拟环境
echo [检查] 后端虚拟环境...
if exist "backend\.venv" (
    echo [√] 后端虚拟环境已创建
) else (
    echo [×] 后端虚拟环境不存在
    set /a error_count+=1
)

:: 检查后端依赖
echo [检查] 后端依赖...
if exist "backend\.venv\Lib\site-packages\fastapi" (
    echo [√] 后端依赖已安装
) else (
    echo [×] 后端依赖未安装或不完整
    set /a error_count+=1
)

:: 检查前端依赖
echo [检查] 前端依赖...
if exist "frontend\node_modules" (
    echo [√] 前端依赖已安装
) else (
    echo [×] 前端依赖不存在
    set /a error_count+=1
)

:: 检查配置文件
echo [检查] 配置文件...
if exist "backend\.env" (
    echo [√] 后端配置文件存在
) else (
    echo [!] 后端 .env 文件不存在 (可选)
)

if exist "frontend\.env" (
    echo [√] 前端配置文件存在
) else (
    echo [!] 前端 .env 文件不存在 (可选)
)

echo.
echo ========================================
echo 检查结果
echo ========================================
echo.

if %error_count%==0 (
    echo [成功] 所有必要环境已就绪,可以启动项目!
    echo.
    echo 下一步:
    echo   - 运行 start-dev.bat 启动完整服务
    echo   - 或运行 start-backend.bat / start-frontend.bat 分别启动
) else (
    echo [警告] 发现 %error_count% 个问题
    echo.
    echo 建议:
    if not exist "backend\.venv" (
        echo   - 运行 reset-env.bat 重置虚拟环境
    )
    echo   - 确保已安装 Python 3.8+ 和 Node.js 18+
)

echo.
pause
