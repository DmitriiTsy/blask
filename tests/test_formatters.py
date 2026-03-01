"""Tests for formatters."""

import pytest

from src.utils.formatters import ResponseFormatter, format_search_results


class TestResponseFormatter:
    """Tests for ResponseFormatter."""

    def test_initialization(self):
        """Test formatter initialization."""
        formatter = ResponseFormatter()
        assert formatter.prompt is not None

    def test_format_without_llm(self):
        """Test formatting without LLM (mock mode)."""
        formatter = ResponseFormatter()
        formatter.llm = None  # Force mock mode

        data = {"search_results": [{"title": "Test", "snippet": "Result"}]}
        result = formatter.format("test query", data, False)

        assert "test query" in result
        assert isinstance(result, str)

    def test_format_simple(self):
        """Test simple formatting."""
        formatter = ResponseFormatter()
        formatter.llm = None

        data = {
            "search_results": [
                {"title": "Result 1", "snippet": "Description 1", "link": "http://1.com"}
            ]
        }

        result = formatter._format_simple("test", data, False)

        assert "test" in result
        assert "Result 1" in result

    def test_data_to_string(self):
        """Test converting data to string."""
        formatter = ResponseFormatter()

        data = {"key": "value", "number": 123}
        result = formatter._data_to_string(data)

        assert "key" in result
        assert "value" in result


class TestFormatSearchResults:
    """Tests for format_search_results function."""

    def test_format_results(self):
        """Test formatting search results."""
        results = [
            {"title": "Result 1", "snippet": "Snippet 1", "link": "http://1.com"},
            {"title": "Result 2", "snippet": "Snippet 2", "link": "http://2.com"},
        ]

        formatted = format_search_results(results)

        assert "Result 1" in formatted
        assert "Result 2" in formatted
        assert "Snippet 1" in formatted

    def test_format_empty_results(self):
        """Test formatting empty results."""
        results = []

        formatted = format_search_results(results)

        assert "No results found" in formatted

    def test_format_with_limit(self):
        """Test formatting with limit."""
        results = [
            {"title": f"Result {i}", "snippet": f"Snippet {i}", "link": f"http://{i}.com"}
            for i in range(20)
        ]

        formatted = format_search_results(results, limit=5)

        # With limit=5, should contain first 5 results (0-4)
        assert "Result 0" in formatted
        assert "Result 4" in formatted
        # Should not contain result 5 (6th result)
        assert "Result 5" not in formatted
        # Should have exactly 5 results
        assert formatted.count("Result") == 5
