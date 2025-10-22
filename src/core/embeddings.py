"""
Google Gemini Embeddings Wrapper
Compatible with n8n workflow embedding model
"""

import logging
from typing import List
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from config.settings import settings

logger = logging.getLogger(__name__)


class GeminiEmbeddings:
    """
    Gemini embeddings wrapper with caching and batching
    Uses same model as n8n workflow for consistency
    """
    
    def __init__(self):
        """Initialize Gemini embeddings"""
        try:
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model=settings.gemini_embedding_model,
                google_api_key=settings.google_api_key,
                task_type="retrieval_document",  # Optimized for document retrieval
            )
            
            # For queries, we'll use a separate instance
            self.query_embeddings = GoogleGenerativeAIEmbeddings(
                model=settings.gemini_embedding_model,
                google_api_key=settings.google_api_key,
                task_type="retrieval_query",  # Optimized for queries
            )
            
            logger.info(f"Initialized Gemini embeddings: {settings.gemini_embedding_model}")
            
        except Exception as e:
            logger.error(f"Failed to initialize embeddings: {e}")
            raise
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed documents (for indexing)
        
        Args:
            texts: List of text documents
            
        Returns:
            List of embedding vectors
        """
        try:
            return self.embeddings.embed_documents(texts)
        except Exception as e:
            logger.error(f"Failed to embed documents: {e}")
            raise
    
    def embed_query(self, text: str) -> List[float]:
        """
        Embed query (for retrieval)
        
        Args:
            text: Query text
            
        Returns:
            Embedding vector
        """
        try:
            return self.query_embeddings.embed_query(text)
        except Exception as e:
            logger.error(f"Failed to embed query: {e}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """Get embedding dimension"""
        return settings.embedding_dimension
    
    def __call__(self, text: str) -> List[float]:
        """Make instance callable for query embedding"""
        return self.embed_query(text)


# Global embeddings instance
_gemini_embeddings = None


def get_gemini_embeddings() -> GeminiEmbeddings:
    """Get or create global embeddings instance"""
    global _gemini_embeddings
    if _gemini_embeddings is None:
        _gemini_embeddings = GeminiEmbeddings()
    return _gemini_embeddings