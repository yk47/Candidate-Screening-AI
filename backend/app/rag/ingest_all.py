"""Helper script to ingest all documents under data/knowledge_base by role.

Usage:
    python -m app.rag.ingest_all

This will walk `backend/data/knowledge_base/*` and ingest PDFs and TXT files
for each role into the role-specific Chroma collection.
"""

import os
from pathlib import Path
from .ingest import KnowledgeBaseIngester


def ingest_all(base_dir: str = None):
    base = Path(base_dir or os.getenv("KNOWLEDGE_BASE_PATH", "./data/knowledge_base"))
    if not base.exists():
        print(f"Knowledge base directory not found: {base}")
        return

    ingester = KnowledgeBaseIngester()

    for role_dir in sorted(base.iterdir()):
        if not role_dir.is_dir():
            continue
        role = role_dir.name
        print(f"Ingesting role: {role} from {role_dir}")

        # Ingest PDFs
        pdf_stats = ingester.ingest_from_directory(role, str(role_dir), file_type="pdf")
        print("  PDF ingestion:", pdf_stats)

        # Ingest TXT files
        txt_stats = ingester.ingest_from_directory(role, str(role_dir), file_type="txt")
        print("  TXT ingestion:", txt_stats)


if __name__ == "__main__":
    ingest_all()
