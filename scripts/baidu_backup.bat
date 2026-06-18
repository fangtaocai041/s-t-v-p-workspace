@echo off
REM 百度网盘整盘镜像同步 — 增量同步整个 Reasonix 工作区到百度网盘
REM 由 Windows 任务计划程序每天 20:00 自动执行

echo ========================================
echo  Reasonix 工作区镜像同步  百度网盘
echo  %date% %time%
echo ========================================

cd /d D:\Reasonix

REM 推送所有 git 仓库
echo [1/3] 推送 git 仓库...
python scripts\backup.py --repo-only

REM 整盘镜像同步
echo [2/3] 整盘同步到百度网盘...
call scripts\sync_to_baidu.bat

echo ========================================
echo  全部完成
echo  百度网盘客户端自动同步到云端
echo  恢复: 下载 Reasonix_full_backup 到 D:\Reasonix
echo ==========================================
pause
