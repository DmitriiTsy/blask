"""Tools for market intelligence in iGaming industry (SOLID principles)."""

from typing import Any, Dict, List, Optional
from langchain.tools import tool

from ..utils.logging import get_logger

logger = get_logger(__name__)


@tool
def analyze_market_size(
    country: str,
    industry: str = "iGaming online casino",
) -> Dict[str, Any]:
    """
    Analyze market size for iGaming industry in a specific country.
    
    Uses search to estimate market size based on:
    - Search volume for casino-related keywords
    - Number of active operators
    - Market reports and statistics
    
    Args:
        country: Country name or code (e.g., "Spain", "UK", "US")
        industry: Industry type (default: "iGaming online casino")
    
    Returns:
        Dictionary with market size analysis:
        {
            "country": str,
            "market_size": str,  # "small", "medium", "large"
            "estimated_volume": int,
            "search_volume": int,
            "active_operators": int,
            "market_maturity": str,  # "emerging", "mature", "saturated"
            "growth_potential": str  # "low", "medium", "high"
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

    # Search for market size information
    queries = [
        f"{country} online casino market size",
        f"{country} iGaming market statistics",
        f"{country} gambling market revenue",
        f"{country} casino operators number",
    ]

    all_results = []
    for query in queries:
        try:
            results = search_tool.search(query)
            all_results.extend(results)
        except Exception as e:
            logger.error(f"Error searching for market size with query '{query}': {e}")
            continue

    # Analyze results to estimate market size
    search_volume = len(all_results)
    
    # Extract numbers from results (revenue, operators count, etc.)
    revenue_indicators = []
    operator_indicators = []
    
    for result in all_results:
        snippet = result.get("snippet", "").lower()
        title = result.get("title", "").lower()
        text = f"{title} {snippet}"
        
        # Look for revenue indicators (millions, billions, EUR, USD, etc.)
        import re
        revenue_patterns = [
            r'(\d+\.?\d*)\s*(million|billion|млн|млрд)',
            r'€(\d+\.?\d*)\s*(million|billion)',
            r'\$(\d+\.?\d*)\s*(million|billion)',
        ]
        
        for pattern in revenue_patterns:
            matches = re.findall(pattern, text)
            if matches:
                revenue_indicators.extend(matches)
        
        # Look for operator count
        operator_patterns = [
            r'(\d+)\s*(operators|casinos|sites|platforms)',
            r'(\d+)\s*(лицензий|операторов)',
        ]
        
        for pattern in operator_patterns:
            matches = re.findall(pattern, text)
            if matches:
                operator_indicators.extend(matches)

    # Estimate market size based on indicators
    estimated_volume = 0
    if revenue_indicators:
        # Simple estimation (in millions)
        try:
            values = [float(m[0]) for m in revenue_indicators if m]
            if values:
                estimated_volume = int(sum(values) / len(values) * 1000000)  # Convert to base units
        except:
            pass

    active_operators = 0
    if operator_indicators:
        try:
            values = [int(m[0]) for m in operator_indicators if m]
            if values:
                active_operators = int(sum(values) / len(values))
        except:
            pass

    # Determine market size category
    if estimated_volume > 1000000000 or active_operators > 50:  # > 1B or > 50 operators
        market_size = "large"
        market_maturity = "mature"
        growth_potential = "medium"
    elif estimated_volume > 100000000 or active_operators > 20:  # > 100M or > 20 operators
        market_size = "medium"
        market_maturity = "mature"
        growth_potential = "high"
    else:
        market_size = "small"
        market_maturity = "emerging"
        growth_potential = "high"

    logger.info(
        f"Analyzed market size for {country}: {market_size} market, "
        f"{active_operators} operators, {estimated_volume} estimated volume"
    )

    return {
        "country": country,
        "industry": industry,
        "market_size": market_size,
        "estimated_volume": estimated_volume,
        "search_volume": search_volume,
        "active_operators": active_operators,
        "market_maturity": market_maturity,
        "growth_potential": growth_potential,
        "data_sources": len(all_results),
    }


@tool
def find_white_label_platforms(
    country: str,
    industry: str = "white label iGaming casino platform",
) -> Dict[str, Any]:
    """
    Find white label iGaming casino platforms operating in a country.
    
    Searches for white label platforms, casino software providers, and
    turnkey solutions in the specified country.
    
    Args:
        country: Country name or code
        industry: Industry type (default: "white label iGaming casino platform")
    
    Returns:
        Dictionary with found platforms:
        {
            "country": str,
            "platforms": List[Dict],
            "count": int,
            "platform_types": List[str]  # "white_label", "software_provider", "turnkey"
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

    # Search queries for white label platforms
    queries = [
        f"{country} white label casino platform",
        f"{country} iGaming software provider",
        f"{country} turnkey casino solution",
        f"{country} casino platform provider",
        f"white label casino {country}",
    ]

    all_platforms = []
    seen_domains = set()

    for query in queries:
        try:
            results = search_tool.search(query)

            for result in results:
                link = result.get("link", "")
                if "/" in link and link.startswith("http"):
                    domain = link.split("/")[2] if len(link.split("/")) > 2 else link
                else:
                    domain = link

                # Filter for white label/platform providers
                title_lower = result.get("title", "").lower()
                snippet_lower = result.get("snippet", "").lower()
                text = f"{title_lower} {snippet_lower}"

                platform_keywords = [
                    "white label",
                    "platform",
                    "software provider",
                    "turnkey",
                    "solution",
                    "igaming",
                    "casino software",
                    "saaS",
                ]

                is_platform = any(keyword in text for keyword in platform_keywords)

                if is_platform and domain not in seen_domains:
                    seen_domains.add(domain)
                    
                    # Determine platform type
                    platform_type = "white_label"
                    if "software provider" in text or "software" in text:
                        platform_type = "software_provider"
                    elif "turnkey" in text or "solution" in text:
                        platform_type = "turnkey"
                    
                    all_platforms.append(
                        {
                            "name": result.get("title", domain),
                            "domain": domain,
                            "url": link,
                            "description": result.get("snippet", ""),
                            "type": platform_type,
                            "source": "search",
                        }
                    )
        except Exception as e:
            logger.error(f"Error searching for platforms with query '{query}': {e}")
            continue

    platform_types = list(set(p.get("type", "white_label") for p in all_platforms))

    logger.info(
        f"Found {len(all_platforms)} white label platforms for {country}"
    )

    return {
        "country": country,
        "industry": industry,
        "platforms": all_platforms[:30],  # Top 30
        "count": len(all_platforms),
        "platform_types": platform_types,
    }


@tool
def identify_growth_opportunities(
    country: str,
    market_data: Optional[Dict] = None,
) -> Dict[str, Any]:
    """
    Identify growth opportunities in a market.
    
    Analyzes market conditions to identify opportunities for:
    - Market entry
    - Expansion
    - New niches
    - Underserved segments
    
    Args:
        country: Country name or code
        market_data: Optional market analysis data
    
    Returns:
        Dictionary with growth opportunities:
        {
            "country": str,
            "opportunities": List[Dict],
            "entry_barriers": List[str],
            "recommendations": List[str]
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

    # Search for market opportunities
    queries = [
        f"{country} iGaming market opportunities",
        f"{country} casino market growth",
        f"{country} gambling regulations",
        f"{country} online casino license",
    ]

    all_results = []
    for query in queries:
        try:
            results = search_tool.search(query)
            all_results.extend(results)
        except Exception as e:
            logger.error(f"Error searching for opportunities with query '{query}': {e}")
            continue

    # Analyze results for opportunities
    opportunities = []
    entry_barriers = []
    
    opportunity_keywords = [
        "growing",
        "expanding",
        "opportunity",
        "potential",
        "emerging",
        "new market",
        "untapped",
    ]
    
    barrier_keywords = [
        "regulation",
        "license",
        "restriction",
        "ban",
        "prohibited",
        "barrier",
        "requirement",
    ]

    for result in all_results:
        snippet = result.get("snippet", "").lower()
        title = result.get("title", "").lower()
        text = f"{title} {snippet}"

        # Check for opportunities
        if any(keyword in text for keyword in opportunity_keywords):
            opportunities.append({
                "title": result.get("title", ""),
                "description": result.get("snippet", ""),
                "source": result.get("link", ""),
                "type": "growth_opportunity",
            })

        # Check for barriers
        if any(keyword in text for keyword in barrier_keywords):
            entry_barriers.append({
                "title": result.get("title", ""),
                "description": result.get("snippet", ""),
                "source": result.get("link", ""),
                "type": "entry_barrier",
            })

    # Generate recommendations based on market data
    recommendations = []
    
    if market_data:
        market_size = market_data.get("market_size", "")
        growth_potential = market_data.get("growth_potential", "")
        
        if market_size == "small" and growth_potential == "high":
            recommendations.append("Early market entry opportunity - low competition, high growth potential")
        elif market_size == "medium":
            recommendations.append("Moderate competition - focus on differentiation")
        elif market_size == "large":
            recommendations.append("Mature market - focus on niche segments or innovation")
        
        if len(entry_barriers) > 0:
            recommendations.append("Review regulatory requirements before market entry")

    logger.info(
        f"Identified {len(opportunities)} opportunities and {len(entry_barriers)} barriers for {country}"
    )

    return {
        "country": country,
        "opportunities": opportunities[:10],  # Top 10
        "entry_barriers": entry_barriers[:10],  # Top 10
        "recommendations": recommendations,
        "opportunity_count": len(opportunities),
        "barrier_count": len(entry_barriers),
    }


@tool
def analyze_regional_market(
    country: str,
    include_neighbors: bool = False,
) -> Dict[str, Any]:
    """
    Analyze regional market including neighboring countries if requested.
    
    Provides comprehensive regional analysis including:
    - Market comparison with neighbors
    - Regional trends
    - Cross-border opportunities
    
    Args:
        country: Country name or code
        include_neighbors: Whether to include neighboring countries analysis
    
    Returns:
        Dictionary with regional analysis:
        {
            "country": str,
            "regional_data": Dict,
            "neighbors": List[Dict] if include_neighbors,
            "regional_trends": List[str]
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

    # Search for regional market information
    queries = [
        f"{country} iGaming regional market",
        f"{country} casino market comparison",
    ]

    if include_neighbors:
        queries.append(f"{country} neighboring countries casino market")

    all_results = []
    for query in queries:
        try:
            results = search_tool.search(query)
            all_results.extend(results)
        except Exception as e:
            logger.error(f"Error searching for regional data with query '{query}': {e}")
            continue

    # Extract regional trends
    regional_trends = []
    for result in all_results[:5]:  # Top 5
        snippet = result.get("snippet", "")
        if snippet:
            regional_trends.append(snippet[:200])  # First 200 chars

    neighbors_data = []
    if include_neighbors:
        # Simple neighbor detection (can be enhanced)
        # For now, just note that neighbors analysis is requested
        neighbors_data.append({
            "note": "Neighbor analysis requested - implement country-specific neighbor detection"
        })

    logger.info(f"Analyzed regional market for {country}")

    return {
        "country": country,
        "regional_data": {
            "search_results": len(all_results),
            "trends_identified": len(regional_trends),
        },
        "neighbors": neighbors_data if include_neighbors else [],
        "regional_trends": regional_trends,
    }
