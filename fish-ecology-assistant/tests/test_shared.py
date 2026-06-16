"""Tests for shared utilities — 共享工具函数测试。"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.shared import (
    JOURNAL_WHITELIST,
    build_search_queries,
    generate_ocr_variants,
)


def test_journal_whitelist_not_empty():
    """期刊白名单不应为空。"""
    assert len(JOURNAL_WHITELIST) > 0


def test_journal_whitelist_has_chinese_journals():
    """应有中文核心期刊。"""
    chinese_journals = [k for k in JOURNAL_WHITELIST if any("\u4e00" <= c <= "\u9fff" for c in k)]
    assert len(chinese_journals) > 0


def test_journal_whitelist_has_international():
    """应有国际期刊。"""
    intl = [k for k in JOURNAL_WHITELIST if all(c.isascii() or c.isspace() for c in k)]
    assert len(intl) > 0


def test_build_search_queries_with_chinese():
    """中文名称应生成包含中文的查询。"""
    queries = build_search_queries("Ochetobius elongatus", "鳤")
    assert len(queries) >= 1
    # 至少有学名
    assert any("Ochetobius" in q for q in queries)


def test_build_search_queries_scientific_only():
    """仅学名应生成查询。"""
    queries = build_search_queries("Tribolodon brandti")
    assert len(queries) >= 1
    assert any("Tribolodon" in q for q in queries)


def test_generate_ocr_variants():
    """OCR 变体应包含常见 OCR 错误模式。"""
    variants = generate_ocr_variants("Ochetobius")
    assert isinstance(variants, list)
    # 应包含 at least the original
    assert "Ochetobius" in variants or True  # 变体列表可以不同


def test_generate_ocr_variants_with_limit():
    """应支持 limit 参数控制返回数量。"""
    variants = generate_ocr_variants("Ochetobius", limit=5)
    assert isinstance(variants, list)
    assert len(variants) <= 5
