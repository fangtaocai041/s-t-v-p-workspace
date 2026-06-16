"""
批判 Agent (Critic Agent)
───────────────────────────
对抗角色 — 在博弈论框架中扮演"找茬"者。

功能:
- 审查其他 Agent 的输出
- 检测逻辑漏洞、数据错误、引文失真
- 生成批判反馈
- 在辩论模式中与生成 Agent 多轮对抗

对应 MAS 理论中的"动态对抗与辩论 (Debate & Adversarial MAS)":
    Generator ↔ Critic 多轮博弈 → 输出收敛到更优解
"""

import logging
from typing import Any

from src.agents.base import BaseAgent
from src.cognitive.bdi import Desire

logger = logging.getLogger(__name__)


class CriticAgent(BaseAgent):
    """
    批判 Agent — 内部审查者

    在 SOP 拓扑中: 接收其他 Agent 的输出，进行质量审查
    在 DEBATE 拓扑中: 与 Generator 多轮对抗

    审查维度:
    - 事实准确性: 引用是否正确?
    - 逻辑一致性: 推理有无漏洞?
    - 方法学: 方法是否合理?
    - 完整性: 是否遗漏关键信息?
    - 安全性: 建议是否安全可行?
    """

    def __init__(self, model: str = "deepseek-reasoner", memory: Any = None):
        super().__init__(name="critic", model=model, memory=memory)

    def _init_desire(self):
        self.bdi.desire = Desire(
            primary_goal="严格审查 Agent 输出，发现错误和漏洞",
            constraints=[
                "只批评内容，不批评 Agent",
                "每个 Reflection 必须包含 evidence 或 reasoning 字段",
                "每个 Reflection 必须包含非空 suggestion 字段",
            ],
        )

    async def handle_message(self, message: Any) -> dict:
        """
        审查消息内容

        输入: 其他 Agent 的输出
        输出: {"issues": [...], "overall_score": 0-100, "verdict": "pass|revise|reject"}
        """
        self._call_count += 1

        content = message.content if hasattr(message, 'content') else message
        source = message.metadata.get("source_agent", "unknown") if hasattr(message, 'metadata') else "unknown"

        logger.info(f"CriticAgent[{self.node_id}]: reviewing output from {source}")

        issues = []
        score = 100

        # 1. 事实准确性检查
        fact_issues = self._check_facts(content)
        issues.extend(fact_issues)
        score -= len(fact_issues) * 15

        # 2. 逻辑一致性检查
        logic_issues = self._check_logic(content)
        issues.extend(logic_issues)
        score -= len(logic_issues) * 10

        # 3. 完整性检查
        completeness_issues = self._check_completeness(content, source)
        issues.extend(completeness_issues)
        score -= len(completeness_issues) * 5

        # 4. 安全性检查
        safety_issues = self._check_safety(content)
        issues.extend(safety_issues)
        score -= len(safety_issues) * 20

        score = max(0, score)

        verdict = (
            "pass" if score >= 80 else
            "revise" if score >= 50 else
            "reject"
        )

        return {
            "agent": "critic",
            "source": source,
            "verdict": verdict,
            "overall_score": score,
            "n_issues": len(issues),
            "issues": issues,
            "suggestion": (
                "Ready to proceed." if verdict == "pass"
                else f"Found {len(issues)} issues. Revise and resubmit."
                if verdict == "revise"
                else f"Major issues ({len(issues)}). Complete revision required."
            ),
        }

    def _check_facts(self, content: Any) -> list[dict]:
        """事实准确性检查"""
        issues = []
        text = str(content).lower()

        # 检查常见错误
        if "baiji" in text and "extinct" not in text:
            issues.append({
                "type": "fact_check",
                "severity": "medium",
                "issue": "白鱀豚 (Baiji) 在 2006 年被宣告功能性灭绝，建议注明",
                "suggestion": "Add: 'Baiji (Lipotes vexillifer) was declared functionally extinct in 2006'",
            })

        # 种群数量检查
        import re
        pop_match = re.search(r'populations?\s*(?:of|is|are|estimated\s*at)?\s*(\d[\d,]*)\s*(?:individuals|heads)?', text)
        if pop_match:
            n = int(pop_match.group(1).replace(",", ""))
            if 500 <= n <= 3000:
                # 在合理范围内，不标记
                pass
            elif n < 100:
                issues.append({
                    "type": "fact_check",
                    "severity": "high",
                    "issue": f"种群数量估计 ({n}) 异常低，可能低估",
                    "suggestion": "验证数据来源，江豚种群约 1,000-1,200 头",
                })

        return issues

    def _check_logic(self, content: Any) -> list[dict]:
        """逻辑一致性检查"""
        issues = []
        text = str(content).lower()

        # 检查自相矛盾
        if "increase" in text and "decrease" in text:
            if text.index("increase") < text.index("decrease"):
                pass  # 可能正常: 先增后减
            # 简单检查, 实际应使用 LLM 进行深度分析

        # 检查因果推断
        if "therefore" in text or "因此" in text:
            issues.append({
                "type": "logic_check",
                "severity": "low",
                "issue": "包含因果推断 ('therefore/因此')，验证因果链是否完整",
                "suggestion": "确保因果推断有统计数据支撑，注明关联≠因果",
            })

        return issues

    def _check_completeness(self, content: Any, source: str) -> list[dict]:
        """完整性检查"""
        issues = []

        if isinstance(content, dict):
            if source == "literature" and "papers" in content:
                papers = content["papers"]
                if len(papers) < 5:
                    issues.append({
                        "type": "completeness",
                        "severity": "medium",
                        "issue": f"仅找到 {len(papers)} 篇文献，覆盖率可能不足",
                        "suggestion": "扩展搜索词或增加数据源",
                    })

            if source == "acoustic" and "n_clicks" in content:
                if content.get("n_clicks", 0) == 0:
                    issues.append({
                        "type": "completeness",
                        "severity": "medium",
                        "issue": "未检测到 click 脉冲，检查音频文件或阈值设置",
                        "suggestion": "确认文件格式和采样率，尝试降低 SPL 阈值",
                    })

        return issues

    def _check_safety(self, content: Any) -> list[dict]:
        """安全性检查"""
        issues = []
        text = str(content)

        dangerous_keywords = [
            "delete all", "remove all", "drop table", "format",
            "删除所有", "清除全部", "格式化",
        ]

        for kw in dangerous_keywords:
            if kw in text.lower():
                issues.append({
                    "type": "safety",
                    "severity": "critical",
                    "issue": f"检测到危险操作关键词: '{kw}'",
                    "suggestion": "此操作需要人工审批，已标记",
                })

        return issues
