@echo off
REM 密钥从 .env 或系统环境变量读取，不要在 bat 中硬编码
if "%EXA_API_KEY%"=="" (
    echo [ERROR] EXA_API_KEY 未设置。请确保 .env 中存在该变量。
    exit /b 1
)
npx -y exa-mcp-server
