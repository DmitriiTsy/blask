"""Main graph definition with routing logic."""

from typing import Literal

from langgraph.graph import END, START, StateGraph

from ..graph.state import GraphState
from ..nodes.analysis_node import analysis_node
from ..nodes.search_node import search_node
from ..nodes.thinking_node import thinking_node
from ..utils.logging import get_logger

logger = get_logger(__name__)


def route_after_thinking(state: GraphState) -> Literal["search_node", "analysis_node"]:
    """
    Route after thinking node based on decision (SOLID - Single Responsibility).

    Args:
        state: Current graph state

    Returns:
        Next node name
    """
    decision = state.get("decision", "")

    if decision == "direct_answer":
        logger.info("Routing to analysis_node (direct answer)")
        return "analysis_node"
    elif decision in ["search", "statistics"]:
        logger.info("Routing to search_node")
        return "search_node"
    else:
        # Default to analysis
        logger.warning(f"Unknown decision: {decision}, routing to analysis_node")
        return "analysis_node"


def route_after_search(state: GraphState) -> Literal["analysis_node"]:
    """
    Route after search node (always goes to analysis).

    Args:
        state: Current graph state

    Returns:
        Next node name (always analysis_node)
    """
    logger.info("Routing to analysis_node after search")
    return "analysis_node"


def create_graph() -> StateGraph:
    """
    Create and configure the LangGraph (SOLID - Single Responsibility).

    Returns:
        Configured StateGraph instance
    """
    # Create graph
    workflow = StateGraph(GraphState)

    # Add nodes
    workflow.add_node("thinking_node", thinking_node)
    workflow.add_node("search_node", search_node)
    workflow.add_node("analysis_node", analysis_node)

    # Set entry point
    workflow.set_entry_point("thinking_node")

    # Add conditional edges
    workflow.add_conditional_edges(
        "thinking_node",
        route_after_thinking,
        {
            "search_node": "search_node",
            "analysis_node": "analysis_node",
        },
    )

    # Add edge from search to analysis
    workflow.add_edge("search_node", "analysis_node")

    # Set exit point
    workflow.add_edge("analysis_node", END)

    logger.info("Graph created successfully")

    return workflow.compile()
