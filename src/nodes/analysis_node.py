"""Analysis node - processes data and creates visualizations (SOLID principles)."""

from ..graph.state import GraphState
from ..nodes.interfaces import DataFormatter
from ..utils.errors import handle_node_error
from ..utils.formatters import ResponseFormatter
from ..utils.logging import get_logger
from ..utils.visualization import create_visualization

logger = get_logger(__name__)


class AnalysisNodeProcessor:
    """
    Analysis node processor (SOLID - Single Responsibility).

    Handles analysis logic separately from node function.
    """

    def __init__(self, formatter: DataFormatter | None = None):
        """
        Initialize analysis processor.

        Args:
            formatter: Optional custom formatter (SOLID - Dependency Inversion)
        """
        self.formatter = formatter or ResponseFormatter()

    def process_analysis(self, state: GraphState) -> GraphState:
        """
        Process analysis and create visualizations.

        Args:
            state: Current graph state

        Returns:
            Updated state with processed data and visualizations
        """
        # Extract data
        search_results = state.get("search_results", [])
        raw_data = state.get("raw_data", {})
        user_query = state.get("user_query", "")
        needs_charts = state.get("needs_charts", False)

        # Prepare data for processing
        data_to_format = {
            "search_results": search_results,
            "raw_data": raw_data,
        }

        # Create visualization if needed
        visualization = None
        charts_created = False

        if needs_charts or state.get("decision") == "statistics":
            logger.info("Creating visualization")
            visualization = create_visualization(state)
            if visualization:
                charts_created = True
                logger.info("Visualization created successfully")

        # Format response
        logger.info("Formatting response")
        formatted_response = self.formatter.format(
            query=user_query, data=data_to_format, has_charts=charts_created
        )

        # Update state
        return {
            **state,
            "processed_data": formatted_response,
            "visualization": visualization,
            "charts_created": charts_created,
            "formatted_response": formatted_response,
            "execution_path": state.get("execution_path", []) + ["analysis_node"],
        }


def analysis_node(state: GraphState) -> GraphState:
    """
    Analysis node - processes data and creates visualizations.

    This node:
    1. Processes search results and raw data
    2. Creates visualizations if needed
    3. Formats response for user
    4. Updates state with final output

    Args:
        state: Current graph state

    Returns:
        Updated state with processed data
    """
    logger.info("Analysis node processing")

    try:
        processor = AnalysisNodeProcessor()
        return processor.process_analysis(state)

    except Exception as e:
        logger.error(f"Error in analysis node: {e}")
        return handle_node_error(state, e, "analysis_node")
