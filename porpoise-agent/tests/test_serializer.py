"""序列化器 + 校验器单元测试"""
import pytest
import sys
sys.path.insert(0, ".")

from src.mapping.serializer import (
    EngineeringSerializer, SerializedFormat, SerializedOutput,
    serialize_to_tool_call, nl_to_python,
)
from src.mapping.validator import (
    OutputValidator, ValidationStatus, ValidationIssue, ValidationResult,
)


class TestEngineeringSerializer:
    def setup_method(self):
        self.ser = EngineeringSerializer()

    def test_serialize_function_call(self):
        out = self.ser.serialize("搜索江豚文献",
                                 target_format=SerializedFormat.FUNCTION_CALL)
        assert out.format == SerializedFormat.FUNCTION_CALL
        assert "(" in out.code
        assert ")" in out.code

    def test_serialize_json(self):
        out = self.ser.serialize("调用搜索",
                                 target_format=SerializedFormat.JSON,
                                 context={"tool": "search", "q": "porpoise"})
        assert out.format == SerializedFormat.JSON
        assert "tool" in out.code

    def test_serialize_sql(self):
        out = self.ser.serialize("查询江豚数据",
                                 target_format=SerializedFormat.SQL)
        assert out.format == SerializedFormat.SQL
        assert "SELECT" in out.code.upper()

    def test_serialize_python_acoustic(self):
        out = self.ser.serialize("分析声学数据",
                                 target_format=SerializedFormat.PYTHON)
        assert out.format == SerializedFormat.PYTHON
        assert "import" in out.code.lower() or "def " in out.code.lower()
        assert out.needs_sandbox

    def test_serialize_python_stats(self):
        out = self.ser.serialize("统计 mean std",
                                 target_format=SerializedFormat.PYTHON)
        assert "describe" in out.code or "mean" in out.code or "std" in out.code

    def test_serialize_http(self):
        out = self.ser.serialize("调用API",
                                 target_format=SerializedFormat.HTTP_REQUEST,
                                 context={"method": "GET", "url": "https://api.example.com/"})
        assert "GET" in out.code
        assert "https://api.example.com" in out.code

    def test_empty_nl(self):
        out = self.ser.serialize("", target_format=SerializedFormat.FUNCTION_CALL)
        assert out.code  # should still produce something

    def test_quick_tool_call(self):
        result = serialize_to_tool_call("搜索", "search_tool", query="test")
        assert result["tool"] == "search_tool"
        assert result["parameters"]["query"] == "test"

    def test_nl_to_python(self):
        code = nl_to_python("计算均值")
        assert "计算均值" in code or "TODO" in code


class TestOutputValidator:
    def test_valid_python(self):
        val = OutputValidator()
        out = SerializedOutput(
            format=SerializedFormat.PYTHON,
            code="print('hello world')",
            original_nl="print hello",
        )
        result = val.validate(out)
        assert result.passed

    def test_syntax_error_python(self):
        val = OutputValidator()
        out = SerializedOutput(
            format=SerializedFormat.PYTHON,
            code="print('missing paren'",
            original_nl="",
        )
        result = val.validate(out)
        assert not result.passed

    def test_danger_detection(self):
        val = OutputValidator(safety_checks=True)
        out = SerializedOutput(
            format=SerializedFormat.PYTHON,
            code="import os; os.system('rm -rf /')",
            original_nl="",
        )
        result = val.validate(out)
        # Should have at least a warning or fail
        has_warning = any(i.severity in ("warning", "error") for i in result.issues)
        assert has_warning or not result.passed

    def test_danger_sql(self):
        val = OutputValidator()
        out = SerializedOutput(
            format=SerializedFormat.SQL,
            code="DROP TABLE observations;",
            original_nl="",
        )
        result = val.validate(out)
        assert not result.passed

    def test_valid_json(self):
        val = OutputValidator()
        out = SerializedOutput(
            format=SerializedFormat.JSON,
            code='{"tool": "search", "parameters": {"q": "test"}}',
            original_nl="",
        )
        result = val.validate(out)
        assert result.passed

    def test_invalid_json(self):
        val = OutputValidator()
        out = SerializedOutput(
            format=SerializedFormat.JSON,
            code='{broken json',
            original_nl="",
        )
        result = val.validate(out)
        assert not result.passed

    def test_empty_output(self):
        val = OutputValidator()
        out = SerializedOutput(
            format=SerializedFormat.PYTHON,
            code="",
            original_nl="",
        )
        result = val.validate(out)
        assert not result.passed

    def test_valid_function_call(self):
        val = OutputValidator()
        out = SerializedOutput(
            format=SerializedFormat.FUNCTION_CALL,
            code="search_literature(query='porpoise', limit=10)",
            original_nl="",
        )
        result = val.validate(out)
        assert result.passed

    def test_safe_python_with_imports(self):
        val = OutputValidator()
        out = SerializedOutput(
            format=SerializedFormat.PYTHON,
            code="import numpy as np\nprint(np.array([1,2,3]))",
            original_nl="",
        )
        result = val.validate(out)
        assert result.passed
