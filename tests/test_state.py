"""Tests for graph state."""

import pytest

from src.graph.state import GraphState, create_initial_state


class TestCreateInitialState:
    """Tests for create_initial_state function."""

    def test_create_with_query(self):
        """Test creating state with query."""
        state = create_initial_state("test query")
        assert state["user_query"] == "test query"
        assert state["user_id"] is None

    def test_create_with_user_id(self):
        """Test creating state with user_id."""
        state = create_initial_state("test query", "user123")
        assert state["user_query"] == "test query"
        assert state["user_id"] == "user123"

    def test_default_values(self):
        """Test that default values are set correctly."""
        state = create_initial_state("test")
        assert state["decision"] == ""
        assert state["search_query"] is None
        assert state["search_type"] is None
        assert state["needs_charts"] is False
        assert state["search_results"] == []
        assert state["raw_data"] is None
        assert state["processed_data"] is None
        assert state["visualization"] is None
        assert state["charts_created"] is False
        assert state["formatted_response"] is None
        assert state["conversation_history"] == []
        assert state["execution_path"] == []
        assert state["error"] is None

    def test_state_type(self):
        """Test that returned state is GraphState type."""
        state = create_initial_state("test")
        assert isinstance(state, dict)
        # Check all required keys exist
        required_keys = [
            "user_query",
            "user_id",
            "decision",
            "search_query",
            "search_type",
            "needs_charts",
            "reasoning",
            "search_results",
            "raw_data",
            "processed_data",
            "visualization",
            "charts_created",
            "formatted_response",
            "conversation_history",
            "execution_path",
            "error",
        ]
        for key in required_keys:
            assert key in state
