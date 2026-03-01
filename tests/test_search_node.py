"""Tests for search node."""

import pytest

from src.graph.state import create_initial_state
from src.nodes.search_node import SearchNodeProcessor, create_search_node, search_node
from src.tools.competitor_tools import MockCompetitorAnalyzer
from src.tools.search_tools import MockSearchTool
from src.tools.trend_tools import MockTrendAnalyzer


class TestSearchNodeProcessor:
    """Tests for SearchNodeProcessor."""

    def test_initialization(self):
        """Test processor initialization."""
        search_tool = MockSearchTool()
        processor = SearchNodeProcessor(search_tool)
        assert processor.search_tool == search_tool

    def test_process_keyword_search(self):
        """Test processing keyword search."""
        mock_results = [{"title": "Result", "snippet": "Test", "link": "http://test.com"}]
        search_tool = MockSearchTool(mock_results)
        processor = SearchNodeProcessor(search_tool)

        state = create_initial_state("test")
        state["search_type"] = "keywords"
        state["search_query"] = "test query"

        result = processor.process_search(state)

        assert len(result["search_results"]) > 0
        assert result["raw_data"] is not None
        assert "search_node" in result["execution_path"]

    def test_process_competitor_search(self):
        """Test processing competitor search."""
        search_tool = MockSearchTool()
        competitor_analyzer = MockCompetitorAnalyzer()
        processor = SearchNodeProcessor(search_tool, competitor_analyzer)

        state = create_initial_state("test")
        state["search_type"] = "competitors"
        state["search_query"] = "test keyword"

        result = processor.process_search(state)

        assert result["raw_data"] is not None
        assert "competitors" in result["raw_data"] or "results" in result["search_results"]

    def test_process_trend_search(self):
        """Test processing trend search."""
        search_tool = MockSearchTool()
        trend_analyzer = MockTrendAnalyzer()
        processor = SearchNodeProcessor(search_tool, trend_analyzer=trend_analyzer)

        state = create_initial_state("test")
        state["search_type"] = "trends"
        state["search_query"] = "AI"

        result = processor.process_search(state)

        assert result["raw_data"] is not None
        assert "trends" in result["raw_data"] or "results" in result["search_results"]

    def test_process_search_without_query(self):
        """Test processing search without query."""
        search_tool = MockSearchTool()
        processor = SearchNodeProcessor(search_tool)

        state = create_initial_state("test")
        state["search_type"] = "keywords"
        # Missing search_query

        with pytest.raises(Exception):
            processor.process_search(state)

    def test_process_unknown_search_type(self):
        """Test processing unknown search type."""
        search_tool = MockSearchTool()
        processor = SearchNodeProcessor(search_tool)

        state = create_initial_state("test")
        state["search_type"] = "unknown"
        state["search_query"] = "test"

        result = processor.process_search(state)

        # Should fallback to keyword search
        assert "search_results" in result


class TestCreateSearchNode:
    """Tests for create_search_node factory function."""

    def test_create_search_node(self):
        """Test creating search node with dependencies."""
        search_tool = MockSearchTool()
        node_func = create_search_node(search_tool)

        state = create_initial_state("test")
        state["search_type"] = "keywords"
        state["search_query"] = "test"

        result = node_func(state)

        assert "search_results" in result


class TestSearchNode:
    """Tests for default search_node function."""

    def test_search_node_default(self):
        """Test default search node."""
        state = create_initial_state("test")
        state["search_type"] = "keywords"
        state["search_query"] = "test query"

        result = search_node(state)

        assert "search_results" in result
        assert "execution_path" in result

    def test_search_node_error_handling(self):
        """Test error handling in search node."""
        state = create_initial_state("test")
        # Missing required fields
        state["search_query"] = None  # type: ignore

        result = search_node(state)

        # Should handle error gracefully
        assert "error" in result or "execution_path" in result
