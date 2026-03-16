"""Streamlit web application for Blask."""

import base64
import io
import sys
from io import BytesIO
from pathlib import Path
from typing import List
from datetime import datetime

import pandas as pd
import streamlit as st
from PIL import Image

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.graph.graph import create_graph
from src.graph.state import create_initial_state
from src.utils.logging import get_logger

logger = get_logger(__name__)

# Page config
st.set_page_config(
    page_title="Blask - Trend & Competitor Analysis",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        margin: 1rem 0;
    }
    .component-item {
        padding: 0.5rem;
        margin: 0.25rem 0;
        border-left: 3px solid #1f77b4;
        padding-left: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def display_visualization(visualization: str | None) -> None:
    """Display visualization if available."""
    if not visualization:
        return

    try:
        # Check if it's base64 encoded
        if visualization.startswith("data:image/png;base64,"):
            # Extract base64 data
            base64_data = visualization.split(",")[1]
            image_data = base64.b64decode(base64_data)
            image = Image.open(BytesIO(image_data))

            st.image(image, caption="Data Visualization", use_container_width=True)
        else:
            st.info(f"Visualization available: {visualization}")
    except Exception as e:
        st.warning(f"Could not display visualization: {e}")


def display_thinking_component(result: dict) -> None:
    """
    Display thinking component showing which nodes and features are being used.
    
    Args:
        result: Graph execution result
    """
    st.markdown("---")
    st.markdown("## 🤔 Thinking Component")
    
    # Execution path
    execution_path = result.get("execution_path", [])
    decision = result.get("decision", "")
    search_type = result.get("search_type")
    needs_charts = result.get("needs_charts", False)
    
    # Create component list with icons and descriptions
    active_components = []
    
    # Thinking node (always executed)
    if "thinking_node" in execution_path:
        active_components.append({
            "icon": "✅",
            "text": "Using Thinking",
            "description": "Analyzing query and making decision"
        })
    
    # Decision-based components
    if decision == "search":
        if search_type == "keywords":
            active_components.append({
                "icon": "🔍",
                "text": "Using Search",
                "description": "Keyword search"
            })
        elif search_type == "competitors":
            active_components.append({
                "icon": "🏢",
                "text": "Using Search",
                "description": "Competitor analysis"
            })
        elif search_type == "trends":
            active_components.append({
                "icon": "📈",
                "text": "Using Trends",
                "description": "Trend analysis"
            })
        else:
            active_components.append({
                "icon": "🔍",
                "text": "Using Search",
                "description": "General search"
            })
    elif decision == "statistics":
        active_components.append({
            "icon": "📊",
            "text": "Using Statistics",
            "description": "Data analysis"
        })
        if needs_charts:
            active_components.append({
                "icon": "📈",
                "text": "Creating Charts",
                "description": "Visualization generation"
            })
    elif decision == "direct_answer":
        active_components.append({
            "icon": "💬",
            "text": "Using Direct Answer",
            "description": "No search needed"
        })
    
    # Search node status
    if "search_node" in execution_path:
        active_components.append({
            "icon": "🔎",
            "text": "Using Search Node",
            "description": "Executing search operations"
        })
    
    # Analysis node (always executed)
    if "analysis_node" in execution_path:
        active_components.append({
            "icon": "📝",
            "text": "Using Analysis Node",
            "description": "Processing and formatting results"
        })
    
    # Display components in a nice format
    if active_components:
        for component in active_components:
            st.markdown(
                f"""
                <div class="component-item">
                    <strong>{component['icon']} {component['text']}</strong><br>
                    <span style="color: #666; font-size: 0.9em;">{component['description']}</span>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.info("No active components detected")
    
    # Show reasoning if available
    if result.get("reasoning"):
        with st.expander("💭 Reasoning"):
            st.info(result["reasoning"])
    
    # Execution path visualization
    if execution_path:
        st.markdown("#### Execution Flow:")
        path_str = " → ".join([node.replace("_node", "").title() for node in execution_path])
        st.code(path_str, language=None)


def display_market_intelligence_results(result: dict, countries: List[str]) -> None:
    """
    Display Market Intelligence Agent results with intermediate steps by country.
    
    Args:
        result: Agent execution result
        countries: List of analyzed countries
    """
    st.markdown("---")
    st.markdown("## 🌍 Market Intelligence Results")
    
    # Summary
    comparison_summary = result.get("comparison_summary", {})
    if comparison_summary:
        st.markdown("### 📊 Summary")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Countries Analyzed", comparison_summary.get("total_countries", 0))
        with col2:
            st.metric("Total Platforms Found", comparison_summary.get("total_platforms", 0))
        with col3:
            st.metric("Total Opportunities", comparison_summary.get("total_opportunities", 0))
        with col4:
            # Count market sizes
            market_sizes = comparison_summary.get("market_sizes", {})
            large_markets = sum(1 for s in market_sizes.values() if s == "large")
            st.metric("Large Markets", large_markets)
    
    # Results by country
    results_by_country = result.get("results", {})
    
    for country in countries:
        if country not in results_by_country:
            continue
            
        country_result = results_by_country[country]
        
        st.markdown("---")
        st.markdown(f"### 🇺🇳 {country}")
        
        # Market Size Analysis
        market_size = country_result.get("market_size", {})
        if market_size:
            st.markdown("#### 📈 Market Size Analysis")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                size = market_size.get("market_size", "unknown")
                size_emoji = {"large": "🔴", "medium": "🟡", "small": "🟢"}.get(size, "⚪")
                st.metric("Market Size", f"{size_emoji} {size.title()}")
            with col2:
                st.metric("Active Operators", market_size.get("active_operators", 0))
            with col3:
                maturity = market_size.get("market_maturity", "unknown")
                st.metric("Market Maturity", maturity.title())
            with col4:
                growth = market_size.get("growth_potential", "unknown")
                growth_emoji = {"high": "📈", "medium": "➡️", "low": "📉"}.get(growth, "⚪")
                st.metric("Growth Potential", f"{growth_emoji} {growth.title()}")
            
            if market_size.get("estimated_volume"):
                st.caption(f"Estimated Market Volume: ${market_size.get('estimated_volume', 0):,}")
        
        # White Label Platforms
        platforms = country_result.get("platforms", {})
        if platforms and platforms.get("platforms"):
            st.markdown("#### 🏢 White Label Platforms Found")
            st.success(f"Found {platforms.get('count', 0)} platforms")
            
            platforms_list = platforms.get("platforms", [])
            with st.expander(f"View {len(platforms_list)} Platforms"):
                for i, platform in enumerate(platforms_list[:20], 1):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        platform_type = platform.get("type", "white_label")
                        type_emoji = {
                            "white_label": "🏷️",
                            "software_provider": "💻",
                            "turnkey": "🔧"
                        }.get(platform_type, "📦")
                        st.markdown(f"**{i}. {type_emoji} {platform.get('name', 'Unknown')}**")
                        st.caption(f"Type: {platform_type.replace('_', ' ').title()}")
                        if platform.get('description'):
                            st.write(platform['description'][:200] + "...")
                    with col2:
                        if platform.get('url'):
                            st.markdown(f"[🔗 Visit]({platform['url']})")
                    st.markdown("---")
        
        # Growth Opportunities
        opportunities = country_result.get("opportunities", {})
        if opportunities:
            st.markdown("#### 🚀 Growth Opportunities")
            
            opps_list = opportunities.get("opportunities", [])
            barriers_list = opportunities.get("entry_barriers", [])
            recommendations = opportunities.get("recommendations", [])
            
            if opps_list:
                st.success(f"Found {len(opps_list)} opportunities")
                with st.expander(f"View {len(opps_list)} Opportunities"):
                    for i, opp in enumerate(opps_list[:10], 1):
                        st.markdown(f"**{i}. {opp.get('title', 'Opportunity')}**")
                        st.write(opp.get('description', '')[:300] + "...")
                        if opp.get('source'):
                            st.markdown(f"[🔗 Source]({opp['source']})")
                        st.markdown("---")
            
            if barriers_list:
                st.warning(f"Found {len(barriers_list)} entry barriers")
                with st.expander(f"View {len(barriers_list)} Entry Barriers"):
                    for i, barrier in enumerate(barriers_list[:10], 1):
                        st.markdown(f"**{i}. {barrier.get('title', 'Barrier')}**")
                        st.write(barrier.get('description', '')[:300] + "...")
                        if barrier.get('source'):
                            st.markdown(f"[🔗 Source]({barrier['source']})")
                        st.markdown("---")
            
            if recommendations:
                st.info("💡 Recommendations:")
                for rec in recommendations:
                    st.markdown(f"- {rec}")
        
        # Jurisdiction Analysis (Legal/Regulatory)
        jurisdiction = country_result.get("jurisdiction", {})
        if jurisdiction and not jurisdiction.get("error"):
            st.markdown("#### ⚖️ Legal & Jurisdiction Analysis")
            
            # Regulations
            regulations = jurisdiction.get("regulations", {})
            if regulations:
                col1, col2, col3 = st.columns(3)
                with col1:
                    legal_status = regulations.get("legal_status", "unknown")
                    status_emoji = {
                        "legal": "✅",
                        "regulated": "📋",
                        "restricted": "⚠️",
                        "illegal": "❌",
                    }.get(legal_status, "❓")
                    st.metric("Legal Status", f"{status_emoji} {legal_status.title()}")
                with col2:
                    licensing = regulations.get("licensing_required", False)
                    st.metric("Licensing Required", "Yes" if licensing else "No")
                with col3:
                    regulatory_body = regulations.get("regulatory_body", "N/A")
                    st.metric("Regulatory Body", regulatory_body[:30] if regulatory_body != "N/A" else "N/A")
                
                # Key Regulations
                key_regulations = regulations.get("key_regulations", [])
                if key_regulations:
                    with st.expander(f"View {len(key_regulations)} Key Regulations"):
                        for i, reg in enumerate(key_regulations[:10], 1):
                            st.markdown(f"**{i}. {reg.get('title', 'Regulation')}**")
                            st.write(reg.get('description', '')[:200] + "...")
                            if reg.get('source'):
                                st.markdown(f"[🔗 Source]({reg['source']})")
                            st.markdown("---")
                
                # Compliance Requirements
                compliance_reqs = regulations.get("compliance_requirements", [])
                if compliance_reqs:
                    st.caption(f"Compliance Requirements: {', '.join(compliance_reqs)}")
            
            # White Label Compliance
            compliance = jurisdiction.get("compliance", {})
            if compliance:
                white_label_allowed = compliance.get("white_label_allowed", False)
                if white_label_allowed:
                    st.success("✅ White Label Platform Model is Allowed")
                else:
                    st.warning("⚠️ White Label Platform Model may have restrictions")
                
                # License Requirements
                license_reqs = compliance.get("license_requirements", [])
                if license_reqs:
                    with st.expander(f"View {len(license_reqs)} License Requirements"):
                        for i, req in enumerate(license_reqs[:5], 1):
                            st.write(f"**{i}.** {req.get('description', '')[:200]}...")
                            if req.get('source'):
                                st.markdown(f"[🔗 Source]({req['source']})")
                            st.markdown("---")
            
            # Risks and Opportunities
            risks_opps = jurisdiction.get("risks_and_opportunities", {})
            if risks_opps:
                col1, col2 = st.columns(2)
                
                with col1:
                    risk_level = risks_opps.get("overall_risk_level", "unknown")
                    risk_emoji = {
                        "critical": "🔴",
                        "high": "🟠",
                        "medium": "🟡",
                        "low": "🟢",
                    }.get(risk_level, "⚪")
                    st.metric("Overall Risk Level", f"{risk_emoji} {risk_level.upper()}")
                
                with col2:
                    opp_level = risks_opps.get("overall_opportunity_level", "unknown")
                    opp_emoji = {
                        "high": "📈",
                        "medium": "➡️",
                        "low": "📉",
                    }.get(opp_level, "⚪")
                    st.metric("Opportunity Level", f"{opp_emoji} {opp_level.upper()}")
                
                # Legal Risks
                risks_list = risks_opps.get("risks", [])
                if risks_list:
                    st.warning(f"⚠️ Found {len(risks_list)} Legal Risks")
                    with st.expander(f"View {len(risks_list)} Legal Risks"):
                        for i, risk in enumerate(risks_list[:10], 1):
                            severity = risk.get("severity", "medium")
                            severity_emoji = {
                                "critical": "🔴",
                                "high": "🟠",
                                "medium": "🟡",
                            }.get(severity, "⚪")
                            st.markdown(f"**{i}. {severity_emoji} {risk.get('title', 'Risk')}**")
                            st.write(risk.get('description', '')[:300] + "...")
                            if risk.get('source'):
                                st.markdown(f"[🔗 Source]({risk['source']})")
                            st.markdown("---")
                
                # Legal Opportunities
                opps_list = risks_opps.get("opportunities", [])
                if opps_list:
                    st.success(f"✅ Found {len(opps_list)} Legal Opportunities")
                    with st.expander(f"View {len(opps_list)} Legal Opportunities"):
                        for i, opp in enumerate(opps_list[:10], 1):
                            st.markdown(f"**{i}. {opp.get('title', 'Opportunity')}**")
                            st.write(opp.get('description', '')[:300] + "...")
                            if opp.get('source'):
                                st.markdown(f"[🔗 Source]({opp['source']})")
                            st.markdown("---")
                
                # Recommendations
                recommendations = risks_opps.get("recommendations", [])
                if recommendations:
                    st.info("💡 Legal Recommendations:")
                    for rec in recommendations:
                        st.markdown(f"- {rec}")
        
        # Intermediate steps for this country
        country_steps = [
            step for step in result.get("total_intermediate_steps", [])
            if step.get("input", {}).get("country") == country
        ]
        
        if country_steps:
            with st.expander(f"🔍 View Analysis Steps for {country}"):
                for i, step in enumerate(country_steps, 1):
                    tool_name = step.get("tool", "unknown")
                    tool_output = step.get("output", {})
                    
                    st.markdown(f"**Step {i}: {tool_name.replace('_', ' ').title()}**")
                    if isinstance(tool_output, dict):
                        # Show key metrics
                        if "market_size" in tool_output:
                            st.caption(f"Market Size: {tool_output.get('market_size', 'N/A')}")
                        if "count" in tool_output:
                            st.caption(f"Count: {tool_output.get('count', 0)}")
                        if "opportunity_count" in tool_output:
                            st.caption(f"Opportunities: {tool_output.get('opportunity_count', 0)}")
                    st.markdown("---")
    
    # Comparison chart
    if len(countries) > 1 and comparison_summary:
        st.markdown("---")
        st.markdown("### 📊 Market Comparison")
        
        market_sizes = comparison_summary.get("market_sizes", {})
        if market_sizes:
            # Create comparison chart
            size_values = {"small": 1, "medium": 2, "large": 3}
            chart_data = {
                "Country": list(market_sizes.keys()),
                "Market Size": [size_values.get(s, 0) for s in market_sizes.values()]
            }
            chart_df = pd.DataFrame(chart_data)
            st.bar_chart(chart_df.set_index("Country")["Market Size"])


def display_competitor_tracker_results(result: dict) -> None:
    """
    Display Competitor Tracker Agent results with intermediate steps.
    
    Args:
        result: Graph execution result
    """
    st.markdown("---")
    st.markdown("## 🎯 Competitor Tracker Results")
    
    # Intermediate steps
    intermediate_steps = result.get("agent_intermediate_steps", [])
    competitors_list = result.get("competitors_list", [])
    competitor_keywords = result.get("competitor_keywords", {})
    competitor_metrics = result.get("competitor_metrics", {})
    
    # Step 1: Competitors Found
    if competitors_list:
        st.markdown("### ✅ Step 1: Competitors Identified")
        st.success(f"Found {len(competitors_list)} competitors")
        
        with st.expander(f"View {len(competitors_list)} Competitors"):
            for i, competitor in enumerate(competitors_list[:20], 1):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{i}. {competitor.get('name', 'Unknown')}**")
                    st.caption(f"Domain: {competitor.get('domain', 'N/A')}")
                    if competitor.get('description'):
                        st.write(competitor['description'][:200] + "...")
                with col2:
                    if competitor.get('url'):
                        st.markdown(f"[🔗 Visit]({competitor['url']})")
    
    # Step 2: Keywords Monitored
    if competitor_keywords:
        st.markdown("### 🔑 Step 2: Keywords Monitored")
        
        for competitor, keywords in competitor_keywords.items():
            if keywords:
                with st.expander(f"Keywords for {competitor} ({len(keywords)} keywords)"):
                    # Group by type
                    rising_keywords = [k for k in keywords if k.get('type') == 'rising']
                    top_keywords = [k for k in keywords if k.get('type') == 'top']
                    
                    if rising_keywords:
                        st.markdown("**📈 Rising Keywords:**")
                        for kw in rising_keywords[:10]:
                            growth = kw.get('growth', 0)
                            st.markdown(f"- {kw.get('keyword', '')} (Growth: {growth})")
                    
                    if top_keywords:
                        st.markdown("**⭐ Top Keywords:**")
                        for kw in top_keywords[:10]:
                            volume = kw.get('volume', 0)
                            st.markdown(f"- {kw.get('keyword', '')} (Volume: {volume})")
    
    # Step 3: Metrics Calculated
    if competitor_metrics:
        st.markdown("### 📊 Step 3: Metrics Calculated")
        
        # Create metrics table
        metrics_data = []
        for competitor, metrics in competitor_metrics.items():
            if metrics and not metrics.get('error'):
                metrics_data.append({
                    "Competitor": competitor,
                    "BAP": metrics.get('bap', 'N/A'),
                    "APS": metrics.get('aps', 'N/A'),
                    "CEB": f"${metrics.get('ceb', 0):,.0f}" if metrics.get('ceb') else 'N/A',
                    "Avg Interest": metrics.get('avg_interest', 'N/A'),
                    "Growth Rate": f"{metrics.get('growth_rate', 0):.2%}" if metrics.get('growth_rate') else 'N/A',
                })
        
        if metrics_data:
            import pandas as pd
            df = pd.DataFrame(metrics_data)
            st.dataframe(df, use_container_width=True)
            
            # Visualizations
            if len(metrics_data) > 0:
                col1, col2 = st.columns(2)
                
                with col1:
                    # BAP comparison chart
                    if any(m.get('BAP') != 'N/A' for m in metrics_data):
                        chart_data = {
                            'Competitor': [m['Competitor'] for m in metrics_data],
                            'BAP': [float(m['BAP']) if m['BAP'] != 'N/A' else 0 for m in metrics_data]
                        }
                        chart_df = pd.DataFrame(chart_data)
                        st.bar_chart(chart_df.set_index('Competitor')['BAP'])
                
                with col2:
                    # APS comparison chart
                    if any(m.get('APS') != 'N/A' for m in metrics_data):
                        chart_data = {
                            'Competitor': [m['Competitor'] for m in metrics_data],
                            'APS': [float(m['APS']) if m['APS'] != 'N/A' else 0 for m in metrics_data]
                        }
                        chart_df = pd.DataFrame(chart_data)
                        st.bar_chart(chart_df.set_index('Competitor')['APS'])
    
    # Intermediate steps details
    if intermediate_steps:
        st.markdown("### 🔍 Agent Execution Steps")
        with st.expander("View Detailed Agent Steps"):
            for i, step in enumerate(intermediate_steps, 1):
                tool_name = step.get("tool", "unknown")
                tool_input = step.get("input", {})
                tool_output = step.get("output", {})
                
                st.markdown(f"**Step {i}: {tool_name}**")
                st.json({
                    "input": tool_input,
                    "output_summary": {
                        "keys": list(tool_output.keys()) if isinstance(tool_output, dict) else "N/A",
                        "type": type(tool_output).__name__
                    }
                })
                st.markdown("---")
    
    # Final summary
    if result.get("tracked_competitors"):
        st.markdown("### 📝 Summary")
        st.info(result.get("tracked_competitors", ""))


def main():
    """Main Streamlit application."""
    # Header
    st.markdown('<h1 class="main-header">🔍 Blask</h1>', unsafe_allow_html=True)
    st.markdown(
        "<h3 style='text-align: center; color: #666;'>Trend & Competitor Analysis Tool</h3>",
        unsafe_allow_html=True,
    )

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        st.markdown("---")
        st.markdown("### 📚 About")
        st.info(
            """
            **Blask** analyzes trends, competitors, and statistics using:
            - 🤔 Thinking Node (decision making)
            - 🔍 Search Node (keyword & competitor search)
            - 🎯 Competitor Tracker Agent (AI-powered competitor tracking)
            - 🌍 Market Intelligence Agent (market analysis & platform discovery)
            - 📊 Analysis Node (data processing & visualization)
            """
        )

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔍 General Analysis",
        "🎯 Competitor Tracker",
        "🌍 Market Intelligence",
        "📚 Knowledge Base",
    ])

    with tab1:
        # Main content
        col1, col2 = st.columns([3, 1])

        with col1:
            # Query input
            user_query = st.text_area(
                "Enter your query:",
                value="",
                height=100,
                placeholder="Example: What are the latest trends in AI?",
                help="Ask about trends, competitors, or statistics",
            )

        with col2:
            st.markdown("<br>", unsafe_allow_html=True)  # Spacing
            analyze_button = st.button("🚀 Analyze", type="primary", use_container_width=True)

        # Process query
        if analyze_button and user_query:
            with st.spinner("🔄 Processing your query..."):
                try:
                    # Create graph
                    graph = create_graph()

                    # Create initial state
                    initial_state = create_initial_state(user_query.strip())

                    # Execute graph
                    result = graph.invoke(initial_state)

                    # Display Thinking Component first
                    display_thinking_component(result)

                    # Display results
                    st.markdown("---")
                    st.markdown("## 📋 Results")

                    # Decision info
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Decision", result.get("decision", "N/A"))
                    with col2:
                        st.metric("Search Type", result.get("search_type", "N/A") or "N/A")
                    with col3:
                        st.metric("Charts Created", "Yes" if result.get("charts_created") else "No")

                    # Formatted response
                    if result.get("formatted_response"):
                        st.markdown("---")
                        st.markdown("## 💬 Response")
                        st.markdown(result["formatted_response"])

                    # Visualization
                    if result.get("visualization"):
                        st.markdown("---")
                        st.markdown("## 📊 Visualization")
                        display_visualization(result["visualization"])

                    # Search results (if available)
                    if result.get("search_results"):
                        st.markdown("---")
                        st.markdown("## 🔍 Search Results")
                        with st.expander(f"View {len(result['search_results'])} results"):
                            for i, res in enumerate(result["search_results"][:10], 1):
                                st.markdown(f"### {i}. {res.get('title', 'No title')}")
                                st.write(res.get("snippet", "No description"))
                                if res.get("link"):
                                    st.markdown(f"[🔗 Link]({res['link']})")
                                st.markdown("---")

                    # Error handling
                    if result.get("error"):
                        st.error(f"❌ Error: {result['error']}")

                    # Raw data (debug)
                    if st.checkbox("Show debug info"):
                        with st.expander("🐛 Debug Information"):
                            st.json(result)

                except Exception as e:
                    st.error(f"❌ Error processing query: {str(e)}")
                    logger.error(f"Error in webapp: {e}", exc_info=True)

        elif analyze_button and not user_query:
            st.warning("⚠️ Please enter a query first!")

    with tab2:
        st.markdown("## 🎯 Competitor Tracker Agent")
        st.info(
            """
            **Competitor Tracker Agent** automatically:
            - Identifies competitors in online casino industry
            - Monitors their keywords
            - Calculates metrics (BAP, APS, CEB)
            - Tracks changes in strategy
            - Discovers new competitors
            """
        )

        col1, col2 = st.columns([3, 1])

        with col1:
            brand_query = st.text_input(
                "Enter brand name to track competitors:",
                value="",
                placeholder="Example: bet365",
                help="Enter the name of the brand to find and analyze competitors",
            )

        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            track_button = st.button("🎯 Track Competitors", type="primary", use_container_width=True)

        country_input = st.text_input(
            "Country (optional):",
            value="",
            placeholder="Example: UK, US",
            help="Optional country code for localized search",
        )

        if track_button and brand_query:
            with st.spinner("🔄 Tracking competitors..."):
                try:
                    # Create graph
                    graph = create_graph()

                    # Create initial state with brand name
                    initial_state = create_initial_state(
                        f"Find and analyze competitors for {brand_query}"
                    )
                    initial_state["brand_name"] = brand_query.strip()
                    if country_input:
                        initial_state["country"] = country_input.strip()

                    # Execute graph
                    result = graph.invoke(initial_state)

                    # Display results
                    display_competitor_tracker_results(result)

                    # Error handling
                    if result.get("error"):
                        st.error(f"❌ Error: {result['error']}")

                    # Debug info
                    if st.checkbox("Show debug info", key="debug_competitor"):
                        with st.expander("🐛 Debug Information"):
                            st.json(result)

                except Exception as e:
                    st.error(f"❌ Error tracking competitors: {str(e)}")
                    logger.error(f"Error in competitor tracker: {e}", exc_info=True)

        elif track_button and not brand_query:
            st.warning("⚠️ Please enter a brand name first!")

    with tab3:
        st.markdown("## 🌍 Market Intelligence Agent")
        st.info(
            """
            **Market Intelligence Agent** analyzes markets for white label iGaming casino platforms:
            - Market size analysis
            - White label platform discovery
            - Growth opportunities identification
            - **Legal & Jurisdiction analysis** (regulations, compliance, risks)
            - Regional market analysis
            
            Enter countries separated by commas to analyze multiple markets.
            """
        )

        col1, col2 = st.columns([3, 1])

        with col1:
            countries_input = st.text_area(
                "Enter countries to analyze (comma-separated):",
                value="",
                height=100,
                placeholder="Example: Spain, UK, Germany",
                help="Enter country names separated by commas. The agent will analyze each country sequentially.",
            )

        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            analyze_button = st.button("🌍 Analyze Markets", type="primary", use_container_width=True)

        col3, col4, col5 = st.columns(3)
        with col3:
            include_platforms = st.checkbox("Find White Label Platforms", value=True)
        with col4:
            include_opportunities = st.checkbox("Identify Growth Opportunities", value=True)
        with col5:
            include_jurisdiction = st.checkbox("Analyze Legal/Jurisdiction", value=True, help="Analyze legal framework, regulations, and compliance requirements")

        if analyze_button and countries_input:
            # Parse countries
            countries = [c.strip() for c in countries_input.split(",") if c.strip()]
            
            if not countries:
                st.warning("⚠️ Please enter at least one country!")
            else:
                with st.spinner(f"🔄 Analyzing {len(countries)} countries..."):
                    try:
                        from src.agents.market_intelligence_agent import MarketIntelligenceAgent
                        
                        # Create agent
                        agent = MarketIntelligenceAgent()
                        
                        # Analyze countries
                        result = agent.analyze_multiple_countries(
                            countries,
                            include_platforms=include_platforms,
                            include_opportunities=include_opportunities,
                            include_jurisdiction=include_jurisdiction,
                        )
                        
                        # Display results
                        display_market_intelligence_results(result, countries)
                        
                        # Generate and provide PDF download
                        try:
                            from src.utils.pdf_report_generator import MarketIntelligencePDFGenerator
                            
                            pdf_generator = MarketIntelligencePDFGenerator()
                            pdf_bytes = pdf_generator.generate_report(result, countries)
                            
                            # Add download button
                            st.markdown("---")
                            st.markdown("### 📄 Download Report")
                            
                            filename = f"market_intelligence_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                            st.download_button(
                                label="📥 Download Report (PDF)",
                                data=pdf_bytes,
                                file_name=filename,
                                mime="application/pdf",
                                type="primary",
                                use_container_width=True,
                            )
                        except ImportError as e:
                            logger.warning(f"PDF generation not available: {e}")
                            st.info("💡 Install reportlab to enable PDF report generation: `pip install reportlab`")
                        except Exception as e:
                            logger.error(f"Error generating PDF: {e}")
                            st.warning(f"⚠️ Could not generate PDF report: {str(e)}")
                        
                    except Exception as e:
                        st.error(f"❌ Error analyzing markets: {str(e)}")
                        logger.error(f"Error in market intelligence: {e}", exc_info=True)

        elif analyze_button and not countries_input:
            st.warning("⚠️ Please enter countries to analyze first!")

    with tab4:
        st.markdown("## 📚 Knowledge Base")
        st.info(
            """
            **Knowledge Base** - Upload documents to enhance AI responses.
            
            Similar to ChatGPT's knowledge base feature:
            - Upload PDF, TXT, MD files
            - Documents are automatically indexed and searchable
            - AI agents will automatically use relevant documents in their responses
            - Documents persist across sessions
            """
        )

        # Knowledge base stats
        try:
            from src.utils.knowledge_base import KnowledgeBaseManager
            
            try:
                kb_manager = KnowledgeBaseManager()
                stats = kb_manager.get_stats()
                documents = kb_manager.list_documents()
            except ImportError as e:
                st.error(f"❌ Knowledge Base dependencies not installed: {str(e)}")
                st.info(
                    """
                    **To enable Knowledge Base feature, install required packages:**
                    
                    ```bash
                    pip install langchain-openai chromadb pypdf
                    ```
                    
                    Or install all dependencies:
                    ```bash
                    pip install -r requirements.txt
                    ```
                    """
                )
                st.stop()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Documents", stats["total_documents"])
            with col2:
                st.metric("Total Size", f"{stats['total_size_mb']} MB")
            with col3:
                st.metric("Storage Location", "knowledge_base/")
            
            st.markdown("---")
            
            # Upload section
            st.markdown("### 📤 Upload Document")
            uploaded_file = st.file_uploader(
                "Choose a file to upload",
                type=["pdf", "txt", "md"],
                help="Supported formats: PDF, TXT, MD. Documents will be automatically indexed."
            )
            
            if uploaded_file is not None:
                # Save uploaded file temporarily
                import tempfile
                import os
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name
                
                # Upload button
                if st.button("📤 Upload to Knowledge Base", type="primary"):
                    with st.spinner("🔄 Uploading and indexing document..."):
                        try:
                            result = kb_manager.add_document(
                                tmp_path,
                                metadata={
                                    "uploaded_by": "user",
                                    "original_filename": uploaded_file.name,
                                }
                            )
                            
                            if result["success"]:
                                st.success(f"✅ {result['message']}")
                                st.info(f"📄 Document indexed with {result['chunk_count']} chunks")
                                
                                # Refresh stats
                                st.rerun()
                            else:
                                st.error(f"❌ {result['message']}")
                                
                        except Exception as e:
                            st.error(f"❌ Error uploading document: {str(e)}")
                            logger.error(f"Error uploading document: {e}", exc_info=True)
                        finally:
                            # Clean up temp file
                            if os.path.exists(tmp_path):
                                os.remove(tmp_path)
            
            st.markdown("---")
            
            # List documents
            st.markdown("### 📋 Uploaded Documents")
            if documents:
                for i, doc in enumerate(documents, 1):
                    with st.expander(f"📄 {doc.get('file_name', 'Unknown')} - {doc.get('chunk_count', 0)} chunks"):
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"**File:** {doc.get('file_name', 'Unknown')}")
                            st.write(f"**Uploaded:** {doc.get('upload_date', 'Unknown')}")
                            st.write(f"**Size:** {doc.get('file_size', 0) / 1024:.2f} KB")
                            st.write(f"**Chunks:** {doc.get('chunk_count', 0)}")
                        with col2:
                            file_hash = doc.get('file_hash')
                            if file_hash and st.button("🗑️ Delete", key=f"delete_{file_hash}"):
                                with st.spinner("Deleting..."):
                                    delete_result = kb_manager.delete_document(file_hash)
                                    if delete_result["success"]:
                                        st.success("✅ Document deleted")
                                        st.rerun()
                                    else:
                                        st.error(f"❌ {delete_result['message']}")
            else:
                st.info("📭 No documents uploaded yet. Upload a document to get started!")
            
            st.markdown("---")
            
            # Test search
            st.markdown("### 🔍 Test Knowledge Base Search")
            test_query = st.text_input(
                "Enter a test query:",
                placeholder="Example: What are the key features?",
                help="Test how the knowledge base retrieves relevant information"
            )
            
            if test_query and st.button("🔍 Search", type="primary"):
                with st.spinner("Searching knowledge base..."):
                    try:
                        results = kb_manager.search(test_query, k=5)
                        
                        if results:
                            st.success(f"✅ Found {len(results)} relevant chunks")
                            for i, result in enumerate(results, 1):
                                with st.expander(f"Result {i} (Score: {result['score']:.4f})"):
                                    st.write(f"**Source:** {result['metadata'].get('file_name', 'Unknown')}")
                                    st.write("**Content:**")
                                    st.write(result['content'][:500] + "..." if len(result['content']) > 500 else result['content'])
                        else:
                            st.info("📭 No relevant documents found for this query.")
                            
                    except Exception as e:
                        st.error(f"❌ Error searching: {str(e)}")
                        logger.error(f"Error searching knowledge base: {e}", exc_info=True)
        
        except ImportError as e:
            st.error(f"❌ Knowledge Base dependencies not installed: {str(e)}")
            st.info(
                """
                **To enable Knowledge Base feature, install required packages:**
                
                ```bash
                    # Activate virtual environment first
                    source venv/bin/activate  # macOS/Linux
                    # or
                    venv\\Scripts\\activate    # Windows
                    
                    # Install all dependencies
                    pip install -r requirements.txt
                ```
                
                **Or install only Knowledge Base dependencies:**
                ```bash
                    pip install langchain langchain-text-splitters langchain-openai langchain-community chromadb pypdf
                ```
                
                **After installation, restart Streamlit:**
                ```bash
                    ./run_webapp.sh
                ```
                """
            )
        except Exception as e:
            st.error(f"❌ Error initializing knowledge base: {str(e)}")
            logger.error(f"Error in knowledge base tab: {e}", exc_info=True)
            st.info("💡 Make sure OPENAI_API_KEY is set in your environment variables.")

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>Built with ❤️ using LangGraph & Streamlit</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
