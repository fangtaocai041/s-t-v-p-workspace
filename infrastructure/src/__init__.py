"""
src/__init__.py — 统一集成接口
==============================
提供 infrastructure 四个模块的统一导入入口。

用法:
    from infrastructure.src import (
        # 涌现引擎
        EmergenceMonitor, EmergenceEngine, DimensionalEmergenceMonitor,
        emerge_domains,
        # 鱼类分类
        classify_60fish, extract_features_dinov2, download_fishvista,
        # 中文 NLP
        segment, ner, synonym_search, ECOLOGY_DICT,
        # 鱼群检测
        detect_image, process_video,
    )
"""

from infrastructure.unified_emergence import (
    EmergenceType,
    DimensionalLevel,
    EmergenceSignal,
    DetectionResult,
    MetricTracker,
    EmergenceMonitor,
    DimensionalEmergenceMonitor,
    EmergenceEngine,
    KNOWN_PATTERNS,
    record_search_result,
    emerge_domains,
)

from infrastructure.fish_classifier import (
    MODELS,
    classify_60fish,
    extract_features_dinov2,
    download_fishvista,
    benchmark as fish_benchmark,
)

from infrastructure.chinese_nlp import (
    ECOLOGY_DICT,
    segment,
    ner,
    synonym_search,
)

from infrastructure.fish_detector import (
    detect_image,
    process_video,
)

# ── 统一导出列表 ────────────────────────────────────────────

__all__ = [
    # unified_emergence
    "EmergenceType",
    "DimensionalLevel",
    "EmergenceSignal",
    "DetectionResult",
    "MetricTracker",
    "EmergenceMonitor",
    "DimensionalEmergenceMonitor",
    "EmergenceEngine",
    "KNOWN_PATTERNS",
    "record_search_result",
    "emerge_domains",
    # fish_classifier
    "MODELS",
    "classify_60fish",
    "extract_features_dinov2",
    "download_fishvista",
    "fish_benchmark",
    # chinese_nlp
    "ECOLOGY_DICT",
    "segment",
    "ner",
    "synonym_search",
    # fish_detector
    "detect_image",
    "process_video",
]
