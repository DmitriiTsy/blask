"""Streamlit web application for Blask."""

import base64
import io
import sys
from io import BytesIO
from pathlib import Path

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
            - 📊 Analysis Node (data processing & visualization)
            """
        )

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

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>Built with ❤️ using LangGraph & Streamlit</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
