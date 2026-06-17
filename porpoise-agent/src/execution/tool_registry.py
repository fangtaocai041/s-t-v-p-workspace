"""
工具注册中心 (Tool Registry)
─────────────────────────────
管理所有可调用工具的生命周期: 注册、发现、调用。

支持:
- 同步/异步工具
- 工具元数据 (名称、描述、参数 schema)
- 人工审批标记
- 调用日志
- 降级 (fallback)
- 优雅降级 (可选依赖缺失时不崩溃)

对应五层模型中的"API调用与控制"层。
"""

import importlib
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


# ── 优雅降级: 安全导入 ──────────────────────────────────────

_IMPORT_WARNED: set[str] = set()  # 避免重复 warning

def safe_import(
    module_name: str,
    feature_name: str = "",
    pip_package: str = "",
) -> Optional[Any]:
    """
    安全导入可选依赖模块，缺失时打印 warning 并返回 None。

    用法:
        librosa = safe_import("librosa", feature_name="声学分析", pip_package="librosa")
        if librosa is None:
            return {"error": "librosa 未安装，声学分析不可用"}
    """
    try:
        return importlib.import_module(module_name)
    except ImportError:
        pkg = pip_package or module_name.split(".")[0]
        feat = feature_name or module_name
        if module_name not in _IMPORT_WARNED:
            logger.warning(
                f"可选依赖缺失: {module_name} ({feat}) — "
                f"请运行 pip install porpoise-agent[{pkg}] 安装"
            )
            _IMPORT_WARNED.add(module_name)
        return None


def is_available(module_name: str) -> bool:
    """检查可选模块是否可用（无 side-effect，不打印 warning）"""
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False


def list_missing_optionals() -> dict[str, bool]:
    """
    列出所有可选依赖的可用状态。

    Returns:
        {"librosa": False, "geopandas": True, ...}
    """
    optional_map = {
        # acoustics 组
        "librosa": "acoustics",
        "obspy": "acoustics",
        # spatial 组
        "geopandas": "spatial",
        "rasterio": "spatial",
        "shapely": "spatial",
        # knowledge 组
        "neo4j": "knowledge",
        "chromadb": "knowledge",
        # ml 组
        "sklearn": "ml",
        "torch": "ml",
    }
    status = {}
    for mod, group in optional_map.items():
        status[f"{mod} ({group})"] = is_available(mod)
    return status


@dataclass
class ToolSpec:
    """工具规范"""
    name: str
    description: str
    parameters: dict = field(default_factory=dict)  # JSON Schema
    fn: Optional[Callable] = None
    requires_approval: bool = False
    is_async: bool = False
    category: str = "general"           # literature / acoustic / ecology / utility
    fallback: Optional[str] = None      # 降级工具名
    tags: list[str] = field(default_factory=list)
    version: str = "0.1.0"


@dataclass
class ToolCall:
    """工具调用记录"""
    tool_name: str
    params: dict
    result: Any = None
    error: Optional[str] = None
    start_time: float = field(default_factory=time.time)
    end_time: float = 0.0
    elapsed_ms: float = 0.0
    success: bool = True


class ToolRegistry:
    """
    工具注册中心

    用法:
        registry = ToolRegistry()
        registry.register(
            name="search_literature",
            description="Search scientific literature",
            parameters={"query": {"type": "string"}},
            fn=my_search_fn,
        )
        result = registry.call("search_literature", query="finless porpoise")
    """

    def __init__(self):
        self._tools: dict[str, ToolSpec] = {}
        self._call_history: list[ToolCall] = []
        self._on_call_hooks: list[Callable] = []
        logger.info("ToolRegistry initialized")

    def register(
        self,
        name: str,
        description: str,
        parameters: Optional[dict] = None,
        fn: Optional[Callable] = None,
        requires_approval: bool = False,
        is_async: bool = False,
        category: str = "general",
        fallback: Optional[str] = None,
        tags: Optional[list[str]] = None,
    ):
        """
        注册工具

        Args:
            name: 工具名称 (唯一标识)
            description: 描述 (用于 LLM tool choice)
            parameters: JSON Schema 参数定义
            fn: 可调用对象
            requires_approval: 是否需要人工审批
            is_async: 是否为异步函数
            category: 分类
            fallback: 降级工具名
            tags: 标签
        """
        spec = ToolSpec(
            name=name,
            description=description,
            parameters=parameters or {},
            fn=fn,
            requires_approval=requires_approval,
            is_async=is_async,
            category=category,
            fallback=fallback,
            tags=tags or [],
        )
        self._tools[name] = spec
        logger.info(f"Tool registered: {name} [{category}]")

    def unregister(self, name: str):
        """注销工具"""
        self._tools.pop(name, None)
        logger.info(f"Tool unregistered: {name}")

    def get(self, name: str) -> Optional[ToolSpec]:
        """获取工具规范"""
        return self._tools.get(name)

    def list_tools(self, category: Optional[str] = None) -> list[ToolSpec]:
        """列出所有工具 (可按分类筛选)"""
        tools = list(self._tools.values())
        if category:
            tools = [t for t in tools if t.category == category]
        return tools

    def get_specs_for_llm(self) -> list[dict]:
        """
        获取 LLM tool choice 格式的工具规范

        Returns:
            list[dict]: OpenAI-compatible tool specs
        """
        specs = []
        for tool in self._tools.values():
            spec = {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": {
                        "type": "object",
                        "properties": tool.parameters,
                        "required": list(tool.parameters.keys()),
                    } if tool.parameters else {
                        "type": "object",
                        "properties": {},
                    },
                },
            }
            specs.append(spec)
        return specs

    def call(self, name: str, **params) -> Any:
        """
        调用工具

        Args:
            name: 工具名
            **params: 参数

        Returns:
            工具返回值

        Raises:
            ValueError: 工具不存在
            Exception: 工具执行异常
        """
        tool = self._tools.get(name)
        if not tool:
            raise ValueError(f"Unknown tool: {name}. Available: {list(self._tools.keys())}")

        call_record = ToolCall(tool_name=name, params=params)

        try:
            if tool.requires_approval:
                logger.warning(f"Tool {name} requires human approval — "
                               f"auto-approving for non-interactive mode")
                # 在实际部署中，此处应返回等待审批状态

            if tool.fn is None:
                result = {"status": "not_implemented", "tool": name}
                call_record.success = False
                call_record.error = "Tool function not implemented"
            else:
                result = tool.fn(**params)

            call_record.result = result

        except Exception as e:
            logger.error(f"Tool {name} failed: {e}")
            call_record.success = False
            call_record.error = str(e)

            # 尝试降级
            if tool.fallback:
                fallback_tool = self._tools.get(tool.fallback)
                if fallback_tool and fallback_tool.fn:
                    logger.info(f"Falling back to {tool.fallback}")
                    try:
                        result = fallback_tool.fn(**params)
                        call_record.result = result
                        call_record.success = True
                        call_record.error = None
                    except Exception as fe:
                        call_record.error = f"{e}; fallback also failed: {fe}"

            if not call_record.success:
                raise

        finally:
            call_record.end_time = time.time()
            call_record.elapsed_ms = (call_record.end_time - call_record.start_time) * 1000
            self._call_history.append(call_record)

            # 触发 hooks
            for hook in self._on_call_hooks:
                try:
                    hook(call_record)
                except Exception as he:
                    logger.debug(f"Hook failed: {he}")

        return result

    def call_with_fallback(
        self,
        name: str,
        fallback_chain: Optional[list[str]] = None,
        **params,
    ) -> tuple[Any, str]:
        """
        带降级链的工具调用

        Args:
            name: 首选工具名
            fallback_chain: 降级链 [fb1, fb2, ...]
            **params: 参数

        Returns:
            (result, tool_used)
        """
        chain = [name] + (fallback_chain or [])
        last_error = None

        for tool_name in chain:
            try:
                result = self.call(tool_name, **params)
                return result, tool_name
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Tool {tool_name} failed: {e}, trying next...")

        raise RuntimeError(f"All tools in chain failed. Last error: {last_error}")

    def add_hook(self, hook: Callable):
        """添加调用钩子 (每次工具调用后触发)"""
        self._on_call_hooks.append(hook)

    def get_history(
        self,
        limit: int = 20,
        success_only: bool = False,
    ) -> list[ToolCall]:
        """获取调用历史"""
        history = self._call_history
        if success_only:
            history = [h for h in history if h.success]
        return history[-limit:]

    def stats(self) -> dict:
        """工具注册中心统计"""
        by_category = {}
        for tool in self._tools.values():
            by_category.setdefault(tool.category, 0)
            by_category[tool.category] += 1

        total_calls = len(self._call_history)
        success_rate = (
            sum(1 for h in self._call_history if h.success) / max(total_calls, 1) * 100
        )

        return {
            "total_tools": len(self._tools),
            "by_category": by_category,
            "total_calls": total_calls,
            "success_rate": f"{success_rate:.1f}%",
        }

    def register_builtin_tools(self) -> dict[str, bool]:
        """
        注册内建工具，自动跳过缺失可选依赖的功能。

        每个可选依赖组在导入失败时只打印一次 warning。

        Returns:
            dict: {"acoustics": True, "spatial": False, ...} 各组注册状态
        """
        status: dict[str, bool] = {}

        # ── 声学分析工具 ──
        librosa_ok = is_available("librosa")
        if librosa_ok:
            self.register(
                name="detect_clicks",
                description="检测 NBHF click 脉冲 (100-180 kHz)",
                parameters={
                    "audio_path": {"type": "string", "description": "音频文件路径"},
                    "threshold_db": {"type": "number", "description": "检测阈值 dB"},
                },
                fn=None,  # 由 AcousticAgent 提供实现
                category="acoustic",
                tags=["nbhf", "click", "acoustic"],
            )
            logger.info("Acoustic tools registered (librosa available)")
        else:
            logger.warning(
                "Acoustic tools skipped — librosa not installed. "
                "Run: pip install porpoise-agent[acoustics]"
            )
        status["acoustics"] = librosa_ok

        # ── 空间分析工具 ──
        geopandas_ok = is_available("geopandas")
        if geopandas_ok:
            self.register(
                name="habitat_model",
                description="栖息地建模与空间分析",
                parameters={
                    "species": {"type": "string"},
                    "region": {"type": "string"},
                    "env_layers": {"type": "array"},
                },
                fn=None,
                category="spatial",
                tags=["habitat", "gis", "modeling"],
            )
            logger.info("Spatial tools registered (geopandas available)")
        else:
            logger.warning(
                "Spatial tools skipped — geopandas not installed. "
                "Run: pip install porpoise-agent[spatial]"
            )
        status["spatial"] = geopandas_ok

        # ── 知识图谱工具 ──
        chromadb_ok = is_available("chromadb")
        if chromadb_ok:
            self.register(
                name="vector_search",
                description="向量相似度搜索 (ChromaDB)",
                parameters={
                    "query": {"type": "string"},
                    "collection": {"type": "string"},
                    "n_results": {"type": "integer"},
                },
                fn=None,
                category="knowledge",
                tags=["vector", "semantic", "chromadb"],
            )
            logger.info("Knowledge tools registered (chromadb available)")
        else:
            logger.warning(
                "Knowledge tools (chromadb) skipped — chromadb not installed. "
                "Run: pip install porpoise-agent[knowledge]"
            )
        status["knowledge"] = chromadb_ok

        # ── ML 工具 ──
        sklearn_ok = is_available("sklearn")
        if sklearn_ok:
            self.register(
                name="classify",
                description="机器学习分类 (scikit-learn)",
                parameters={
                    "data": {"type": "array"},
                    "labels": {"type": "array"},
                    "method": {"type": "string", "description": "分类方法 (rf/svm/knn)"},
                },
                fn=None,
                category="ml",
                tags=["classification", "sklearn"],
            )
            logger.info("ML tools registered (sklearn available)")
        else:
            logger.warning(
                "ML tools skipped — scikit-learn not installed. "
                "Run: pip install porpoise-agent[ml]"
            )
        status["ml"] = sklearn_ok

        return status


# ── 快捷注册函数 ────────────────────────────────────────────

def tool(
    name: str,
    description: str = "",
    parameters: Optional[dict] = None,
    category: str = "general",
    requires_approval: bool = False,
):
    """
    装饰器: 快速注册工具

    用法:
        @tool("search_literature", description="Search papers", category="literature")
        def search(query: str, limit: int = 10) -> dict:
            ...
    """
    def decorator(fn: Callable):
        # 注册到全局 registry
        from src.execution.tool_registry import tools as global_registry
        global_registry.register(
            name=name,
            description=description or (fn.__doc__ or "").strip(),
            parameters=parameters or {},
            fn=fn,
            category=category,
            requires_approval=requires_approval,
        )
        return fn
    return decorator


# 全局工具注册中心实例
tools = ToolRegistry()
