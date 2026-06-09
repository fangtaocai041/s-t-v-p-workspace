"""
IProjectAdapter — 四项目统一适配器协议 (ABC)

所有4个领域项目 (fish/cognitive/porpoise/coilia) 的适配器
必须实现此接口。project_loader.py 和所有 adapter.py 均从此模块导入，
避免循环依赖。

用法:
    from scripts.adapter_protocol import IProjectAdapter
    class MyAdapter(IProjectAdapter): ...
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class IProjectAdapter(ABC):
    """标准适配器接口 — 四项目必须实现。

    每个领域项目的 adapter.py 暴露:
      - search(query, **kwargs) → dict     (执行搜索/查询)
      - health() → dict                     (返回健康状态)
      - info() → dict                       (返回版本 + 能力信息)

    验证: scripts/project_loader.py 在加载时检查 isinstance(adapter, IProjectAdapter)
    """

    project_name: str = ""

    @abstractmethod
    def search(self, query: str, **kwargs) -> Dict[str, Any]:
        """执行领域特定搜索或查询。"""
        ...

    @abstractmethod
    def health(self) -> Dict[str, Any]:
        """返回健康状态。"""
        ...

    @abstractmethod
    def info(self) -> Dict[str, Any]:
        """返回版本 + 能力信息。"""
        ...
