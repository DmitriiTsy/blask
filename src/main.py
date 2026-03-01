"""Main entry point for Blask application."""

import sys
from typing import Optional

from src.graph.graph import create_graph
from src.graph.state import create_initial_state
from src.utils.logging import get_logger

logger = get_logger(__name__)


def get_user_query() -> str:
    """
    Get user query from command line arguments or interactive input.

    Returns:
        User query string
    """
    # Check if query provided as command line argument
    if len(sys.argv) > 1:
        # Join all arguments as query (allows multi-word queries)
        query = " ".join(sys.argv[1:])
        logger.info(f"Query from command line: {query}")
        return query

    # Interactive input
    print("\n" + "=" * 50)
    print("Blask - Trend and Competitor Analysis")
    print("=" * 50)
    print("\nEnter your query (or press Enter for default example):")
    query = input("> ").strip()

    if not query:
        # Default example
        query = "What are the latest AI trends?"
        print(f"\nUsing default query: {query}")

    return query


def main():
    """Main function to run the graph."""
    logger.info("Starting Blask application")

    # Get user query
    user_query = get_user_query()

    # Create graph
    graph = create_graph()

    # Create initial state with user query
    initial_state = create_initial_state(user_query)

    try:
        # Execute graph
        logger.info(f"Processing query: {user_query}")
        result = graph.invoke(initial_state)

        logger.info("Graph execution completed")
        logger.info(f"Decision: {result.get('decision')}")
        logger.info(f"Execution path: {result.get('execution_path')}")

        if result.get("formatted_response"):
            print("\n" + "=" * 50)
            print("RESPONSE:")
            print("=" * 50)
            print(result["formatted_response"])

        if result.get("visualization"):
            print("\n" + "=" * 50)
            print("VISUALIZATION:")
            print("=" * 50)
            print("Chart created! (Base64 encoded image in state)")

        if result.get("error"):
            logger.error(f"Error occurred: {result['error']}")
            print(f"\n❌ Error: {result['error']}")

    except Exception as e:
        logger.error(f"Error executing graph: {e}")
        print(f"\n❌ Fatal error: {e}")
        raise


if __name__ == "__main__":
    main()
