@echo off
REM 密钥从 .env 或系统环境变量读取，不要在 bat 中硬编码
if "%TAVILY_API_KEY%"=="" (
    echo [ERROR] TAVILY_API_KEY 未设置。请确保 .env 中存在该变量。
    exit /b 1
)
set DEFAULT_PARAMETERS={"include_images": true, "max_results": 15, "search_depth": "advanced"}
npx -y tavily-mcp@latest
