#!/bin/bash
# PaddleOCR MCP — Linux/macOS
export AUTH_TOKEN="${PADDLEOCR_AUTH_TOKEN:-}"
node "$(dirname "$0")/paddleocr-server.mjs"
