"""Tools for competitor tracking in iGaming industry (SOLID principles)."""

from typing import Any, Dict, List, Optional
from langchain.tools import tool

from ..utils.logging import get_logger

logger = get_logger(__name__)


@tool
def identify_igaming_competitors(
    brand_name: str,
    country: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Identify competitors in online casino industry for a given brand.
    
    Focuses specifically on iGaming/online casino brands.
    Uses search to find competitors and filters results to ensure they are casino-related.
    
    Args:
        brand_name: Name of the brand to find competitors for (e.g., "bet365")
        country: Optional country code for localized search (e.g., "UK", "US")
    
    Returns:
        Dictionary with list of competitors and their basic info:
        {
            "brand": str,
            "country": Optional[str],
            "competitors": List[Dict],
            "count": int
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

    # Search queries for finding competitors
    queries = [
        f"{brand_name} online casino competitors",
        f"best online casino like {brand_name}",
        f"{brand_name} alternative casino sites",
    ]

    if country:
        queries.append(f"{brand_name} casino competitors {country}")

    all_competitors = []
    seen_domains = set()

    for query in queries:
        try:
            results = search_tool.search(query)

            for result in results:
                link = result.get("link", "")
                # Extract domain
                if "/" in link and link.startswith("http"):
                    domain = link.split("/")[2] if len(link.split("/")) > 2 else link
                else:
                    domain = link

                # Filter to ensure it's casino-related
                title_lower = result.get("title", "").lower()
                snippet_lower = result.get("snippet", "").lower()

                casino_keywords = [
                    "casino",
                    "bet",
                    "gambling",
                    "poker",
                    "slot",
                    "jackpot",
                    "wager",
                    "bookmaker",
                ]
                is_casino = any(
                    keyword in title_lower or keyword in snippet_lower
                    for keyword in casino_keywords
                )

                if is_casino and domain not in seen_domains:
                    seen_domains.add(domain)
                    all_competitors.append(
                        {
                            "name": result.get("title", domain),
                            "domain": domain,
                            "url": link,
                            "description": result.get("snippet", ""),
                            "source": "search",
                        }
                    )
        except Exception as e:
            logger.error(f"Error searching for competitors with query '{query}': {e}")
            continue

    logger.info(f"Found {len(all_competitors)} iGaming competitors for {brand_name}")

    return {
        "brand": brand_name,
        "country": country,
        "competitors": all_competitors[:20],  # Top 20
        "count": len(all_competitors),
    }


@tool
def monitor_competitor_keywords(
    competitor_domain: str,
    timeframe: str = "30d",
) -> Dict[str, Any]:
    """
    Monitor keywords that a competitor is targeting.
    
    Uses existing trend analysis functionality to extract keywords from Google Trends.
    
    Args:
        competitor_domain: Domain of the competitor (e.g., "bet365.com")
        timeframe: Time period for analysis (e.g., "30d", "90d", "1y")
    
    Returns:
        Dictionary with competitor's keywords and metrics:
        {
            "competitor": str,
            "brand_name": str,
            "keywords": List[Dict],
            "total_keywords": int,
            "timeframe": str
        }
    """
    from ..config import get_settings
    from ..tools.trend_tools import SerpAPIGoogleTrendsAnalyzer, SearchBasedTrendAnalyzer
    from ..tools.search_tools import SerpAPISearchTool, MockSearchTool

    settings = get_settings()

    if not settings.serpapi_key:
        logger.warning("SerpAPI key not available for keyword monitoring")
        return {
            "competitor": competitor_domain,
            "keywords": [],
            "error": "SerpAPI key not available",
        }

    # Extract brand name from domain
    brand_name = (
        competitor_domain.replace(".com", "")
        .replace("www.", "")
        .replace(".net", "")
        .replace(".org", "")
        .strip()
    )

    trend_analyzer = SerpAPIGoogleTrendsAnalyzer(settings.serpapi_key)

    try:
        trend_data = trend_analyzer.get_trends(brand_name, timeframe)

        # Extract keywords from related queries
        keywords = []
        if trend_data.get("related_queries"):
            rising = trend_data["related_queries"].get("rising", [])
            top = trend_data["related_queries"].get("top", [])

            for query in rising[:10]:
                if isinstance(query, dict):
                    keywords.append(
                        {
                            "keyword": query.get("query", ""),
                            "type": "rising",
                            "growth": query.get("value", 0),
                        }
                    )

            for query in top[:10]:
                if isinstance(query, dict):
                    keywords.append(
                        {
                            "keyword": query.get("query", ""),
                            "type": "top",
                            "volume": query.get("value", 0),
                        }
                    )

        logger.info(
            f"Monitored {len(keywords)} keywords for {competitor_domain}"
        )

        return {
            "competitor": competitor_domain,
            "brand_name": brand_name,
            "keywords": keywords,
            "total_keywords": len(keywords),
            "trend_data": trend_data,
            "timeframe": timeframe,
        }
    except Exception as e:
        logger.error(f"Error monitoring keywords for {competitor_domain}: {e}")
        return {
            "competitor": competitor_domain,
            "keywords": [],
            "error": str(e),
        }


@tool
def calculate_competitor_metrics(
    competitor_domain: str,
    market_data: Optional[Dict] = None,
) -> Dict[str, Any]:
    """
    Calculate metrics (BAP, APS, CEB) for a competitor.
    
    Uses trend data to estimate brand metrics.
    Note: This is a simplified calculation. Real implementation would need
    comprehensive market data.
    
    Args:
        competitor_domain: Domain of the competitor (e.g., "bet365.com")
        market_data: Optional market data for comparison (not used in simplified version)
    
    Returns:
        Dictionary with calculated metrics:
        {
            "competitor": str,
            "brand_name": str,
            "bap": float,
            "aps": float,
            "ceb": float,
            "avg_interest": float,
            "growth_rate": float
        }
    """
    from ..config import get_settings
    from ..tools.trend_tools import SerpAPIGoogleTrendsAnalyzer

    settings = get_settings()

    if not settings.serpapi_key:
        return {
            "competitor": competitor_domain,
            "bap": None,
            "aps": None,
            "ceb": None,
            "error": "SerpAPI key not available",
        }

    trend_analyzer = SerpAPIGoogleTrendsAnalyzer(settings.serpapi_key)
    brand_name = (
        competitor_domain.replace(".com", "")
        .replace("www.", "")
        .replace(".net", "")
        .replace(".org", "")
        .strip()
    )

    try:
        # Get trend data
        trend_data = trend_analyzer.get_trends(brand_name, "1y")

        # Calculate average interest
        interest_over_time = trend_data.get("interest_over_time", [])
        if interest_over_time and isinstance(interest_over_time, list):
            values = [
                point.get("value", 0)
                for point in interest_over_time
                if isinstance(point, dict)
            ]
            avg_interest = sum(values) / len(values) if values else 0
        else:
            avg_interest = 0

        # BAP (Brand's Accumulated Power) - simplified calculation
        # Normalize interest to 0-1 scale (assuming max interest is 100)
        bap = min(avg_interest / 100.0, 1.0) if avg_interest > 0 else 0.0

        # APS (Acquisition Power Score) - simplified calculation
        # Based on growth in related queries
        rising_queries = trend_data.get("related_queries", {}).get("rising", [])
        growth_rate = (
            len(rising_queries) / 10.0 if rising_queries else 0.0
        )  # Normalize to 0-1
        aps = bap * (1 + growth_rate * 0.1)

        # CEB (Competitive Earning Baseline) - simplified calculation
        # Based on BAP and APS (assuming base market size)
        base_revenue = 1000000  # Base market size estimate
        ceb = base_revenue * bap * aps

        logger.info(
            f"Calculated metrics for {competitor_domain}: BAP={bap:.4f}, APS={aps:.4f}, CEB={ceb:.2f}"
        )

        return {
            "competitor": competitor_domain,
            "brand_name": brand_name,
            "bap": round(bap, 4),
            "aps": round(aps, 4),
            "ceb": round(ceb, 2),
            "avg_interest": round(avg_interest, 2),
            "growth_rate": round(growth_rate, 4),
        }
    except Exception as e:
        logger.error(f"Error calculating metrics for {competitor_domain}: {e}")
        return {
            "competitor": competitor_domain,
            "error": str(e),
        }


@tool
def detect_competitor_changes(
    competitor_domain: str,
    previous_data: Dict[str, Any],
    current_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Detect changes in competitor's strategy (keywords, metrics).
    
    Compares previous and current monitoring data to identify changes.
    
    Args:
        competitor_domain: Domain of the competitor
        previous_data: Previous monitoring data (from previous run)
        current_data: Current monitoring data
    
    Returns:
        Dictionary with detected changes:
        {
            "competitor": str,
            "changes_detected": List[Dict],
            "severity": str  # "low", "medium", "high"
        }
    """
    changes = {
        "competitor": competitor_domain,
        "changes_detected": [],
        "severity": "low",
    }

    try:
        # Compare keywords
        prev_keywords = set(
            k.get("keyword", "")
            for k in previous_data.get("keywords", [])
            if isinstance(k, dict)
        )
        curr_keywords = set(
            k.get("keyword", "")
            for k in current_data.get("keywords", [])
            if isinstance(k, dict)
        )

        new_keywords = curr_keywords - prev_keywords
        dropped_keywords = prev_keywords - curr_keywords

        if new_keywords:
            changes["changes_detected"].append(
                {
                    "type": "new_keywords",
                    "keywords": list(new_keywords),
                    "count": len(new_keywords),
                }
            )
            changes["severity"] = "medium"

        if dropped_keywords:
            changes["changes_detected"].append(
                {
                    "type": "dropped_keywords",
                    "keywords": list(dropped_keywords),
                    "count": len(dropped_keywords),
                }
            )

        # Compare metrics
        prev_metrics = previous_data.get("metrics", {})
        curr_metrics = current_data.get("metrics", {})

        if prev_metrics and curr_metrics:
            prev_bap = prev_metrics.get("bap", 0)
            curr_bap = curr_metrics.get("bap", 0)

            if prev_bap > 0 and abs(curr_bap - prev_bap) > 0.05:  # Change > 5%
                change_percent = ((curr_bap - prev_bap) / prev_bap) * 100
                changes["changes_detected"].append(
                    {
                        "type": "metric_change",
                        "metric": "bap",
                        "previous": prev_bap,
                        "current": curr_bap,
                        "change": curr_bap - prev_bap,
                        "change_percent": round(change_percent, 2),
                    }
                )
                if abs(curr_bap - prev_bap) > 0.1:  # Change > 10%
                    changes["severity"] = "high"

        logger.info(
            f"Detected {len(changes['changes_detected'])} changes for {competitor_domain}"
        )

    except Exception as e:
        logger.error(f"Error detecting changes for {competitor_domain}: {e}")
        changes["error"] = str(e)

    return changes


@tool
def discover_new_igaming_brands(
    country: Optional[str] = None,
    timeframe: str = "30d",
) -> Dict[str, Any]:
    """
    Discover new online casino brands in the market.
    
    Searches for recently launched or newly discovered casino brands.
    
    Args:
        country: Optional country code for localized search
        timeframe: Time period (e.g., "30d")
    
    Returns:
        Dictionary with newly discovered brands:
        {
            "country": Optional[str],
            "timeframe": str,
            "new_brands": List[Dict],
            "count": int
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

    queries = [
        "new online casino 2024",
        "latest casino sites",
        "new gambling platforms",
    ]

    if country:
        queries.append(f"new casino {country} 2024")

    new_brands = []
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

                if domain not in seen_domains:
                    seen_domains.add(domain)
                    new_brands.append(
                        {
                            "name": result.get("title", domain),
                            "domain": domain,
                            "url": link,
                            "description": result.get("snippet", ""),
                            "discovered_via": query,
                        }
                    )
        except Exception as e:
            logger.error(f"Error discovering brands with query '{query}': {e}")
            continue

    logger.info(f"Discovered {len(new_brands)} new iGaming brands")

    return {
        "country": country,
        "timeframe": timeframe,
        "new_brands": new_brands[:15],  # Top 15
        "count": len(new_brands),
    }
