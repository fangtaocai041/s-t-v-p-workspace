"""
输出校验器 (Output Validator)
──────────────────────────────
在执行前校验序列化输出的正确性。

校验维度:
- JSON Schema: 工具调用参数格式
- Python AST: 语法正确性
- SQL Syntax: 基本语法检查
- Type Check: 参数类型匹配
- Safety Check: 危险操作检测 (文件删除、网络外连等)

对应五层模型中的输出校验:
    序列化 → 校验 → 执行 (校验失败 → 反馈 → 重新序列化)
"""

import ast
import json
import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from src.mapping.serializer import SerializedFormat, SerializedOutput

logger = logging.getLogger(__name__)


class ValidationStatus(str, Enum):
    """校验状态"""
    PASS = "pass"
    WARN = "warn"               # 通过但有警告
    FAIL = "fail"               # 失败
    NEEDS_REVIEW = "needs_review"  # 需要人工审查


@dataclass
class ValidationIssue:
    """校验问题"""
    severity: str           # error / warning / info
    code: str               # 问题代码
    message: str
    line: int = 0
    suggestion: str = ""


@dataclass
class ValidationResult:
    """校验结果"""
    status: ValidationStatus
    issues: list[ValidationIssue] = field(default_factory=list)
    sanitized_output: Optional[str] = None   # 清理后的输出
    passed: bool = True


# ── 校验器 ────────────────────────────────────────────────

class OutputValidator:
    """
    输出校验器 — 多维度验证序列化输出

    用法:
        validator = OutputValidator()
        result = validator.validate(serialized_output)
        if result.passed:
            execute(result.sanitized_output)
        else:
            return result.issues  # 反馈给 Reflexion
    """

    def __init__(self, safety_checks: bool = True):
        self.safety_checks = safety_checks
        logger.info("OutputValidator initialized")

    def validate(self, output: SerializedOutput) -> ValidationResult:
        """
        主校验入口

        Args:
            output: 序列化输出

        Returns:
            ValidationResult: 校验结果
        """
        format_handlers = {
            SerializedFormat.PYTHON: self._validate_python,
            SerializedFormat.SQL: self._validate_sql,
            SerializedFormat.JSON: self._validate_json,
            SerializedFormat.HTTP_REQUEST: self._validate_http,
            SerializedFormat.FUNCTION_CALL: self._validate_fn_call,
        }

        handler = format_handlers.get(output.format, self._validate_generic)
        return handler(output)

    # ── Python 校验 ──────────────────────────────────

    def _validate_python(self, output: SerializedOutput) -> ValidationResult:
        """Python 代码校验 (AST + 安全检查)"""
        issues: list[ValidationIssue] = []

        # 0. 空代码检查
        if not output.code.strip():
            issues.append(ValidationIssue(
                severity="error",
                code="EMPTY_CODE",
                message="Python code is empty",
            ))
            return ValidationResult(status=ValidationStatus.FAIL, issues=issues, passed=False)

        # 1. AST 语法检查
        try:
            tree = ast.parse(output.code)
        except SyntaxError as e:
            issues.append(ValidationIssue(
                severity="error",
                code="PYTHON_SYNTAX",
                message=f"Python syntax error: {e.msg}",
                line=e.lineno or 0,
                suggestion=f"Fix syntax at line {e.lineno}: {e.text}",
            ))
            return ValidationResult(
                status=ValidationStatus.FAIL,
                issues=issues,
                passed=False,
            )

        # 2. 危险操作检测
        if self.safety_checks:
            danger_issues = self._check_python_danger(tree, output.code)
            issues.extend(danger_issues)

        # 3. 导入检查
        import_issues = self._check_python_imports(tree)
        issues.extend(import_issues)

        # 判定
        errors = [i for i in issues if i.severity == "error"]
        warnings = [i for i in issues if i.severity == "warning"]

        if errors:
            return ValidationResult(
                status=ValidationStatus.FAIL,
                issues=issues,
                passed=False,
            )
        elif warnings:
            return ValidationResult(
                status=ValidationStatus.WARN,
                issues=issues,
                sanitized_output=output.code,
                passed=True,
            )
        else:
            return ValidationResult(
                status=ValidationStatus.PASS,
                issues=issues,
                sanitized_output=output.code,
                passed=True,
            )

    def _check_python_danger(
        self, tree: ast.AST, code: str
    ) -> list[ValidationIssue]:
        """检测危险 Python 操作"""
        issues: list[ValidationIssue] = []

        # 危险函数/模块
        DANGER_PATTERNS = [
            (["os.system", "subprocess.call", "subprocess.run", "subprocess.Popen"],
             "DANGER_SUBPROCESS", "Shell 命令执行"),
            (["os.remove", "os.unlink", "shutil.rmtree", "os.rmdir"],
             "DANGER_FILE_DELETE", "文件/目录删除操作"),
            (["eval(", "exec(", "compile("],
             "DANGER_CODE_EXEC", "动态代码执行"),
            (["requests.post", "requests.put", "requests.delete", "urllib"],
             "DANGER_NETWORK_WRITE", "网络写入操作 (需确认目标)"),
            (["__import__(", "importlib"],
             "DANGER_DYNAMIC_IMPORT", "动态导入"),
        ]

        for node in ast.walk(tree):
            # 检查函数调用
            if isinstance(node, ast.Call):
                func_str = ast.unparse(node.func) if hasattr(ast, 'unparse') else str(node.func)

                for patterns, code, desc in DANGER_PATTERNS:
                    for pattern in patterns:
                        if pattern in func_str:
                            issues.append(ValidationIssue(
                                severity="warning",
                                code=code,
                                message=f"{desc}: {func_str}",
                                line=node.lineno if hasattr(node, 'lineno') else 0,
                                suggestion=f"Evaluate if {desc} is necessary. "
                                            f"If so, add approval gate.",
                            ))

            # 检查文件写入
            if isinstance(node, ast.Call):
                func_str = ast.unparse(node.func) if hasattr(ast, 'unparse') else str(node.func)
                if "open" in func_str and node.args:
                    first_arg = ast.unparse(node.args[0]) if hasattr(ast, 'unparse') else str(node.args[0])
                    if any(mode in first_arg.lower() for mode in ["'w'", '"w"', "'a'", '"a"']):
                        issues.append(ValidationIssue(
                            severity="warning",
                            code="FILE_WRITE",
                            message=f"文件写入操作: {first_arg}",
                            line=node.lineno if hasattr(node, 'lineno') else 0,
                            suggestion="确认写入路径和内容安全",
                        ))

        return issues

    def _check_python_imports(self, tree: ast.AST) -> list[ValidationIssue]:
        """检查 Python 导入"""
        issues: list[ValidationIssue] = []
        imports = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split(".")[0])

        # 标记可能缺失的依赖
        NON_STANDARD = {
            "numpy", "scipy", "pandas", "librosa", "soundfile",
            "sklearn", "matplotlib", "torch", "tensorflow",
            "chromadb", "neo4j", "langchain",
        }
        non_standard_imports = imports & NON_STANDARD

        if non_standard_imports:
            issues.append(ValidationIssue(
                severity="info",
                code="NON_STANDARD_IMPORTS",
                message=f"Non-standard imports: {non_standard_imports}",
                suggestion="Ensure these packages are installed in the sandbox",
            ))

        return issues

    # ── SQL 校验 ─────────────────────────────────────

    def _validate_sql(self, output: SerializedOutput) -> ValidationResult:
        """SQL 基本校验"""
        issues: list[ValidationIssue] = []
        sql = output.code.strip()

        # 基本结构检查
        if not sql.upper().startswith(("SELECT", "INSERT", "UPDATE", "DELETE", "WITH", "CREATE")):
            issues.append(ValidationIssue(
                severity="warning",
                code="SQL_STRUCTURE",
                message="SQL 可能缺少标准开头 (SELECT/INSERT/...)",
                suggestion="确认 SQL 语句完整",
            ))

        # 危险操作
        dangerous = ["DROP ", "TRUNCATE ", "ALTER ", "GRANT ", "REVOKE "]
        for op in dangerous:
            if op in sql.upper():
                issues.append(ValidationIssue(
                    severity="error",
                    code="DANGER_SQL",
                    message=f"危险 SQL 操作: {op}",
                    suggestion=f"{op} 操作需要人工审批",
                ))

        # DELETE 检查
        if "DELETE " in sql.upper() and "WHERE " not in sql.upper():
            issues.append(ValidationIssue(
                severity="error",
                code="DELETE_WITHOUT_WHERE",
                message="DELETE 语句缺少 WHERE 子句",
                suggestion="添加 WHERE 条件或确认全表删除",
            ))

        errors = [i for i in issues if i.severity == "error"]
        return ValidationResult(
            status=ValidationStatus.FAIL if errors else ValidationStatus.PASS,
            issues=issues,
            sanitized_output=sql,
            passed=len(errors) == 0,
        )

    # ── JSON 校验 ────────────────────────────────────

    def _validate_json(self, output: SerializedOutput) -> ValidationResult:
        """JSON 格式校验"""
        issues: list[ValidationIssue] = []

        try:
            data = json.loads(output.code)
            logger.debug(f"JSON valid: {list(data.keys())}")
        except json.JSONDecodeError as e:
            issues.append(ValidationIssue(
                severity="error",
                code="JSON_PARSE",
                message=f"JSON parse error: {e.msg}",
                line=e.lineno,
                suggestion=f"Fix JSON at line {e.lineno}, col {e.colno}",
            ))
            return ValidationResult(
                status=ValidationStatus.FAIL,
                issues=issues,
                passed=False,
            )

        # Schema 检查 (工具调用参数)
        if "tool" in data:
            if "parameters" not in data:
                issues.append(ValidationIssue(
                    severity="warning",
                    code="MISSING_PARAMS",
                    message="工具调用缺少 parameters",
                    suggestion="添加 parameters 字段",
                ))

        return ValidationResult(
            status=ValidationStatus.PASS if not issues else ValidationStatus.WARN,
            issues=issues,
            sanitized_output=output.code,
            passed=True,
        )

    # ── HTTP 校验 ────────────────────────────────────

    def _validate_http(self, output: SerializedOutput) -> ValidationResult:
        """HTTP 请求校验"""
        issues: list[ValidationIssue] = []
        code = output.code

        # 提取 URL
        url_match = re.search(r'(?:GET|POST|PUT|DELETE|PATCH)\s+(\S+)', code, re.IGNORECASE)
        if not url_match:
            issues.append(ValidationIssue(
                severity="error",
                code="HTTP_NO_URL",
                message="HTTP 请求缺少 URL",
                suggestion="添加 URL",
            ))

        return ValidationResult(
            status=ValidationStatus.FAIL if any(
                i.severity == "error" for i in issues
            ) else ValidationStatus.PASS,
            issues=issues,
            sanitized_output=code,
            passed=all(i.severity != "error" for i in issues),
        )

    # ── 函数调用校验 ────────────────────────────────

    def _validate_fn_call(self, output: SerializedOutput) -> ValidationResult:
        """函数调用校验"""
        issues: list[ValidationIssue] = []
        code = output.code

        # 基本格式: fn_name(args)
        if not re.match(r'^\w+\(.*\)$', code.strip()):
            issues.append(ValidationIssue(
                severity="warning",
                code="FN_CALL_FORMAT",
                message="函数调用格式可能不正确",
                suggestion="格式应为: function_name(param1=val1, ...)",
            ))

        return ValidationResult(
            status=ValidationStatus.WARN if issues else ValidationStatus.PASS,
            issues=issues,
            sanitized_output=code,
            passed=True,
        )

    # ── 通用校验 ────────────────────────────────────

    def _validate_generic(self, output: SerializedOutput) -> ValidationResult:
        """通用校验"""
        if not output.code.strip():
            return ValidationResult(
                status=ValidationStatus.FAIL,
                issues=[ValidationIssue(
                    severity="error",
                    code="EMPTY_OUTPUT",
                    message="序列化输出为空",
                    suggestion="检查序列化逻辑",
                )],
                passed=False,
            )
        return ValidationResult(
            status=ValidationStatus.PASS,
            sanitized_output=output.code,
            passed=True,
        )
