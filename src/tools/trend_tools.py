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
            # Get interest over time
            timeseries_params = {
                "engine": "google_trends",
                "q": topic,
                "api_key": self.api_key,
                "data_type": "TIMESERIES",
                "date": self._convert_timeframe(timeframe),
            }

            timeseries_search = client(timeseries_params)
            timeseries_results = timeseries_search.get_dict()

            # Get related queries
            related_params = {
                "engine": "google_trends",
                "q": topic,
                "api_key": self.api_key,
                "data_type": "RELATED_QUERIES",
            }

            related_search = client(related_params)
            related_results = related_search.get_dict()

            # Extract interest over time data
            interest_over_time = timeseries_results.get("interest_over_time", {})
            timeline_data = interest_over_time.get("timeline_data", [])

            # Extract related queries
            related_queries_data = related_results.get("related_queries", {})
            rising_queries = related_queries_data.get("rising", [])
            top_queries = related_queries_data.get("top", [])

            # Format trends list
            trends = []
            for query in rising_queries[:10]:
                trends.append(
                    {
                        "title": query.get("query", ""),
                        "description": f"Rising query with {query.get('value', 0)}% increase",
                        "source": "google_trends",
                        "type": "rising",
                        "value": query.get("value", 0),
                    }
                )

            for query in top_queries[:10]:
                trends.append(
                    {
                        "title": query.get("query", ""),
                        "description": f"Top related query",
                        "source": "google_trends",
                        "type": "top",
                        "value": query.get("value", 0),
                    }
                )

            logger.info(
                f"Found {len(trends)} trends for topic: {topic} "
                f"(Interest over time: {len(timeline_data)} data points)"
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
            logger.error(f"Error in Google Trends API: {e}")
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
