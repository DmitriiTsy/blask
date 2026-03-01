"""Error handling utilities."""

from typing import Optional

from ..graph.state import GraphState


class GraphError(Exception):
    """Base exception for graph-related errors."""

    def __init__(self, message: str, node_name: Optional[str] = None):
        """
        Initialize graph error.

        Args:
            message: Error message
            node_name: Name of the node where error occurred
        """
        super().__init__(message)
        self.node_name = node_name
        self.message = message


def handle_node_error(state: GraphState, error: Exception, node_name: str) -> GraphState:
    """
    Handle error in a node and update state.

    Args:
        state: Current graph state
        error: Exception that occurred
        node_name: Name of the node where error occurred

    Returns:
        Updated state with error information
    """
    error_message = f"Error in {node_name}: {str(error)}"
    return {
        **state,
        "error": error_message,
        "execution_path": state.get("execution_path", []) + [f"{node_name}:ERROR"],
    }
