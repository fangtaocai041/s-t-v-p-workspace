#!/bin/bash
# Zotero MCP — Linux/macOS
# 修改 --db-path 为你的 Zotero SQLite 路径
npx -y mcp-server-sqlite --db-path "${ZOTERO_DB_PATH:-$HOME/Zotero/zotero.sqlite}"
