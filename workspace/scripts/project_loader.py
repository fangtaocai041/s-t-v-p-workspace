#!/usr/bin/env python
"""project_loader.py — 子项目适配器加载器

为 workspace 的 _get_adapter() 提供各子项目的适配器实例。
利用 __init__.py 已设置的 sys.path（含 _PROJECTS_ROOT 下各子项目路径），
使用 importlib 加载各项目的 adapter 模块。

每个适配器必须实现 IProjectAdapter 协议:
    adapter.search(query: str, **kwargs) → dict
"""

from __future__ import annotations

import importlib
import logging
import sys
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# 已缓存的适配器实例
_adapters: Dict[str, Any] = {}


def _import_project_adapter(
    project_key: str,
    project_dir: str,
    rel_path: str,
    class_name: str,
) -> Optional[Any]:
    """用 importlib.util 从文件路径直接加载适配器。

    避免 src 命名空间冲突 — 每个子项目都有自己的 src/，而 sys.path
    只有一个，所以用 spec_from_file_location 直接指定文件路径。
    """
    if project_key in _adapters:
        return _adapters[project_key]

    import importlib.util

    try:
        # 适配器文件路径: PROJECTS_ROOT / project_dir / rel_path
        from pathlib import Path
        proj_root = Path(__file__).resolve().parent.parent.parent / project_dir
        file_path = proj_root / rel_path

        if not file_path.is_file():
            logger.debug(f"Adapter file not found: {file_path}")
            return None

        spec = importlib.util.spec_from_file_location(
            f"{project_key}_adapter",
            str(file_path),
        )
        if spec is None or spec.loader is None:
            return None

        mod = importlib.util.module_from_spec(spec)
        # 先添加到 sys.modules 防止递归导入
        sys.modules[f"_{project_key}_adapter_loader"] = mod
        spec.loader.exec_module(mod)

        cls = getattr(mod, class_name, None)
        if cls is None:
            logger.warning(f"Adapter class {class_name} not found in {file_path}")
            return None

        adapter = cls()
        _adapters[project_key] = adapter
        return adapter
    except Exception as e:
        logger.debug(f"Failed to load {project_key} adapter from {project_dir}: {e}")
        return None


def get_fish() -> Optional[Any]:
    """加载 fish-ecology-assistant (V0/S-State) 适配器。"""
    return _import_project_adapter(
        "fish",
        "fish-ecology-assistant",
        "src/adapter.py",
        "FishEcologyAdapter",
    )


def get_cognitive() -> Optional[Any]:
    """加载 cognitive-search-engine (V1) 适配器。"""
    return _import_project_adapter(
        "cognitive",
        "cognitive-search-engine",
        "src/adapter.py",
        "CognitiveSearchAdapter",
    )


def get_porpoise() -> Optional[Any]:
    """加载 porpoise-agent (V2/P₁) 适配器。"""
    return _import_project_adapter(
        "porpoise",
        "porpoise-agent",
        "src/adapter.py",
        "PorpoiseAdapter",
    )


def get_coilia() -> Optional[Any]:
    """加载 coilia-agent (V3/P₂) 适配器。"""
    return _import_project_adapter(
        "coilia",
        "coilia-agent",
        "src/adapter.py",
        "CoiliaAdapter",
    )


def get_culter() -> Optional[Any]:
    """加载 culter-agent (V4/P₃) 适配器。"""
    return _import_project_adapter(
        "culter",
        "culter-agent",
        "src/adapter.py",
        "CulterAdapter",
    )


def get_conflict() -> Optional[Any]:
    """加载 conflict-arbiter (🔥) 适配器。"""
    return _import_project_adapter(
        "conflict",
        "conflict-arbiter",
        "src/adapter.py",
        "ConflictArbiterAdapter",
    )


def reload_all():
    """清除缓存，下次调用时重新加载所有适配器。"""
    _adapters.clear()
    for loader in [get_fish, get_cognitive, get_porpoise, get_coilia, get_culter, get_conflict]:
        try:
            loader()
        except Exception:
            pass
