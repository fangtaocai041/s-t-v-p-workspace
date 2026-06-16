#!/bin/bash
# OCR Fallback (Tesseract.js) MCP — Linux/macOS
cd "$(dirname "$0")/ocr-fallback"
if [ ! -d "node_modules" ]; then
    npm install --silent
fi
node index.js
