"""Jurisdiction Agent for legal and regulatory analysis (SOLID principles)."""

from typing import Dict, Any, Optional

try:
    from langchain_openai import ChatOpenAI
except ImportError:
    from langchain.chat_models import ChatOpenAI

from langchain_core.prompts import ChatPromptTemplate

from ..config import get_settings
from ..utils.logging import get_logger
from ..tools.jurisdiction_tools import (
    analyze_igaming_regulations,
    analyze_white_label_compliance,
    identify_legal_risks_and_opportunities,
)

logger = get_logger(__name__)


class JurisdictionAgent:
    """
    LangChain Agent for jurisdiction and legal analysis in iGaming industry.
    
    Analyzes legal framework, regulations, and compliance requirements
    specifically for white label iGaming solutions like Maincard.io.
    
    Follows SOLID principles:
    - Single Responsibility: Only handles legal/jurisdiction analysis
    - Open/Closed: Can be extended with new tools
    - Dependency Inversion: Depends on abstractions (tools)
    """

    def __init__(self, llm: Optional[ChatOpenAI] = None):
        """
        Initialize Jurisdiction Agent.

        Args:
            llm: Optional LLM instance (creates default if not provided)
        """
        settings = get_settings()

        if llm is None:
            if not settings.openai_api_key:
                raise ValueError("OPENAI_API_KEY is required for JurisdictionAgent")
            self.llm = ChatOpenAI(
                model=settings.default_model,
                temperature=0,  # Low temperature for consistent legal analysis
                api_key=settings.openai_api_key,
            )
        else:
            self.llm = llm

        # Create tools
        self.tools = [
            analyze_igaming_regulations,
            analyze_white_label_compliance,
            identify_legal_risks_and_opportunities,
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

    def analyze_jurisdiction(
        self,
        country: str,
        include_compliance: bool = True,
        include_risks_opportunities: bool = True,
    ) -> Dict[str, Any]:
        """
        Analyze jurisdiction and legal framework for a country.
        
        Args:
            country: Country name or code
            include_compliance: Whether to analyze white label compliance
            include_risks_opportunities: Whether to identify risks and opportunities
        
        Returns:
            Dictionary with jurisdiction analysis results including intermediate steps
        """
        intermediate_steps = []

        try:
            # Step 1: Analyze iGaming regulations
            logger.info(f"Analyzing iGaming regulations for {country}")
            regulations_result = self._call_tool(
                "analyze_igaming_regulations",
                {"country": country, "industry": "iGaming online casino white label"}
            )
            intermediate_steps.append({
                "tool": "analyze_igaming_regulations",
                "input": {"country": country},
                "output": regulations_result
            })

            # Step 2: Analyze white label compliance
            compliance_result = None
            if include_compliance:
                logger.info(f"Analyzing white label compliance for {country}")
                compliance_result = self._call_tool(
                    "analyze_white_label_compliance",
                    {"country": country, "platform_type": "white label iGaming casino platform"}
                )
                intermediate_steps.append({
                    "tool": "analyze_white_label_compliance",
                    "input": {"country": country},
                    "output": compliance_result
                })

            # Step 3: Identify risks and opportunities
            risks_opportunities_result = None
            if include_risks_opportunities:
                logger.info(f"Identifying legal risks and opportunities for {country}")
                risks_opportunities_result = self._call_tool(
                    "identify_legal_risks_and_opportunities",
                    {
                        "country": country,
                        "regulations_data": regulations_result,
                        "compliance_data": compliance_result,
                    }
                )
                intermediate_steps.append({
                    "tool": "identify_legal_risks_and_opportunities",
                    "input": {"country": country},
                    "output": risks_opportunities_result
                })

            # Compile results
            result = {
                "country": country,
                "regulations": regulations_result,
                "compliance": compliance_result,
                "risks_and_opportunities": risks_opportunities_result,
                "intermediate_steps": intermediate_steps,
            }

            logger.info(f"Jurisdiction analysis completed for {country}")
            return result

        except Exception as e:
            logger.error(f"Error analyzing jurisdiction for {country}: {e}")
            return {
                "country": country,
                "error": str(e),
                "intermediate_steps": intermediate_steps,
            }
