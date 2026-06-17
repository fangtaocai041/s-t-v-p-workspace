#!/usr/bin/env python3
"""conflict-arbiter CLI — 物种保护等级冲突仲裁命令行工具 (火 🟥)

用法:
    # 单物种仲裁 (本地数据)
    python scripts/arbitrate.py --species "Coilia nasus"

    # 单物种仲裁 (含实时 API)
    python scripts/arbitrate.py --species "Coilia nasus" --live

    # 从文件批量仲裁
    python scripts/arbitrate.py --species-file species.txt --output report.json

    # 从 YAML 索引批量仲裁
    python scripts/arbitrate.py --batch fish_species_index.yaml --output report.json

    # 指定区域策略
    python scripts/arbitrate.py --species "Acipenser sinensis" --region global

    # 导出完整报告 (含 API 元数据)
    python scripts/arbitrate.py --species "Anguilla japonica" --live --verbose

环境变量:
    IUCN_API_KEY     — IUCN Red List API v4 token
    CITES_API_KEY    — CITES Species+ API token
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import List

# 确保项目 src/ 在 sys.path 中
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_src = _PROJECT_ROOT / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))


def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="conflict-arbiter — 物种保护等级冲突仲裁工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --species "Coilia nasus"
  %(prog)s --species "Acipenser sinensis" --live --verbose
  %(prog)s --species-file species.txt --output report.json
  %(prog)s --batch index.yaml --region global
        """,
    )

    # 输入组 (互斥)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--species", "-s",
        type=str,
        help="单个物种学名 (如 'Coilia nasus')",
    )
    input_group.add_argument(
        "--species-file", "-f",
        type=str,
        help="物种列表文件, 每行一个学名",
    )
    input_group.add_argument(
        "--batch", "-b",
        type=str,
        help="YAML 物种索引文件, 格式见 fish_species_index.yaml 示例",
    )

    # 选项
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="输出 JSON 报告文件路径 (默认输出到 stdout)",
    )
    parser.add_argument(
        "--region", "-r",
        type=str,
        default="china",
        choices=["china", "global"],
        help="区域策略: china (中国权威) | global (常规加权). 默认: china",
    )
    parser.add_argument(
        "--live", "-l",
        action="store_true",
        help="启用 IUCN/CITES 实时 API 查询 (需要 API key)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="详细输出 (含 API 元数据、调试信息)",
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="arbiter 配置文件路径 (默认: config/agent.yaml)",
    )
    parser.add_argument(
        "--pretty", "-p",
        action="store_true",
        default=True,
        help="格式化 JSON 输出 (默认启用)",
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="紧凑 JSON 输出 (覆盖 --pretty)",
    )
    parser.add_argument(
        "--cache-dir",
        type=str,
        default=None,
        help="缓存目录 (默认: ~/.conflict_arbiter_cache/)",
    )

    return parser.parse_args(argv)


def load_species_list(filepath: str) -> List[str]:
    """从文本文件加载物种列表 (每行一个学名)。"""
    path = Path(filepath)
    if not path.is_file():
        print(f"错误: 文件不存在 — {filepath}", file=sys.stderr)
        sys.exit(1)
    species = []
    text = path.read_text(encoding="utf-8-sig")  # utf-8-sig 自动去除 BOM
    for line in text.splitlines():
        name = line.strip()
        if name and not name.startswith("#"):
            species.append(name)
    return species


def load_yaml_batch(filepath: str) -> List[str]:
    """从 YAML 索引文件加载物种列表。"""
    path = Path(filepath)
    if not path.is_file():
        print(f"错误: 文件不存在 — {filepath}", file=sys.stderr)
        sys.exit(1)
    try:
        import yaml
    except ImportError:
        print("错误: 需要 pyyaml 来解析 YAML 文件", file=sys.stderr)
        sys.exit(1)

    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        print(f"错误: YAML 解析失败 — {exc}", file=sys.stderr)
        sys.exit(1)

    # 支持多种 YAML 结构
    if isinstance(data, list):
        return [str(item) if isinstance(item, str) else item.get("name", str(item)) for item in data]
    if isinstance(data, dict):
        # {"species": ["...", "..."]} 或 {"Coilia nasus": {...}, ...}
        if "species" in data:
            return data["species"]
        return list(data.keys())
    print("错误: 无法识别的 YAML 结构", file=sys.stderr)
    sys.exit(1)


def main(argv: List[str] | None = None) -> None:
    args = parse_args(argv)

    # 日志级别
    log_level = logging.DEBUG if args.verbose else logging.WARNING
    logging.basicConfig(level=log_level, format="%(levelname)s: %(message)s")

    # 缓存目录
    if args.cache_dir:
        import os
        os.environ["CONFLICT_ARBITER_CACHE_DIR"] = args.cache_dir

    # 配置文件
    config_path = None
    if args.config:
        config_path = Path(args.config)
    else:
        default_cfg = _PROJECT_ROOT / "config" / "agent.yaml"
        if default_cfg.is_file():
            config_path = default_cfg

    from arbiter import ConflictArbiter

    # ── 执行 ──
    if args.species:
        # 单物种
        arbiter = ConflictArbiter(config_path=config_path)
        if args.live:
            result = ConflictArbiter.from_live_data(
                species_name=args.species,
                region=args.region,
                config_path=config_path,
            )
        else:
            local_sources = ConflictArbiter._load_local_species_data(args.species)
            result = arbiter.detect_conflicts(
                species_name=args.species,
                sources=local_sources,
                region=args.region,
            )
        _output(result, args)
    else:
        # 批量
        if args.species_file:
            species_list = load_species_list(args.species_file)
        else:
            species_list = load_yaml_batch(args.batch)

        arbiter = ConflictArbiter(config_path=config_path)
        batch_result = arbiter.batch_arbitrate(
            species_list=species_list,
            region=args.region,
            use_api=args.live,
        )
        _output(batch_result, args)


def _output(data: dict, args: argparse.Namespace) -> None:
    """输出结果到文件或 stdout。"""
    indent = 2 if args.pretty and not args.compact else None
    json_str = json.dumps(data, ensure_ascii=False, default=str, indent=indent)

    if args.output:
        Path(args.output).write_text(json_str, encoding="utf-8")
        print(f"报告已保存: {args.output}")
    else:
        # 处理 Windows 控制台 GBK 编码问题
        try:
            print(json_str)
        except UnicodeEncodeError:
            # 回退: 使用 ASCII 安全模式, 或替换不可编码字符
            safe = json.dumps(data, ensure_ascii=True, default=str, indent=indent)
            print(safe)


if __name__ == "__main__":
    main()
