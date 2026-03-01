"""Pytest configuration and fixtures."""

import pytest

from src.graph.state import GraphState, create_initial_state


@pytest.fixture
def sample_state() -> GraphState:
    """Create sample graph state for testing."""
    return create_initial_state("test query", "test_user")


@pytest.fixture
def empty_state() -> GraphState:
    """Create empty graph state for testing."""
    return create_initial_state("")


@pytest.fixture
def state_with_decision() -> GraphState:
    """Create state with decision made."""
    state = create_initial_state("test query")
    state["decision"] = "search"
    state["search_type"] = "keywords"
    state["search_query"] = "test search"
    return state


@pytest.fixture
def state_with_results() -> GraphState:
    """Create state with search results."""
    state = create_initial_state("test query")
    state["decision"] = "search"
    state["search_type"] = "keywords"
    state["search_query"] = "test"
    state["search_results"] = [
        {"title": "Test Result", "snippet": "Test snippet", "link": "http://test.com"}
    ]
    state["raw_data"] = {"type": "keywords", "results": state["search_results"]}
    return state
