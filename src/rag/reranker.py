"""
Cross-Encoder Reranker for improved relevance ranking
"""

import logging
from typing import List, Tuple, Optional
from langchain.schema import Document
from sentence_transformers import CrossEncoder
from config.settings import settings

logger = logging.getLogger(__name__)


class CrossEncoderReranker:
    """
    Cross-encoder based reranker for accurate relevance scoring
    """
    
    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize cross-encoder reranker
        
        Args:
            model_name: Model name (default from settings)
        """
        self.model_name = model_name or settings.rerank_model
        
        try:
            self.model = CrossEncoder(self.model_name)
            logger.info(f"Loaded reranker model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to load reranker model: {e}")
            self.model = None
    
    def rerank(
        self,
        query: str,
        documents: List[Document],
        top_k: int = 5
    ) -> List[Document]:
        """
        Rerank documents using cross-encoder
        
        Args:
            query: Search query
            documents: Documents to rerank
            top_k: Number of top documents to return
            
        Returns:
            Reranked documents
        """
        if not self.model or not documents:
            return documents[:top_k]
        
        try:
            # Prepare query-document pairs
            pairs = [[query, doc.page_content] for doc in documents]
            
            # Score all pairs
            scores = self.model.predict(pairs)
            
            # Sort by score (higher is better)
            doc_scores = list(zip(documents, scores))
            doc_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Add scores to metadata
            reranked = []
            for doc, score in doc_scores[:top_k]:
                doc_copy = Document(
                    page_content=doc.page_content,
                    metadata={**doc.metadata, "rerank_score": float(score)}
                )
                reranked.append(doc_copy)
            
            logger.debug(f"Reranked {len(documents)} docs, returning top {top_k}")
            return reranked
            
        except Exception as e:
            logger.error(f"Reranking failed: {e}")
            return documents[:top_k]
    
    def get_scores(
        self,
        query: str,
        documents: List[Document]
    ) -> List[Tuple[Document, float]]:
        """
        Get relevance scores for documents
        
        Args:
            query: Search query
            documents: Documents to score
            
        Returns:
            List of (document, score) tuples
        """
        if not self.model or not documents:
            return [(doc, 0.0) for doc in documents]
        
        try:
            pairs = [[query, doc.page_content] for doc in documents]
            scores = self.model.predict(pairs)
            return list(zip(documents, scores))
        except Exception as e:
            logger.error(f"Scoring failed: {e}")
            return [(doc, 0.0) for doc in documents]