@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo 寻戏之旅——经典戏曲文化分享互动管理系统的设计与实现 - 开发服务器启动脚本
echo ========================================
echo.

:: 检查后端虚拟环境是否存在
if not exist "backend\.venv" (
    echo [错误] 后端虚拟环境不存在
    echo [提示] 请先运行 reset-env.bat 初始化环境
    pause
    exit /b 1
)

:: 检查前端依赖是否存在
if not exist "frontend\node_modules" (
    echo [错误] 前端依赖不存在
    echo [提示] 请先运行 reset-env.bat 初始化环境
    pause
    exit /b 1
)

echo [启动] 正在启动后端服务...
echo [后端] 地址: http://127.0.0.1:8000
echo [后端] API文档: http://127.0.0.1:8000/docs
echo.

:: 启动后端服务(在新窗口)
start "寻戏之旅——经典戏曲文化分享互动管理系统的设计与实现-后端服务" cmd /k "cd /d %~dp0backend && .venv\Scripts\uvicorn.exe app.main:app --reload"

:: 等待后端启动
timeout /t 3 /nobreak >nul

echo [启动] 正在启动前端服务...
echo [前端] 地址: http://localhost:5173/
echo.

:: 启动前端服务(在新窗口)
start "寻戏之旅——经典戏曲文化分享互动管理系统的设计与实现-前端服务" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ========================================
echo 服务启动完成!
echo ========================================
echo.
echo 前后端服务已在独立窗口中启动:
echo   - 后端窗口: 寻戏之旅——经典戏曲文化分享互动管理系统的设计与实现-后端服务
echo   - 前端窗口: 寻戏之旅——经典戏曲文化分享互动管理系统的设计与实现-前端服务
echo.
echo 访问地址:
echo   - 前端页面: http://localhost:5173/
echo   - 后端API: http://127.0.0.1:8000
echo   - API文档: http://127.0.0.1:8000/docs
echo.
echo 测试账号:
echo   - 管理员: admin / Admin123
echo   - 戏曲从业者: opera_practitioner / Practitioner123
echo   - 普通用户: heritage_user / Heritage123
echo.
echo 提示: 关闭对应窗口即可停止服务
echo.

pause
