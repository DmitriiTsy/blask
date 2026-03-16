"""Tools for jurisdiction and legal analysis in iGaming industry (SOLID principles)."""

from typing import Any, Dict, List, Optional
from langchain.tools import tool

from ..utils.logging import get_logger

logger = get_logger(__name__)


@tool
def analyze_igaming_regulations(
    country: str,
    industry: str = "iGaming online casino white label",
) -> Dict[str, Any]:
    """
    Analyze iGaming regulations and legal framework in a specific country.
    
    Searches for:
    - Gambling laws and regulations
    - Licensing requirements
    - Legal status of online casinos
    - Regulatory bodies
    - Compliance requirements
    
    Args:
        country: Country name or code (e.g., "Spain", "UK", "US")
        industry: Industry type (default: "iGaming online casino white label")
    
    Returns:
        Dictionary with regulatory analysis:
        {
            "country": str,
            "legal_status": str,  # "legal", "illegal", "regulated", "restricted"
            "licensing_required": bool,
            "regulatory_body": str,
            "key_regulations": List[str],
            "compliance_requirements": List[str],
            "risks": List[Dict],
            "opportunities": List[Dict]
        }
    """
    from ..config import get_settings
    from ..tools.search_tools import SerpAPISearchTool, MockSearchTool

    settings = get_settings()

    if settings.serpapi_key:
        search_tool = SerpAPISearchTool(settings.serpapi_key)
    else:
        logger.warning("SerpAPI key not available, using mock search")
        search_tool = MockSearchTool()

    # Search for regulatory information
    queries = [
        f"{country} online casino legal status",
        f"{country} iGaming gambling laws",
        f"{country} casino license requirements",
        f"{country} gambling regulations",
        f"{country} online gambling legal",
        f"{country} white label casino legal",
    ]

    all_results = []
    for query in queries:
        try:
            results = search_tool.search(query)
            all_results.extend(results)
        except Exception as e:
            logger.error(f"Error searching for regulations with query '{query}': {e}")
            continue

    # Analyze results to determine legal status
    legal_keywords = {
        "legal": ["legal", "licensed", "regulated", "permitted", "allowed", "authorized"],
        "illegal": ["illegal", "banned", "prohibited", "forbidden", "not allowed"],
        "regulated": ["regulated", "license required", "must have license", "regulated market"],
        "restricted": ["restricted", "limited", "conditional", "with restrictions"],
    }

    legal_status = "unknown"
    licensing_required = False
    regulatory_body = ""
    key_regulations = []
    compliance_requirements = []
    risks = []
    opportunities = []

    for result in all_results:
        snippet = result.get("snippet", "").lower()
        title = result.get("title", "").lower()
        text = f"{title} {snippet}"

        # Determine legal status
        for status, keywords in legal_keywords.items():
            if any(keyword in text for keyword in keywords):
                if legal_status == "unknown" or status in ["legal", "regulated"]:
                    legal_status = status
                break

        # Check for licensing requirements
        if any(kw in text for kw in ["license", "licensing", "permit", "authorization"]):
            licensing_required = True

        # Extract regulatory body
        regulatory_keywords = ["gaming commission", "gambling authority", "regulatory body", "gaming board"]
        for keyword in regulatory_keywords:
            if keyword in text:
                # Try to extract the name
                import re
                pattern = rf"({keyword}[^\s,\.]+)"
                match = re.search(pattern, text, re.IGNORECASE)
                if match and not regulatory_body:
                    regulatory_body = match.group(1).title()

        # Extract key regulations
        if any(kw in text for kw in ["regulation", "law", "act", "decree"]):
            key_regulations.append({
                "title": result.get("title", ""),
                "description": result.get("snippet", "")[:200],
                "source": result.get("link", ""),
            })

        # Identify risks
        risk_keywords = ["ban", "prohibit", "restrict", "penalty", "fine", "illegal", "criminal"]
        if any(kw in text for kw in risk_keywords):
            risks.append({
                "title": result.get("title", ""),
                "description": result.get("snippet", "")[:200],
                "type": "regulatory_risk",
                "source": result.get("link", ""),
            })

        # Identify opportunities
        opportunity_keywords = ["legal", "licensed", "regulated market", "opportunity", "growing market"]
        if any(kw in text for kw in opportunity_keywords) and legal_status in ["legal", "regulated"]:
            opportunities.append({
                "title": result.get("title", ""),
                "description": result.get("snippet", "")[:200],
                "type": "regulatory_opportunity",
                "source": result.get("link", ""),
            })

    # Extract compliance requirements
    compliance_keywords = ["KYC", "AML", "responsible gambling", "player protection", "data protection", "GDPR"]
    for result in all_results:
        snippet = result.get("snippet", "").lower()
        for keyword in compliance_keywords:
            if keyword.lower() in snippet:
                compliance_requirements.append(keyword.upper())

    logger.info(
        f"Analyzed regulations for {country}: {legal_status}, "
        f"licensing_required={licensing_required}, {len(risks)} risks, {len(opportunities)} opportunities"
    )

    return {
        "country": country,
        "industry": industry,
        "legal_status": legal_status,
        "licensing_required": licensing_required,
        "regulatory_body": regulatory_body,
        "key_regulations": key_regulations[:10],  # Top 10
        "compliance_requirements": list(set(compliance_requirements)),
        "risks": risks[:10],  # Top 10
        "opportunities": opportunities[:10],  # Top 10
        "data_sources": len(all_results),
    }


@tool
def analyze_white_label_compliance(
    country: str,
    platform_type: str = "white label iGaming casino platform",
) -> Dict[str, Any]:
    """
    Analyze compliance requirements specifically for white label iGaming platforms.
    
    Focuses on Maincard.io type solutions - white label casino platforms.
    
    Args:
        country: Country name or code
        platform_type: Type of platform (default: "white label iGaming casino platform")
    
    Returns:
        Dictionary with compliance analysis:
        {
            "country": str,
            "white_label_allowed": bool,
            "license_requirements": List[str],
            "operator_requirements": List[str],
            "technical_requirements": List[str],
            "compliance_risks": List[Dict],
            "compliance_opportunities": List[Dict]
        }
    """
    from ..config import get_settings
    from ..tools.search_tools import SerpAPISearchTool, MockSearchTool

    settings = get_settings()

    if settings.serpapi_key:
        search_tool = SerpAPISearchTool(settings.serpapi_key)
    else:
        logger.warning("SerpAPI key not available, using mock search")
        search_tool = MockSearchTool()

    # Search for white label specific information
    queries = [
        f"{country} white label casino legal",
        f"{country} white label gambling license",
        f"{country} turnkey casino solution legal",
        f"{country} casino platform provider regulations",
        f"{country} iGaming software provider license",
    ]

    all_results = []
    for query in queries:
        try:
            results = search_tool.search(query)
            all_results.extend(results)
        except Exception as e:
            logger.error(f"Error searching for white label compliance with query '{query}': {e}")
            continue

    white_label_allowed = False
    license_requirements = []
    operator_requirements = []
    technical_requirements = []
    compliance_risks = []
    compliance_opportunities = []

    for result in all_results:
        snippet = result.get("snippet", "").lower()
        title = result.get("title", "").lower()
        text = f"{title} {snippet}"

        # Check if white label is allowed
        if any(kw in text for kw in ["white label allowed", "white label legal", "white label permitted"]):
            white_label_allowed = True

        # Extract license requirements
        if "license" in text or "licensing" in text:
            license_requirements.append({
                "description": result.get("snippet", "")[:200],
                "source": result.get("link", ""),
            })

        # Extract operator requirements
        operator_keywords = ["operator", "license holder", "entity", "company registration"]
        if any(kw in text for kw in operator_keywords):
            operator_requirements.append({
                "description": result.get("snippet", "")[:200],
                "source": result.get("link", ""),
            })

        # Extract technical requirements
        technical_keywords = ["server location", "data storage", "geolocation", "payment processing"]
        if any(kw in text for kw in technical_keywords):
            technical_requirements.append({
                "description": result.get("snippet", "")[:200],
                "source": result.get("link", ""),
            })

        # Identify compliance risks
        risk_keywords = ["not allowed", "prohibited", "restricted", "requires license", "must be licensed"]
        if any(kw in text for kw in risk_keywords) and not white_label_allowed:
            compliance_risks.append({
                "title": result.get("title", ""),
                "description": result.get("snippet", "")[:200],
                "type": "compliance_risk",
                "severity": "high" if "prohibited" in text or "illegal" in text else "medium",
                "source": result.get("link", ""),
            })

        # Identify compliance opportunities
        if white_label_allowed or ("legal" in text and "white label" in text):
            compliance_opportunities.append({
                "title": result.get("title", ""),
                "description": result.get("snippet", "")[:200],
                "type": "compliance_opportunity",
                "source": result.get("link", ""),
            })

    logger.info(
        f"Analyzed white label compliance for {country}: "
        f"allowed={white_label_allowed}, {len(compliance_risks)} risks, {len(compliance_opportunities)} opportunities"
    )

    return {
        "country": country,
        "platform_type": platform_type,
        "white_label_allowed": white_label_allowed,
        "license_requirements": license_requirements[:5],
        "operator_requirements": operator_requirements[:5],
        "technical_requirements": technical_requirements[:5],
        "compliance_risks": compliance_risks[:10],
        "compliance_opportunities": compliance_opportunities[:10],
        "data_sources": len(all_results),
    }


@tool
def identify_legal_risks_and_opportunities(
    country: str,
    regulations_data: Optional[Dict] = None,
    compliance_data: Optional[Dict] = None,
) -> Dict[str, Any]:
    """
    Identify specific legal risks and opportunities for Maincard.io type white label solution.
    
    Combines regulatory and compliance data to provide actionable insights.
    
    Args:
        country: Country name or code
        regulations_data: Optional regulatory analysis data
        compliance_data: Optional compliance analysis data
    
    Returns:
        Dictionary with risks and opportunities:
        {
            "country": str,
            "overall_risk_level": str,  # "low", "medium", "high", "critical"
            "overall_opportunity_level": str,  # "low", "medium", "high"
            "risks": List[Dict],
            "opportunities": List[Dict],
            "recommendations": List[str]
        }
    """
    risks = []
    opportunities = []
    recommendations = []

    # Combine risks from regulations and compliance
    if regulations_data:
        risks.extend(regulations_data.get("risks", []))
        opportunities.extend(regulations_data.get("opportunities", []))

    if compliance_data:
        risks.extend(compliance_data.get("compliance_risks", []))
        opportunities.extend(compliance_data.get("compliance_opportunities", []))

    # Determine overall risk level
    risk_levels = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
    }

    for risk in risks:
        severity = risk.get("severity", "medium")
        if severity in risk_levels:
            risk_levels[severity] += 1

    if risk_levels["critical"] > 0 or risk_levels["high"] > 3:
        overall_risk_level = "critical"
    elif risk_levels["high"] > 0 or risk_levels["medium"] > 3:
        overall_risk_level = "high"
    elif risk_levels["medium"] > 0:
        overall_risk_level = "medium"
    else:
        overall_risk_level = "low"

    # Determine overall opportunity level
    legal_status = regulations_data.get("legal_status", "unknown") if regulations_data else "unknown"
    white_label_allowed = compliance_data.get("white_label_allowed", False) if compliance_data else False

    if legal_status in ["legal", "regulated"] and white_label_allowed:
        overall_opportunity_level = "high"
    elif legal_status in ["legal", "regulated"]:
        overall_opportunity_level = "medium"
    elif legal_status == "restricted":
        overall_opportunity_level = "low"
    else:
        overall_opportunity_level = "low"

    # Generate recommendations
    if overall_risk_level == "critical":
        recommendations.append("⚠️ CRITICAL: High legal risk - consult with legal experts before market entry")
    elif overall_risk_level == "high":
        recommendations.append("⚠️ HIGH RISK: Review all regulatory requirements and obtain necessary licenses")
    elif overall_risk_level == "medium":
        recommendations.append("⚠️ MEDIUM RISK: Ensure compliance with all local regulations")

    if overall_opportunity_level == "high":
        recommendations.append("✅ HIGH OPPORTUNITY: Market is legally accessible for white label solutions")
    elif overall_opportunity_level == "medium":
        recommendations.append("✅ MEDIUM OPPORTUNITY: Market accessible with proper licensing")

    if regulations_data and regulations_data.get("licensing_required"):
        recommendations.append("📋 ACTION REQUIRED: Obtain appropriate gaming license before operations")

    if compliance_data and not compliance_data.get("white_label_allowed"):
        recommendations.append("⚠️ WARNING: White label model may have restrictions - verify with legal counsel")

    logger.info(
        f"Identified risks and opportunities for {country}: "
        f"risk={overall_risk_level}, opportunity={overall_opportunity_level}, "
        f"{len(risks)} risks, {len(opportunities)} opportunities"
    )

    return {
        "country": country,
        "overall_risk_level": overall_risk_level,
        "overall_opportunity_level": overall_opportunity_level,
        "risks": risks[:15],  # Top 15
        "opportunities": opportunities[:15],  # Top 15
        "recommendations": recommendations,
        "risk_count": len(risks),
        "opportunity_count": len(opportunities),
    }
