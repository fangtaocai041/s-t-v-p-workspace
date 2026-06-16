#!/bin/bash
# GitHub MCP — Linux/macOS
if [ -z "$GITHUB_TOKEN" ]; then
    echo "[ERROR] GITHUB_TOKEN not set. Check .env file." >&2
    exit 1
fi
export GITHUB_TOKEN
npx -y @modelcontextprotocol/server-github
