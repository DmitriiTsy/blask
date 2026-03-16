"""Tools for knowledge base operations (SOLID principles)."""

from typing import Any, Dict, List, Optional
from langchain.tools import tool

from ..utils.knowledge_base import KnowledgeBaseManager
from ..utils.logging import get_logger

logger = get_logger(__name__)

# Global knowledge base manager instance
_kb_manager: Optional[KnowledgeBaseManager] = None


def get_knowledge_base_manager() -> Optional[KnowledgeBaseManager]:
    """Get or create knowledge base manager instance."""
    global _kb_manager
    if _kb_manager is None:
        try:
            _kb_manager = KnowledgeBaseManager()
        except (ImportError, ValueError) as e:
            logger.warning(f"Knowledge Base not available: {e}")
            return None
    return _kb_manager


@tool
def search_knowledge_base(
    query: str,
    max_results: int = 5,
) -> Dict[str, Any]:
    """
    Search the knowledge base for relevant information.
    
    This tool automatically searches uploaded documents to find relevant context
    for answering queries. Similar to ChatGPT's knowledge base feature.
    
    Args:
        query: Search query
        max_results: Maximum number of results to return
    
    Returns:
        Dictionary with search results:
        {
            "results": List[Dict],  # List of relevant document chunks
            "count": int,  # Number of results
            "query": str  # Original query
        }
    """
    try:
        kb_manager = get_knowledge_base_manager()
        if kb_manager is None:
            return {
                "results": [],
                "count": 0,
                "query": query,
                "error": "Knowledge Base not available. Install dependencies: pip install langchain-openai chromadb pypdf",
            }
        results = kb_manager.search(query, k=max_results)

        logger.info(f"Knowledge base search: '{query}' -> {len(results)} results")

        return {
            "results": results,
            "count": len(results),
            "query": query,
        }
    except Exception as e:
        logger.error(f"Error searching knowledge base: {e}")
        return {
            "results": [],
            "count": 0,
            "query": query,
            "error": str(e),
        }


@tool
def get_knowledge_base_context(
    query: str,
    max_chunks: int = 5,
) -> str:
    """
    Get relevant context from knowledge base formatted for LLM.
    
    This tool retrieves and formats relevant document chunks as context
    that can be used in LLM prompts. Automatically used by agents.
    
    Args:
        query: Query to find relevant context for
        max_chunks: Maximum number of chunks to include
    
    Returns:
        Formatted context string with relevant document excerpts
    """
    try:
        kb_manager = get_knowledge_base_manager()
        if kb_manager is None:
            return ""
        context = kb_manager.get_relevant_context(query, max_chunks=max_chunks)

        if context:
            logger.info(f"Retrieved {max_chunks} chunks of context for query: {query[:50]}...")
        else:
            logger.info(f"No relevant context found for query: {query[:50]}...")

        return context
    except Exception as e:
        logger.error(f"Error getting knowledge base context: {e}")
        return ""


@tool
def list_knowledge_base_documents() -> Dict[str, Any]:
    """
    List all documents in the knowledge base.
    
    Returns:
        Dictionary with list of documents and metadata
    """
    try:
        kb_manager = get_knowledge_base_manager()
        if kb_manager is None:
            return {
                "documents": [],
                "count": 0,
                "error": "Knowledge Base not available. Install dependencies: pip install langchain-openai chromadb pypdf",
            }
        documents = kb_manager.list_documents()
        stats = kb_manager.get_stats()

        return {
            "documents": documents,
            "stats": stats,
            "count": len(documents),
        }
    except Exception as e:
        logger.error(f"Error listing knowledge base documents: {e}")
        return {
            "documents": [],
            "count": 0,
            "error": str(e),
        }
