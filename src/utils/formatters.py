"""Data formatting utilities (SOLID - Single Responsibility)."""

from typing import Any, Dict, List

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from ..config import get_settings
from ..utils.logging import get_logger

logger = get_logger(__name__)


class ResponseFormatter:
    """
    Formats data into user-friendly responses (SOLID - Single Responsibility).

    Handles formatting logic separately from analysis node.
    """

    def __init__(self, llm: Any | None = None):
        """
        Initialize formatter.

        Args:
            llm: LangChain LLM instance (optional)
        """
        self.llm = llm or self._create_llm()
        self.prompt = self._create_prompt()

    def _create_llm(self) -> Any:
        """Create LLM instance."""
        settings = get_settings()

        if settings.openai_api_key:
            return ChatOpenAI(
                model=settings.default_model,
                temperature=settings.default_temperature,
                api_key=settings.openai_api_key,
            )

        logger.warning("No API key found, using mock formatter")
        return None

    def _create_prompt(self) -> ChatPromptTemplate:
        """Create formatting prompt."""
        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are a helpful assistant that formats data into clear, 
user-friendly responses. Format the provided data in a structured, readable way.
If charts were created, mention them in the response.

IMPORTANT:
- Only mention specific years if they are in the original user query
- Do NOT invent or assume years (like 2023, 2024) if not in the query
- Focus on the actual data provided, not assumptions
- If no data is available, say so clearly without mentioning specific years""",
                ),
                (
                    "human",
                    """Original query: {query}
Data: {data}
Has charts: {has_charts}

Knowledge Base Context:
{kb_context}

Format this into a clear response for the user. Use the knowledge base context if it's relevant to the query.""",
                ),
            ]
        )

    def format(self, query: str, data: Dict[str, Any], has_charts: bool, kb_context: str = "") -> str:
        """
        Format data into response.

        Args:
            query: Original user query
            data: Data to format
            has_charts: Whether charts were created
            kb_context: Optional knowledge base context

        Returns:
            Formatted response string
        """
        if self.llm is None:
            # Mock formatting
            return self._format_simple(query, data, has_charts)

        try:
            chain = self.prompt | self.llm
            data_str = self._data_to_string(data)
            result = chain.invoke(
                {
                    "query": query,
                    "data": data_str,
                    "has_charts": "Yes" if has_charts else "No",
                    "kb_context": kb_context if kb_context else "No relevant context found in knowledge base.",
                }
            )

            return result.content if hasattr(result, "content") else str(result)

        except Exception as e:
            logger.error(f"Error in LLM formatting: {e}")
            return self._format_simple(query, data, has_charts)

    def _format_simple(self, query: str, data: Dict[str, Any], has_charts: bool) -> str:
        """Simple formatting without LLM."""
        response_parts = [f"Query: {query}\n\n"]

        if "search_results" in data:
            results = data.get("search_results", [])
            response_parts.append(f"Found {len(results)} results:\n\n")
            for i, result in enumerate(results[:5], 1):
                title = result.get("title", "No title")
                snippet = result.get("snippet", "No description")
                response_parts.append(f"{i}. {title}\n   {snippet}\n")

        if has_charts:
            response_parts.append("\n[Charts have been created]")

        return "\n".join(response_parts)

    def _data_to_string(self, data: Dict[str, Any]) -> str:
        """Convert data dictionary to string representation."""
        import json

        try:
            return json.dumps(data, indent=2, ensure_ascii=False)
        except Exception:
            return str(data)


def format_search_results(results: List[Dict[str, Any]], limit: int = 10) -> str:
    """
    Format search results into readable string.

    Args:
        results: List of search results
        limit: Maximum number of results to format

    Returns:
        Formatted string
    """
    if not results:
        return "No results found."

    formatted = []
    for i, result in enumerate(results[:limit], 1):
        title = result.get("title", "No title")
        snippet = result.get("snippet", "No description")
        link = result.get("link", "")
        formatted.append(f"{i}. {title}\n   {snippet}\n   {link}\n")

    return "\n".join(formatted)
