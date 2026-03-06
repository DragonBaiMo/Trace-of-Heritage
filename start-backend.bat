@echo off
chcp 65001 >nul

echo ========================================
echo 遗迹之光 - 仅启动后端服务
echo ========================================
echo.

:: 检查虚拟环境
if not exist "backend\.venv" (
    echo [错误] 后端虚拟环境不存在
    echo [提示] 请先运行 reset-env.bat 初始化环境
    pause
    exit /b 1
)

cd backend
echo [启动] 后端服务启动中...
echo [地址] http://127.0.0.1:8000
echo [文档] http://127.0.0.1:8000/docs
echo.
echo 按 Ctrl+C 停止服务
echo.

.venv\Scripts\uvicorn.exe app.main:app --reload
