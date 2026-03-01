"""Competitor analysis tools (SOLID - Single Responsibility)."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from ..utils.logging import get_logger

logger = get_logger(__name__)


class CompetitorAnalyzer(ABC):
    """
    Abstract base class for competitor analysis (SOLID - Open/Closed).

    Allows extension with different analysis strategies.
    """

    @abstractmethod
    def analyze(self, keyword: str) -> Dict[str, Any]:
        """
        Analyze competitors for given keyword.

        Args:
            keyword: Keyword to analyze

        Returns:
            Dictionary with competitor analysis data
        """
        pass


class BasicCompetitorAnalyzer(CompetitorAnalyzer):
    """
    Basic competitor analyzer using search results.

    Uses search tools to find and analyze competitors.
    """

    def __init__(self, search_tool: "SearchTool"):
        """
        Initialize competitor analyzer.

        Args:
            search_tool: Search tool instance (SOLID - Dependency Inversion)
        """
        from ..tools.search_tools import SearchTool

        if not isinstance(search_tool, SearchTool):
            raise TypeError("search_tool must be a SearchTool instance")
        self.search_tool = search_tool

    def analyze(self, keyword: str) -> Dict[str, Any]:
        """
        Analyze competitors by searching for keyword.

        Args:
            keyword: Keyword to analyze

        Returns:
            Competitor analysis results
        """
        # Search for companies/products related to keyword
        search_query = f"{keyword} competitors alternatives"
        results = self.search_tool.search(search_query)

        # Extract competitor names from results
        competitors = []
        for result in results[:5]:  # Top 5 results
            title = result.get("title", "")
            snippet = result.get("snippet", "")
            competitors.append(
                {
                    "name": title,
                    "description": snippet,
                    "source": result.get("link", ""),
                }
            )

        logger.info(f"Found {len(competitors)} competitors for keyword: {keyword}")

        return {
            "keyword": keyword,
            "competitors": competitors,
            "count": len(competitors),
        }


class MockCompetitorAnalyzer(CompetitorAnalyzer):
    """Mock competitor analyzer for testing."""

    def __init__(self, mock_data: Dict[str, Any] | None = None):
        """
        Initialize mock analyzer.

        Args:
            mock_data: Optional predefined analysis data
        """
        self.mock_data = mock_data or {
            "keyword": "test",
            "competitors": [],
            "count": 0,
        }

    def analyze(self, keyword: str) -> Dict[str, Any]:
        """
        Return mock analysis.

        Args:
            keyword: Keyword (ignored in mock)

        Returns:
            Mock analysis data
        """
        return {**self.mock_data, "keyword": keyword}
