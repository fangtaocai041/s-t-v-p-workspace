#!/bin/bash
# Tavily Search MCP — Linux/macOS
if [ -z "$TAVILY_API_KEY" ]; then
    echo "[ERROR] TAVILY_API_KEY not set. Check .env file." >&2
    exit 1
fi
export TAVILY_API_KEY
npx -y tavily-mcp@latest
