"""Graph state definition with strict typing."""

from typing import Any, Dict, List, Optional, TypedDict


class GraphState(TypedDict):
    """
    State that flows through the LangGraph.

    All nodes receive and return this state, ensuring type safety
    and clear data contracts between components.
    """

    # Input data
    user_query: str
    user_id: Optional[str]

    # Thinking node output
    decision: str  # "search", "direct_answer", "statistics"
    search_query: Optional[str]
    search_type: Optional[str]  # "keywords", "competitors", "trends"
    needs_charts: bool
    reasoning: Optional[str]

    # Search node output
    search_results: List[Dict[str, Any]]
    raw_data: Optional[Dict[str, Any]]

    # Analysis node output
    processed_data: Optional[str]
    visualization: Optional[str]  # Base64 encoded image or file path
    charts_created: bool
    formatted_response: Optional[str]

    # Context and history
    conversation_history: List[Dict[str, str]]
    execution_path: List[str]  # For tracing and debugging
    error: Optional[str]


def create_initial_state(user_query: str, user_id: Optional[str] = None) -> GraphState:
    """
    Create initial state for the graph.

    Args:
        user_query: User's input query
        user_id: Optional user identifier

    Returns:
        Initialized GraphState with default values
    """
    return GraphState(
        user_query=user_query,
        user_id=user_id,
        decision="",
        search_query=None,
        search_type=None,
        needs_charts=False,
        reasoning=None,
        search_results=[],
        raw_data=None,
        processed_data=None,
        visualization=None,
        charts_created=False,
        formatted_response=None,
        conversation_history=[],
        execution_path=[],
        error=None,
    )
