"""
Reciprocal Rank Fusion for combining multiple retrieval results
"""

import logging
from typing import List, Dict, Optional
from collections import defaultdict
from langchain.schema import Document

logger = logging.getLogger(__name__)


class ReciprocalRankFusion:
    """
    Reciprocal Rank Fusion algorithm for combining ranked lists
    """
    
    def __init__(self, k: int = 60):
        """
        Initialize RRF
        
        Args:
            k: Constant for RRF formula (default 60 from research)
        """
        self.k = k
        logger.info(f"Initialized RRF with k={k}")
    
    def fuse(
        self,
        ranked_lists: List[List[Document]],
        weights: Optional[List[float]] = None
    ) -> List[Document]:
        """
        Fuse multiple ranked lists using RRF
        
        Args:
            ranked_lists: List of ranked document lists
            weights: Optional weights for each list
            
        Returns:
            Fused and reranked documents
        """
        if not ranked_lists:
            return []
        
        # Default to equal weights
        if weights is None:
            weights = [1.0] * len(ranked_lists)
        
        # Calculate RRF scores
        doc_scores = defaultdict(float)
        doc_objects = {}
        
        for weight, ranked_list in zip(weights, ranked_lists):
            for rank, doc in enumerate(ranked_list, start=1):
                # Create unique doc identifier
                doc_id = self._get_doc_id(doc)
                
                # RRF formula: score = weight / (k + rank)
                rrf_score = weight / (self.k + rank)
                doc_scores[doc_id] += rrf_score
                
                # Store document object (keep first occurrence)
                if doc_id not in doc_objects:
                    doc_objects[doc_id] = doc
        
        # Sort by RRF score
        sorted_docs = sorted(
            doc_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Return documents in fused order
        fused = []
        for doc_id, score in sorted_docs:
            doc = doc_objects[doc_id]
            # Add RRF score to metadata
            doc_copy = Document(
                page_content=doc.page_content,
                metadata={**doc.metadata, "rrf_score": score}
            )
            fused.append(doc_copy)
        
        logger.debug(f"Fused {len(ranked_lists)} lists into {len(fused)} unique documents")
        return fused
    
    def _get_doc_id(self, doc: Document) -> str:
        """Generate unique identifier for document"""
        # Use content hash or document ID if available
        if "id" in doc.metadata:
            return str(doc.metadata["id"])
        
        # Fallback to content hash
        return str(hash(doc.page_content))