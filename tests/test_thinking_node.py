"""Tests for thinking node."""

import pytest

from src.graph.state import create_initial_state
from src.nodes.thinking_node import LLMDecisionMaker, thinking_node


class TestLLMDecisionMaker:
    """Tests for LLMDecisionMaker."""

    def test_initialization(self):
        """Test decision maker initialization."""
        maker = LLMDecisionMaker()
        assert maker.parser is not None
        assert maker.prompt is not None

    def test_make_decision_without_llm(self):
        """Test decision making without LLM (mock mode)."""
        maker = LLMDecisionMaker()
        maker.llm = None  # Force mock mode

        result = maker.make_decision("test query", [])

        assert "decision" in result
        assert "search_type" in result
        assert "search_query" in result
        assert "needs_charts" in result
        assert "reasoning" in result

    def test_make_decision_structure(self):
        """Test that decision result has correct structure."""
        maker = LLMDecisionMaker()
        maker.llm = None

        result = maker.make_decision("test", [])

        assert isinstance(result["decision"], str)
        assert isinstance(result["needs_charts"], bool)
        assert result["search_query"] is not None


class TestThinkingNode:
    """Tests for thinking_node function."""

    def test_thinking_node_with_query(self):
        """Test thinking node with valid query."""
        state = create_initial_state("test query")

        result = thinking_node(state)

        assert result["user_query"] == "test query"
        assert "decision" in result
        assert "execution_path" in result
        assert "thinking_node" in result["execution_path"]

    def test_thinking_node_empty_query(self):
        """Test thinking node with empty query."""
        state = create_initial_state("")

        result = thinking_node(state)

        # Should handle error gracefully
        assert "error" in result or result["decision"] != ""

    def test_thinking_node_updates_state(self):
        """Test that thinking node updates state correctly."""
        state = create_initial_state("test query")

        result = thinking_node(state)

        assert result["decision"] != ""
        assert result.get("search_query") is not None or result["decision"] == "direct_answer"
        assert result.get("reasoning") is not None

    def test_thinking_node_preserves_input(self):
        """Test that thinking node preserves input values."""
        state = create_initial_state("test query", "user123")
        state["conversation_history"] = [{"role": "user", "content": "previous"}]

        result = thinking_node(state)

        assert result["user_query"] == "test query"
        assert result["user_id"] == "user123"
        assert len(result["conversation_history"]) == 1

    def test_thinking_node_error_handling(self):
        """Test error handling in thinking node."""
        state = create_initial_state("test")
        # Force an error by making state invalid
        state["user_query"] = None  # type: ignore

        result = thinking_node(state)

        # Should handle error and return state with error field
        assert "error" in result or "execution_path" in result
