"""Analysis node - processes data and creates visualizations (SOLID principles)."""

from ..graph.state import GraphState
from ..nodes.interfaces import DataFormatter
from ..utils.errors import handle_node_error
from ..utils.formatters import ResponseFormatter
from ..utils.logging import get_logger
from ..utils.visualization import create_visualization
from ..tools.knowledge_base_tools import get_knowledge_base_context

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

        # Log incoming data
        logger.info(f"[Analysis Node] Processing analysis for query: '{user_query}'")
        logger.info(f"[Analysis Node] Search results count: {len(search_results)}")
        logger.info(f"[Analysis Node] Raw data keys: {list(raw_data.keys()) if raw_data else 'None'}")
        
        if raw_data:
            if "count" in raw_data:
                logger.info(f"[Analysis Node] Raw data count: {raw_data.get('count')}")
            if "trends" in raw_data:
                logger.info(f"[Analysis Node] Raw data trends count: {len(raw_data.get('trends', []))}")
            if "error" in raw_data:
                logger.warning(f"[Analysis Node] Raw data contains error: {raw_data.get('error')}")
        
        if len(search_results) == 0:
            logger.warning(
                f"[Analysis Node] WARNING: No search results to process. "
                f"This may indicate: 1) Empty API response, 2) No data found, 3) Processing error"
            )

        # Get relevant context from knowledge base (RAG)
        kb_context = ""
        try:
            kb_context = get_knowledge_base_context(user_query, max_chunks=5)
            if kb_context:
                logger.info(f"Retrieved {len(kb_context)} chars of context from knowledge base for analysis")
        except Exception as e:
            logger.warning(f"Could not retrieve knowledge base context: {e}")

        # Prepare data for processing
        data_to_format = {
            "search_results": search_results,
            "raw_data": raw_data,
            "kb_context": kb_context,  # Include KB context for formatter
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

        # Format response (include KB context)
        logger.info(f"[Analysis Node] Formatting response (has_charts={charts_created})")
        formatted_response = self.formatter.format(
            query=user_query, data=data_to_format, has_charts=charts_created, kb_context=kb_context
        )
        logger.info(f"[Analysis Node] Formatted response length: {len(formatted_response) if formatted_response else 0} characters")

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
