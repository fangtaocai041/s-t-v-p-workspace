#!/bin/bash
# Porpoise Agent Setup Script
# 江豚研究智能体 环境配置脚本

set -e

echo "=========================================="
echo "  Porpoise Agent - 江豚研究智能体"
echo "  环境配置脚本"
echo "=========================================="

# Python version check
echo ""
echo "[1/5] Checking Python version..."
python --version

# Create virtual environment
echo ""
echo "[2/5] Creating virtual environment..."
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies
echo ""
echo "[3/5] Installing Python dependencies..."
pip install --upgrade pip
pip install -e .

# Install dev dependencies
pip install -e ".[dev]"

# Setup .env
echo ""
echo "[4/5] Setting up configuration..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "  Created .env from .env.example"
    echo "  IMPORTANT: Edit .env and add your DEEPSEEK_API_KEY"
else
    echo "  .env already exists, skipping"
fi

# Create directories
echo ""
echo "[5/5] Creating data directories..."
mkdir -p data/raw data/processed data/references data/knowledge_base data/templates
mkdir -p outputs logs

# Install Node.js deps for Reasonix (optional)
echo ""
echo "---"
echo "Optional: Install Reasonix CLI"
echo "  npm install -g reasonix"
echo ""
echo "=========================================="
echo "  Setup complete!"
echo ""
echo "  Quick start:"
echo "    source .venv/bin/activate"
echo "    porpoise doctor"
echo "    porpoise chat"
echo "=========================================="
