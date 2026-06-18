@echo off
chcp 65001 >nul
REM Full workspace mirror sync to Baidu Netdisk

set "SRC=D:\Reasonix"
set "DST=D:\BaiduSyncdisk\百度网盘同步空间\Reasonix_full_backup"

echo ========================================
echo  Mirroring %SRC% to Baidu Netdisk
echo  %date% %time%
echo ========================================

robocopy "%SRC%" "%DST%" /MIR /NDL /NJH /NJS /R:2 /W:3 /XD .git node_modules __pycache__ .playwright-mcp .pytest_cache .reasonix\attachments .reasonix\sessions .reasonix\truncated-results logs __pycache__ .git .cache /XF *.pyc *.pyo *.exe
robocopy "%SRC%\.reasonix\mcp-servers\cnki" "%DST%\.reasonix\mcp-servers\cnki" "CNKICrawlerMCP.exe" /NDL /NJH /NJS

echo ========================================
echo  Done. Baidu Netdisk auto-syncs to cloud.
echo  Restore: download Reasonix_full_backup to D:\Reasonix
echo ========================================
