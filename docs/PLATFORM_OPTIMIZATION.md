# 平台生态优化方案 — GitHub · Hugging Face · Gitee

> 当前 eon-workspace 是封闭的本地系统。接入外部平台可将能力提升一个数量级。

---

## 一、Hugging Face — 10 个可集成资源

### 🥇 优先集成（低投入，高回报）

| # | 项目 | 用途 | 接入方式 |
|:-:|:-----|:-----|:---------|
| 1 | **Fish-Vista** (`imageomics/fish-vista`) | 60K 张鱼类图片 + 1900 物种标签 + 9 种性状分割 | → `infrastructure/fish_classifier.py` — 长江鱼类自动识别 |
| 2 | **FishDet-M** (`GE9X/FishDet-M`) | 105K 图片 + 296K 标注 + 28 个预训练 YOLO 模型 | → `infrastructure/fish_detector.py` — 水下视频鱼群计数 |
| 3 | **60fishmodel** (`NeroZ02/60fishmodel`) | 60 种鱼类分类器（含鲤科） | → 直接 `pipeline("image-classification")` 一行代码 |
| 4 | **OceanBench** (`zjunlp/OceanBench`) | 10K+ 中英文渔业指令数据 | → 微调中文生态 LLM agent |

### 🥈 中期集成（中投入，高回报）

| # | 项目 | 用途 | 接入方式 |
|:-:|:-----|:-----|:---------|
| 5 | **BioAnalyst BFM** (`BioDT/bfm-pretrained`) | 首个生态学 Transformer 基础模型（10 模态） | → 微调长江鱼类分布预测（需 GBIF 数据） |
| 6 | **Weecology 模型套件** | 12 个生态 CV 模型（海洋生物多样性检测等） | → 作为基线对比 |
| 7 | **OzFish YOLOv7** | 507 物种鱼群检测 | → 补充水下监控场景 |

### 🥉 储备资源

| # | 项目 | 用途 |
|:-:|:-----|:-----|
| 8 | `timm/timm` | 通用图像分类骨干网络（ResNet/ViT/Swin） |
| 9 | `facebook/dinov2` | 自监督视觉特征提取（适合少样本鱼类识别） |
| 10 | `openai/whisper` | 野外录音转文字（鸟类/江豚声学监测） |

---

## 二、GitHub — 6 项存量优化

### 1. 仓库 Badge 补全

当前只有 license badge。补充：

```markdown
[![CI](https://github.com/fangtaocai041/fish-ecology-assistant/actions/workflows/validate.yml/badge.svg)](...)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue)](...)
[![Hugging Face](https://img.shields.io/badge/🤗-Models-yellow)](...)
[![Species](https://img.shields.io/badge/species-26-green)](...)
```

### 2. Issue 模板

```
.github/ISSUE_TEMPLATE/
├── species_request.md      ← "请求添加物种: ___"
├── literature_gap.md       ← "文献缺口: ___"
└── bug_report.md           ← 标准 bug 模板
```

### 3. PR 模板 + CODEOWNERS

```
.github/
├── PULL_REQUEST_TEMPLATE.md
└── CODEOWNERS              ← * @fangtaocai041
```

### 4. GitHub Pages 文档站

```
启用 Settings → Pages → Source: GitHub Actions
使用 mkdocs-material 自动从 docs/ 生成文档站
```

### 5. Dependabot 自动更新

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule: { interval: "weekly" }
```

### 6. Release 自动打包

```yaml
# .github/workflows/release.yml
on:
  push:
    tags: ["v*"]
jobs:
  build:
    steps:
      - run: pip install build && python -m build
      - uses: softprops/action-gh-release@v1
```

---

## 三、Gitee（码云）— 3 项中国特色优化

### 1. 仓库镜像

```bash
# 自动同步 GitHub → Gitee
git remote add gitee https://gitee.com/fangtaocai/fish-ecology-assistant.git
git push gitee master
```

配置 GitHub Actions 自动镜像：
```yaml
- name: Sync to Gitee
  uses: Yikun/hub-mirror-action@v1
  with:
    src: github/fangtaocai041
    dst: gitee/fangtaocai
```

### 2. CNKI 工具链集成

| 工具 | 用途 | 状态 |
|:-----|:-----|:----:|
| `caj2pdf` | CAJ → PDF 转换 | 已有脚本 |
| `cnki-downloader` | CNKI 批量下载 | 可集成 |
| `CNKI_2_BibTeX` | 文献元数据导出 | 可集成 |
| `CNKICrawlerMCP` | CNKI MCP 服务器 | **推荐集成** — 直接作为第 20 个 MCP 服务器 |

### 3. 中文 NLP 集成

| 工具 | 用途 | 优先级 |
|:-----|:-----|:-----:|
| **HanLP** | 中文分词/NER/依存句法 | 🥇 |
| **Jiagu** | 轻量中文 NLP（BiLSTM） | 🥈 |
| **Synonyms** | 中文生态学术语同义词匹配 | 🥇 |

---

## 四、数据源接入（超过 Hugging Face 范围）

| 数据源 | 数据类型 | API | 用途 |
|:-------|:---------|:---|:-----|
| **GBIF** | 物种出现记录 | REST API | SDM 分布建模 |
| **IUCN Red List** | 保护等级 | API v3 | 冲突仲裁输入 |
| **FishBase** | 鱼类生物学数据 | REST API | 知识库补充 |
| **OBIS** | 海洋生物多样性 | REST API | 刀鲚河口数据 |
| **CIWF-BON** | 长江鱼类监测 | figshare | 本地基线数据 |

---

## 五、实施优先级矩阵

```
                    高回报
                      │
       🥇 1-4       │       🥇 5-7
    Badge/Issue/   │   HuggingFace
    Dependabot    │   模型集成
    (本周可做)    │   (需数据集)
                      │
  ──────────────────┼──────────────────
    低投入           │           高投入
                      │
       🥈 Gitee     │       🥉 数据源
       镜像+CNKI   │     GBIF/IUCN/
       (半天)      │     FishBase
                      │
                    低回报
```

---

## 六、本周可执行的 5 件事

```bash
# 1. 给所有仓库加 CI badge
echo "[![CI](https://github.com/fangtaocai041/fish-ecology-assistant/actions/workflows/validate.yml/badge.svg)]" >> README.md

# 2. 配置 Dependabot
mkdir -p .github && cat > .github/dependabot.yml << 'EOF'
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule: { interval: "weekly" }
EOF

# 3. Gitee 镜像
git remote add gitee https://gitee.com/fangtaocai/fish-ecology-assistant.git

# 4. 测试 HuggingFace 模型
python -c "from transformers import pipeline; p = pipeline('image-classification', 'NeroZ02/60fishmodel'); print(p('test.jpg'))"

# 5. 创建 Issue 模板
mkdir -p .github/ISSUE_TEMPLATE
```
