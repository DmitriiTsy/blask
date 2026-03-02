"""Trend analysis tools (SOLID - Single Responsibility)."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from ..utils.logging import get_logger

logger = get_logger(__name__)


class TrendAnalyzer(ABC):
    """
    Abstract base class for trend analysis (SOLID - Open/Closed).

    Allows extension with different trend sources.
    """

    @abstractmethod
    def get_trends(self, topic: str, timeframe: str = "30d") -> Dict[str, Any]:
        """
        Get trends for given topic.

        Args:
            topic: Topic to analyze
            timeframe: Time period (e.g., "7d", "30d", "1y")

        Returns:
            Dictionary with trend data
        """
        pass


class SearchBasedTrendAnalyzer(TrendAnalyzer):
    """
    Trend analyzer based on search results.

    Uses search tools to identify trending topics.
    """

    def __init__(self, search_tool: "SearchTool"):
        """
        Initialize trend analyzer.

        Args:
            search_tool: Search tool instance (SOLID - Dependency Inversion)
        """
        from ..tools.search_tools import SearchTool

        if not isinstance(search_tool, SearchTool):
            raise TypeError("search_tool must be a SearchTool instance")
        self.search_tool = search_tool

    def get_trends(self, topic: str, timeframe: str = "30d") -> Dict[str, Any]:
        """
        Get trends by searching for recent information.

        Args:
            topic: Topic to analyze
            timeframe: Time period (used in query)

        Returns:
            Trend analysis results
        """
        # Search for recent trends
        search_query = f"{topic} trends {timeframe} latest"
        results = self.search_tool.search(search_query)

        # Extract trend information
        trends = []
        for result in results[:10]:
            trends.append(
                {
                    "title": result.get("title", ""),
                    "description": result.get("snippet", ""),
                    "source": result.get("link", ""),
                }
            )

        logger.info(f"Found {len(trends)} trends for topic: {topic}")

        return {
            "topic": topic,
            "timeframe": timeframe,
            "trends": trends,
            "count": len(trends),
        }


class SerpAPIGoogleTrendsAnalyzer(TrendAnalyzer):
    """
    Real Google Trends analyzer using SerpAPI Google Trends API.

    Uses special Google Trends API (engine="google_trends") to get:
    - Interest over time (TIMESERIES)
    - Related queries (RELATED_QUERIES)
    - Regional data (GEO_MAP)
    """

    def __init__(self, api_key: str):
        """
        Initialize Google Trends analyzer.

        Args:
            api_key: SerpAPI API key
        """
        self.api_key = api_key
        self._client = None

    def _get_client(self):
        """Lazy initialization of SerpAPI client."""
        if self._client is None:
            try:
                from serpapi import GoogleSearch

                self._client = GoogleSearch
            except ImportError:
                logger.warning("serpapi not installed, using fallback")
                self._client = None
        return self._client

    def _convert_timeframe(self, timeframe: str) -> str:
        """
        Convert timeframe string to SerpAPI format.

        Args:
            timeframe: Timeframe string (e.g., "7d", "30d", "1y")

        Returns:
            SerpAPI timeframe format
        """
        # SerpAPI uses: "now 7-d", "now 1-m", "now 1-y", etc.
        timeframe_map = {
            "7d": "now 7-d",
            "30d": "now 1-m",
            "90d": "now 3-m",
            "1y": "now 1-y",
            "5y": "today 5-y",
        }
        return timeframe_map.get(timeframe, "now 1-m")

    def get_trends(self, topic: str, timeframe: str = "30d") -> Dict[str, Any]:
        """
        Get trends using real Google Trends API.

        Args:
            topic: Topic to analyze
            timeframe: Time period (e.g., "7d", "30d", "1y")

        Returns:
            Dictionary with trend data including:
            - interest_over_time: Time series data
            - related_queries: Related queries
            - regional_data: Regional interest
            - trends: Formatted trends list
        """
        client = self._get_client()
        if client is None:
            logger.warning("SerpAPI not available, returning empty trends")
            return {
                "topic": topic,
                "timeframe": timeframe,
                "trends": [],
                "count": 0,
                "interest_over_time": [],
                "related_queries": [],
            }

        try:
            logger.info(f"[Google Trends API] Starting request for topic: '{topic}', timeframe: {timeframe}")
            
            # Get interest over time
            # Note: For TIMESERIES, 'date' parameter may not be required or may need different format
            # Try without date first, or use timeframe directly
            timeseries_params = {
                "engine": "google_trends",
                "q": topic,
                "api_key": self.api_key,
                "data_type": "TIMESERIES",
            }
            # Only add date if timeframe is specified and not default
            # Some SerpAPI versions may not support 'date' parameter for TIMESERIES
            # Try without it first - API may use default timeframe
            logger.debug(f"[Google Trends API] TIMESERIES params: engine={timeseries_params['engine']}, q={timeseries_params['q']}, data_type={timeseries_params['data_type']}")

            timeseries_search = client(timeseries_params)
            timeseries_results = timeseries_search.get_dict()
            
            # Log TIMESERIES response structure
            logger.debug(f"[Google Trends API] TIMESERIES response keys: {list(timeseries_results.keys())}")
            if "error" in timeseries_results:
                logger.warning(f"[Google Trends API] TIMESERIES error: {timeseries_results.get('error')}")

            # Get related queries
            related_params = {
                "engine": "google_trends",
                "q": topic,
                "api_key": self.api_key,
                "data_type": "RELATED_QUERIES",
            }
            logger.debug(f"[Google Trends API] RELATED_QUERIES params: engine={related_params['engine']}, q={related_params['q']}")

            related_search = client(related_params)
            related_results = related_search.get_dict()
            
            # Log RELATED_QUERIES response structure
            logger.debug(f"[Google Trends API] RELATED_QUERIES response keys: {list(related_results.keys())}")
            if "error" in related_results:
                logger.warning(f"[Google Trends API] RELATED_QUERIES error: {related_results.get('error')}")

            # Extract interest over time data
            interest_over_time = timeseries_results.get("interest_over_time", {})
            timeline_data = interest_over_time.get("timeline_data", [])
            logger.info(f"[Google Trends API] Interest over time data points: {len(timeline_data)}")
            if timeline_data:
                logger.debug(f"[Google Trends API] First timeline entry: {timeline_data[0] if len(timeline_data) > 0 else 'N/A'}")
            else:
                logger.warning(f"[Google Trends API] No timeline data found. interest_over_time structure: {list(interest_over_time.keys())}")

            # Extract related queries
            related_queries_data = related_results.get("related_queries", {})
            rising_queries = related_queries_data.get("rising", [])
            top_queries = related_queries_data.get("top", [])
            logger.info(f"[Google Trends API] Rising queries found: {len(rising_queries)}, Top queries found: {len(top_queries)}")
            if not rising_queries and not top_queries:
                logger.warning(f"[Google Trends API] No related queries found. related_queries structure: {list(related_queries_data.keys())}")
                logger.debug(f"[Google Trends API] Full related_queries_data: {related_queries_data}")

            # Format trends list
            trends = []
            for query in rising_queries[:10]:
                query_text = query.get("query", "")
                query_value = query.get("value", 0)
                logger.debug(f"[Google Trends API] Adding rising query: '{query_text}' (value: {query_value})")
                trends.append(
                    {
                        "title": query_text,
                        "description": f"Rising query with {query_value}% increase",
                        "source": "google_trends",
                        "type": "rising",
                        "value": query_value,
                    }
                )

            for query in top_queries[:10]:
                query_text = query.get("query", "")
                query_value = query.get("value", 0)
                logger.debug(f"[Google Trends API] Adding top query: '{query_text}' (value: {query_value})")
                trends.append(
                    {
                        "title": query_text,
                        "description": f"Top related query",
                        "source": "google_trends",
                        "type": "top",
                        "value": query_value,
                    }
                )

            logger.info(
                f"[Google Trends API] Total trends formatted: {len(trends)} for topic: '{topic}' "
                f"(Interest over time: {len(timeline_data)} data points, "
                f"Rising: {len(rising_queries)}, Top: {len(top_queries)})"
            )
            
            if len(trends) == 0:
                logger.warning(
                    f"[Google Trends API] WARNING: No trends found for topic '{topic}'. "
                    f"This may indicate: 1) Topic too specific/rare, 2) No data in Google Trends, "
                    f"3) API response structure different than expected"
                )

            return {
                "topic": topic,
                "timeframe": timeframe,
                "trends": trends,
                "count": len(trends),
                "interest_over_time": timeline_data,
                "related_queries": {
                    "rising": rising_queries[:10],
                    "top": top_queries[:10],
                },
                "raw_timeseries": interest_over_time,
            }

        except Exception as e:
            import traceback
            logger.error(f"[Google Trends API] Exception occurred: {type(e).__name__}: {e}")
            logger.debug(f"[Google Trends API] Full traceback: {traceback.format_exc()}")
            # Fallback to empty results
            return {
                "topic": topic,
                "timeframe": timeframe,
                "trends": [],
                "count": 0,
                "interest_over_time": [],
                "related_queries": [],
                "error": str(e),
            }


class MockTrendAnalyzer(TrendAnalyzer):
    """Mock trend analyzer for testing."""

    def __init__(self, mock_data: Dict[str, Any] | None = None):
        """
        Initialize mock analyzer.

        Args:
            mock_data: Optional predefined trend data
        """
        self.mock_data = mock_data or {
            "topic": "test",
            "timeframe": "30d",
            "trends": [],
            "count": 0,
        }

    def get_trends(self, topic: str, timeframe: str = "30d") -> Dict[str, Any]:
        """
        Return mock trends.

        Args:
            topic: Topic (ignored in mock)
            timeframe: Timeframe (ignored in mock)

        Returns:
            Mock trend data
        """
        return {**self.mock_data, "topic": topic, "timeframe": timeframe}
