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
