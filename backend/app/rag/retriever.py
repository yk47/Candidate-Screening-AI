"""Retrieval module for RAG pipeline."""

from typing import List, Dict, Optional


class RAGRetriever:
    """Retrieve relevant context for question generation."""
    
    def __init__(self):
        """Initialize retriever."""
        # Lazy import to avoid loading heavy dependencies (chromadb, sentence-transformers) at startup
        from .ingest import KnowledgeBaseIngester
        self.ingester = KnowledgeBaseIngester()
    
    def retrieve_context(self, role: str, query: str, k: int = 5) -> Dict:
        """Retrieve relevant context for a query.
        
        Args:
            role: Job role
            query: Search query (typically based on resume + topic)
            k: Number of results to return
            
        Returns:
            Retrieved context with metadata
        """
        store = self.ingester.get_or_create_store(role)
        
        results = store.search(query, k=k, role=role)
        
        return {
            "query": query,
            "role": role,
            "results_count": len(results),
            "results": results,
            "context": "\n\n".join([r["content"] for r in results])
        }
    
    def retrieve_for_topics(self, role: str, topics: List[str], k: int = 3) -> Dict:
        """Retrieve context for multiple topics.
        
        Args:
            role: Job role
            topics: List of topics
            k: Results per topic
            
        Returns:
            Context organized by topic
        """
        context_by_topic = {}
        
        for topic in topics:
            retrieval = self.retrieve_context(role, topic, k=k)
            context_by_topic[topic] = retrieval
        
        return {
            "role": role,
            "topics_count": len(topics),
            "context_by_topic": context_by_topic
        }
    
    def enhance_query(self, resume_text: str, topic: str, role: str) -> str:
        """Create an enhanced query combining resume data and topic.
        
        Args:
            resume_text: Candidate's resume
            topic: Interview topic
            role: Job role
            
        Returns:
            Enhanced query string
        """
        # Extract key keywords from resume
        resume_keywords = []
        keywords_to_look_for = ["python", "java", "javascript", "react", "fastapi", 
                               "machine learning", "deep learning", "sql", "docker",
                               "kubernetes", "aws", "gcp", "azure"]
        
        resume_lower = resume_text.lower()
        for keyword in keywords_to_look_for:
            if keyword in resume_lower:
                resume_keywords.append(keyword)
        
        # Build enhanced query
        query_parts = [topic, role]
        if resume_keywords:
            query_parts.extend(resume_keywords[:3])  # Top 3 keywords
        
        return " ".join(query_parts)
    
    def get_store_stats(self, role: str) -> Dict:
        """Get statistics for a role's knowledge base.
        
        Args:
            role: Job role
            
        Returns:
            Store statistics
        """
        store = self.ingester.get_or_create_store(role)
        return store.get_stats()
