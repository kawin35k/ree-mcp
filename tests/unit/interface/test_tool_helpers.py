"""Unit tests for tool helper classes."""

import json

from src.ree_mcp.domain.exceptions import InvalidIndicatorIdError
from src.ree_mcp.interface.tool_helpers import DateTimeHelper, ResponseFormatter


class TestDateTimeHelper:
    """Tests for DateTimeHelper class."""

    def test_build_datetime_range(self) -> None:
        """Test building datetime range for a specific hour."""
        start, end = DateTimeHelper.build_datetime_range("2025-10-08", "12")
        assert start == "2025-10-08T12:00"
        assert end == "2025-10-08T12:59"

    def test_build_datetime_range_zero_pads_hour(self) -> None:
        """Test that hour is zero-padded."""
        start, end = DateTimeHelper.build_datetime_range("2025-10-08", "5")
        assert start == "2025-10-08T05:00"
        assert end == "2025-10-08T05:59"

    def test_build_datetime_range_already_padded(self) -> None:
        """Test with already zero-padded hour."""
        start, end = DateTimeHelper.build_datetime_range("2025-10-08", "05")
        assert start == "2025-10-08T05:00"
        assert end == "2025-10-08T05:59"

    def test_build_day_range(self) -> None:
        """Test building datetime range for a full day."""
        start, end = DateTimeHelper.build_day_range("2025-10-08")
        assert start == "2025-10-08T00:00"
        assert end == "2025-10-08T23:59"

    def test_validate_date_format_valid(self) -> None:
        """Test date format validation with valid dates."""
        assert DateTimeHelper.validate_date_format("2025-10-08") is True
        assert DateTimeHelper.validate_date_format("2025-01-01") is True
        assert DateTimeHelper.validate_date_format("2025-12-31") is True

    def test_validate_date_format_invalid(self) -> None:
        """Test date format validation with invalid dates."""
        assert DateTimeHelper.validate_date_format("10-08-2025") is False
        assert DateTimeHelper.validate_date_format("2025/10/08") is False
        assert DateTimeHelper.validate_date_format("invalid") is False
        assert DateTimeHelper.validate_date_format("2025-13-01") is False


class TestResponseFormatter:
    """Tests for ResponseFormatter class."""

    def test_success_basic(self) -> None:
        """Test formatting successful response."""
        data = {"result": "success", "value": 42}
        result = ResponseFormatter.success(data)

        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed["result"] == "success"
        assert parsed["value"] == 42

    def test_success_with_ensure_ascii_false(self) -> None:
        """Test success with non-ASCII characters."""
        data = {"message": "España"}
        result = ResponseFormatter.success(data, ensure_ascii=False)

        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed["message"] == "España"

    def test_success_custom_indent(self) -> None:
        """Test success with custom indentation."""
        data = {"key": "value"}
        result = ResponseFormatter.success(data, indent=4)

        assert isinstance(result, str)
        # Should have 4-space indentation
        assert "    " in result

    def test_error_basic(self) -> None:
        """Test formatting error response."""
        result = ResponseFormatter.error("Something went wrong")

        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed["error"] == "Something went wrong"
        assert "type" not in parsed

    def test_error_with_type(self) -> None:
        """Test error with type information."""
        result = ResponseFormatter.error("Invalid ID", error_type="ValueError")

        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed["error"] == "Invalid ID"
        assert parsed["type"] == "ValueError"

    def test_domain_exception(self) -> None:
        """Test formatting domain exception."""
        exception = InvalidIndicatorIdError(-1)
        result = ResponseFormatter.domain_exception(exception)

        assert isinstance(result, str)
        parsed = json.loads(result)
        assert "error" in parsed
        assert parsed["type"] == "InvalidIndicatorIdError"
        assert "-1" in parsed["error"]

    def test_unexpected_error_without_context(self) -> None:
        """Test unexpected error without context."""
        exception = ValueError("Something broke")
        result = ResponseFormatter.unexpected_error(exception)

        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed["error"] == "Unexpected error: Something broke"

    def test_unexpected_error_with_context(self) -> None:
        """Test unexpected error with context."""
        exception = ValueError("Connection failed")
        result = ResponseFormatter.unexpected_error(exception, context="API call")

        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed["error"] == "API call: Connection failed"


# Note: ToolExecutor tests require async and mocking, handled in integration tests
