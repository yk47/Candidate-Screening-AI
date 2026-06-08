"""Vector store management for RAG."""

import os
import json
from typing import List, Dict, Optional
from pathlib import Path

try:
    from langchain_community.vectorstores import Chroma
except ImportError:
    Chroma = None

try:
    from langchain_openai import OpenAIEmbeddings
except ImportError:
    OpenAIEmbeddings = None

try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    HuggingFaceEmbeddings = None


# Global cache for embeddings to avoid reloading model multiple times
_embedding_cache = {}


class VectorStore:
    """Vector store wrapper for managing embeddings and retrieval."""
    
    def __init__(self, collection_name: str = "candidate_screening", embedding_type: str = "openai"):
        """Initialize vector store.
        
        Args:
            collection_name: Name of the collection
            embedding_type: Type of embeddings - 'openai' or 'huggingface'
        """
        self.collection_name = collection_name
        self.embedding_type = embedding_type
        self.persist_dir = os.getenv("VECTORSTORE_PATH", "./data/vectorstore")
        self._embeddings = None  # Lazy load
        self._store = None  # Lazy load
    
    @property
    def embeddings(self):
        """Lazy load embeddings on first access."""
        if self._embeddings is not None:
            return self._embeddings
        
        # Check cache first
        cache_key = f"{self.embedding_type}_embeddings"
        if cache_key in _embedding_cache:
            self._embeddings = _embedding_cache[cache_key]
            return self._embeddings
        
        # Initialize embeddings
        if self.embedding_type == "openai" and OpenAIEmbeddings is not None:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self._embeddings = OpenAIEmbeddings(openai_api_key=api_key)
            else:
                self._embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        elif HuggingFaceEmbeddings is not None:
            self._embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        else:
            raise RuntimeError("No embedding backend available. Install langchain and required embedding packages.")
        
        # Cache it
        _embedding_cache[cache_key] = self._embeddings
        return self._embeddings
    
    @property
    def store(self):
        """Lazy load Chroma store on first access."""
        if self._store is not None:
            return self._store
        
        if Chroma is None:
            raise RuntimeError("Chroma vector store is not available. Install the chromadb and langchain packages.")
        
        # Initialize Chroma store only when accessed
        Path(self.persist_dir).mkdir(parents=True, exist_ok=True)
        self._store = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.persist_dir
        )
        return self._store
    
    def add_documents(self, documents: List[Dict], collection_role: str = "general") -> List[str]:
        """Add documents to vector store.
        
        Args:
            documents: List of documents with 'content' and optional 'metadata'
            collection_role: Role or category for these documents
            
        Returns:
            List of document IDs
        """
        ids = []
        texts = []
        metadatas = []
        
        for i, doc in enumerate(documents):
            doc_id = f"{collection_role}_{i}_{hash(doc.get('content', '')) % 100000}"
            ids.append(doc_id)
            texts.append(doc.get("content", ""))
            
            metadata = doc.get("metadata", {})
            metadata["role"] = collection_role
            metadata["id"] = doc_id
            metadatas.append(metadata)
        
        self.store.add_texts(texts=texts, metadatas=metadatas, ids=ids)
        self.store.persist()
        
        return ids
    
    def search(self, query: str, k: int = 5, role: Optional[str] = None) -> List[Dict]:
        """Search for relevant documents.
        
        Args:
            query: Search query
            k: Number of results to return
            role: Filter by role if specified
            
        Returns:
            List of documents with scores
        """
        if role:
            docs = self.store.similarity_search_with_score(
                query,
                k=k,
                filter={"role": role}
            )
        else:
            docs = self.store.similarity_search_with_score(query, k=k)
        
        results = []
        for doc, score in docs:
            results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": float(score),
                "id": doc.metadata.get("id", "unknown")
            })
        
        return results
    
    def get_stats(self) -> Dict:
        """Get vector store statistics."""
        try:
            collection = self.store._collection
            count = collection.count()
            return {
                "total_documents": count,
                "collection_name": self.collection_name,
                "embedding_type": self.embedding_type,
                "persist_dir": self.persist_dir
            }
        except Exception as e:
            return {
                "error": str(e),
                "collection_name": self.collection_name
            }
