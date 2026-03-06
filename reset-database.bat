@echo off
chcp 65001 >nul

echo ========================================
echo 遗迹之光 - 数据库重置脚本
echo ========================================
echo.
echo [警告] 此操作将删除所有数据,包括:
echo   - 所有用户账号(除了默认账号)
echo   - 所有资源数据
echo   - 所有审计日志
echo   - 所有其他业务数据
echo.
echo 重置后将重新创建默认测试账号:
echo   - 管理员: admin / Admin123!
echo   - 戏曲从业者: opera_practitioner / Practitioner123!
echo   - 普通用户: heritage_user / Heritage123!
echo.

set /p confirm="确认要重置数据库吗? 此操作不可恢复! (输入 YES 继续): "
if /i not "%confirm%"=="YES" (
    echo [取消] 用户取消操作
    pause
    exit /b 0
)

echo.
echo [备份] 正在备份现有数据库...
if exist "backend\data\app.db" (
    set backup_name=app.db.backup.%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
    set backup_name=%backup_name: =0%
    copy "backend\data\app.db" "backend\data\%backup_name%"
    if errorlevel 1 (
        echo [错误] 备份失败
    ) else (
        echo [完成] 数据库已备份到: backend\data\%backup_name%
    )
)

echo [删除] 正在删除数据库文件...
if exist "backend\data\app.db" (
    del "backend\data\app.db"
    echo [完成] 数据库文件已删除
) else (
    echo [跳过] 数据库文件不存在
)

echo.
echo ========================================
echo 数据库重置完成!
echo ========================================
echo.
echo 下一步:
echo   1. 重新启动后端服务
echo   2. 系统将自动创建新的数据库并初始化默认账号
echo.
echo 提示:
echo   - 如果后端服务正在运行,请手动重启
echo   - 或运行 start-dev.bat 重新启动所有服务
echo.

pause
