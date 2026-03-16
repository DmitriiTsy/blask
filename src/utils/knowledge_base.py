"""Knowledge Base Manager for document storage and retrieval (RAG)."""

import os
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Try multiple import paths for OpenAIEmbeddings
OpenAIEmbeddings = None
try:
    from langchain_openai import OpenAIEmbeddings
except ImportError:
    try:
        from langchain_community.embeddings import OpenAIEmbeddings
    except ImportError:
        try:
            from langchain.embeddings import OpenAIEmbeddings
        except ImportError:
            OpenAIEmbeddings = None

# Try multiple import paths for Chroma
Chroma = None
try:
    # New recommended package (LangChain 0.2.9+)
    from langchain_chroma import Chroma
except ImportError:
    try:
        from langchain_community.vectorstores import Chroma
    except ImportError:
        try:
            from langchain.vectorstores import Chroma
        except ImportError:
            Chroma = None

# Try multiple import paths for text splitter
RecursiveCharacterTextSplitter = None
try:
    # New LangChain versions (0.1+) - separate package
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    try:
        # Most common path in newer LangChain versions
        from langchain.text_splitters import RecursiveCharacterTextSplitter
    except ImportError:
        try:
            # Older LangChain versions
            from langchain.text_splitter import RecursiveCharacterTextSplitter
        except ImportError:
            try:
                # Community package
                from langchain_community.text_splitter import RecursiveCharacterTextSplitter
            except ImportError:
                try:
                    # Core package
                    from langchain_core.text_splitter import RecursiveCharacterTextSplitter
                except ImportError:
                    RecursiveCharacterTextSplitter = None

# Try multiple import paths for document loaders
PyPDFLoader = None
TextLoader = None
UnstructuredMarkdownLoader = None

try:
    from langchain_community.document_loaders import (
        PyPDFLoader,
        TextLoader,
        UnstructuredMarkdownLoader,
    )
except ImportError:
    try:
        from langchain.document_loaders import (
            PyPDFLoader,
            TextLoader,
            UnstructuredMarkdownLoader,
        )
    except ImportError:
        # Try individual imports
        try:
            from langchain_community.document_loaders import PyPDFLoader
        except ImportError:
            try:
                from langchain.document_loaders import PyPDFLoader
            except ImportError:
                PyPDFLoader = None
        
        try:
            from langchain_community.document_loaders import TextLoader
        except ImportError:
            try:
                from langchain.document_loaders import TextLoader
            except ImportError:
                TextLoader = None
        
        try:
            from langchain_community.document_loaders import UnstructuredMarkdownLoader
        except ImportError:
            try:
                from langchain.document_loaders import UnstructuredMarkdownLoader
            except ImportError:
                UnstructuredMarkdownLoader = None

from ..config import get_settings
from ..utils.logging import get_logger

logger = get_logger(__name__)


class KnowledgeBaseManager:
    """
    Manages knowledge base with vector store for RAG (Retrieval-Augmented Generation).
    
    Similar to ChatGPT's knowledge base:
    - Upload documents
    - Store in vector database
    - Automatically retrieve relevant context for queries
    - Persistent storage
    """

    def __init__(self, persist_directory: Optional[str] = None):
        """
        Initialize Knowledge Base Manager.

        Args:
            persist_directory: Directory to persist vector store (default: ./knowledge_base)
        """
        settings = get_settings()

        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required for KnowledgeBaseManager")

        # Set up persistence directory
        if persist_directory is None:
            persist_directory = os.path.join(os.getcwd(), "knowledge_base")
        
        self.persist_directory = persist_directory
        Path(self.persist_directory).mkdir(parents=True, exist_ok=True)

        # Set up document storage
        self.documents_dir = os.path.join(self.persist_directory, "documents")
        Path(self.documents_dir).mkdir(parents=True, exist_ok=True)

        # Initialize embeddings
        if OpenAIEmbeddings is None:
            raise ImportError(
                "OpenAIEmbeddings not available. "
                "Install one of: langchain-openai, langchain-community, or langchain. "
                "Try: pip install langchain-openai"
            )
        
        # Initialize embeddings with proper parameters
        try:
            # Try with model parameter (newer versions)
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=settings.openai_api_key,
                model="text-embedding-3-small",
            )
        except TypeError:
            # Fallback for older versions that don't support model parameter
            try:
                self.embeddings = OpenAIEmbeddings(
                    openai_api_key=settings.openai_api_key,
                )
            except Exception as e:
                # Try without explicit api_key (might use env var)
                try:
                    self.embeddings = OpenAIEmbeddings()
                except Exception as e2:
                    raise ImportError(
                        f"Failed to initialize OpenAIEmbeddings: {e}. "
                        f"Also tried: {e2}. "
                        "Make sure OPENAI_API_KEY is set in environment or .env file."
                    )

        # Initialize text splitter
        if RecursiveCharacterTextSplitter is None:
            raise ImportError(
                "RecursiveCharacterTextSplitter not available. "
                "Install langchain package: pip install langchain"
            )
        
        try:
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
            )
        except Exception as e:
            raise ImportError(
                f"Failed to initialize RecursiveCharacterTextSplitter: {e}. "
                "Make sure langchain is properly installed: pip install langchain"
            )

        # Initialize vector store
        self.vector_store = None
        self._load_or_create_vector_store()

        # Track uploaded documents
        self.documents_metadata_file = os.path.join(self.persist_directory, "documents_metadata.json")
        self.documents_metadata = self._load_metadata()

    def _load_or_create_vector_store(self):
        """Load existing vector store or create new one."""
        try:
            if Chroma:
                # Try to load existing vector store
                if os.path.exists(os.path.join(self.persist_directory, "chroma.sqlite3")):
                    logger.info("Loading existing vector store...")
                    self.vector_store = Chroma(
                        persist_directory=self.persist_directory,
                        embedding_function=self.embeddings,
                    )
                else:
                    logger.info("Creating new vector store...")
                    self.vector_store = Chroma(
                        persist_directory=self.persist_directory,
                        embedding_function=self.embeddings,
                    )
            else:
                raise ImportError("Chroma not available. Install chromadb.")
        except Exception as e:
            logger.error(f"Error loading vector store: {e}")
            raise

    def _load_metadata(self) -> Dict[str, Any]:
        """Load documents metadata."""
        import json
        if os.path.exists(self.documents_metadata_file):
            try:
                with open(self.documents_metadata_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading metadata: {e}")
                return {}
        return {}

    def _save_metadata(self):
        """Save documents metadata."""
        import json
        try:
            with open(self.documents_metadata_file, "w", encoding="utf-8") as f:
                json.dump(self.documents_metadata, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving metadata: {e}")

    def _get_file_hash(self, file_path: str) -> str:
        """Calculate file hash for deduplication."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def _load_document(self, file_path: str) -> List[Any]:
        """
        Load document based on file type.
        
        Args:
            file_path: Path to document file
        
        Returns:
            List of Document objects
        """
        file_ext = Path(file_path).suffix.lower()

        if file_ext == ".pdf":
            if not PyPDFLoader:
                raise ImportError("PyPDFLoader not available. Install pypdf.")
            loader = PyPDFLoader(file_path)
        elif file_ext in [".txt", ".md"]:
            if file_ext == ".md":
                if UnstructuredMarkdownLoader:
                    loader = UnstructuredMarkdownLoader(file_path)
                else:
                    # Fallback to TextLoader
                    loader = TextLoader(file_path, encoding="utf-8")
            else:
                if not TextLoader:
                    raise ImportError("TextLoader not available.")
                loader = TextLoader(file_path, encoding="utf-8")
        else:
            # Try text loader as fallback
            if not TextLoader:
                raise ImportError(f"Unsupported file type: {file_ext}")
            loader = TextLoader(file_path, encoding="utf-8")

        try:
            documents = loader.load()
            logger.info(f"Loaded {len(documents)} pages/chunks from {file_path}")
            return documents
        except Exception as e:
            logger.error(f"Error loading document {file_path}: {e}")
            raise

    def add_document(
        self,
        file_path: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Add document to knowledge base.
        
        Args:
            file_path: Path to document file
            metadata: Optional metadata (title, description, etc.)
        
        Returns:
            Dictionary with upload result
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            # Calculate file hash
            file_hash = self._get_file_hash(file_path)
            
            # Check for duplicates
            if file_hash in self.documents_metadata:
                logger.warning(f"Document already exists: {file_path}")
                return {
                    "success": False,
                    "message": "Document already exists in knowledge base",
                    "file_hash": file_hash,
                }

            # Load document
            documents = self._load_document(file_path)

            # Split into chunks
            chunks = self.text_splitter.split_documents(documents)

            # Prepare metadata
            file_name = Path(file_path).name
            doc_metadata = {
                "file_path": file_path,
                "file_name": file_name,
                "file_hash": file_hash,
                "upload_date": datetime.now().isoformat(),
                "chunk_count": len(chunks),
                "file_size": os.path.getsize(file_path),
            }
            if metadata:
                doc_metadata.update(metadata)

            # Add to vector store
            if self.vector_store:
                # Add metadata to each chunk
                for i, chunk in enumerate(chunks):
                    chunk.metadata.update({
                        **doc_metadata,
                        "chunk_index": i,
                    })

                self.vector_store.add_documents(chunks)
                self.vector_store.persist()

            # Save document copy
            saved_path = os.path.join(self.documents_dir, file_name)
            import shutil
            shutil.copy2(file_path, saved_path)
            doc_metadata["saved_path"] = saved_path

            # Update metadata
            self.documents_metadata[file_hash] = doc_metadata
            self._save_metadata()

            logger.info(f"Successfully added document: {file_name} ({len(chunks)} chunks)")

            return {
                "success": True,
                "message": f"Document added successfully: {file_name}",
                "file_hash": file_hash,
                "chunk_count": len(chunks),
                "metadata": doc_metadata,
            }

        except Exception as e:
            logger.error(f"Error adding document: {e}")
            return {
                "success": False,
                "message": f"Error adding document: {str(e)}",
                "error": str(e),
            }

    def search(
        self,
        query: str,
        k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search knowledge base for relevant documents.
        
        Args:
            query: Search query
            k: Number of results to return
            filter_metadata: Optional metadata filters
        
        Returns:
            List of relevant document chunks with scores
        """
        if not self.vector_store:
            logger.warning("Vector store not initialized")
            return []

        try:
            # Search with similarity search
            if filter_metadata:
                results = self.vector_store.similarity_search_with_score(
                    query,
                    k=k,
                    filter=filter_metadata,
                )
            else:
                results = self.vector_store.similarity_search_with_score(query, k=k)

            # Format results
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": float(score),
                })

            logger.info(f"Found {len(formatted_results)} relevant chunks for query: {query[:50]}...")
            return formatted_results

        except Exception as e:
            logger.error(f"Error searching knowledge base: {e}")
            return []

    def get_relevant_context(
        self,
        query: str,
        max_chunks: int = 5,
        min_score: float = 0.0,
    ) -> str:
        """
        Get relevant context from knowledge base for a query.
        
        Args:
            query: Query string
            max_chunks: Maximum number of chunks to include
            min_score: Minimum similarity score (0-1, lower is better for distance)
        
        Returns:
            Formatted context string
        """
        results = self.search(query, k=max_chunks)

        if not results:
            return ""

        # Filter by score (for distance-based scores, lower is better)
        # For cosine similarity, we might need to adjust this
        filtered_results = [
            r for r in results
            if r["score"] >= min_score or r["score"] <= (1 - min_score)  # Handle both distance and similarity
        ]

        if not filtered_results:
            return ""

        # Format context
        context_parts = []
        for i, result in enumerate(filtered_results, 1):
            content = result["content"]
            metadata = result["metadata"]
            file_name = metadata.get("file_name", "Unknown")
            
            context_parts.append(
                f"[Document: {file_name}]\n{content}\n"
            )

        context = "\n---\n".join(context_parts)
        return context

    def list_documents(self) -> List[Dict[str, Any]]:
        """List all documents in knowledge base."""
        return list(self.documents_metadata.values())

    def delete_document(self, file_hash: str) -> Dict[str, Any]:
        """
        Delete document from knowledge base.
        
        Args:
            file_hash: Hash of document to delete
        
        Returns:
            Deletion result
        """
        if file_hash not in self.documents_metadata:
            return {
                "success": False,
                "message": "Document not found",
            }

        try:
            # Remove from metadata
            metadata = self.documents_metadata.pop(file_hash)
            
            # Delete saved file
            if "saved_path" in metadata and os.path.exists(metadata["saved_path"]):
                os.remove(metadata["saved_path"])

            # Note: ChromaDB doesn't have a simple delete by metadata
            # We would need to implement a more complex deletion strategy
            # For now, we'll just remove from metadata
            # In production, you might want to rebuild the vector store

            self._save_metadata()

            logger.info(f"Deleted document: {metadata.get('file_name', 'Unknown')}")

            return {
                "success": True,
                "message": "Document deleted successfully",
            }

        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            return {
                "success": False,
                "message": f"Error deleting document: {str(e)}",
            }

    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics."""
        total_documents = len(self.documents_metadata)
        total_size = sum(
            doc.get("file_size", 0) for doc in self.documents_metadata.values()
        )

        return {
            "total_documents": total_documents,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "persist_directory": self.persist_directory,
        }
