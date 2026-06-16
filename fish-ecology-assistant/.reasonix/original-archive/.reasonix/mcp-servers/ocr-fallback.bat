@echo off
cd /d .reasonix\mcp-servers\ocr-fallback
if not exist node_modules (
    echo [OCR-Fallback] Installing dependencies...
    call npm install --silent 2>nul
)
node index.js
