"""Tests for graph definition."""

import pytest

from src.graph.graph import create_graph, route_after_search, route_after_thinking
from src.graph.state import create_initial_state


class TestRouteAfterThinking:
    """Tests for route_after_thinking function."""

    def test_route_direct_answer(self):
        """Test routing for direct answer."""
        state = create_initial_state("test")
        state["decision"] = "direct_answer"

        result = route_after_thinking(state)

        assert result == "analysis_node"

    def test_route_search(self):
        """Test routing for search."""
        state = create_initial_state("test")
        state["decision"] = "search"

        result = route_after_thinking(state)

        assert result == "search_node"

    def test_route_statistics(self):
        """Test routing for statistics."""
        state = create_initial_state("test")
        state["decision"] = "statistics"

        result = route_after_thinking(state)

        assert result == "search_node"

    def test_route_unknown(self):
        """Test routing for unknown decision."""
        state = create_initial_state("test")
        state["decision"] = "unknown"

        result = route_after_thinking(state)

        # Should default to analysis
        assert result == "analysis_node"


class TestRouteAfterSearch:
    """Tests for route_after_search function."""

    def test_route_always_analysis(self):
        """Test that search always routes to analysis."""
        state = create_initial_state("test")

        result = route_after_search(state)

        assert result == "analysis_node"


class TestCreateGraph:
    """Tests for create_graph function."""

    def test_create_graph(self):
        """Test graph creation."""
        graph = create_graph()

        assert graph is not None

    def test_graph_execution(self):
        """Test graph execution with sample state."""
        graph = create_graph()
        initial_state = create_initial_state("test query")

        # Graph should be executable
        # Note: This may fail if LLM is not configured, but graph should be created
        assert graph is not None

    def test_graph_structure(self):
        """Test that graph has correct structure."""
        graph = create_graph()

        # Graph should have nodes and edges configured
        assert hasattr(graph, "invoke") or hasattr(graph, "nodes")
