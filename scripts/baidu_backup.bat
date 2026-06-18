@echo off
REM 百度网盘自动备份 — 每天执行一次
REM 用法: 双击运行, 或加入 Windows 任务计划程序

echo ========================================
echo  Reasonix 工作区备份 -> 百度网盘
echo  %date% %time%
echo ========================================

cd /d D:\Reasonix

REM 推送所有 git 仓库
python scripts\backup.py --repo-only

REM 备份配置到百度网盘
python scripts\backup.py --baidu

echo ========================================
echo  备份完成
echo ========================================
pause
