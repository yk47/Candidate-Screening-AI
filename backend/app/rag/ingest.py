"""Knowledge base ingestion and document processing."""

import os
import PyPDF2
from typing import List, Dict
from pathlib import Path


class DocumentProcessor:
    """Process and chunk documents for RAG."""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """Initialize document processor."""
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_text(self, text: str, source: str = "unknown") -> List[Dict]:
        """Chunk text into overlapping segments."""
        chunks: List[Dict] = []
        paragraphs = text.split("\n\n")
        current_chunk = ""
        chunk_id = 0
        
        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) < self.chunk_size:
                current_chunk += paragraph + "\n\n"
            else:
                if current_chunk:
                    chunks.append({
                        "content": current_chunk.strip(),
                        "metadata": {
                            "source": source,
                            "chunk_id": chunk_id,
                            "chunk_size": len(current_chunk)
                        }
                    })
                    chunk_id += 1
                    current_chunk = current_chunk[-self.chunk_overlap:] + paragraph
                else:
                    current_chunk = paragraph
        
        if current_chunk:
            chunks.append({
                "content": current_chunk.strip(),
                "metadata": {
                    "source": source,
                    "chunk_id": chunk_id,
                    "chunk_size": len(current_chunk)
                }
            })
        
        return chunks
    
    def process_pdf(self, pdf_path: str) -> List[Dict]:
        """Extract and chunk text from PDF."""
        text = ""
        try:
            with open(pdf_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    page_text = page.extract_text() or ""
                    text += page_text + "\n"
        except Exception as e:
            raise Exception(f"Error processing PDF: {str(e)}")
        return self.chunk_text(text, source=Path(pdf_path).name)
    
    def process_text(self, text: str, source: str = "text_input") -> List[Dict]:
        """Process plain text."""
        return self.chunk_text(text, source=source)


class KnowledgeBaseIngester:
    """Manage knowledge base ingestion for different roles."""
    
    def __init__(self):
        self.processor = DocumentProcessor()
        self._vector_store_cls = None  # Lazy loaded
        self.vector_stores = {}
    
    def _get_vector_store_cls(self):
        """Lazy import VectorStore class."""
        if self._vector_store_cls is None:
            from .vectorstore import VectorStore
            self._vector_store_cls = VectorStore
        return self._vector_store_cls
    
    def normalize_role(self, role: str) -> str:
        """Normalize role name for display."""
        return role.strip().replace("_", " ").title()
    
    def sanitize_collection_name(self, role: str) -> str:
        """Sanitize role name for use in collection name (alphanumeric, dots, underscores, hyphens only)."""
        import re
        # Replace special characters with underscores, then remove any remaining invalid characters
        sanitized = re.sub(r'[^a-zA-Z0-9._-]', '_', role.lower().strip())
        # Remove leading/trailing underscores
        sanitized = sanitized.strip('_')
        return sanitized
    
    def get_or_create_store(self, role: str):
        role_key = self.normalize_role(role)
        if role_key not in self.vector_stores:
            VectorStore = self._get_vector_store_cls()
            sanitized_name = self.sanitize_collection_name(role)
            self.vector_stores[role_key] = VectorStore(
                collection_name=f"knowledge_{sanitized_name}"
            )
        return self.vector_stores[role_key]
    
    def ingest_documents(self, role: str, documents: List[Dict]) -> Dict:
        store = self.get_or_create_store(role)
        all_chunks: List[Dict] = []
        
        for doc in documents:
            if "path" in doc:
                chunks = self.processor.process_pdf(doc["path"])
                all_chunks.extend(chunks)
            elif "content" in doc:
                chunks = self.processor.process_text(
                    doc["content"],
                    source=doc.get("source", "text_input")
                )
                all_chunks.extend(chunks)
        
        document_ids = store.add_documents(all_chunks, collection_role=self.normalize_role(role))
        return {
            "role": self.normalize_role(role),
            "documents_ingested": len(documents),
            "chunks_created": len(all_chunks),
            "ids_created": document_ids,
            "status": "success"
        }
    
    def ingest_role_directory(self, role: str, directory: str, file_types: List[str] = None) -> Dict:
        if file_types is None:
            file_types = ["pdf", "txt"]
        directory_path = Path(directory)
        if not directory_path.exists() or not directory_path.is_dir():
            return {
                "role": self.normalize_role(role),
                "status": "error",
                "message": f"Directory not found: {directory}"
            }
        
        documents: List[Dict] = []
        for file_type in file_types:
            for file_path in directory_path.glob(f"*.{file_type}"):
                documents.append({"path": str(file_path)})
        
        if not documents:
            return {
                "role": self.normalize_role(role),
                "status": "error",
                "message": f"No supported files found in {directory}"
            }
        
        return self.ingest_documents(role, documents)
    
    def ingest_all_roles(self, base_directory: str) -> Dict:
        base_path = Path(base_directory)
        if not base_path.exists() or not base_path.is_dir():
            return {
                "status": "error",
                "message": f"Knowledge base path not found: {base_directory}"
            }
        
        # Check if any vectorstore already has documents (skip if already ingested)
        from .vectorstore import VectorStore
        test_store = VectorStore(collection_name="knowledge_test")
        try:
            # Try to search for any documents - if this succeeds with non-empty results,
            # vectorstore is already populated
            results = test_store.search("test", k=1)
            if results and len(results) > 0:
                return {
                    "base_directory": str(base_path),
                    "status": "skipped",
                    "message": "Knowledge base already ingested. Skipping re-ingestion."
                }
        except Exception:
            pass  # Continue with ingestion if search fails
        
        results: Dict[str, Dict] = {}
        for role_path in sorted(base_path.iterdir()):
            if role_path.is_dir():
                role_name = self.normalize_role(role_path.name)
                results[role_name] = self.ingest_role_directory(role_name, str(role_path))
        
        if not results:
            general_role = "General"
            results[general_role] = self.ingest_role_directory(general_role, str(base_path))
        
        return {
            "base_directory": str(base_path),
            "roles_ingested": list(results.keys()),
            "results": results,
            "status": "completed"
        }
