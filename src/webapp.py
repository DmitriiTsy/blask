"""Streamlit web application for Blask."""

import base64
import io
import sys
from io import BytesIO
from pathlib import Path

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
            - 📊 Analysis Node (data processing & visualization)
            """
        )

    # Tabs
    tab1, tab2 = st.tabs(["🔍 General Analysis", "🎯 Competitor Tracker"])

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

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>Built with ❤️ using LangGraph & Streamlit</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
