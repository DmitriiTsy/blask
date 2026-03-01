"""Tests for analysis node."""

import pytest

from src.graph.state import create_initial_state
from src.nodes.analysis_node import AnalysisNodeProcessor, analysis_node
from src.utils.formatters import ResponseFormatter


class TestAnalysisNodeProcessor:
    """Tests for AnalysisNodeProcessor."""

    def test_initialization(self):
        """Test processor initialization."""
        processor = AnalysisNodeProcessor()
        assert processor.formatter is not None

    def test_initialization_with_formatter(self):
        """Test initialization with custom formatter."""
        formatter = ResponseFormatter()
        processor = AnalysisNodeProcessor(formatter)
        assert processor.formatter == formatter

    def test_process_analysis_with_results(self):
        """Test processing analysis with search results."""
        processor = AnalysisNodeProcessor()

        state = create_initial_state("test query")
        state["search_results"] = [
            {"title": "Result", "snippet": "Test", "link": "http://test.com"}
        ]
        state["raw_data"] = {"type": "keywords", "results": state["search_results"]}
        state["needs_charts"] = False

        result = processor.process_analysis(state)

        assert result["processed_data"] is not None
        assert result["formatted_response"] is not None
        assert "analysis_node" in result["execution_path"]

    def test_process_analysis_with_charts(self):
        """Test processing analysis with charts needed."""
        processor = AnalysisNodeProcessor()

        state = create_initial_state("test query")
        state["decision"] = "statistics"
        state["needs_charts"] = True
        state["raw_data"] = {
            "values": [1, 2, 3, 4, 5],
            "labels": ["A", "B", "C", "D", "E"],
        }

        result = processor.process_analysis(state)

        assert result["processed_data"] is not None
        # Visualization may or may not be created depending on data
        assert "charts_created" in result

    def test_process_analysis_empty_state(self):
        """Test processing analysis with empty state."""
        processor = AnalysisNodeProcessor()

        state = create_initial_state("test")
        state["search_results"] = []
        state["raw_data"] = {}

        result = processor.process_analysis(state)

        assert result["processed_data"] is not None
        assert result["formatted_response"] is not None


class TestAnalysisNode:
    """Tests for analysis_node function."""

    def test_analysis_node(self):
        """Test analysis node function."""
        state = create_initial_state("test query")
        state["search_results"] = [{"title": "Test", "snippet": "Result"}]
        state["raw_data"] = {"results": state["search_results"]}

        result = analysis_node(state)

        assert "processed_data" in result
        assert "formatted_response" in result
        assert "execution_path" in result
        assert "analysis_node" in result["execution_path"]

    def test_analysis_node_error_handling(self):
        """Test error handling in analysis node."""
        state = create_initial_state("test")
        # Create invalid state that might cause error
        state["raw_data"] = None  # type: ignore

        result = analysis_node(state)

        # Should handle error gracefully
        assert "error" in result or "processed_data" in result
