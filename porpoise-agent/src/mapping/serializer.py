"""
工程语言化序列化器 (Engineering Language Serializer)
─────────────────────────────────────────────────────
将自然语言决策精确转化为机器语言格式。

LLM 输出 → 计算机可执行格式:
- Python 代码生成 (数据分析脚本)
- SQL 查询构建 (数据库查询)
- JSON 对象格式化 (API 参数 / 工具调用)
- HTTP 请求参数构建 (RESTful API)

对应五层模型中的"工程语言化 (Serialization)":
    NL 决策 → 结构化指令 → 执行

核心原则:
    自然语言描述 → 可执行的函数签名
    "计算财务指标" → financial_metrics(df).compute()
"""

import json
import logging
import re
import ast
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class SerializedFormat(str, Enum):
    """序列化目标格式"""
    PYTHON = "python"           # Python 代码
    SQL = "sql"                 # SQL 查询
    JSON = "json"               # JSON 对象
    HTTP_REQUEST = "http"       # HTTP 请求
    FUNCTION_CALL = "fn_call"   # 函数调用


@dataclass
class SerializedOutput:
    """序列化输出"""
    format: SerializedFormat
    code: str                           # 序列化后的代码/指令
    original_nl: str                    # 原始自然语言描述
    params: dict = field(default_factory=dict)  # 提取的参数
    errors: list[str] = field(default_factory=list)
    needs_sandbox: bool = False         # 是否需要沙盒执行


# ── 序列化器 ───────────────────────────────────────────────

class EngineeringSerializer:
    """
    工程语言序列化器 — NL → 可执行代码

    三通道:
    1. Python: 数据分析 / 科学计算
    2. SQL: 数据库查询
    3. JSON: API 参数 / 工具调用

    用法:
        serializer = EngineeringSerializer()
        output = serializer.serialize(
            nl="计算江豚 click 脉冲的 ICI 均值和标准差",
            target_format=SerializedFormat.PYTHON,
        )
        # → Python 代码
    """

    def __init__(self, llm_client: Any = None):
        self.llm = llm_client
        self._template_cache: dict[str, str] = {}

        # 预定义模板
        self._init_templates()

        logger.info("EngineeringSerializer initialized")

    def _init_templates(self):
        """初始化代码模板"""
        self._template_cache = {
            # Python 声学分析模板
            "acoustic_analysis": """
import numpy as np
import librosa

def analyze_clicks(audio_path: str, threshold_db: float = -134.0):
    \"\"\"分析声学文件中的 click 脉冲\"\"\"
    y, sr = librosa.load(audio_path, sr=None)
    # 带通滤波 100-180 kHz
    from scipy.signal import butter, filtfilt
    nyq = sr / 2
    b, a = butter(4, [100000/nyq, 180000/nyq], btype='band')
    y_filt = filtfilt(b, a, y)
    # SPL 阈值检测
    rms = librosa.feature.rms(y=y_filt)[0]
    rms_db = 20 * np.log10(rms + 1e-10)
    clicks = np.where(rms_db > threshold_db)[0]
    return {"n_clicks": len(clicks), "rms_db": rms_db.tolist()}
""",
            # SQL 查询模板
            "species_query": """
SELECT * FROM observations
WHERE species = '{species}'
  AND date BETWEEN '{start_date}' AND '{end_date}'
ORDER BY date DESC
LIMIT {limit};
""",
            # JSON 工具调用模板
            "tool_call": """
{
  "tool": "{tool_name}",
  "parameters": {params_json}
}
""",
        }

    def serialize(
        self,
        nl: str,
        target_format: SerializedFormat = SerializedFormat.FUNCTION_CALL,
        context: Optional[dict] = None,
    ) -> SerializedOutput:
        """
        序列化: NL → 可执行格式

        Args:
            nl: 自然语言描述
            target_format: 目标格式
            context: 附加上下文 (变量、数据源等)

        Returns:
            SerializedOutput: 序列化结果
        """
        context = context or {}

        if target_format == SerializedFormat.PYTHON:
            return self._serialize_python(nl, context)
        elif target_format == SerializedFormat.SQL:
            return self._serialize_sql(nl, context)
        elif target_format == SerializedFormat.JSON:
            return self._serialize_json(nl, context)
        elif target_format == SerializedFormat.HTTP_REQUEST:
            return self._serialize_http(nl, context)
        elif target_format == SerializedFormat.FUNCTION_CALL:
            return self._serialize_fn_call(nl, context)
        else:
            return SerializedOutput(
                format=target_format,
                code="",
                original_nl=nl,
                errors=[f"Unknown format: {target_format}"],
            )

    # ── Python 序列化 ────────────────────────────────

    def _serialize_python(
        self, nl: str, context: dict
    ) -> SerializedOutput:
        """NL → Python 代码"""
        nl_lower = nl.lower()
        errors = []

        # 模板匹配
        if any(kw in nl_lower for kw in ["声学", "acoustic", "click", "wav", "脉冲"]):
            template = self._template_cache["acoustic_analysis"]
            # 提取参数
            params = {
                "audio_path": context.get("audio_path", "data/input.wav"),
                "threshold_db": context.get("threshold_db", -134.0),
            }
            code = template.strip()
            needs_sandbox = True

        elif any(kw in nl_lower for kw in ["统计", "统计", "mean", "std", "平均"]):
            params = self._extract_python_params(nl)
            code = self._generate_python_stats(params, context)
            needs_sandbox = True

        elif any(kw in nl_lower for kw in ["绘图", "plot", "图表", "可视化"]):
            code = self._generate_python_plot(nl, context)
            needs_sandbox = True

        else:
            # 通用 Python: 用 docstring 包裹自然语言描述
            code = f'"""\n{nl}\n"""\n# TODO: Implement based on the description above\npass'
            needs_sandbox = False
            errors.append("No specific template matched — generated stub")

        return SerializedOutput(
            format=SerializedFormat.PYTHON,
            code=code,
            original_nl=nl,
            params=params if 'params' in dir() else {},
            errors=errors,
            needs_sandbox=needs_sandbox,
        )

    def _extract_python_params(self, nl: str) -> dict:
        """从 NL 中提取 Python 相关参数"""
        params = {}

        # 提取列名
        col_match = re.findall(r'["\'](\w+)["\']|\b(列|字段|变量)\s*["\']?(\w+)', nl)
        if col_match:
            params["columns"] = [m[0] or m[2] for m in col_match if m[0] or m[2]]

        # 提取数值
        num_matches = re.findall(r'(\d+\.?\d*)', nl)
        if num_matches:
            params["numeric_args"] = [float(n) for n in num_matches[:5]]

        return params

    def _generate_python_stats(self, params: dict, context: dict) -> str:
        """生成 Python 统计分析代码"""
        cols = params.get("columns", ["data"])
        cols_str = json.dumps(cols)
        return f'''
import pandas as pd
import numpy as np

# Load data
df = pd.read_csv("{context.get("data_path", "data.csv")}")

# Compute statistics for columns: {cols_str}
columns = {cols_str}
stats = df[columns].describe()
print(stats)

# Additional metrics
for col in columns:
    print(f"\\n{{col}}:")
    print(f"  Mean: {{df[col].mean():.4f}}")
    print(f"  Std:  {{df[col].std():.4f}}")
    print(f"  Min:  {{df[col].min():.4f}}")
    print(f"  Max:  {{df[col].max():.4f}}")
'''.strip()

    def _generate_python_plot(self, nl: str, context: dict) -> str:
        """生成 Python 绑图代码"""
        return '''
import matplotlib.pyplot as plt
import numpy as np

# Generate plot
fig, ax = plt.subplots(figsize=(10, 6))

# TODO: Customize based on: {nl}
x = np.linspace(0, 10, 100)
y = np.sin(x)
ax.plot(x, y)
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_title("Plot")

plt.savefig("{output_path}")
print(f"Plot saved to {{output_path}}")
'''.format(nl=nl, output_path=context.get("output_path", "output.png")).strip()

    # ── SQL 序列化 ───────────────────────────────────

    def _serialize_sql(
        self, nl: str, context: dict
    ) -> SerializedOutput:
        """NL → SQL 查询"""
        nl_lower = nl.lower()

        # 检测查询类型
        if any(kw in nl_lower for kw in ["查询", "select", "检索", "物种"]):
            template = self._template_cache["species_query"]
            sql = template.format(
                species=context.get("species", "Neophocaena"),
                start_date=context.get("start_date", "2020-01-01"),
                end_date=context.get("end_date", "2024-12-31"),
                limit=context.get("limit", 100),
            )
        else:
            # 通用 SQL
            sql = f"-- Generated from: {nl}\nSELECT * FROM observations LIMIT 100;"

        return SerializedOutput(
            format=SerializedFormat.SQL,
            code=sql,
            original_nl=nl,
            params=context,
            needs_sandbox=False,
        )

    # ── JSON 序列化 ──────────────────────────────────

    def _serialize_json(
        self, nl: str, context: dict
    ) -> SerializedOutput:
        """NL → JSON 对象 (工具调用参数)"""
        # 提取工具名
        tool_match = re.search(
            r'(调用|使用|call|use|invoke)\s*["\']?(\w+)',
            nl, re.IGNORECASE,
        )
        tool_name = tool_match.group(2) if tool_match else "unknown_tool"

        # 构建 JSON
        params = {}
        for key, value in context.items():
            if key not in ("nl", "raw"):
                params[key] = value

        json_obj = {
            "tool": tool_name,
            "parameters": params,
            "_original_nl": nl,
        }

        return SerializedOutput(
            format=SerializedFormat.JSON,
            code=json.dumps(json_obj, ensure_ascii=False, indent=2),
            original_nl=nl,
            params=params,
        )

    # ── HTTP 序列化 ──────────────────────────────────

    def _serialize_http(
        self, nl: str, context: dict
    ) -> SerializedOutput:
        """NL → HTTP 请求参数"""
        method = context.get("method", "GET")
        url = context.get("url", "https://api.example.com/")

        if method == "GET":
            params_str = "&".join(f"{k}={v}" for k, v in context.get("params", {}).items())
            http = f"{method} {url}?{params_str}"
        elif method == "POST":
            body = json.dumps(context.get("body", {}), ensure_ascii=False, indent=2)
            http = f"{method} {url}\nContent-Type: application/json\n\n{body}"
        else:
            http = f"{method} {url}"

        return SerializedOutput(
            format=SerializedFormat.HTTP_REQUEST,
            code=http,
            original_nl=nl,
            params=context.get("params", {}),
        )

    # ── 函数调用序列化 ──────────────────────────────

    def _serialize_fn_call(
        self, nl: str, context: dict
    ) -> SerializedOutput:
        """NL → 函数调用签名"""
        # 推断函数名
        fn_name = self._infer_function_name(nl)

        # 推断参数
        params = self._extract_fn_params(nl, context)

        # 构建调用字符串
        params_str = ", ".join(f"{k}={repr(v)}" for k, v in params.items())
        code = f"{fn_name}({params_str})"

        return SerializedOutput(
            format=SerializedFormat.FUNCTION_CALL,
            code=code,
            original_nl=nl,
            params=params,
        )

    def _infer_function_name(self, nl: str) -> str:
        """从 NL 推断函数名"""
        nl_lower = nl.lower()

        mapping = [
            (["搜索", "检索", "search", "find", "look up"], "search_literature"),
            (["加载", "load", "open", "read"], "load_acoustic_file"),
            (["检测", "detect", "find click"], "detect_clicks"),
            (["估计", "估算", "estimate", "compute"], "estimate_abundance"),
            (["生成", "写", "generate", "create", "draft"], "generate_report"),
            (["分析", "analyze"], "analyze_acoustic"),
            (["分类", "classify"], "classify_vocalizations"),
            (["查询", "query", "lookup"], "query_species_profile"),
            (["地理编码", "geocode", "location"], "geocode_location"),
        ]

        for keywords, fn_name in mapping:
            if any(kw in nl_lower for kw in keywords):
                return fn_name

        # 默认: 使用 NL 中的第一个动词
        words = nl.split()
        if words:
            return words[0].lower().replace(" ", "_")
        return "execute"

    def _extract_fn_params(self, nl: str, context: dict) -> dict:
        """从 NL + context 提取函数参数"""
        params = dict(context)

        # 如果没有显式参数，从 NL 提取 query
        if "query" not in params:
            # 去掉动作词，剩余作为查询
            action_words = [
                "搜索", "检索", "分析", "检测", "估计", "生成",
                "search", "find", "analyze", "detect", "generate",
            ]
            query = nl
            for word in action_words:
                query = query.replace(word, "", 1)
            params["query"] = query.strip()

        return params


# ── 快速序列化函数 ─────────────────────────────────────────

def serialize_to_tool_call(nl: str, tool_name: str, **params) -> dict:
    """
    快速序列化为工具调用 JSON

    这是最常用的序列化路径:
        NL 意图 → 工具名 + 参数 → JSON
    """
    return {
        "tool": tool_name,
        "parameters": params,
        "_nl": nl,
    }


def nl_to_python(nl: str, template: str = "") -> str:
    """NL → Python 代码快捷方式"""
    if template:
        return template.strip()
    return f'"""\n{nl}\n"""\n# TODO: Implement\npass'
