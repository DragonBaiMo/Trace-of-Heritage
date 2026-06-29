@echo off
chcp 65001 >nul

echo ========================================
echo 寻戏之旅——经典戏曲文化分享互动管理系统的设计与实现 - 仅启动前端服务
echo ========================================
echo.

:: 检查依赖
if not exist "frontend\node_modules" (
    echo [错误] 前端依赖不存在
    echo [提示] 请先运行 reset-env.bat 初始化环境
    pause
    exit /b 1
)

cd frontend
echo [启动] 前端服务启动中...
echo [地址] http://localhost:5173/
echo.
echo 按 Ctrl+C 停止服务
echo.

npm run dev
