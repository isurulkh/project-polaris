"""
Fixed Supabase Vector Store Implementation
Addresses compatibility issues with newer Supabase Python client versions
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from langchain.schema import Document
from langchain_community.vectorstores import SupabaseVectorStore
from supabase.client import Client
import numpy as np

logger = logging.getLogger(__name__)


class FixedSupabaseVectorStore(SupabaseVectorStore):
    """
    Fixed Supabase Vector Store that addresses API compatibility issues
    with newer Supabase Python client versions
    """
    
    def __init__(self, client: Client, embedding, table_name: str, query_name: str):
        """Initialize with proper attribute setup"""
        super().__init__(client=client, embedding=embedding, table_name=table_name, query_name=query_name)
        # Ensure attributes are properly set for our methods
        self._client = client
        self._embedding = embedding
        self._table_name = table_name
        self._query_name = query_name
    
    def similarity_search_by_vector_with_relevance_scores(
        self,
        embedding: List[float],
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None,
        postgrest_filter: Optional[str] = None,
        **kwargs: Any,
    ) -> List[Tuple[Document, float]]:
        """
        Fixed version of similarity search with relevance scores
        """
        try:
            # Use the RPC function directly instead of the deprecated query builder
            rpc_params = {
                "query_embedding": embedding,
                "match_count": k,
            }
            
            # Add filter if provided
            if filter:
                rpc_params["filter"] = filter
            elif postgrest_filter:
                # Handle postgrest filter format
                rpc_params["filter"] = {}
            else:
                rpc_params["filter"] = {}
            
            # Call the RPC function directly
            res = self._client.rpc(self._query_name, rpc_params).execute()
            
            if res.data:
                match_result = [
                    (
                        Document(
                            metadata=search.get("metadata", {}),
                            page_content=search.get("content", ""),
                        ),
                        search.get("similarity", 0.0),
                    )
                    for search in res.data
                ]
                return match_result
            else:
                logger.warning(f"RPC function {self._query_name} returned no results, using fallback")
                # Fallback to direct table query if RPC returns no results
                return self._fallback_similarity_search(embedding, k, filter)
            
        except Exception as e:
            logger.error(f"Fixed similarity search failed: {e}")
            # Fallback to direct table query if RPC fails
            return self._fallback_similarity_search(embedding, k, filter)
    
    def _fallback_similarity_search(
        self,
        embedding: List[float],
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[Tuple[Document, float]]:
        """
        Fallback method using direct table queries
        """
        try:
            # Build query
            query = self._client.table(self._table_name).select(
                "id, content, metadata, embedding"
            )
            
            # Apply metadata filter if provided
            if filter:
                for key, value in filter.items():
                    query = query.eq(f"metadata->{key}", value)
            
            # Execute query and get all results
            response = query.execute()
            
            # Calculate similarities manually
            results_with_similarity = []
            query_embedding = np.array(embedding)
            
            for row in response.data:
                if row.get("embedding"):
                    # Parse embedding from database (it's stored as a string)
                    embedding_str = row["embedding"]
                    if isinstance(embedding_str, str):
                        import json
                        doc_embedding = np.array(json.loads(embedding_str))
                    else:
                        doc_embedding = np.array(embedding_str)
                    
                    # Calculate cosine similarity
                    similarity = np.dot(query_embedding, doc_embedding) / (
                        np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
                    )
                    
                    doc = Document(
                        metadata=row.get("metadata", {}),
                        page_content=row.get("content", ""),
                    )
                    
                    results_with_similarity.append((doc, float(similarity)))
            
            # Sort by similarity (descending) and return top k
            results_with_similarity.sort(key=lambda x: x[1], reverse=True)
            return results_with_similarity[:k]
            
        except Exception as e:
            logger.error(f"Fallback similarity search failed: {e}")
            return []
    
    def similarity_search_with_relevance_scores(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> List[Tuple[Document, float]]:
        """
        Fixed version of similarity search with relevance scores using query string
        """
        try:
            # Get embedding for the query
            embedding = self._embedding.embed_query(query)
            return self.similarity_search_by_vector_with_relevance_scores(
                embedding, k=k, filter=filter, **kwargs
            )
        except Exception as e:
            logger.error(f"Similarity search with relevance scores failed: {e}")
            return []
    
    def similarity_search(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> List[Document]:
        """
        Fixed version of similarity search
        """
        try:
            docs_and_scores = self.similarity_search_with_relevance_scores(
                query, k=k, filter=filter, **kwargs
            )
            return [doc for doc, _ in docs_and_scores]
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            return []