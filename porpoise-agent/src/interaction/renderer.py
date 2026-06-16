"""
响应渲染器 (Response Renderer)
───────────────────────────────
将底层执行结果包装为人类可读的自然语言或可视化格式。

支持格式:
- Markdown (默认): 结构化文本，含表格/列表/代码块
- JSON: 结构化数据，供下游程序消费
- Table: 纯 ASCII 表格 (终端友好)
- Rich: 富文本终端输出 (颜色/面板/进度条)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional
import json
import logging

logger = logging.getLogger(__name__)


class OutputFormat(str, Enum):
    """输出格式枚举"""
    MARKDOWN = "markdown"
    JSON = "json"
    TABLE = "table"
    RICH = "rich"
    PLAIN = "plain"


@dataclass
class RenderedOutput:
    """渲染后的输出"""
    content: str
    format: OutputFormat
    metadata: dict = field(default_factory=dict)


class ResponseRenderer:
    """
    响应渲染器

    将 Agent 执行结果转化为目标格式。

    用法:
        renderer = ResponseRenderer()
        output = renderer.render(result, format=OutputFormat.MARKDOWN)
        print(output.content)
    """

    def __init__(self, default_format: OutputFormat = OutputFormat.MARKDOWN):
        self.default_format = default_format
        logger.info(f"ResponseRenderer initialized (default={default_format})")

    def render(
        self,
        result: dict[str, Any],
        format: Optional[OutputFormat] = None,
        verbose: bool = False,
    ) -> RenderedOutput:
        """
        渲染执行结果

        Args:
            result: Agent 执行结果字典
            format: 目标输出格式 (None = default)
            verbose: 是否包含调试/推理细节

        Returns:
            RenderedOutput: 格式化后的输出
        """
        fmt = format or self.default_format

        if fmt == OutputFormat.MARKDOWN:
            content = self._render_markdown(result, verbose)
        elif fmt == OutputFormat.JSON:
            content = self._render_json(result, verbose)
        elif fmt == OutputFormat.TABLE:
            content = self._render_table(result, verbose)
        elif fmt == OutputFormat.RICH:
            content = self._render_markdown(result, verbose)  # fallback
        else:
            content = self._render_plain(result, verbose)

        return RenderedOutput(
            content=content,
            format=fmt,
            metadata={
                "result_keys": list(result.keys()),
            },
        )

    # ── Markdown 渲染 ──────────────────────────────────

    def _render_markdown(self, result: dict, verbose: bool) -> str:
        """渲染为结构化 Markdown"""
        lines: list[str] = []

        # 标题
        phase = result.get("phase", "")
        status = result.get("status", "completed")
        if phase:
            lines.append(f"## 📋 {self._phase_label(phase)}")

        # 状态
        icon = "✅" if status == "completed" else "⏳" if status == "pending" else "⚠️"
        lines.append(f"{icon} 状态: **{status}**")
        lines.append("")

        # 消息
        if "message" in result:
            lines.append(f"> {result['message']}")
            lines.append("")

        # 响应文本 (LLM 输出)
        if "response" in result:
            lines.append(result["response"])
            lines.append("")

        # 文献结果
        if "papers" in result:
            lines.append(f"### 📚 文献结果 ({len(result['papers'])} 篇)")
            lines.append("")
            for i, paper in enumerate(result["papers"][:10], 1):
                lines.append(self._render_paper_md(i, paper))
            if len(result.get("papers", [])) > 10:
                lines.append(f"*...还有 {len(result['papers']) - 10} 篇结果*")
            lines.append("")

        # 声学分析结果
        if "acoustic" in result:
            lines.append("### 🔊 声学分析")
            lines.append("")
            ac = result["acoustic"]
            if "n_clicks" in ac:
                lines.append(f"- 检测到 **{ac['n_clicks']}** 个 click 脉冲")
            if "n_buzzes" in ac:
                lines.append(f"- Buzz 事件: **{ac['n_buzzes']}**")
            if "foraging_index" in ac:
                lines.append(f"- 觅食活动指数: **{ac['foraging_index']:.2f}**")
            lines.append("")

        # 推理追踪 (verbose 模式)
        if verbose and "reasoning" in result:
            lines.append("### 🧠 推理追踪")
            lines.append("")
            lines.append("```")
            lines.append(str(result["reasoning"])[:2000])
            lines.append("```")
            lines.append("")

        # 错误
        if "error" in result:
            lines.append(f"### ❌ 错误")
            lines.append(f"```")
            lines.append(str(result["error"]))
            lines.append(f"```")
            lines.append("")

        # 置信度
        if "confidence" in result:
            conf = result["confidence"]
            label = "🟢 高" if conf > 0.8 else "🟡 中" if conf > 0.5 else "🔴 低"
            lines.append(f"**置信度**: {label} ({conf:.0%})")

        return "\n".join(lines)

    def _render_paper_md(self, index: int, paper: dict) -> str:
        """渲染单篇文献"""
        title = paper.get("title", "Unknown")
        authors = paper.get("authors", [])
        year = paper.get("year", "?")
        journal = paper.get("journal", "")
        doi = paper.get("doi", "")
        relevance = paper.get("relevance", "medium")

        author_str = ", ".join(authors[:3])
        if len(authors) > 3:
            author_str += f" et al."

        rel_icon = {"high": "⭐", "medium": "●", "low": "○"}.get(relevance, "●")

        lines = [
            f"{rel_icon} **{index}. {title}**",
            f"   {author_str} ({year}). *{journal}*.",
        ]
        if doi:
            lines.append(f"   DOI: [{doi}](https://doi.org/{doi})")
        if paper.get("key_findings"):
            for kf in paper["key_findings"][:2]:
                lines.append(f"   - {kf}")
        lines.append("")
        return "\n".join(lines)

    # ── JSON 渲染 ─────────────────────────────────────

    def _render_json(self, result: dict, verbose: bool) -> str:
        """渲染为 JSON"""
        output = dict(result)
        if not verbose:
            output.pop("reasoning_traces", None)
            output.pop("raw_response", None)
        return json.dumps(output, ensure_ascii=False, indent=2, default=str)

    # ── 表格渲染 ─────────────────────────────────────

    def _render_table(self, result: dict, verbose: bool) -> str:
        """渲染为纯文本表格"""
        lines: list[str] = []

        # 文献表格
        if "papers" in result:
            lines.append(f"{'#':>3} {'Year':>4} {'Relevance':>8}  Title")
            lines.append("-" * 80)
            for i, paper in enumerate(result["papers"][:20], 1):
                title = paper.get("title", "Unknown")[:55]
                year = str(paper.get("year", "?"))
                rel = paper.get("relevance", "med")[:8]
                lines.append(f"{i:>3} {year:>4} {rel:>8}  {title}")
            lines.append("")

        # 声学表格
        if "acoustic" in result:
            ac = result["acoustic"]
            lines.append(f"{'Metric':<25} {'Value':>15}")
            lines.append("-" * 42)
            for k, v in ac.items():
                if isinstance(v, (int, float, str)):
                    lines.append(f"{k:<25} {str(v):>15}")

        return "\n".join(lines)

    # ── 纯文本渲染 ───────────────────────────────────

    def _render_plain(self, result: dict, verbose: bool) -> str:
        """渲染为纯文本 (fallback)"""
        if "response" in result:
            return result["response"]
        if "message" in result:
            return result["message"]
        return str(result)

    # ── 辅助 ─────────────────────────────────────────

    def _phase_label(self, phase: str) -> str:
        """阶段标签映射"""
        labels = {
            "literature_review": "文献调研",
            "data_analysis": "数据分析",
            "field_survey": "野外调查",
            "conservation_assessment": "保护评估",
            "report_generation": "成果产出",
        }
        return labels.get(phase, phase)

    def render_reasoning_trace(self, trace: dict) -> str:
        """单独渲染推理追踪 (R1 thought harvesting)"""
        lines = ["### 🧠 推理过程", ""]

        if trace.get("subgoals"):
            lines.append("**子目标:**")
            for sg in trace["subgoals"]:
                lines.append(f"- {sg}")
            lines.append("")

        if trace.get("hypotheses"):
            lines.append("**假设:**")
            for h in trace["hypotheses"]:
                lines.append(f"- {h}")
            lines.append("")

        if trace.get("uncertainties"):
            lines.append("**不确定性:**")
            for u in trace["uncertainties"]:
                lines.append(f"- {u}")
            lines.append("")

        if trace.get("rejected_paths"):
            lines.append("**已排除路径:**")
            for rp in trace["rejected_paths"]:
                lines.append(f"- {rp}")
            lines.append("")

        return "\n".join(lines)
