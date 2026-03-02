"""Search node - performs search operations (SOLID principles)."""

from typing import Any, Dict, List

from ..graph.state import GraphState
from ..tools.competitor_tools import CompetitorAnalyzer
from ..tools.search_tools import SearchTool
from ..tools.trend_tools import TrendAnalyzer
from ..utils.errors import GraphError, handle_node_error
from ..utils.logging import get_logger

logger = get_logger(__name__)


class SearchNodeProcessor:
    """
    Search node processor (SOLID - Single Responsibility).

    Handles search logic separately from node function.
    """

    def __init__(
        self,
        search_tool: SearchTool,
        competitor_analyzer: CompetitorAnalyzer | None = None,
        trend_analyzer: TrendAnalyzer | None = None,
    ):
        """
        Initialize search processor.

        Args:
            search_tool: Search tool instance (SOLID - Dependency Inversion)
            competitor_analyzer: Optional competitor analyzer
            trend_analyzer: Optional trend analyzer
        """
        self.search_tool = search_tool
        self.competitor_analyzer = competitor_analyzer
        self.trend_analyzer = trend_analyzer

    def _extract_topic_from_query(self, query: str) -> str:
        """
        Extract clean topic from search query, removing trend-related words and years.

        Args:
            query: Search query that may contain "trends", years, etc.

        Returns:
            Clean topic string
        """
        import re

        # Remove common trend-related words
        query = re.sub(r'\b(trends?|trending|latest|current|recent)\b', '', query, flags=re.IGNORECASE)
        
        # Remove years (2020-2029)
        query = re.sub(r'\b20[0-9]{2}\b', '', query)
        
        # Remove extra whitespace
        query = ' '.join(query.split())
        
        return query.strip() or "trends"  # Fallback if everything was removed

    def process_search(self, state: GraphState) -> GraphState:
        """
        Process search based on state.

        Args:
            state: Current graph state

        Returns:
            Updated state with search results
        """
        search_type = state.get("search_type")
        search_query = state.get("search_query")

        if not search_query:
            raise GraphError("search_query is required for search", "search_node")

        results: List[Dict[str, Any]] = []
        raw_data: Dict[str, Any] = {}

        # Route to appropriate search tool based on type
        if search_type == "keywords":
            logger.info(f"Performing keyword search: {search_query}")
            results = self.search_tool.search(search_query)
            raw_data = {"type": "keywords", "query": search_query, "results": results}

        elif search_type == "competitors":
            if not self.competitor_analyzer:
                # Fallback to regular search
                logger.warning("Competitor analyzer not available, using regular search")
                results = self.search_tool.search(search_query)
            else:
                logger.info(f"Analyzing competitors: {search_query}")
                competitor_data = self.competitor_analyzer.analyze(search_query)
                raw_data = competitor_data
                # Convert to results format
                results = [
                    {
                        "title": comp.get("name", ""),
                        "snippet": comp.get("description", ""),
                        "link": comp.get("source", ""),
                        "type": "competitor",
                    }
                    for comp in competitor_data.get("competitors", [])
                ]

        elif search_type == "trends":
            if not self.trend_analyzer:
                # Fallback to regular search
                logger.warning("Trend analyzer not available, using regular search")
                results = self.search_tool.search(search_query)
            else:
                # Extract clean topic from search_query (remove "trends", years, etc.)
                topic = self._extract_topic_from_query(search_query)
                logger.info(f"[Search Node] Original query: '{search_query}' -> Extracted topic: '{topic}'")
                logger.info(f"[Search Node] Calling trend_analyzer.get_trends() for topic: '{topic}'")
                trend_data = self.trend_analyzer.get_trends(topic)
                
                # Log trend data structure
                logger.info(f"[Search Node] Trend data received - keys: {list(trend_data.keys())}")
                logger.info(f"[Search Node] Trend count: {trend_data.get('count', 0)}")
                logger.info(f"[Search Node] Trends list length: {len(trend_data.get('trends', []))}")
                logger.info(f"[Search Node] Interest over time data points: {len(trend_data.get('interest_over_time', []))}")
                
                if trend_data.get("error"):
                    logger.warning(f"[Search Node] Trend data contains error: {trend_data.get('error')}")
                
                if trend_data.get("count", 0) == 0:
                    logger.warning(
                        f"[Search Node] WARNING: No trends found (count=0) for topic '{topic}'. "
                        f"Raw data structure: {list(trend_data.keys())}"
                    )
                
                raw_data = trend_data
                # Convert to results format
                trends_list = trend_data.get("trends", [])
                logger.debug(f"[Search Node] Converting {len(trends_list)} trends to results format")
                results = [
                    {
                        "title": trend.get("title", ""),
                        "snippet": trend.get("description", ""),
                        "link": trend.get("source", ""),
                        "type": "trend",
                    }
                    for trend in trends_list
                ]
                logger.info(f"[Search Node] Converted {len(results)} trend results for search_type='trends'")

        else:
            # Default to keyword search
            logger.info(f"Unknown search_type, using keyword search: {search_query}")
            results = self.search_tool.search(search_query)
            raw_data = {"type": "keywords", "query": search_query, "results": results}

        return {
            **state,
            "search_results": results,
            "raw_data": raw_data,
            "execution_path": state.get("execution_path", []) + ["search_node"],
        }


def create_search_node(
    search_tool: SearchTool,
    competitor_analyzer: CompetitorAnalyzer | None = None,
    trend_analyzer: TrendAnalyzer | None = None,
):
    """
    Factory function to create search node with dependencies (SOLID - Dependency Injection).

    Args:
        search_tool: Search tool instance
        competitor_analyzer: Optional competitor analyzer
        trend_analyzer: Optional trend analyzer

    Returns:
        Search node function
    """
    processor = SearchNodeProcessor(search_tool, competitor_analyzer, trend_analyzer)

    def search_node(state: GraphState) -> GraphState:
        """
        Search node - performs search operations.

        Args:
            state: Current graph state

        Returns:
            Updated state with search results
        """
        logger.info(
            f"Search node processing: type={state.get('search_type')}, "
            f"query={state.get('search_query')}"
        )

        try:
            return processor.process_search(state)
        except Exception as e:
            logger.error(f"Error in search node: {e}")
            return handle_node_error(state, e, "search_node")

    return search_node


# Default search node (can be overridden)
def search_node(state: GraphState) -> GraphState:
    """
    Default search node implementation.

    Automatically creates analyzers based on available API keys.
    For production, use create_search_node() with proper dependencies.

    Args:
        state: Current graph state

    Returns:
        Updated state
    """
    logger.info(
        f"Search node processing: type={state.get('search_type')}, "
        f"query={state.get('search_query')}"
    )

    try:
        from ..config import get_settings
        from ..tools.competitor_tools import BasicCompetitorAnalyzer
        from ..tools.search_tools import MockSearchTool, SerpAPISearchTool
        from ..tools.trend_tools import (
            SearchBasedTrendAnalyzer,
            SerpAPIGoogleTrendsAnalyzer,
        )

        settings = get_settings()

        # Create search tool
        if settings.serpapi_key:
            logger.info("Using SerpAPI for search")
            search_tool = SerpAPISearchTool(settings.serpapi_key)
        else:
            logger.warning("SerpAPI key not found, using mock search")
            search_tool = MockSearchTool()

        # Create analyzers
        competitor_analyzer = BasicCompetitorAnalyzer(search_tool) if search_tool else None

        # Use real Google Trends API if SerpAPI key available, otherwise fallback
        if settings.serpapi_key:
            logger.info("Using real Google Trends API via SerpAPI")
            trend_analyzer = SerpAPIGoogleTrendsAnalyzer(settings.serpapi_key)
        else:
            logger.warning("Using SearchBasedTrendAnalyzer (fallback to regular search)")
            trend_analyzer = SearchBasedTrendAnalyzer(search_tool) if search_tool else None

        processor = SearchNodeProcessor(
            search_tool, competitor_analyzer, trend_analyzer
        )
        return processor.process_search(state)
    except Exception as e:
        logger.error(f"Error in search node: {e}")
        return handle_node_error(state, e, "search_node")
