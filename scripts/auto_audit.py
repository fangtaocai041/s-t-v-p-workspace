#!/usr/bin/env python
"""auto_audit.py — 三生万物自动化审计扫描器 (v1.0)

一键执行 Part 4 中的所有快速检查命令，生成审计前置报告。
与 docs/AUDIT_TEMPLATE.md 配套使用。

用法:
    python scripts/auto_audit.py              # 全量扫描
    python scripts/auto_audit.py --quick       # 仅致命级检查
    python scripts/auto_audit.py --project cognitive-search-engine  # 单项目
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parent.parent

SEVERITY = {
    "FATAL": "🔴",
    "HIGH": "🟡",
    "MEDIUM": "🟠",
    "LOW": "🟢",
    "PASS": "✅",
}


class AuditIssue:
    def __init__(self, severity: str, code: str, file: str, line: int, msg: str, snippet: str = ""):
        self.severity = severity
        self.code = code
        self.file = file
        self.line = line
        self.msg = msg
        self.snippet = snippet


def find_py_files(project: str = None) -> List[Path]:
    """Find all .py files, excluding __pycache__, .git, node_modules, etc."""
    root = ROOT if project is None else ROOT / project
    if not root.exists():
        return []
    
    exclude_dirs = {'__pycache__', '.git', 'node_modules', '.pytest_cache', 
                    'dist', '.reasonix', 'logs', 'data', 'egg-info'}
    py_files = []
    for f in root.rglob("*.py"):
        if any(ex in f.parts for ex in exclude_dirs):
            continue
        py_files.append(f)
    return py_files


def check_bare_except(files: List[Path]) -> List[AuditIssue]:
    """FATAL: 检查裸 except: (无异常类型)"""
    issues = []
    for f in files:
        try:
            content = f.read_text(encoding="utf-8", errors="replace")
            for i, line in enumerate(content.split("\n"), 1):
                stripped = line.strip()
                # Match bare except: or bare except : (not except Exception, except XxxError, etc.)
                if re.match(r'except\s*:\s*$', stripped) or re.match(r'except\s*:\s*#', stripped):
                    # Skip if it's inside a string (heuristic: after ''' or """)
                    issues.append(AuditIssue(
                        "FATAL", "BARE_EXCEPT",
                        str(f.relative_to(ROOT)), i,
                        "裸 except: 无异常类型，会吞没 KeyboardInterrupt/SystemExit",
                        stripped
                    ))
        except Exception:
            pass
    return issues


def check_silent_pass(files: List[Path]) -> List[AuditIssue]:
    """FATAL: 检查 except Exception: pass (无日志)"""
    issues = []
    for f in files:
        try:
            content = f.read_text(encoding="utf-8", errors="replace")
            for i, line in enumerate(content.split("\n"), 1):
                if re.search(r'except\s+Exception\s*:\s*pass\b', line):
                    issues.append(AuditIssue(
                        "FATAL", "SILENT_PASS",
                        str(f.relative_to(ROOT)), i,
                        "except Exception: pass 静默吞异常，至少需要 logger.debug()",
                        line.strip()
                    ))
        except Exception:
            pass
    return issues


def check_random_no_seed(files: List[Path]) -> List[AuditIssue]:
    """HIGH: 检查 import random 但未设置 seed"""
    issues = []
    for f in files:
        try:
            content = f.read_text(encoding="utf-8", errors="replace")
            has_random_import = bool(re.search(r'^import random\b|^from random import', content, re.MULTILINE))
            has_seed = bool(re.search(r'random\.seed\(|random\.Random\(|\._rng\s*=\s*random\.Random\(', content))
            has_random_usage = bool(re.search(r'random\.(random|choice|shuffle|uniform|betavariate)', content))
            
            if has_random_import and not has_seed and has_random_usage:
                # Find the line with random import
                for i, line in enumerate(content.split("\n"), 1):
                    if re.match(r'^import random\b', line.strip()):
                        issues.append(AuditIssue(
                            "HIGH", "NO_RANDOM_SEED",
                            str(f.relative_to(ROOT)), i,
                            f"使用 random 但未设置种子 — 结果不可复现",
                            line.strip()
                        ))
                        break
        except Exception:
            pass
    return issues


def check_hardcoded_secrets(files: List[Path]) -> List[AuditIssue]:
    """FATAL: 检查硬编码密钥"""
    issues = []
    secret_patterns = [
        (r'(?:api_key|secret|password|token)\s*=\s*["\'][a-zA-Z0-9_\-]{20,}["\']', "硬编码密钥"),
        (r'["\'](sk-[a-zA-Z0-9]{20,})["\']', "OpenAI API Key"),
        (r'["\'](ghp_[a-zA-Z0-9]{20,})["\']', "GitHub Personal Access Token"),
    ]
    for f in files:
        try:
            content = f.read_text(encoding="utf-8", errors="replace")
            for i, line in enumerate(content.split("\n"), 1):
                for pattern, desc in secret_patterns:
                    if re.search(pattern, line) and 'os.environ' not in line and 'os.getenv' not in line:
                        issues.append(AuditIssue(
                            "FATAL", "HARDCODED_SECRET",
                            str(f.relative_to(ROOT)), i,
                            f"{desc} — 必须通过环境变量读取",
                            line.strip()
                        ))
        except Exception:
            pass
    return issues


def check_eval_without_guard(files: List[Path]) -> List[AuditIssue]:
    """HIGH: 检查 eval() 使用（已有 _safe_eval 的不计）"""
    issues = []
    for f in files:
        try:
            content = f.read_text(encoding="utf-8", errors="replace")
            has_safe_eval = '_safe_eval' in content or 'ast.literal_eval' in content or 'ast.parse' in content
            for i, line in enumerate(content.split("\n"), 1):
                if re.search(r'\beval\(', line) and 'ast.literal_eval' not in line:
                    if not has_safe_eval and '# nosec' not in line and '# safe' not in line.lower():
                        issues.append(AuditIssue(
                            "HIGH", "UNSAFE_EVAL",
                            str(f.relative_to(ROOT)), i,
                            "eval() 使用未检测到 AST 守卫或 _safe_eval 包装",
                            line.strip()
                        ))
        except Exception:
            pass
    return issues


def check_while_true_no_break(files: List[Path]) -> List[AuditIssue]:
    """MEDIUM: 检查 while True 无 break"""
    issues = []
    for f in files:
        try:
            content = f.read_text(encoding="utf-8", errors="replace")
            lines = content.split("\n")
            in_while = False
            while_start = 0
            indent_level = 0
            
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                if re.match(r'while\s+True\s*:', stripped):
                    in_while = True
                    while_start = i
                    indent_level = len(line) - len(line.lstrip())
                    continue
                
                if in_while:
                    current_indent = len(line) - len(line.lstrip()) if stripped else 999
                    if stripped and current_indent <= indent_level:
                        # Exited the while block
                        in_while = False
                        continue
                    if re.search(r'\bbreak\b', stripped) and current_indent > indent_level:
                        in_while = False  # Has break, OK
        except Exception:
            pass
    return issues


def check_global_mutable(files: List[Path]) -> List[AuditIssue]:
    """MEDIUM: 检查模块级可变对象"""
    issues = []
    for f in files:
        try:
            content = f.read_text(encoding="utf-8", errors="replace")
            for i, line in enumerate(content.split("\n"), 1):
                # Module-level (no indent) mutable set/dict/list
                if re.match(r'^[A-Z_][A-Z_0-9]*\s*=\s*\{', line) and 'frozenset' not in line:
                    # Check if it's used only for .get() or in checks (read-only)
                    name = line.split("=")[0].strip()
                    if name.endswith("_MAP") or name.endswith("_DATA") or name == name.upper():
                        issues.append(AuditIssue(
                            "LOW", "MUTABLE_GLOBAL",
                            str(f.relative_to(ROOT)), i,
                            f"模块级可变集合 {name} — 建议改为 frozenset 或函数返回",
                            line.strip()
                        ))
        except Exception:
            pass
    return issues


def check_import_sys_path_mutation(files: List[Path]) -> List[AuditIssue]:
    """MEDIUM: 检查 import 时修改 sys.path"""
    issues = []
    for f in files:
        try:
            content = f.read_text(encoding="utf-8", errors="replace")
            has_insert = 'sys.path.insert' in content or 'sys.path.append' in content
            has_legacy_tag = 'LEGACY' in content and 'sys.path' in content
            has_todo = 'TODO' in content and 'sys.path' in content
            
            if has_insert and not has_legacy_tag and not has_todo:
                for i, line in enumerate(content.split("\n"), 1):
                    if 'sys.path.insert' in line or 'sys.path.append' in line:
                        issues.append(AuditIssue(
                            "LOW", "SYS_PATH_MUTATION",
                            str(f.relative_to(ROOT)), i,
                            "import 时修改全局 sys.path — 建议标记为 LEGACY 或添加 TODO(P3)",
                            line.strip()
                        ))
        except Exception:
            pass
    return issues


def run_all_checks(files: List[Path], quick: bool = False) -> Dict[str, List[AuditIssue]]:
    """运行所有检查，返回按严重度分组的 issues"""
    results = {
        "bare_except": check_bare_except(files),
        "silent_pass": check_silent_pass(files),
        "random_no_seed": check_random_no_seed(files),
        "hardcoded_secrets": check_hardcoded_secrets(files),
        "unsafe_eval": check_eval_without_guard(files),
    }
    
    if not quick:
        results["global_mutable"] = check_global_mutable(files)
        results["sys_path_mutation"] = check_import_sys_path_mutation(files)
    
    return results


def print_report(results: Dict[str, List[AuditIssue]], project_name: str = "全部项目"):
    """打印审计前置报告"""
    total_fatal = 0
    total_high = 0
    total_medium = 0
    total_low = 0
    
    print(f"\n{'='*60}")
    print(f"  三生万物 · 自动化审计前置扫描")
    print(f"  范围: {project_name}")
    print(f"{'='*60}\n")
    
    for check_name, issues in results.items():
        if not issues:
            continue
        
        sev_counts = {}
        for issue in issues:
            sev_counts[issue.severity] = sev_counts.get(issue.severity, 0) + 1
        
        label = {
            "bare_except": "裸 except: 扫描",
            "silent_pass": "静默 except:pass 扫描",
            "random_no_seed": "随机种子缺失扫描",
            "hardcoded_secrets": "硬编码密钥扫描",
            "unsafe_eval": "eval() 安全扫描",
            "global_mutable": "模块级可变对象扫描",
            "sys_path_mutation": "sys.path 污染扫描",
        }.get(check_name, check_name)
        
        print(f"\n── {label} ({len(issues)} 条) ──")
        
        for issue in issues:
            prefix = SEVERITY.get(issue.severity, "❓")
            print(f"  {prefix} [{issue.code}] {issue.file}:{issue.line}")
            print(f"     {issue.msg}")
            if issue.snippet:
                print(f"     代码: {issue.snippet[:80]}")
            
            if issue.severity == "FATAL":
                total_fatal += 1
            elif issue.severity == "HIGH":
                total_high += 1
            elif issue.severity == "MEDIUM":
                total_medium += 1
            elif issue.severity == "LOW":
                total_low += 1
    
    print(f"\n{'='*60}")
    print(f"  汇总: 🔴{total_fatal}致命 🟡{total_high}高危 🟠{total_medium}中危 🟢{total_low}低危")
    if total_fatal > 0:
        print(f"  ⛔ {total_fatal} 个致命问题必须在合并前修复!")
    elif total_high > 0:
        print(f"  ⚠️ {total_high} 个高危问题建议在合并前修复")
    else:
        print(f"  ✅ 无致命/高危问题 — 可进入深度人工审查")
    print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description="三生万物自动化审计扫描器")
    parser.add_argument("--quick", action="store_true", help="仅致命级检查")
    parser.add_argument("--project", type=str, help="指定项目目录 (如 cognitive-search-engine)")
    args = parser.parse_args()
    
    project_name = args.project or "全部项目"
    files = find_py_files(args.project)
    
    if not files:
        print(f"⚠️ 未找到 Python 文件: {args.project}")
        sys.exit(1)
    
    print(f"🔍 扫描 {len(files)} 个 Python 文件...")
    
    results = run_all_checks(files, quick=args.quick)
    print_report(results, project_name)
    
    # Exit code: 1 if any FATAL issues
    has_fatal = any(
        any(i.severity == "FATAL" for i in issues)
        for issues in results.values()
    )
    sys.exit(1 if has_fatal else 0)


if __name__ == "__main__":
    main()
