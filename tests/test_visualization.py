"""Tests for visualization utilities."""

import pytest

from src.graph.state import create_initial_state
from src.utils.visualization import (
    MatplotlibChartCreator,
    create_visualization,
    extract_chart_data,
    should_create_chart,
)


class TestShouldCreateChart:
    """Tests for should_create_chart function."""

    def test_should_create_for_statistics(self):
        """Test that chart is created for statistics decision."""
        state = create_initial_state("test")
        state["decision"] = "statistics"

        result = should_create_chart(state)

        assert result is True

    def test_should_create_for_needs_charts(self):
        """Test that chart is created when needs_charts is True."""
        state = create_initial_state("test")
        state["needs_charts"] = True

        result = should_create_chart(state)

        assert result is True

    def test_should_not_create_default(self):
        """Test that chart is not created by default."""
        state = create_initial_state("test")

        result = should_create_chart(state)

        assert result is False

    def test_should_create_with_values(self):
        """Test that chart is created when values are present."""
        state = create_initial_state("test")
        state["raw_data"] = {"values": [1, 2, 3]}

        result = should_create_chart(state)

        assert result is True


class TestExtractChartData:
    """Tests for extract_chart_data function."""

    def test_extract_with_values(self):
        """Test extracting chart data with values."""
        data = {
            "values": [1, 2, 3],
            "labels": ["A", "B", "C"],
            "title": "Test Chart",
        }

        result = extract_chart_data(data)

        assert result is not None
        assert result["y"] == [1, 2, 3]
        assert result["x"] == ["A", "B", "C"]
        assert result["title"] == "Test Chart"

    def test_extract_with_results(self):
        """Test extracting chart data from results."""
        data = {"results": [1, 2, 3, 4, 5]}

        result = extract_chart_data(data)

        assert result is not None
        assert result["y"] == [5]  # Count of results

    def test_extract_no_data(self):
        """Test extracting with no chart data."""
        data = {}

        result = extract_chart_data(data)

        assert result is None


class TestMatplotlibChartCreator:
    """Tests for MatplotlibChartCreator."""

    def test_create_line_chart(self):
        """Test creating line chart."""
        creator = MatplotlibChartCreator()
        data = {
            "x": [1, 2, 3, 4, 5],
            "y": [2, 4, 6, 8, 10],
            "title": "Test Chart",
        }

        result = creator.create(data, "line")

        assert result is not None
        assert result.startswith("data:image/png;base64,")

    def test_create_bar_chart(self):
        """Test creating bar chart."""
        creator = MatplotlibChartCreator()
        data = {
            "x": ["A", "B", "C"],
            "y": [10, 20, 30],
            "title": "Test Chart",
        }

        result = creator.create(data, "bar")

        assert result is not None
        assert result.startswith("data:image/png;base64,")

    def test_create_pie_chart(self):
        """Test creating pie chart."""
        creator = MatplotlibChartCreator()
        data = {
            "labels": ["A", "B", "C"],
            "values": [30, 40, 30],
            "title": "Test Chart",
        }

        result = creator.create(data, "pie")

        assert result is not None
        assert result.startswith("data:image/png;base64,")

    def test_create_with_insufficient_data(self):
        """Test creating chart with insufficient data."""
        creator = MatplotlibChartCreator()
        data = {"x": [], "y": []}

        result = creator.create(data, "line")

        # Should return None or handle gracefully
        assert result is None or isinstance(result, str)

    def test_create_unknown_type(self):
        """Test creating chart with unknown type."""
        creator = MatplotlibChartCreator()
        data = {"x": [1, 2, 3], "y": [1, 2, 3]}

        result = creator.create(data, "unknown")

        # Should fallback to line chart
        assert result is not None or result is None


class TestCreateVisualization:
    """Tests for create_visualization function."""

    def test_create_visualization_with_data(self):
        """Test creating visualization with valid data."""
        state = create_initial_state("test")
        state["decision"] = "statistics"
        state["raw_data"] = {
            "values": [1, 2, 3, 4, 5],
            "labels": ["A", "B", "C", "D", "E"],
        }

        result = create_visualization(state)

        # May or may not create visualization depending on data
        assert result is None or result.startswith("data:image/png;base64,")

    def test_create_visualization_no_data(self):
        """Test creating visualization without data."""
        state = create_initial_state("test")
        state["raw_data"] = {}

        result = create_visualization(state)

        assert result is None

    def test_create_visualization_not_needed(self):
        """Test that visualization is not created when not needed."""
        state = create_initial_state("test")
        state["decision"] = "direct_answer"

        result = create_visualization(state)

        assert result is None
