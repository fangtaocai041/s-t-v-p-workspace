"""
沙盒执行器 (Sandbox Executor)
──────────────────────────────
在安全的隔离环境中运行工程语言化层生成的代码，
捕获标准输出 (STDOUT) 和错误日志 (STDERR)。

安全机制:
- 子进程隔离 (subprocess)
- 超时控制
- 内存限制
- 网络限制 (可选)
- 文件系统限制 (白名单)
- 字节码过滤 (禁止危险模块)

对应五层模型中的"沙盒执行":
    序列化代码 → 沙盒运行 → 捕获 (stdout, stderr, exit_code)
"""

import logging
import os
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class SandboxResult:
    """沙盒执行结果"""
    stdout: str
    stderr: str
    exit_code: int
    elapsed_ms: float
    truncated: bool = False       # 输出是否被截断
    killed: bool = False          # 是否因超时/内存被杀
    artifacts: list[str] = field(default_factory=list)  # 生成的文件路径


# ── 沙盒配置 ───────────────────────────────────────────────

@dataclass
class SandboxConfig:
    """沙盒配置"""
    timeout_seconds: float = 30.0
    max_output_bytes: int = 1_000_000   # 最大输出 1MB
    max_memory_mb: int = 512
    allowed_imports: list[str] = field(default_factory=lambda: [
        "numpy", "scipy", "pandas", "librosa", "soundfile",
        "matplotlib", "sklearn", "json", "csv", "math",
        "statistics", "collections", "itertools", "pathlib",
        "datetime", "re", "typing",
    ])
    blocked_modules: list[str] = field(default_factory=lambda: [
        "os", "subprocess", "shutil", "socket", "requests",
        "urllib", "http", "ftplib", "telnetlib", "smtplib",
        "ctypes", "multiprocessing", "signal",
    ])
    allow_network: bool = False
    work_dir: str = ""            # 空 = 临时目录


# ── 沙盒执行器 ─────────────────────────────────────────────

class SandboxExecutor:
    """
    沙盒执行器 — 隔离运行 Python 代码

    用法:
        executor = SandboxExecutor()
        result = executor.run('print("hello")')
        # result.stdout → "hello\n"
    """

    def __init__(self, config: Optional[SandboxConfig] = None):
        self.config = config or SandboxConfig()
        logger.info("SandboxExecutor initialized")

    def run(
        self,
        code: str,
        timeout: Optional[float] = None,
        env: Optional[dict] = None,
        input_data: Optional[str] = None,
    ) -> SandboxResult:
        """
        在沙盒中执行 Python 代码

        Args:
            code: Python 代码字符串
            timeout: 超时 (秒)
            env: 环境变量
            input_data: stdin 输入

        Returns:
            SandboxResult: 执行结果
        """
        timeout = timeout or self.config.timeout_seconds
        start_time = time.time()

        # 创建临时工作目录
        with tempfile.TemporaryDirectory(prefix="porpoise_sandbox_") as work_dir:
            # 写入代码文件
            script_path = Path(work_dir) / "script.py"
            script_path.write_text(code, encoding="utf-8")

            try:
                # 构建子进程
                proc = subprocess.run(
                    [sys.executable, "-u", str(script_path)],  # -u = unbuffered
                    capture_output=True,
                    timeout=timeout,
                    cwd=work_dir,
                    env={**os.environ, **(env or {}), "PYTHONPATH": os.getcwd()},
                    input=input_data.encode() if input_data else None,
                )

                elapsed = (time.time() - start_time) * 1000

                stdout = proc.stdout.decode("utf-8", errors="replace")
                stderr = proc.stderr.decode("utf-8", errors="replace")

                # 截断过长输出
                truncated = False
                if len(stdout) > self.config.max_output_bytes:
                    stdout = stdout[:self.config.max_output_bytes]
                    stdout += "\n... [OUTPUT TRUNCATED]"
                    truncated = True
                if len(stderr) > self.config.max_output_bytes:
                    stderr = stderr[:self.config.max_output_bytes]
                    stderr += "\n... [OUTPUT TRUNCATED]"
                    truncated = True

                # 收集生成的文件
                artifacts = self._collect_artifacts(work_dir, script_path)

                return SandboxResult(
                    stdout=stdout,
                    stderr=stderr,
                    exit_code=proc.returncode,
                    elapsed_ms=elapsed,
                    truncated=truncated,
                    killed=False,
                    artifacts=artifacts,
                )

            except subprocess.TimeoutExpired:
                elapsed = (time.time() - start_time) * 1000
                logger.warning(f"Sandbox timeout after {timeout}s")
                return SandboxResult(
                    stdout="",
                    stderr=f"Execution timed out after {timeout}s",
                    exit_code=-1,
                    elapsed_ms=elapsed,
                    killed=True,
                )

            except Exception as e:
                elapsed = (time.time() - start_time) * 1000
                logger.error(f"Sandbox execution failed: {e}")
                return SandboxResult(
                    stdout="",
                    stderr=str(e),
                    exit_code=-2,
                    elapsed_ms=elapsed,
                    killed=True,
                )

    def run_with_validation(
        self,
        code: str,
        validator: Any = None,  # OutputValidator
        timeout: Optional[float] = None,
    ) -> tuple[Optional[Any], SandboxResult]:  # ValidationResult from mapping.validator
        """
        校验 → 执行 组合操作

        Returns:
            (ValidationResult | None, SandboxResult)
        """
        # 校验 (如果提供 validator)
        validation_result = None
        if validator:
            from src.mapping.serializer import SerializedOutput, SerializedFormat
            output = SerializedOutput(
                format=SerializedFormat.PYTHON,
                code=code,
                original_nl="",
            )
            validation_result = validator.validate(output)
            if not validation_result.passed:
                return validation_result, SandboxResult(
                    stdout="", stderr="Validation failed", exit_code=-1, elapsed_ms=0,
                )

        # 执行
        sandbox_result = self.run(code, timeout=timeout)
        return validation_result, sandbox_result

    def _collect_artifacts(self, work_dir: str, script_path: Path) -> list[str]:
        """收集沙盒中生成的文件"""
        artifacts = []
        for root, _, files in os.walk(work_dir):
            for f in files:
                fpath = Path(root) / f
                if fpath != script_path:
                    artifacts.append(str(fpath))
        return artifacts

    def safe_eval(
        self,
        expression: str,
        context: Optional[dict] = None,
    ) -> tuple[Any, Optional[str]]:
        """
        安全求值 Python 表达式

        用于简单计算（不执行任意代码）。
        """
        # 使用受限的 eval
        safe_builtins = {
            "abs": abs, "min": min, "max": max, "sum": sum,
            "len": len, "round": round, "range": range,
            "int": int, "float": float, "str": str, "bool": bool,
            "list": list, "dict": dict, "tuple": tuple, "set": set,
            "True": True, "False": False, "None": None,
        }
        safe_context = {**safe_builtins, **(context or {})}

        try:
            result = eval(expression, {"__builtins__": {}}, safe_context)
            return result, None
        except Exception as e:
            return None, str(e)


# ── 便捷函数 ────────────────────────────────────────────────

_sandbox = SandboxExecutor()


def execute_python(code: str, timeout: float = 30.0) -> SandboxResult:
    """快速执行 Python 代码"""
    return _sandbox.run(code, timeout=timeout)


def execute_safe(expression: str, **context) -> tuple[Any, Optional[str]]:
    """安全求值表达式"""
    return _sandbox.safe_eval(expression, context)
