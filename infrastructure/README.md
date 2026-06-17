# infrastructure — Reasonix 统一涌现检测引擎

> **道生一 · 一生二 · 二生三 · 三生万物**
>
> 融合三项目涌现能力: 实时监控 + 三层分析 + 领域发现 + 中文 NLP + 视觉检测

---

## 项目概述

`infrastructure` 是 [Reasonix 七项目体系](https://github.com/NeroZ02) 的统一基础引擎。它将三个核心项目的涌现检测能力融合到一个可组合的代码库中:

| 模块 | 来源 | 能力 |
|:-----|:-----|:-----|
| **unified_emergence** | p/f/c 三项目融合 | 实时 Z-score 监控 · D₀→D₃ 维度追踪 · 三层分析(异常→突变→理论) · 自组织领域发现 |
| **fish_classifier** | 独立集成 | HuggingFace 鱼类识别: 60fishmodel (60种) / Fish-Vista (1900种) / DINOv2 特征提取 |
| **chinese_nlp** | 独立集成 | 中文生态学术语 NLP: HanLP + Jiagu 分词/词性标注 · NER 实体识别 · 同义词匹配 |
| **fish_detector** | 独立集成 | FishDet-M + YOLO 鱼群检测: 水下摄像头鱼群计数 · 物种级检测框 · 视频帧批量分析 |

### 在"三生万物"生态中的角色

```
道 (操作者)
 │
 ├─ 一 (IProjectAdapter 统一接口)
 │    └─ infrastructure 为所有 adapter 提供共享的涌现检测能力
 │
 ├─ 二 (阳·扩张 / 阴·收敛)
 │    └─ EmergenceMonitor → 实时阳面扩张监控
 │    └─ EmergenceEngine → 离线阴面收敛分析
 │
 ├─ 三 (三角闭环: fish ↔ cognitive ↔ porpoise/coilia/culter)
 │    └─ infrastructure 横切三个项目的共用引擎
 │
 └─ 万物 (P₁...Pₙ 无限物种专研)
      └─ 任何 Pₙ agent 均可 import infrastructure 获得涌现感知
```

**权威架构文档:** [`docs/SANSHENG_WANWU.md`](https://github.com/NeroZ02/Reasonix/blob/main/docs/SANSHENG_WANWU.md) — 替代所有旧架构 (WUXING / TAIJI / LAYERS)

---

## 安装

### 基础安装 (只装核心，无需额外依赖)

```bash
cd infrastructure
pip install -e .
```

核心功能 (EmergenceMonitor / EmergenceEngine / emerge_domains) 开箱即用。

### 按需安装可选依赖

```bash
# 涌现统计显著性 (p-value)
pip install -e ".[emergence]"

# 中文生态学 NLP (分词/NER/同义词)
pip install -e ".[nlp]"

# 鱼类图像分类 (HuggingFace 模型)
pip install -e ".[vision]"

# 鱼群目标检测 (YOLO)
pip install -e ".[detection]"

# 一键全装
pip install -e ".[all]"

# 开发环境
pip install -e ".[dev]"
```

---

## 快速开始

### 1. 实时涌现监控

```python
from infrastructure import EmergenceMonitor, DimensionalLevel

# 初始化监控器
mon = EmergenceMonitor(emergence_threshold_sigma=3.0, min_sources=3)

# 记录多维指标
mon.record("recall", 0.85, DimensionalLevel.D1)
mon.record("precision", 0.92, DimensionalLevel.D1)
mon.record("throughput", 1250, DimensionalLevel.D1)

# 批量记录
mon.record_batch({
    "accuracy": 0.88,
    "latency": 45,
    "error_rate": 0.02,
}, DimensionalLevel.D2)

# 检测涌现
signals = mon.check_emergence()
for sig in signals:
    print(f"{sig.description} | σ={sig.deviation_sigma:.1f} | 置信度={sig.confidence:.2f}")

# 健康报告
print(mon.health_report())
```

### 2. 离线批次分析 (三层扫描)

```python
from infrastructure import EmergenceEngine

engine = EmergenceEngine()

# 一层扫描: 异常→突变→理论匹配
data = {
    "years": [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025],
    "body_size": [100, 95, 88, 105, 130, 175, 210, 260],
    "diversity": [35, 34, 33, 32, 33, 34, 35, 36],
}

results = engine.scan(data=data, species="鳤 (Ochetobius elongatus)")
for r in results:
    if r["detection_type"] == "theory_match":
        print(f"理论: {r['pattern_name']} ({r['suggested_theory']}) 置信度={r['confidence']:.3f}")
```

### 3. 自组织领域发现

```python
from infrastructure import emerge_domains, record_search_result

# 记录搜索反馈
record_search_result("鳤 洄游路线", db="fishbase", result_count=12, useful=True)
record_search_result("鳤 保护", db="cnki", result_count=8, useful=True)

# 发现跨领域聚类
catalog = {"domains": {"fishbase": {"label": "FishBase"}, "cnki": {"label": "中国知网"}}}
suggestions = emerge_domains(catalog)
for s in suggestions:
    print(f"新领域: {s['label']} (置信度={s['confidence']:.2f})")
```

### 4. 鱼类图像分类

```python
from infrastructure import classify_60fish, extract_features_dinov2

# 60 种常见鱼类快速分类
predictions = classify_60fish("fish.jpg")
# → [("Carassius auratus", 0.95), ...]

# DINOv2 自监督特征 (少样本长江特有种)
features = extract_features_dinov2("rare_fish.jpg")
# → 768维向量
```

### 5. 中文生态学 NLP

```python
from infrastructure import segment, ner, synonym_search

# 分词 + 词性标注
words = segment("2024年长江安庆段刀鲚资源调查")
# → [("2024年", "TIME"), ("长江", "NS"), ...]

# 命名实体识别
entities = ner("刀鲚洄游群体在鄱阳湖产卵场聚集")
# → [{"text":"刀鲚","type":"SPECIES"}, {"text":"鄱阳湖","type":"LOCATION"}, ...]

# 同义词匹配
synonyms = synonym_search("刀鲚")
# → ["长江刀鱼", "Coilia nasus", "刀鱼", "长颌鲚"]
```

### 6. 鱼群目标检测

```python
from infrastructure import detect_image, process_video

# 单张图片检测
detections = detect_image("underwater.jpg", conf=0.25)
# → [{"bbox":[x1,y1,x2,y2], "confidence":0.87, "class":"fish"}, ...]

# 视频帧采样检测
process_video("survey.mp4", output_dir="results/", fps_sample=10)
```

---

## API 参考

### 核心数据类型

| 类型 | 说明 |
|:-----|:-----|
| `EmergenceType` | 涌现类型枚举: BENEFICIAL / NEUTRAL / HARMFUL / PHASE_TRANSITION / ANOMALY |
| `DimensionalLevel` | 维度等级 D₀(Point) / D₁(Line) / D₂(Plane) / D₃(Body) |
| `EmergenceSignal` | 实时涌现事件信号 (id, timestamp, sources, deviation_sigma, confidence, ...) |
| `DetectionResult` | 离线批次分析检测结果 (detection_type, species, evidence, suggested_theory, ...) |
| `MetricTracker` | Welford 在线方差追踪器 (mean, std, deviation_sigma, stats) |

### 核心类

| 类 | 方法 | 说明 |
|:---|:-----|:-----|
| `EmergenceMonitor` | `record()`, `record_batch()`, `check_emergence()`, `health_report()` | 实时涌现监控 |
| `DimensionalEmergenceMonitor` | `track_dimension_transition()`, `check_dimensional_emergence()` | 维度跃迁监控 |
| `EmergenceEngine` | `detect_anomalies()`, `detect_change_points()`, `match_theory()`, `scan()` | 离线三层分析 |

### 工具函数

| 函数 | 说明 |
|:-----|:-----|
| `emerge_domains(catalog)` | 自组织领域发现 — 分析反馈日志，发现跨领域 DB 聚类 |
| `record_search_result(query, db, count, useful)` | 记录搜索反馈到日志文件 |

### 模块级函数 (fish_classifier / chinese_nlp / fish_detector)

| 函数 | 模块 | 说明 |
|:-----|:-----|:-----|
| `classify_60fish(image_path)` | fish_classifier | 60fishmodel 分类，返回 [(物种, 置信度), ...] |
| `extract_features_dinov2(image_path)` | fish_classifier | DINOv2 768维特征向量 |
| `download_fishvista()` | fish_classifier | 下载 Fish-Vista 数据集 (1900种) |
| `segment(text)` | chinese_nlp | Jiagu 分词 + 词性标注 |
| `ner(text)` | chinese_nlp | 自定义词典 NER 实体识别 |
| `synonym_search(word)` | chinese_nlp | 生态学术语同义词匹配 |
| `detect_image(image_path, conf)` | fish_detector | YOLO 单张图片鱼类检测 |
| `process_video(video_path, output_dir, fps_sample)` | fish_detector | 视频帧采样鱼群检测 |

---

## 项目结构

```
infrastructure/
├── unified_emergence.py    # 统一涌现引擎 (融合 p/f/c 三项目)
├── fish_classifier.py      # HuggingFace 鱼类识别 (60fish/Fish-Vista/DINOv2)
├── chinese_nlp.py          # 中文生态学 NLP (Jiagu/Synonyms)
├── fish_detector.py        # YOLO 鱼群检测 (FishDet-M)
├── src/
│   └── __init__.py         # 统一导出接口
├── tests/
│   ├── test_unified_emergence.py   # 涌现引擎测试 (30项)
│   └── test_integration.py         # 集成测试
├── pyproject.toml          # 项目元数据与依赖声明
└── README.md               # 本文件
```

---

## 开发

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行所有测试
pytest tests/ -v

# 运行集成测试
pytest tests/test_integration.py -v

# 带覆盖率
pytest tests/ -v --cov=infrastructure --cov-report=term
```

---

## 相关资源

- **权威架构:** [`docs/SANSHENG_WANWU.md`](https://github.com/NeroZ02/Reasonix/blob/main/docs/SANSHENG_WANWU.md)
- **运行流程:** [`docs/EXECUTION_FLOW.md`](https://github.com/NeroZ02/Reasonix/blob/main/docs/EXECUTION_FLOW.md)
- **项目关系:** [`docs/PROJECT_RELATIONSHIPS.md`](https://github.com/NeroZ02/Reasonix/blob/main/docs/PROJECT_RELATIONSHIPS.md)
- **协调配置:** `coordination.yaml`
- **方陶文库:** `../方陶文库/` — 个人知识库 (生态学理论 · 中国生态哲学 · 分析报告 · 科幻)

---

> ⚡ *"涌现不只是现象 — 它是系统向更高复杂度跃迁的证明。"*
