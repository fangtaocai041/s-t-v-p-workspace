@echo off
REM CNKI MCP Server - CNKI literature scraper (Go pre-built binary)

cd /d D:\Reasonix\.reasonix\mcp-servers\cnki

if not exist "CNKICrawlerMCP.exe" (
    echo CNKI MCP not installed. Run: python cnki_setup.py install
    exit 1
)

CNKICrawlerMCP.exe
