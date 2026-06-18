# 灾难恢复指南

> 当 D:\Reasonix 丢失后，如何从零恢复。

---

## 一、恢复优先级

| 优先级 | 项目 | 恢复方式 | 预估时间 |
|:------:|:-----|:---------|:--------:|
| 🔴 1 | code 代码 (10 个仓库) | `git clone` | 2 分钟 |
| 🔴 2 | API Keys | 从 `.env.backup` 或环境变量 | 1 分钟 |
| 🟡 3 | MCP 服务器 | `pip install` + 下载二进制 | 10 分钟 |
| 🟡 4 | Zotero 文献库 | 从备份恢复 `zotero.sqlite` | 1 分钟 |
| 🟢 5 | 会话历史 | 非必需 | 可选 |

## 二、恢复步骤

### Step 1: 克隆代码

```bash
mkdir D:\Reasonix && cd D:\Reasonix

# 工作区根 (含 coordination.yaml、AGENTS.md 等)
git clone https://github.com/fangtaocai041/s-t-v-p-workspace.git .

# 子项目
git clone https://github.com/fangtaocai041/fish-ecology-assistant.git
git clone https://github.com/fangtaocai041/san-sheng-wanwu-core.git
git clone https://github.com/fangtaocai041/cognitive-search-engine.git
git clone https://github.com/fangtaocai041/eon-core.git
git clone https://github.com/fangtaocai041/porpoise-agent.git
git clone https://github.com/fangtaocai041/coilia-agent.git
git clone https://github.com/fangtaocai041/culter-agent.git
git clone https://github.com/fangtaocai041/conflict-arbiter.git

# infrastructure (需先在 GitHub 创建仓库)
cd D:\Reasonix\infrastructure
git init
git remote add origin https://github.com/fangtaocai041/infrastructure.git
```

### Step 2: 恢复 API Keys

```bash
# 从备份或密码管理器
set DEEPSEEK_API_KEY=sk-xxx
set GITHUB_TOKEN=ghp_xxx
set PADDLE_AUTH_TOKEN=97fc64ce...
set TAVILY_API_KEY=tvly-xxx
set EXA_API_KEY=xxx
```

### Step 3: 恢复 MCP 服务器

```bash
# CNKI MCP
mkdir -p .reasonix/mcp-servers/cnki
# 从 GitHub Releases 下载:
# https://github.com/Mangofang/CNKICrawlerMCP/releases

# PaddleOCR (在 reasonix.toml 中自动配置)
uvx --from paddleocr-mcp paddleocr_mcp
```

### Step 4: 恢复 Zotero 数据库

```bash
# 从备份恢复
copy D:\backup\zotero.sqlite D:\ZoteroData\
```

### Step 5: 验证

```bash
cd D:\Reasonix\fish-ecology-assistant
pip install -e .
python -m pytest tests/
# → 82 passed ✅

cd D:\Reasonix\san-sheng-wanwu-core
pip install -e .
python scripts/verify_architecture.py
# → 36/36 checks passed ✅
```

## 三、预防措施

### 每日备份

```bash
# 推送所有 git 仓库 + 备份配置文件
python D:\Reasonix\scripts\backup.py

# 只推送 git
python D:\Reasonix\scripts\backup.py --repo-only
```

### 建议

1. **API Keys 存密码管理器**（Bitwarden/1Password），不要只靠 `.env`
2. **Zotero 文献库** 开启 Zotero 云同步（官方已支持）
3. **每周运行一次** `python scripts/backup.py`
4. **基础设施项目** 在 GitHub 创建仓库后推送

## 四、备份脚本

```bash
# 备份到默认位置 (D:\Reasonix_backup\)
python D:\Reasonix\scripts\backup.py

# 备份到指定位置
python D:\Reasonix\scripts\backup.py --dest "D:\my_backup"

# 只推送 git（不备份大文件）
python D:\Reasonix\scripts\backup.py --repo-only
```
