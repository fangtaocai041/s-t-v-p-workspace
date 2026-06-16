#!/bin/bash
# Exa Semantic Search MCP — Linux/macOS
if [ -z "$EXA_API_KEY" ]; then
    echo "[ERROR] EXA_API_KEY not set. Check .env file." >&2
    exit 1
fi
export EXA_API_KEY
npx -y exa-mcp-server
