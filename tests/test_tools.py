"""Tests for search and analysis tools."""

import pytest

from src.tools.competitor_tools import (
    BasicCompetitorAnalyzer,
    MockCompetitorAnalyzer,
)
from src.tools.search_tools import MockSearchTool, SerpAPISearchTool
from src.tools.trend_tools import MockTrendAnalyzer, SearchBasedTrendAnalyzer


class TestMockSearchTool:
    """Tests for MockSearchTool."""

    def test_search_with_mock_results(self):
        """Test search with predefined mock results."""
        mock_results = [{"title": "Test", "link": "http://test.com"}]
        tool = MockSearchTool(mock_results)
        results = tool.search("test query")
        assert results == mock_results

    def test_search_without_results(self):
        """Test search without predefined results."""
        tool = MockSearchTool()
        results = tool.search("test query")
        assert results == []


class TestSerpAPISearchTool:
    """Tests for SerpAPISearchTool."""

    def test_initialization(self):
        """Test tool initialization."""
        tool = SerpAPISearchTool("test_key")
        assert tool.api_key == "test_key"
        assert tool._client is None

    def test_search_without_client(self):
        """Test search when client is not available."""
        tool = SerpAPISearchTool("test_key")
        # Mock that client is None
        tool._client = None
        results = tool.search("test")
        # Should return empty list when client unavailable
        assert isinstance(results, list)


class TestBasicCompetitorAnalyzer:
    """Tests for BasicCompetitorAnalyzer."""

    def test_initialization(self):
        """Test analyzer initialization."""
        search_tool = MockSearchTool()
        analyzer = BasicCompetitorAnalyzer(search_tool)
        assert analyzer.search_tool == search_tool

    def test_initialization_with_wrong_type(self):
        """Test that initialization fails with wrong type."""
        with pytest.raises(TypeError):
            BasicCompetitorAnalyzer("not a search tool")

    def test_analyze(self):
        """Test competitor analysis."""
        mock_results = [
            {
                "title": "Competitor 1",
                "snippet": "Description 1",
                "link": "http://comp1.com",
            }
        ]
        search_tool = MockSearchTool(mock_results)
        analyzer = BasicCompetitorAnalyzer(search_tool)

        result = analyzer.analyze("test keyword")

        assert result["keyword"] == "test keyword"
        assert len(result["competitors"]) > 0
        assert result["count"] > 0


class TestMockCompetitorAnalyzer:
    """Tests for MockCompetitorAnalyzer."""

    def test_analyze_with_mock_data(self):
        """Test analysis with mock data."""
        mock_data = {
            "keyword": "test",
            "competitors": [{"name": "Comp1"}],
            "count": 1,
        }
        analyzer = MockCompetitorAnalyzer(mock_data)
        result = analyzer.analyze("new_keyword")
        assert result["keyword"] == "new_keyword"
        assert result["count"] == 1


class TestSearchBasedTrendAnalyzer:
    """Tests for SearchBasedTrendAnalyzer."""

    def test_initialization(self):
        """Test analyzer initialization."""
        search_tool = MockSearchTool()
        analyzer = SearchBasedTrendAnalyzer(search_tool)
        assert analyzer.search_tool == search_tool

    def test_initialization_with_wrong_type(self):
        """Test that initialization fails with wrong type."""
        with pytest.raises(TypeError):
            SearchBasedTrendAnalyzer("not a search tool")

    def test_get_trends(self):
        """Test getting trends."""
        mock_results = [
            {"title": "Trend 1", "snippet": "Description", "link": "http://trend1.com"}
        ]
        search_tool = MockSearchTool(mock_results)
        analyzer = SearchBasedTrendAnalyzer(search_tool)

        result = analyzer.get_trends("AI", "30d")

        assert result["topic"] == "AI"
        assert result["timeframe"] == "30d"
        assert len(result["trends"]) > 0
        assert result["count"] > 0


class TestMockTrendAnalyzer:
    """Tests for MockTrendAnalyzer."""

    def test_get_trends_with_mock_data(self):
        """Test getting trends with mock data."""
        mock_data = {
            "topic": "test",
            "timeframe": "30d",
            "trends": [{"title": "Trend 1"}],
            "count": 1,
        }
        analyzer = MockTrendAnalyzer(mock_data)
        result = analyzer.get_trends("new_topic", "7d")
        assert result["topic"] == "new_topic"
        assert result["timeframe"] == "7d"
        assert result["count"] == 1
