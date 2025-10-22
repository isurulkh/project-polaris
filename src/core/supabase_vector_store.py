"""
Supabase Native Vector Store Implementation
Compatible with n8n Supabase Vector Store Node
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from langchain.schema import Document
from langchain_community.vectorstores import SupabaseVectorStore
from supabase.client import Client, create_client
import numpy as np

from config.settings import settings
from src.core.fixed_supabase_vector_store import FixedSupabaseVectorStore

logger = logging.getLogger(__name__)


class SupabaseVectorStoreWrapper:
    """
    Wrapper for Supabase native vector store
    Compatible with n8n workflow schema
    """
    
    def __init__(self, embedding_function):
        """
        Initialize Supabase vector store
        
        Args:
            embedding_function: LangChain embedding function
        """
        self.embedding_function = embedding_function
        self.table_name = settings.supabase_table_name
        self.query_name = settings.supabase_query_name
        
        # Parse Supabase URL and key from DATABASE_URL
        supabase_url, supabase_key = self._parse_supabase_credentials()
        
        # Initialize Supabase client
        self.client: Client = create_client(supabase_url, supabase_key)
        
        # Initialize LangChain Supabase vector store with fixed implementation
        self.vector_store = FixedSupabaseVectorStore(
            client=self.client,
            embedding=embedding_function,
            table_name=self.table_name,
            query_name=self.query_name,
        )
        
        logger.info(f"Initialized Supabase vector store: table={self.table_name}, query={self.query_name}")
    
    def _parse_supabase_credentials(self) -> Tuple[str, str]:
        """
        Parse Supabase credentials from environment variables and DATABASE_URL
        Returns: (supabase_url, supabase_key)
        """
        try:
            # Get Supabase key from settings
            supabase_key = settings.supabase_key
            
            if not supabase_key:
                raise ValueError(
                    "SUPABASE_KEY not found in environment. "
                    "Please add SUPABASE_KEY to your .env file. "
                    "Get it from Supabase Dashboard > Settings > API > anon public"
                )
            
            # Extract project reference from DATABASE_URL
            # Format: postgresql://postgres:PASSWORD@db.PROJECT_REF.supabase.co:5432/postgres
            db_url = settings.database_url
            
            # Extract project reference
            if "supabase.co" in db_url:
                # Split by @ to get the host part
                host_part = db_url.split("@")[1].split(":")[0]  # db.PROJECT_REF.supabase.co
                # Split by . and find the part before supabase
                host_parts = host_part.split(".")
                # Find the project ref (should be the part before 'supabase')
                for i, part in enumerate(host_parts):
                    if part == "supabase" and i > 0:
                        project_ref = host_parts[i-1]
                        break
                else:
                    raise ValueError("Could not find project reference in DATABASE_URL")
                
                supabase_url = f"https://{project_ref}.supabase.co"
            else:
                raise ValueError(
                    f"Invalid Supabase DATABASE_URL format. "
                    f"Expected format: postgresql://postgres:PASSWORD@db.PROJECT_REF.supabase.co:5432/postgres"
                )
            
            logger.info(f"Parsed Supabase URL: {supabase_url}")
            return supabase_url, supabase_key
            
        except Exception as e:
            logger.error(f"Failed to parse Supabase credentials: {e}")
            raise ValueError(
                "Could not parse Supabase credentials. Please check:\n"
                "1. DATABASE_URL is in correct format\n"
                "2. SUPABASE_KEY is set in .env file"
            )
    
    def similarity_search(
        self,
        query: str,
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
        score_threshold: Optional[float] = None
    ) -> List[Document]:
        """
        Perform similarity search
        
        Args:
            query: Search query
            k: Number of results
            filter: Metadata filter (note: Supabase filters may work differently)
            score_threshold: Minimum similarity score
            
        Returns:
            List of relevant documents
        """
        try:
            # Use LangChain's Supabase vector store
            results = self.vector_store.similarity_search(
                query=query,
                k=k,
                filter=filter
            )
            
            # Filter by threshold if provided
            if score_threshold:
                results = [
                    doc for doc in results 
                    if doc.metadata.get("score", 1.0) >= score_threshold
                ]
            
            return results
            
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            return []
    
    def similarity_search_with_score(
        self,
        query: str,
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[Document, float]]:
        """
        Perform similarity search with relevance scores
        
        Args:
            query: Search query
            k: Number of results
            filter: Metadata filter
            
        Returns:
            List of (document, score) tuples
        """
        try:
            return self.vector_store.similarity_search_with_relevance_scores(
                query=query,
                k=k,
                filter=filter
            )
        except Exception as e:
            logger.error(f"Similarity search with score failed: {e}")
            return []
    
    def max_marginal_relevance_search(
        self,
        query: str,
        k: int = 5,
        fetch_k: int = 20,
        lambda_mult: float = 0.5,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        Perform MMR search for diversity
        
        Args:
            query: Search query
            k: Number of results
            fetch_k: Number of initial candidates
            lambda_mult: Diversity parameter
            filter: Metadata filter
            
        Returns:
            Diverse list of relevant documents
        """
        try:
            # Note: MMR may not be directly supported in Supabase
            # Fall back to regular search
            logger.warning("MMR not directly supported, using similarity search")
            return self.similarity_search(query, k=k, filter=filter)
        except Exception as e:
            logger.error(f"MMR search failed: {e}")
            return []
    
    def hybrid_search(
        self,
        query: str,
        k: int = 5,
        vector_weight: float = 0.7,
        keyword_weight: float = 0.3
    ) -> List[Document]:
        """
        Hybrid search combining vector similarity and keyword matching
        
        Args:
            query: Search query
            k: Number of results
            vector_weight: Weight for vector similarity
            keyword_weight: Weight for keyword matching
            
        Returns:
            Hybrid search results
        """
        try:
            # Vector search
            vector_results = self.similarity_search_with_score(query, k=k*2)
            
            # Keyword search using Supabase full-text search
            keyword_results = self._keyword_search(query, k=k*2)
            
            # Combine results
            combined = self._combine_results(
                vector_results,
                keyword_results,
                vector_weight,
                keyword_weight
            )
            
            return combined[:k]
        except Exception as e:
            logger.error(f"Hybrid search failed: {e}")
            return self.similarity_search(query, k=k)
    
    def _keyword_search(self, query: str, k: int = 10) -> List[Tuple[Document, float]]:
        """Perform keyword-based search using Supabase"""
        try:
            # Use Supabase text search on content column
            # Build query step by step to handle API compatibility
            query_builder = (self.client.table(self.table_name)
                           .select("id, content, metadata")
                           .text_search("content", query))
            
            # Apply limit using the correct method for text search
            response = query_builder.limit(k).execute()
            
            results = []
            for row in response.data:
                doc = Document(
                    page_content=row.get("content", ""),
                    metadata=row.get("metadata", {})
                )
                # Simple scoring based on query term frequency
                score = self._simple_keyword_score(query, doc.page_content)
                results.append((doc, score))
            
            return results
        except Exception as e:
            logger.error(f"Keyword search failed: {e}")
            # Fallback to simple content filtering if text search fails
            try:
                # Simple fallback using ilike for partial matching
                response = (self.client.table(self.table_name)
                           .select("id, content, metadata")
                           .ilike("content", f"%{query}%")
                           .limit(k)
                           .execute())
                
                results = []
                for row in response.data:
                    doc = Document(
                        page_content=row.get("content", ""),
                        metadata=row.get("metadata", {})
                    )
                    score = self._simple_keyword_score(query, doc.page_content)
                    results.append((doc, score))
                
                return results
            except Exception as fallback_e:
                logger.error(f"Keyword search fallback also failed: {fallback_e}")
                return []
    
    def _simple_keyword_score(self, query: str, text: str) -> float:
        """Simple keyword scoring"""
        query_terms = query.lower().split()
        text_lower = text.lower()
        
        matches = sum(1 for term in query_terms if term in text_lower)
        return matches / len(query_terms) if query_terms else 0.0
    
    def _combine_results(
        self,
        vector_results: List[Tuple[Document, float]],
        keyword_results: List[Tuple[Document, float]],
        vector_weight: float,
        keyword_weight: float
    ) -> List[Document]:
        """Combine and rank results from vector and keyword search"""
        
        # Normalize scores
        def normalize_scores(results):
            if not results:
                return []
            scores = [score for _, score in results]
            max_score = max(scores) if scores else 1.0
            min_score = min(scores) if scores else 0.0
            score_range = max_score - min_score if max_score != min_score else 1.0
            
            return [
                (doc, (score - min_score) / score_range)
                for doc, score in results
            ]
        
        vector_normalized = normalize_scores(vector_results)
        keyword_normalized = normalize_scores(keyword_results)
        
        # Combine scores
        doc_scores = {}
        for doc, score in vector_normalized:
            doc_id = id(doc.page_content)  # Simple deduplication
            doc_scores[doc_id] = {
                'doc': doc,
                'vector_score': score,
                'keyword_score': 0.0
            }
        
        for doc, score in keyword_normalized:
            doc_id = id(doc.page_content)
            if doc_id in doc_scores:
                doc_scores[doc_id]['keyword_score'] = score
            else:
                doc_scores[doc_id] = {
                    'doc': doc,
                    'vector_score': 0.0,
                    'keyword_score': score
                }
        
        # Calculate final scores
        results = []
        for doc_id, data in doc_scores.items():
            final_score = (
                data['vector_score'] * vector_weight +
                data['keyword_score'] * keyword_weight
            )
            results.append((data['doc'], final_score))
        
        # Sort by final score
        results.sort(key=lambda x: x[1], reverse=True)
        
        return [doc for doc, _ in results]
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector collection"""
        try:
            # Count total documents
            count_response = self.client.table(self.table_name)\
                .select("*", count="exact")\
                .execute()
            
            total_docs = count_response.count if hasattr(count_response, 'count') else 0
            
            # Try to get unique files
            try:
                files_response = self.client.table(self.table_name)\
                    .select("metadata->>filename")\
                    .execute()
                
                unique_files = len(set(
                    row.get("filename") for row in files_response.data 
                    if row.get("filename")
                ))
            except:
                unique_files = 0
            
            return {
                "total_documents": total_docs,
                "unique_files": unique_files,
                "table_name": self.table_name,
                "query_name": self.query_name
            }
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {
                "total_documents": 0,
                "unique_files": 0,
                "table_name": self.table_name,
                "error": str(e)
            }
    
    def as_retriever(self, **kwargs):
        """Return LangChain retriever interface"""
        return self.vector_store.as_retriever(**kwargs)