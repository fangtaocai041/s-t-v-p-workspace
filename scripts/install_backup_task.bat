@echo off
REM 添加到 Windows 任务计划程序 — 开机自启 + 每天备份
REM 以管理员身份运行: 右键 → 以管理员身份运行

echo ========================================
echo  设置 Reasonix 自动备份任务
echo ========================================

schtasks /create /tn "ReasonixAutoBackup" /tr "cmd.exe /c D:\Reasonix\scripts\baidu_backup.bat" /sc daily /st 20:00 /f

if %errorlevel% equ 0 (
    echo ✅ 自动备份任务已创建
    echo    每天 20:00 执行备份
    echo    备份到百度网盘(自动同步)
) else (
    echo ❌ 创建失败, 请以管理员身份运行
)

pause
