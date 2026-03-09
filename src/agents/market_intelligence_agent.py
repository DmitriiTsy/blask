"""Market Intelligence Agent using LangChain (SOLID principles)."""

from typing import Dict, Any, List, Optional

try:
    from langchain_openai import ChatOpenAI
except ImportError:
    from langchain.chat_models import ChatOpenAI

from langchain_core.prompts import ChatPromptTemplate

from ..config import get_settings
from ..utils.logging import get_logger
from ..tools.market_intelligence_tools import (
    analyze_market_size,
    find_white_label_platforms,
    identify_growth_opportunities,
    analyze_regional_market,
)

logger = get_logger(__name__)


class MarketIntelligenceAgent:
    """
    LangChain Agent for market intelligence in iGaming industry.
    
    Uses tools to analyze markets, find platforms, and identify opportunities.
    Follows SOLID principles:
    - Single Responsibility: Only handles market intelligence
    - Open/Closed: Can be extended with new tools
    - Dependency Inversion: Depends on abstractions (tools)
    """

    def __init__(self, llm: Optional[ChatOpenAI] = None):
        """
        Initialize Market Intelligence Agent.

        Args:
            llm: Optional LLM instance (creates default if not provided)
        """
        settings = get_settings()

        if llm is None:
            if not settings.openai_api_key:
                raise ValueError("OPENAI_API_KEY is required for MarketIntelligenceAgent")
            self.llm = ChatOpenAI(
                model=settings.default_model,
                temperature=0,  # Low temperature for consistent analysis
                api_key=settings.openai_api_key,
            )
        else:
            self.llm = llm

        # Create tools
        self.tools = [
            analyze_market_size,
            find_white_label_platforms,
            identify_growth_opportunities,
            analyze_regional_market,
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

    def analyze_country_market(
        self,
        country: str,
        include_platforms: bool = True,
        include_opportunities: bool = True,
        include_regional: bool = False,
    ) -> Dict[str, Any]:
        """
        Analyze market for a specific country.
        
        Args:
            country: Country name or code
            include_platforms: Whether to find white label platforms
            include_opportunities: Whether to identify opportunities
            include_regional: Whether to include regional analysis
        
        Returns:
            Dictionary with market analysis results including intermediate steps
        """
        intermediate_steps = []
        
        try:
            # Step 1: Analyze market size
            logger.info(f"Analyzing market size for {country}")
            market_size_result = self._call_tool(
                "analyze_market_size",
                {"country": country, "industry": "white label iGaming casino platform"}
            )
            intermediate_steps.append({
                "tool": "analyze_market_size",
                "input": {"country": country},
                "output": market_size_result
            })
            
            # Step 2: Find white label platforms
            platforms_result = None
            if include_platforms:
                logger.info(f"Finding white label platforms for {country}")
                platforms_result = self._call_tool(
                    "find_white_label_platforms",
                    {"country": country, "industry": "white label iGaming casino platform"}
                )
                intermediate_steps.append({
                    "tool": "find_white_label_platforms",
                    "input": {"country": country},
                    "output": platforms_result
                })
            
            # Step 3: Identify growth opportunities
            opportunities_result = None
            if include_opportunities:
                logger.info(f"Identifying growth opportunities for {country}")
                opportunities_result = self._call_tool(
                    "identify_growth_opportunities",
                    {"country": country, "market_data": market_size_result}
                )
                intermediate_steps.append({
                    "tool": "identify_growth_opportunities",
                    "input": {"country": country},
                    "output": opportunities_result
                })
            
            # Step 4: Regional analysis (optional)
            regional_result = None
            if include_regional:
                logger.info(f"Analyzing regional market for {country}")
                regional_result = self._call_tool(
                    "analyze_regional_market",
                    {"country": country, "include_neighbors": True}
                )
                intermediate_steps.append({
                    "tool": "analyze_regional_market",
                    "input": {"country": country},
                    "output": regional_result
                })
            
            # Compile results
            result = {
                "country": country,
                "market_size": market_size_result,
                "platforms": platforms_result,
                "opportunities": opportunities_result,
                "regional": regional_result,
                "intermediate_steps": intermediate_steps,
            }
            
            logger.info(f"Market analysis completed for {country}")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing market for {country}: {e}")
            return {
                "country": country,
                "error": str(e),
                "intermediate_steps": intermediate_steps,
            }

    def analyze_multiple_countries(
        self,
        countries: List[str],
        include_platforms: bool = True,
        include_opportunities: bool = True,
    ) -> Dict[str, Any]:
        """
        Analyze markets for multiple countries sequentially.
        
        Args:
            countries: List of country names or codes
            include_platforms: Whether to find white label platforms
            include_opportunities: Whether to identify opportunities
        
        Returns:
            Dictionary with analysis results for all countries
        """
        all_results = {}
        all_intermediate_steps = []
        
        for country in countries:
            logger.info(f"Analyzing market for {country} ({countries.index(country) + 1}/{len(countries)})")
            
            country_result = self.analyze_country_market(
                country,
                include_platforms=include_platforms,
                include_opportunities=include_opportunities,
            )
            
            all_results[country] = country_result
            all_intermediate_steps.extend(country_result.get("intermediate_steps", []))
        
        # Generate comparison summary
        comparison_summary = self._generate_comparison_summary(all_results)
        
        return {
            "countries_analyzed": countries,
            "results": all_results,
            "comparison_summary": comparison_summary,
            "total_intermediate_steps": all_intermediate_steps,
        }

    def _generate_comparison_summary(self, results: Dict[str, Dict]) -> Dict[str, Any]:
        """
        Generate comparison summary for multiple countries.
        
        Args:
            results: Dictionary with country analysis results
        
        Returns:
            Comparison summary
        """
        summary = {
            "total_countries": len(results),
            "market_sizes": {},
            "total_platforms": 0,
            "total_opportunities": 0,
        }
        
        for country, result in results.items():
            market_size_data = result.get("market_size", {})
            if market_size_data:
                summary["market_sizes"][country] = market_size_data.get("market_size", "unknown")
            
            platforms_data = result.get("platforms", {})
            if platforms_data:
                summary["total_platforms"] += platforms_data.get("count", 0)
            
            opportunities_data = result.get("opportunities", {})
            if opportunities_data:
                summary["total_opportunities"] += opportunities_data.get("opportunity_count", 0)
        
        return summary
