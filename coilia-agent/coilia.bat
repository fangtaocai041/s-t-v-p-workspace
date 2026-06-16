@echo off
setlocal
set "COILIA_ROOT=%~dp0"
python "%COILIA_ROOT%src\main.py" %*
endlocal
