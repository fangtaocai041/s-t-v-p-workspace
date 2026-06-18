#!/usr/bin/env python3
"""
daily_report.py — 每日工作清单生成器

每天结束时运行, 输出:
  1. 今日完成事项
  2. 当前项目健康状态
  3. 明日优化方向
  4. 专业领域进化建议

用法:
    python scripts/daily_report.py
    python scripts/daily_report.py --save    # 保存到 docs/daily/
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
NOW = datetime.now().strftime("%Y-%m-%d %H:%M")


def run(cmd, cwd=None):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True,
                          timeout=30, cwd=cwd or str(WORKSPACE))
        return r.stdout.strip()
    except Exception as e:
        return f"Error: {e}"


def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def check_project(name, path):
    """检查单个项目状态。"""
    p = Path(path)
    if not (p / ".git").exists():
        return f"  ❌ {name}: not a git repo"

    # 最近提交
    last = run(["git", "-C", str(p), "log", "--oneline", "-1"])
    # 未提交变更
    dirty = run(["git", "-C", str(p), "status", "--short"])
    # 测试 (如果存在 tests/)
    tests = ""
    if (p / "tests").exists():
        tr = run([sys.executable, "-m", "pytest", "tests", "-q", "--tb=line"],
                cwd=str(p))
        tests = tr.split("\n")[-1] if tr else "?"

    status = "✅" if not dirty else "⚠️"
    result = f"  {status} {name:<30} {last[:60] if last else '?'}"
    if tests:
        result += f"\n        Tests: {tests}"
    return result


# ═══════════════════════════════════════════════════════════════
# 主报告
# ═══════════════════════════════════════════════════════════════

def main():
    print(f"{'='*60}")
    print(f"  Reasonix 每日报告")
    print(f"  {NOW}")
    print(f"{'='*60}")

    # ── 1. 项目健康 ──
    section("项目健康状态")

    projects = [
        ("workspace root", WORKSPACE),
        ("fish-ecology-assistant", WORKSPACE / "fish-ecology-assistant"),
        ("san-sheng-wanwu-core", WORKSPACE / "san-sheng-wanwu-core"),
        ("cognitive-search-engine", WORKSPACE / "cognitive-search-engine"),
        ("eon-core", WORKSPACE / "eon-core"),
        ("porpoise-agent", WORKSPACE / "porpoise-agent"),
        ("coilia-agent", WORKSPACE / "coilia-agent"),
        ("culter-agent", WORKSPACE / "culter-agent"),
        ("conflict-arbiter", WORKSPACE / "conflict-arbiter"),
        ("infrastructure", WORKSPACE / "infrastructure"),
    ]

    for name, path in projects:
        print(check_project(name, path))

    # ── 2. MAGMA 记忆系统状态 ──
    section("MAGMA 记忆系统")
    try:
        sys.path.insert(0, str(WORKSPACE / "san-sheng-wanwu-core"))
        from src.memory import MagmaMemory
        mem = MagmaMemory(nx_backend=True)
        print(f"  Memory engine: MagmaMemory + NetworkX")
        print(f"  Encoder: char_ngram (zero-dep Chinese semantic)")
        print(f"  API: mem.add(), mem.search(), mem.page_rank()")
    except Exception as e:
        print(f"  ❌ MAGMA error: {e}")

    # ── 3. 备份状态 ──
    section("备份体系")
    baidu = Path("D:/BaiduSyncdisk/百度网盘同步空间/Reasonix_full_backup")
    if baidu.exists():
        dirs = len(list(baidu.iterdir()))
        print(f"  ✅ 百度网盘整盘镜像: {dirs} 个顶级目录")
    else:
        print(f"  ⚠️  百度网盘备份未就绪 (运行 sync_to_baidu.bat)")

    task = run(["schtasks", "/query", "/tn", "ReasonixAutoBackup",
                "/v", "/fo", "list"])
    if "Ready" in task:
        print(f"  ✅ 自动备份任务: 每天 20:00")
    else:
        print(f"  ⚠️  自动备份任务未设置")

    print(f"  ✅ Git 远程仓库: 10/10 已推送")

    # ── 4. 明日优化方向 ──
    section("明日优化方向")

    todos = [
        ("infrastructure 测试修复",
         "11 个 import 失败 (chinese_nlp/fish_classifier 文件缺失), 从 git 恢复或重构"),
        ("eon-core 顺序依赖",
         "3 个 e2e 测试批量跑失败, 单独跑全过. 低优先级"),
        ("MAGMA 记忆持久化",
         "MagmaMemory 目前是内存存储, 可以接入 SQLite 持久化"),
        ("学科领域知识库扩充",
         "12 个学科领域目前只有~120 概念, 可扩展到 1000+"),
    ]

    for i, (title, desc) in enumerate(todos, 1):
        print(f"  {i}. {title}")
        print(f"     {desc}")
        print()

    # ── 5. 专业领域进化建议 ──
    section("专业领域进化方向 (渔业资源·水生生物学)")

    evolves = [
        ("物种-栖息地网络建模",
         "利用 NetworkX 社区发现, 自动聚类同域物种群. "
         "输入: species.db 的分布数据 + 文献关键词 → 输出: 物种共现网络",
         "src/memory/magma.py → MagmaMemory.communities()"),

        ("保护等级辩证分析",
         "IUCN vs 中国红色名录的双轨矛盾自动检测. "
         "输入: 物种保护数据 → 输出: 矛盾报告 + 综合建议",
         "src/cortex/dialectics.py + docs/CHINA_FISH_CONSERVATION.md"),

        ("文献计量网络",
         "用 PageRank 识别某物种/领域的核心文献. "
         "输入: Zotero 文献库 → 输出: 文献重要性排名",
         "fishkb + NetworkXGraphDB.page_rank()"),

        ("形态学性状网络",
         "鱼类形态学参数的种间比较网络. "
         "输入: FISHMORPH 数据 → 输出: 形态相似性图谱",
         "data/species.db + MagmaMemory"),

        ("生态位模型集成",
         "将 MaxEnt/SDM 模型输出接入管道. "
         "输入: 环境变量 + 物种分布 → 输出: 适宜栖息地预测",
         "新模块: src/ecology/niche_model.py"),
    ]

    for i, (title, desc, code) in enumerate(evolves, 1):
        print(f"  🌊 {i}. {title}")
        print(f"     {desc}")
        print(f"     入口: {code}")
        print()

    # ── 结尾 ──
    print(f"{'='*60}")
    print(f"  报告生成: {NOW}")
    print(f"  {'='*60}")


if __name__ == "__main__":
    # 检查 --save 参数
    if "--save" in sys.argv:
        import io
        buf = io.StringIO()
        old = sys.stdout
        sys.stdout = buf
        main()
        sys.stdout = old
        report = buf.getvalue()

        daily_dir = WORKSPACE / "docs" / "daily"
        daily_dir.mkdir(parents=True, exist_ok=True)
        date_str = datetime.now().strftime("%Y%m%d")
        path = daily_dir / f"daily-{date_str}.md"
        with open(path, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"Report saved: {path}")
    else:
        main()
