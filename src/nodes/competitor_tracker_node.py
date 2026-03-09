"""Competitor Tracker Node using LangChain Agent (SOLID principles)."""

from typing import Dict, Any
from ..graph.state import GraphState
from ..agents.competitor_tracker_agent import CompetitorTrackerAgent
from ..utils.errors import handle_node_error
from ..utils.logging import get_logger

logger = get_logger(__name__)


def competitor_tracker_node(state: GraphState) -> GraphState:
    """
    Node that uses Competitor Tracker Agent to track competitors.
    
    Follows SOLID principles:
    - Single Responsibility: Only handles competitor tracking
    - Dependency Inversion: Depends on agent abstraction
    
    Args:
        state: Current graph state
    
    Returns:
        Updated state with competitor tracking results
    """
    try:
        logger.info("Starting competitor tracker node")

        # Get brand name from state
        brand_name = state.get("brand_name") or state.get("search_query")

        if not brand_name:
            raise ValueError("brand_name or search_query is required")

        # Get country if available
        country = state.get("country")

        # Create agent
        agent = CompetitorTrackerAgent()

        # Track competitors
        result = agent.track_competitors(brand_name, country)

        # Update state with results
        if "error" in result:
            state["error"] = result["error"]
        else:
            # Store main result
            state["tracked_competitors"] = result.get("output", {})
            
            # Extract and store intermediate steps
            intermediate_steps = result.get("intermediate_steps", [])
            state["agent_intermediate_steps"] = intermediate_steps
            
            # Extract competitors list from intermediate steps
            competitors_list = []
            competitor_keywords = {}
            competitor_metrics = {}
            
            for step in intermediate_steps:
                tool_name = step.get("tool", "")
                tool_output = step.get("output", {})
                
                if tool_name == "identify_igaming_competitors":
                    # Extract competitors
                    competitors = tool_output.get("competitors", [])
                    competitors_list = competitors
                    state["competitors_list"] = competitors
                
                elif tool_name == "monitor_competitor_keywords":
                    # Extract keywords
                    competitor = tool_output.get("competitor", "")
                    keywords = tool_output.get("keywords", [])
                    if competitor:
                        competitor_keywords[competitor] = keywords
                
                elif tool_name == "calculate_competitor_metrics":
                    # Extract metrics
                    competitor = tool_output.get("competitor", "")
                    metrics = {
                        "bap": tool_output.get("bap"),
                        "aps": tool_output.get("aps"),
                        "ceb": tool_output.get("ceb"),
                        "avg_interest": tool_output.get("avg_interest"),
                        "growth_rate": tool_output.get("growth_rate"),
                    }
                    if competitor:
                        competitor_metrics[competitor] = metrics
            
            # Update state with extracted data
            state["competitor_keywords"] = competitor_keywords
            state["competitor_metrics"] = competitor_metrics

        state["execution_path"].append("competitor_tracker_node")

        logger.info(f"Competitor tracking completed for {brand_name}")

        return state

    except Exception as e:
        logger.error(f"Error in competitor tracker node: {e}")
        return handle_node_error(state, e, "competitor_tracker_node")
