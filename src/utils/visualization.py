"""Visualization utilities for creating charts (SOLID - Single Responsibility)."""

import base64
import io
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("Agg")  # Non-interactive backend

from ..utils.logging import get_logger

logger = get_logger(__name__)


class ChartCreator(ABC):
    """
    Abstract chart creator (SOLID - Open/Closed Principle).

    Allows extension with different chart types.
    """

    @abstractmethod
    def create(self, data: Dict[str, Any], chart_type: str) -> Optional[str]:
        """
        Create chart and return as base64 string or file path.

        Args:
            data: Data to visualize
            chart_type: Type of chart (line, bar, pie, etc.)

        Returns:
            Base64 encoded image or file path, None if creation fails
        """
        pass


class MatplotlibChartCreator(ChartCreator):
    """
    Matplotlib-based chart creator (SOLID - Single Responsibility).

    Handles creation of static charts using matplotlib.
    """

    def create(self, data: Dict[str, Any], chart_type: str) -> Optional[str]:
        """
        Create chart using matplotlib.

        Args:
            data: Data to visualize
            chart_type: Type of chart

        Returns:
            Base64 encoded PNG image
        """
        try:
            fig, ax = plt.subplots(figsize=(10, 6))

            if chart_type == "line":
                self._create_line_chart(ax, data)
            elif chart_type == "bar":
                self._create_bar_chart(ax, data)
            elif chart_type == "pie":
                self._create_pie_chart(ax, data)
            else:
                logger.warning(f"Unknown chart type: {chart_type}, using line")
                self._create_line_chart(ax, data)

            # Convert to base64
            buffer = io.BytesIO()
            fig.savefig(buffer, format="png", bbox_inches="tight", dpi=100)
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode("utf-8")
            plt.close(fig)

            return f"data:image/png;base64,{image_base64}"

        except Exception as e:
            logger.error(f"Error creating chart: {e}")
            return None

    def _create_line_chart(self, ax: Any, data: Dict[str, Any]) -> None:
        """Create line chart."""
        x = data.get("x", [])
        y = data.get("y", [])
        title = data.get("title", "Chart")

        if not x or not y:
            logger.warning("Insufficient data for line chart")
            return

        ax.plot(x, y, marker="o")
        ax.set_title(title)
        ax.set_xlabel(data.get("xlabel", "X"))
        ax.set_ylabel(data.get("ylabel", "Y"))
        ax.grid(True, alpha=0.3)

    def _create_bar_chart(self, ax: Any, data: Dict[str, Any]) -> None:
        """Create bar chart."""
        x = data.get("x", [])
        y = data.get("y", [])
        title = data.get("title", "Chart")

        if not x or not y:
            logger.warning("Insufficient data for bar chart")
            return

        ax.bar(x, y)
        ax.set_title(title)
        ax.set_xlabel(data.get("xlabel", "X"))
        ax.set_ylabel(data.get("ylabel", "Y"))
        ax.tick_params(axis="x", rotation=45)
        plt.tight_layout()

    def _create_pie_chart(self, ax: Any, data: Dict[str, Any]) -> None:
        """Create pie chart."""
        labels = data.get("labels", [])
        values = data.get("values", [])
        title = data.get("title", "Chart")

        if not labels or not values:
            logger.warning("Insufficient data for pie chart")
            return

        ax.pie(values, labels=labels, autopct="%1.1f%%")
        ax.set_title(title)


def should_create_chart(state: Dict[str, Any]) -> bool:
    """
    Determine if chart should be created based on state.

    Args:
        state: Graph state dictionary

    Returns:
        True if chart should be created
    """
    # Check if decision is statistics
    if state.get("decision") == "statistics":
        return True

    # Check if needs_charts flag is set
    if state.get("needs_charts", False):
        return True

    # Check if data is numeric and suitable for charts
    raw_data = state.get("raw_data", {})
    if isinstance(raw_data, dict) and "values" in raw_data:
        return True

    return False


def extract_chart_data(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Extract chart data from raw data.

    Args:
        data: Raw data dictionary

    Returns:
        Chart data dictionary or None
    """
    # Try to extract interest over time data (Google Trends)
    if "interest_over_time" in data and data["interest_over_time"]:
        timeline_data = data["interest_over_time"]
        if isinstance(timeline_data, list) and len(timeline_data) > 0:
            # Extract dates and values
            dates = []
            values = []
            for point in timeline_data:
                if isinstance(point, dict):
                    dates.append(point.get("date", ""))
                    # Extract value (can be in different formats)
                    value = point.get("values", [{}])[0].get("value", 0) if isinstance(
                        point.get("values"), list
                    ) else point.get("value", 0)
                    values.append(value if isinstance(value, (int, float)) else 0)

            if dates and values:
                return {
                    "x": dates,
                    "y": values,
                    "title": f"Interest Over Time: {data.get('topic', 'Trend')}",
                    "xlabel": "Date",
                    "ylabel": "Interest",
                    "chart_type": "line",  # Force line chart for time series
                }

    # Try to extract numeric data
    if "values" in data:
        return {
            "x": data.get("labels", list(range(len(data["values"])))),
            "y": data["values"],
            "title": data.get("title", "Data Visualization"),
            "xlabel": data.get("xlabel", "Category"),
            "ylabel": data.get("ylabel", "Value"),
        }

    # Try to extract from search results count
    if "results" in data and isinstance(data["results"], list):
        # Create simple bar chart from result count
        return {
            "x": ["Results"],
            "y": [len(data["results"])],
            "title": "Search Results Count",
            "xlabel": "Type",
            "ylabel": "Count",
        }

    return None


def create_visualization(state: Dict[str, Any]) -> Optional[str]:
    """
    Create visualization if needed.

    Args:
        state: Graph state

    Returns:
        Base64 encoded image or None
    """
    if not should_create_chart(state):
        return None

    raw_data = state.get("raw_data", {})
    if not raw_data:
        return None

    chart_data = extract_chart_data(raw_data)
    if not chart_data:
        return None

    # Determine chart type
    chart_type = chart_data.get("chart_type", "bar")  # Use specified type if available
    if not chart_type or chart_type == "bar":
        # Auto-detect based on data
        if len(chart_data.get("x", [])) > 10:
            chart_type = "line"
        elif len(chart_data.get("x", [])) <= 5:
            chart_type = "pie"
        else:
            chart_type = "bar"

    creator = MatplotlibChartCreator()
    return creator.create(chart_data, chart_type)
