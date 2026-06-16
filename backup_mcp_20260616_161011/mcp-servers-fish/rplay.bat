@echo off
REM R Playground MCP — 从环境变量读取路径，不在 bat 中硬编码
set RPLAYGROUND_MCP_SUPPORT_IMAGE_OUTPUT=True
if not "%R_HOME%"=="" goto :check_r
set R_HOME=C:\Program Files\R\R-4.6.0
:check_r
if not exist "%R_HOME%\bin\R.exe" (
    echo [WARN] R not found at %%R_HOME%%=^%R_HOME%. Set R_HOME env var if different.
)
if "%TMPDIR%"=="" set TMPDIR=%TEMP%
REM 查找 uvx（优先 PATH，其次常见位置）
where uvx >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    uvx --python 3.13 rplayground-mcp
) else (
    echo [ERROR] uvx not found. Install with: pip install uvx  or: npm install -g uvx
    exit /b 1
)