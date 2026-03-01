"""Interfaces for nodes (SOLID - Interface Segregation Principle)."""

from abc import ABC, abstractmethod
from typing import Protocol

from ..graph.state import GraphState


class NodeProcessor(Protocol):
    """
    Protocol for node processors.

    All nodes should follow this protocol for consistency.
    """

    def __call__(self, state: GraphState) -> GraphState:
        """
        Process state and return updated state.

        Args:
            state: Current graph state

        Returns:
            Updated graph state
        """
        ...


class DecisionMaker(ABC):
    """
    Interface for decision-making components (SOLID - ISP).

    Separates decision logic from node implementation.
    """

    @abstractmethod
    def make_decision(self, query: str, history: list) -> dict:
        """
        Make decision based on query and history.

        Args:
            query: User query
            history: Conversation history

        Returns:
            Dictionary with decision, search_type, search_query, needs_charts
        """
        pass


class DataFormatter(ABC):
    """
    Interface for data formatting (SOLID - ISP).

    Separates formatting logic from analysis node.
    """

    @abstractmethod
    def format_response(self, data: dict, needs_charts: bool) -> str:
        """
        Format data into user-friendly response.

        Args:
            data: Raw data to format
            needs_charts: Whether charts were created

        Returns:
            Formatted response string
        """
        pass
