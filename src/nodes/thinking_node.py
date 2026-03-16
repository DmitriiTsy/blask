"""Thinking node - analyzes query and makes decisions (SOLID principles)."""

from typing import Any, Dict

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from ..config import get_settings
from ..graph.state import GraphState
from ..nodes.interfaces import DecisionMaker
from ..utils.errors import GraphError, handle_node_error
from ..utils.logging import get_logger
from ..tools.knowledge_base_tools import get_knowledge_base_context

logger = get_logger(__name__)


class LLMDecisionMaker(DecisionMaker):
    """
    LLM-based decision maker (SOLID - Single Responsibility).

    Handles decision logic separately from node implementation.
    """

    def __init__(self, llm: Any | None = None):
        """
        Initialize decision maker.

        Args:
            llm: LangChain LLM instance (optional, will create if not provided)
        """
        self.llm = llm or self._create_llm()
        self.parser = JsonOutputParser()
        self.prompt = self._create_prompt()

    def _create_llm(self) -> Any:
        """Create LLM instance based on settings."""
        settings = get_settings()

        if settings.openai_api_key:
            return ChatOpenAI(
                model=settings.default_model,
                temperature=settings.default_temperature,
                api_key=settings.openai_api_key,
            )

        # Fallback to mock for testing
        logger.warning("No API key found, using mock LLM")
        return None

    def _create_prompt(self) -> ChatPromptTemplate:
        """Create prompt template for decision making."""
        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are an expert query analyzer. Your task:
1. Determine query type: "search", "direct_answer", or "statistics"
2. If search needed, determine type: "keywords", "competitors", or "trends"
3. Create optimized search query - DO NOT add years or dates unless user explicitly mentions them
4. Determine if charts are needed (for statistics)

IMPORTANT: 
- Do NOT add years (like 2023, 2024) to search_query unless user explicitly asks for them
- For trends queries, use current/recent trends, not specific past years
- Keep search_query clean and focused on the topic
- If knowledge base context is provided, use it to inform your decision

Respond in JSON format:
{{
    "decision": "search|direct_answer|statistics",
    "search_type": "keywords|competitors|trends|null",
    "search_query": "optimized query or null",
    "needs_charts": true/false,
    "reasoning": "explanation"
}}""",
                ),
                ("human", "User query: {query}\nHistory: {history}\n\nKnowledge Base Context:\n{kb_context}"),
            ]
        )

    def make_decision(self, query: str, history: list) -> Dict[str, Any]:
        """
        Make decision based on query and history.

        Args:
            query: User query
            history: Conversation history

        Returns:
            Dictionary with decision data
        """
        # Get relevant context from knowledge base (RAG)
        kb_context = ""
        try:
            kb_context = get_knowledge_base_context(query, max_chunks=3)
            if kb_context:
                logger.info(f"Retrieved {len(kb_context)} chars of context from knowledge base")
        except Exception as e:
            logger.warning(f"Could not retrieve knowledge base context: {e}")

        if self.llm is None:
            # Mock decision for testing
            return {
                "decision": "search",
                "search_type": "keywords",
                "search_query": query,
                "needs_charts": False,
                "reasoning": "Mock decision",
                "kb_context": kb_context,  # Include KB context even in mock
            }

        try:
            formatted = self.prompt.format_messages(
                query=query,
                history=str(history) if history else "None",
                kb_context=kb_context if kb_context else "No relevant context found in knowledge base."
            )
            response = self.llm.invoke(formatted)
            result = self.parser.parse(response.content)
            
            # Add KB context to result for use in other nodes
            result["kb_context"] = kb_context

            # Validate result structure
            required_keys = ["decision", "search_type", "search_query", "needs_charts"]
            for key in required_keys:
                if key not in result:
                    raise ValueError(f"Missing required key: {key}")

            return result

        except Exception as e:
            logger.error(f"Error in decision making: {e}")
            # Fallback decision
            return {
                "decision": "search",
                "search_type": "keywords",
                "search_query": query,
                "needs_charts": False,
                "reasoning": f"Fallback due to error: {str(e)}",
            }


def thinking_node(state: GraphState) -> GraphState:
    """
    Thinking node - analyzes query and makes routing decisions.

    This node:
    1. Analyzes user query
    2. Determines next steps (search, direct answer, statistics)
    3. Forms optimized search queries
    4. Updates state with decision

    Args:
        state: Current graph state

    Returns:
        Updated state with decision information
    """
    logger.info(f"Thinking node processing query: {state.get('user_query', '')}")

    try:
        # Extract inputs
        user_query = state.get("user_query", "")
        if not user_query:
            raise GraphError("user_query is required", "thinking_node")

        conversation_history = state.get("conversation_history", [])

        # Make decision using decision maker (SOLID - Dependency Inversion)
        decision_maker = LLMDecisionMaker()
        decision = decision_maker.make_decision(user_query, conversation_history)

        # Update state with decision
        updated_state: GraphState = {
            **state,
            "decision": decision.get("decision", "search"),
            "search_type": decision.get("search_type"),
            "search_query": decision.get("search_query"),
            "needs_charts": decision.get("needs_charts", False),
            "reasoning": decision.get("reasoning"),
            "execution_path": state.get("execution_path", []) + ["thinking_node"],
        }

        logger.info(
            f"Decision made: {updated_state['decision']}, "
            f"search_type: {updated_state['search_type']}"
        )

        return updated_state

    except Exception as e:
        logger.error(f"Error in thinking node: {e}")
        return handle_node_error(state, e, "thinking_node")
