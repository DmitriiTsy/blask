"""Competitor Tracker Agent using LangChain (SOLID principles)."""

from typing import Dict, Any, List, Optional

try:
    from langchain_openai import ChatOpenAI
except ImportError:
    # Fallback for older versions
    from langchain.chat_models import ChatOpenAI

from langchain_core.prompts import ChatPromptTemplate

# Simplified agent implementation without AgentExecutor
# We'll use LLM with tools directly

from ..config import get_settings
from ..utils.logging import get_logger
from ..tools.competitor_tracking_tools import (
    identify_igaming_competitors,
    monitor_competitor_keywords,
    calculate_competitor_metrics,
    detect_competitor_changes,
    discover_new_igaming_brands,
)

logger = get_logger(__name__)


class CompetitorTrackerAgent:
    """
    LangChain Agent for tracking competitors in iGaming industry.
    
    Uses tools to identify, monitor, and analyze competitors.
    Follows SOLID principles:
    - Single Responsibility: Only handles competitor tracking
    - Open/Closed: Can be extended with new tools
    - Dependency Inversion: Depends on abstractions (tools)
    """

    def __init__(self, llm: Optional[ChatOpenAI] = None):
        """
        Initialize Competitor Tracker Agent.

        Args:
            llm: Optional LLM instance (creates default if not provided)
        """
        settings = get_settings()

        if llm is None:
            if not settings.openai_api_key:
                raise ValueError("OPENAI_API_KEY is required for CompetitorTrackerAgent")
            self.llm = ChatOpenAI(
                model=settings.default_model,
                temperature=0,  # Low temperature for consistent tracking
                api_key=settings.openai_api_key,
            )
        else:
            self.llm = llm

        # Create tools
        self.tools = [
            identify_igaming_competitors,
            monitor_competitor_keywords,
            calculate_competitor_metrics,
            detect_competitor_changes,
            discover_new_igaming_brands,
        ]

        # Store tools for direct use
        self.tools_dict = {tool.name: tool for tool in self.tools}

    def _call_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Any:
        """
        Call a tool by name.
        
        Args:
            tool_name: Name of the tool to call
            tool_input: Input parameters for the tool
        
        Returns:
            Tool output
        """
        if tool_name in self.tools_dict:
            tool = self.tools_dict[tool_name]
            return tool.invoke(tool_input)
        else:
            raise ValueError(f"Tool {tool_name} not found")

    def _execute_agent_workflow(self, input_text: str) -> Dict[str, Any]:
        """
        Execute agent workflow manually (simplified version without AgentExecutor).
        
        Args:
            input_text: User input text
        
        Returns:
            Dictionary with results and intermediate steps
        """
        intermediate_steps = []
        
        # Create prompt for LLM
        system_prompt = """You are an expert competitor tracking agent for the iGaming (online casino) industry.

Your task is to:
1. Identify competitors for online casino brands
2. Monitor their keywords and metrics
3. Track changes in their strategy
4. Discover new competitors in the market

Available tools:
- identify_igaming_competitors(brand_name, country): Find competitors for a brand
- monitor_competitor_keywords(competitor_domain, timeframe): Monitor keywords
- calculate_competitor_metrics(competitor_domain): Calculate BAP, APS, CEB metrics
- detect_competitor_changes(competitor_domain, previous_data, current_data): Detect changes
- discover_new_igaming_brands(country, timeframe): Find new brands

Analyze the user's request and determine which tools to use. Then execute them step by step."""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({"input": input_text})
        
        # Extract tool calls from response (simplified - in real implementation would parse)
        # For now, we'll execute tools based on the input text
        return {
            "output": response.content if hasattr(response, 'content') else str(response),
            "intermediate_steps": intermediate_steps
        }

    def track_competitors(
        self, brand_name: str, country: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Track competitors for a given brand.

        Args:
            brand_name: Name of the brand to track competitors for
            country: Optional country code

        Returns:
            Dictionary with competitor tracking results including intermediate steps
        """
        input_text = f"Identify and analyze competitors for {brand_name}"
        if country:
            input_text += f" in {country}"
        input_text += (
            ". Provide detailed analysis including their keywords and metrics. "
            "Show intermediate results for each step: which competitors were found, "
            "what keywords they use, and what metrics they have."
        )

        try:
            # Execute workflow
            result = self._execute_agent_workflow(input_text)
            
            # Also execute tools directly to get intermediate results
            intermediate_steps = []
            
            # Step 1: Identify competitors
            competitors_result = self._call_tool(
                "identify_igaming_competitors",
                {"brand_name": brand_name, "country": country}
            )
            intermediate_steps.append({
                "tool": "identify_igaming_competitors",
                "input": {"brand_name": brand_name, "country": country},
                "output": competitors_result
            })
            
            # Step 2: Monitor keywords and calculate metrics for each competitor
            competitors = competitors_result.get("competitors", [])[:5]  # Top 5
            for competitor in competitors:
                domain = competitor.get("domain", "")
                if domain:
                    # Monitor keywords
                    keywords_result = self._call_tool(
                        "monitor_competitor_keywords",
                        {"competitor_domain": domain, "timeframe": "30d"}
                    )
                    intermediate_steps.append({
                        "tool": "monitor_competitor_keywords",
                        "input": {"competitor_domain": domain},
                        "output": keywords_result
                    })
                    
                    # Calculate metrics
                    metrics_result = self._call_tool(
                        "calculate_competitor_metrics",
                        {"competitor_domain": domain}
                    )
                    intermediate_steps.append({
                        "tool": "calculate_competitor_metrics",
                        "input": {"competitor_domain": domain},
                        "output": metrics_result
                    })
            
            logger.info(f"Competitor tracking completed for {brand_name}")

            return {
                "output": result.get("output", ""),
                "intermediate_steps": intermediate_steps,
                "brand": brand_name,
                "country": country,
            }
        except Exception as e:
            logger.error(f"Error in competitor tracking: {e}")
            return {
                "error": str(e),
                "brand": brand_name,
                "intermediate_steps": [],
            }

    def monitor_competitor(
        self,
        competitor_domain: str,
        previous_data: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Monitor a specific competitor.

        Args:
            competitor_domain: Domain of the competitor
            previous_data: Optional previous monitoring data for comparison

        Returns:
            Dictionary with monitoring results including intermediate steps
        """
        input_text = f"Monitor competitor {competitor_domain}"

        if previous_data:
            input_text += (
                f" and compare with previous data. Detect any changes. "
                f"Show what keywords were monitored and what metrics were calculated."
            )
        else:
            input_text += (
                ". Analyze their keywords and calculate metrics. "
                "Show intermediate results: keywords found and metrics calculated."
            )

        try:
            intermediate_steps = []
            
            # Monitor keywords
            keywords_result = self._call_tool(
                "monitor_competitor_keywords",
                {"competitor_domain": competitor_domain, "timeframe": "30d"}
            )
            intermediate_steps.append({
                "tool": "monitor_competitor_keywords",
                "input": {"competitor_domain": competitor_domain},
                "output": keywords_result
            })
            
            # Calculate metrics
            metrics_result = self._call_tool(
                "calculate_competitor_metrics",
                {"competitor_domain": competitor_domain}
            )
            intermediate_steps.append({
                "tool": "calculate_competitor_metrics",
                "input": {"competitor_domain": competitor_domain},
                "output": metrics_result
            })
            
            # Compare with previous data if available
            if previous_data:
                changes_result = self._call_tool(
                    "detect_competitor_changes",
                    {
                        "competitor_domain": competitor_domain,
                        "previous_data": previous_data,
                        "current_data": {
                            "keywords": keywords_result.get("keywords", []),
                            "metrics": metrics_result
                        }
                    }
                )
                intermediate_steps.append({
                    "tool": "detect_competitor_changes",
                    "input": {"competitor_domain": competitor_domain},
                    "output": changes_result
                })
            
            logger.info(f"Competitor monitoring completed for {competitor_domain}")

            return {
                "output": f"Monitoring completed for {competitor_domain}",
                "intermediate_steps": intermediate_steps,
                "competitor": competitor_domain,
            }
        except Exception as e:
            logger.error(f"Error in competitor monitoring: {e}")
            return {
                "error": str(e),
                "competitor": competitor_domain,
                "intermediate_steps": [],
            }

    def discover_new_competitors(
        self, country: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Discover new competitors in the market.

        Args:
            country: Optional country code

        Returns:
            Dictionary with newly discovered competitors
        """
        input_text = f"Discover new online casino brands"
        if country:
            input_text += f" in {country}"
        input_text += " and analyze them. Show which brands were discovered."

        try:
            # Discover new brands
            discovery_result = self._call_tool(
                "discover_new_igaming_brands",
                {"country": country, "timeframe": "30d"}
            )
            
            intermediate_steps = [{
                "tool": "discover_new_igaming_brands",
                "input": {"country": country, "timeframe": "30d"},
                "output": discovery_result
            }]
            
            logger.info("New competitor discovery completed")

            return {
                "output": f"Discovered {discovery_result.get('count', 0)} new brands",
                "intermediate_steps": intermediate_steps,
            }
        except Exception as e:
            logger.error(f"Error in competitor discovery: {e}")
            return {
                "error": str(e),
                "intermediate_steps": [],
            }

