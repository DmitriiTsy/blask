"""Search tools for keyword search (SOLID - Single Responsibility)."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from ..utils.logging import get_logger

logger = get_logger(__name__)


class SearchTool(ABC):
    """
    Abstract base class for search tools (SOLID - Open/Closed Principle).

    Allows easy extension with new search providers without modifying existing code.
    """

    @abstractmethod
    def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Perform search with given query.

        Args:
            query: Search query string

        Returns:
            List of search results with metadata
        """
        pass


class SerpAPISearchTool(SearchTool):
    """
    SerpAPI search implementation.

    Uses SerpAPI for Google search results.
    """

    def __init__(self, api_key: str):
        """
        Initialize SerpAPI search tool.

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
                logger.warning("serpapi not installed, using mock")
                self._client = None
        return self._client

    def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Search using SerpAPI.

        Args:
            query: Search query

        Returns:
            List of search results
        """
        client = self._get_client()
        if client is None:
            logger.warning("SerpAPI not available, returning empty results")
            return []

        try:
            search = client({"q": query, "api_key": self.api_key})
            results = search.get_dict()

            # Extract organic results
            organic_results = results.get("organic_results", [])
            formatted_results = [
                {
                    "title": r.get("title", ""),
                    "link": r.get("link", ""),
                    "snippet": r.get("snippet", ""),
                    "source": "serpapi",
                }
                for r in organic_results[:10]  # Limit to top 10
            ]

            logger.info(f"Found {len(formatted_results)} results for query: {query}")
            return formatted_results

        except Exception as e:
            logger.error(f"Error in SerpAPI search: {e}")
            return []


class MockSearchTool(SearchTool):
    """
    Mock search tool for testing (SOLID - Dependency Inversion).

    Allows testing without external API dependencies.
    """

    def __init__(self, mock_results: List[Dict[str, Any]] | None = None):
        """
        Initialize mock search tool.

        Args:
            mock_results: Optional predefined results
        """
        self.mock_results = mock_results or []

    def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Return mock search results.

        Args:
            query: Search query (ignored in mock)

        Returns:
            Mock results
        """
        return self.mock_results
