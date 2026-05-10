"""
ChromaDB client for vector embedding and RAG pipeline.
AI Developer 2 responsibility.
"""

import logging
import os
from typing import List, Dict, Any, Optional
import chromadb
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class ChromaClient:
    """
    ChromaDB wrapper for semantic search and RAG.
    Features:
    - Persistent collection storage
    - Sentence-transformers embeddings
    - Query and insert operations
    - Metadata tracking
    """

    def __init__(
        self,
        collection_name: str = "compliance_docs",
        embedding_model: str = "all-MiniLM-L6-v2",
        persist_dir: str = "./chroma_data",
    ):
        self.collection_name = collection_name
        self.persist_dir = persist_dir
        self.embedding_model_name = embedding_model

        # Create persistent client
        try:
            self.client = chromadb.PersistentClient(path=persist_dir)
            logger.info(f"ChromaDB client initialized with persist_dir: {persist_dir}")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise

        # Load embedding model
        try:
            self.embedding_model = SentenceTransformer(embedding_model)
            logger.info(f"Loaded embedding model: {embedding_model}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise

        # Get or create collection
        try:
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"},
            )
            logger.info(f"Collection '{collection_name}' ready")
        except Exception as e:
            logger.error(f"Failed to initialize collection: {e}")
            raise

    def add_documents(
        self, texts: List[str], metadatas: Optional[List[Dict]] = None
    ) -> bool:
        """
        Add documents to ChromaDB collection.

        Args:
            texts: List of document texts
            metadatas: Optional list of metadata dicts

        Returns:
            True if successful
        """
        try:
            if not metadatas:
                metadatas = [{"source": "uploaded"} for _ in texts]

            # Generate IDs
            ids = [f"doc_{i}_{hash(texts[i]) % 10000}" for i in range(len(texts))]

            self.collection.add(
                documents=texts,
                metadatas=metadatas,
                ids=ids,
            )
            logger.info(f"Added {len(texts)} documents to collection")
            return True

        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            return False

    def query(
        self, query_text: str, top_k: int = 3
    ) -> Dict[str, Any]:
        """
        Query the collection with semantic search.

        Args:
            query_text: Query string
            top_k: Number of results to return

        Returns:
            {
                "success": bool,
                "results": [
                    {
                        "text": str,
                        "distance": float (0-1, lower is better),
                        "metadata": dict
                    }
                ],
                "doc_count": int
            }
        """
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=top_k,
            )

            # Parse results
            documents = results["documents"][0] if results["documents"] else []
            distances = results["distances"][0] if results["distances"] else []
            metadatas = results["metadatas"][0] if results["metadatas"] else []

            parsed_results = [
                {
                    "text": doc,
                    "distance": float(dist),
                    "metadata": meta,
                }
                for doc, dist, meta in zip(documents, distances, metadatas)
            ]

            doc_count = self.collection.count()

            logger.info(f"Query returned {len(parsed_results)} results")

            return {
                "success": True,
                "results": parsed_results,
                "doc_count": doc_count,
            }

        except Exception as e:
            logger.error(f"Query failed: {e}")
            return {
                "success": False,
                "results": [],
                "doc_count": 0,
            }

    def get_doc_count(self) -> int:
        """Get total document count in collection."""
        try:
            return self.collection.count()
        except Exception as e:
            logger.error(f"Failed to get doc count: {e}")
            return 0

    def seed_documents(self) -> bool:
        """
        Seed collection with compliance training documents.
        Called on startup for demo.
        """
        if self.get_doc_count() > 0:
            logger.info("Collection already seeded, skipping...")
            return True

        compliance_docs = [
            "GDPR requires explicit consent before processing personal data. Organizations must implement data protection impact assessments and maintain detailed records of processing activities.",
            "ISO 27001 is an international standard for information security management. It requires organizations to identify risks, implement controls, and regularly audit compliance.",
            "HIPAA compliance ensures patient privacy in healthcare. PHI must be encrypted, access logs maintained, and breach notifications issued within 60 days.",
            "SOX compliance for financial reporting requires internal control assessments. Management must certify financial statements and IT controls must be documented.",
            "PCI-DSS standard protects credit card data. It mandates encryption, access controls, regular security testing, and incident response procedures.",
            "CCPA gives California residents data rights including access, deletion, and opt-out from sales. Organizations must disclose data practices clearly.",
            "FERPA protects student education records. Schools must get written consent before disclosing information and allow parents/students access to records.",
            "ADA compliance requires organizations to provide equal access to services. Digital accessibility, reasonable accommodations, and non-discrimination policies are essential.",
            "Export controls require compliance for goods and data moving internationally. Sanctions screening and license requirements must be verified.",
            "Anti-bribery laws like FCPA prohibit paying foreign officials. Organizations must implement controls, train employees, and audit third-party relationships.",
        ]

        metadatas = [
            {"category": "Data Privacy", "priority": "High"},
            {"category": "Security", "priority": "High"},
            {"category": "Healthcare", "priority": "Critical"},
            {"category": "Financial", "priority": "Critical"},
            {"category": "Security", "priority": "High"},
            {"category": "Data Privacy", "priority": "High"},
            {"category": "Education", "priority": "High"},
            {"category": "Accessibility", "priority": "Medium"},
            {"category": "Trade", "priority": "Medium"},
            {"category": "Ethics", "priority": "High"},
        ]

        return self.add_documents(compliance_docs, metadatas)
