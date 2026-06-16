@echo off
REM CNKI MCP Server — 知网文献爬取
REM 使用: 首次运行 python cnki_setup.py 安装依赖

cd /d D:\Reasonix\.reasonix\mcp-servers\cnki

if not exist "venv\Scripts\python.exe" (
    echo ⚠️ CNKI MCP 未安装，运行: python D:\Reasonix\.reasonix\mcp-servers\cnki_setup.py
    exit 1
)

venv\Scripts\python.exe -m cnki_mcp
