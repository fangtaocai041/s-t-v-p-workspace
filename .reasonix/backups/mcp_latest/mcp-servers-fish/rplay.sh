#!/bin/bash
# R Playground MCP — Linux/macOS
export RPLAYGROUND_MCP_SUPPORT_IMAGE_OUTPUT=True
export R_HOME="${R_HOME:-/usr/lib/R}"
export TMPDIR="${TMPDIR:-/tmp}"

if ! command -v uvx &> /dev/null; then
    echo "[ERROR] uvx not found. Install with: pip install uvx" >&2
    exit 1
fi

uvx --python 3.13 rplayground-mcp
