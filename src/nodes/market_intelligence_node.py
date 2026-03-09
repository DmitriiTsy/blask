"""Market Intelligence Node using LangChain Agent (SOLID principles)."""

from typing import Dict, Any
from ..graph.state import GraphState
from ..agents.market_intelligence_agent import MarketIntelligenceAgent
from ..utils.errors import handle_node_error
from ..utils.logging import get_logger

logger = get_logger(__name__)


def market_intelligence_node(state: GraphState) -> GraphState:
    """
    Node that uses Market Intelligence Agent to analyze markets.
    
    Follows SOLID principles:
    - Single Responsibility: Only handles market intelligence
    - Dependency Inversion: Depends on agent abstraction
    
    Args:
        state: Current graph state
    
    Returns:
        Updated state with market analysis results
    """
    try:
        logger.info("Starting market intelligence node")

        # Get countries from state
        countries = state.get("countries_to_analyze", [])
        
        # If no countries in state, try to extract from user_query
        if not countries:
            user_query = state.get("user_query", "")
            # Simple extraction - can be improved with LLM
            # For now, expect comma-separated list
            if "," in user_query:
                countries = [c.strip() for c in user_query.split(",")]
            else:
                countries = [user_query.strip()]

        if not countries:
            raise ValueError("countries_to_analyze is required")

        # Create agent
        agent = MarketIntelligenceAgent()

        # Analyze countries sequentially
        result = agent.analyze_multiple_countries(
            countries,
            include_platforms=True,
            include_opportunities=True,
        )

        # Update state with results
        if "error" in result:
            state["error"] = result["error"]
        else:
            # Store results by country
            state["market_analysis_results"] = result.get("results", {})
            state["market_comparison_summary"] = result.get("comparison_summary", {})
            state["market_intermediate_steps"] = result.get("total_intermediate_steps", [])
            state["countries_to_analyze"] = countries

        state["execution_path"].append("market_intelligence_node")

        logger.info(f"Market intelligence analysis completed for {len(countries)} countries")

        return state

    except Exception as e:
        logger.error(f"Error in market intelligence node: {e}")
        return handle_node_error(state, e, "market_intelligence_node")
