"""Tests for error handling utilities."""

import pytest

from src.graph.state import create_initial_state
from src.utils.errors import GraphError, handle_node_error


class TestGraphError:
    """Tests for GraphError exception."""

    def test_create_error(self):
        """Test creating GraphError."""
        error = GraphError("test message", "test_node")
        assert str(error) == "test message"
        assert error.node_name == "test_node"
        assert error.message == "test message"

    def test_error_without_node(self):
        """Test creating error without node name."""
        error = GraphError("test message")
        assert str(error) == "test message"
        assert error.node_name is None


class TestHandleNodeError:
    """Tests for handle_node_error function."""

    def test_handle_error(self):
        """Test handling error in node."""
        state = create_initial_state("test query")
        error = Exception("test error")

        result = handle_node_error(state, error, "test_node")

        assert result["error"] == "Error in test_node: test error"
        assert "test_node:ERROR" in result["execution_path"]

    def test_preserves_state(self):
        """Test that error handling preserves other state values."""
        state = create_initial_state("test query")
        state["decision"] = "search"
        error = Exception("test error")

        result = handle_node_error(state, error, "test_node")

        assert result["user_query"] == "test query"
        assert result["decision"] == "search"
        assert result["error"] is not None

    def test_adds_to_execution_path(self):
        """Test that error is added to execution path."""
        state = create_initial_state("test query")
        state["execution_path"] = ["node1", "node2"]
        error = Exception("test error")

        result = handle_node_error(state, error, "test_node")

        assert len(result["execution_path"]) == 3
        assert result["execution_path"][-1] == "test_node:ERROR"
