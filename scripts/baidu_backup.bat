@echo off
REM 百度网盘自动备份 — 文件写入后由百度网盘客户端自动同步到云端
REM 建议: 每周手动运行一次, 或加入开机启动

echo ========================================
echo  Reasonix 工作区备份  百度网盘
echo  %date% %time%
echo ========================================

cd /d D:\Reasonix

REM 推送所有 git 仓库（代码安全第一）
echo [1/2] 推送 git 仓库...
python scripts\backup.py --repo-only

REM 备份配置到百度网盘同步目录
echo [2/2] 备份配置文件到百度网盘...
python scripts\backup.py --baidu

echo ========================================
echo  备份完成
echo  百度网盘客户端将在有网时自动同步
echo  备份位置: D:\BaiduSyncdisk\百度网盘同步空间\Reasonix_backup
echo ========================================
pause
