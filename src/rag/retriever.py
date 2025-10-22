"""
Advanced RAG Retriever with Hybrid Search, HyDE, and Reranking
Production-ready retrieval pipeline
"""

import logging
from typing import List, Dict, Any, Optional
from langchain.schema import Document
from langchain.retrievers import EnsembleRetriever
from langchain.retrievers.multi_query import MultiQueryRetriever

from src.core.vector_store import SupabasePGVectorStore
from src.core.llm import get_gemini_llm
from src.rag.hyde import HyDERetriever
from src.rag.reranker import CrossEncoderReranker
from src.rag.fusion import ReciprocalRankFusion
from config.settings import settings

logger = logging.getLogger(__name__)


class AdvancedRAGRetriever:
    """
    Advanced RAG retrieval pipeline with multiple enhancement techniques:
    - HyDE (Hypothetical Document Embeddings)
    - Hybrid Search (Vector + Keyword)
    - Multi-Query Generation
    - Cross-Encoder Reranking
    - Reciprocal Rank Fusion
    """
    
    def __init__(
        self,
        vector_store: SupabasePGVectorStore,
        enable_hyde: bool = None,
        enable_reranking: bool = None,
        enable_hybrid: bool = None
    ):
        """
        Initialize advanced retriever
        
        Args:
            vector_store: Vector store instance
            enable_hyde: Enable HyDE (default from settings)
            enable_reranking: Enable reranking (default from settings)
            enable_hybrid: Enable hybrid search (default from settings)
        """
        self.vector_store = vector_store
        self.llm = get_gemini_llm().get_flash_model()
        
        # Feature flags
        self.enable_hyde = enable_hyde if enable_hyde is not None else settings.enable_hyde
        self.enable_reranking = enable_reranking if enable_reranking is not None else settings.enable_reranking
        self.enable_hybrid = enable_hybrid if enable_hybrid is not None else settings.enable_hybrid_search
        
        # Initialize components
        self.reranker = CrossEncoderReranker() if self.enable_reranking else None
        self.fusion = ReciprocalRankFusion()
        
        logger.info(
            f"Initialized AdvancedRAGRetriever - "
            f"HyDE: {self.enable_hyde}, "
            f"Reranking: {self.enable_reranking}, "
            f"Hybrid: {self.enable_hybrid}"
        )
    
    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
        retrieval_strategy: str = "auto"
    ) -> List[Document]:
        """
        Main retrieval method with automatic strategy selection
        
        Args:
            query: User query
            top_k: Number of documents to return
            filters: Metadata filters
            retrieval_strategy: Strategy to use (auto, simple, hybrid, advanced)
            
        Returns:
            List of relevant documents
        """
        top_k = top_k or settings.top_k_final
        initial_k = settings.top_k_retrieval
        
        try:
            # Select retrieval strategy
            if retrieval_strategy == "auto":
                strategy = self._select_strategy(query)
            else:
                strategy = retrieval_strategy
            
            logger.info(f"Using retrieval strategy: {strategy}")
            
            # Execute retrieval
            if strategy == "simple":
                documents = self._simple_retrieve(query, initial_k, filters)
            elif strategy == "hybrid":
                documents = self._hybrid_retrieve(query, initial_k, filters)
            elif strategy == "advanced":
                documents = self._advanced_retrieve(query, initial_k, filters)
            else:
                documents = self._simple_retrieve(query, initial_k, filters)
            
            # Rerank if enabled
            if self.enable_reranking and documents:
                documents = self.reranker.rerank(query, documents, top_k=top_k)
            else:
                documents = documents[:top_k]
            
            # Filter by similarity threshold
            if settings.similarity_threshold > 0:
                documents = self._filter_by_threshold(documents)
            
            logger.info(f"Retrieved {len(documents)} documents")
            return documents
            
        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            # Fallback to simple retrieval
            return self._simple_retrieve(query, top_k, filters)
    
    def _select_strategy(self, query: str) -> str:
        """Automatically select best retrieval strategy based on query"""
        query_length = len(query.split())
        
        # Simple queries: direct search
        if query_length < 5:
            return "simple"
        
        # Medium queries: hybrid search if enabled
        elif query_length < 15 and self.enable_hybrid:
            return "hybrid"
        
        # Complex queries: advanced search if HyDE enabled
        elif self.enable_hyde:
            return "advanced"
        
        return "hybrid" if self.enable_hybrid else "simple"
    
    def _simple_retrieve(
        self,
        query: str,
        k: int,
        filters: Optional[Dict] = None
    ) -> List[Document]:
        """Simple vector similarity search"""
        return self.vector_store.similarity_search(
            query=query,
            k=k,
            filter=filters
        )
    
    def _hybrid_retrieve(
        self,
        query: str,
        k: int,
        filters: Optional[Dict] = None
    ) -> List[Document]:
        """Hybrid search combining vector and keyword"""
        return self.vector_store.hybrid_search(
            query=query,
            k=k,
            vector_weight=0.7,
            keyword_weight=0.3
        )
    
    def _advanced_retrieve(
        self,
        query: str,
        k: int,
        filters: Optional[Dict] = None
    ) -> List[Document]:
        """
        Advanced retrieval with HyDE and multi-query
        Combines multiple retrieval approaches and fuses results
        """
        all_results = []
        
        # 1. Standard retrieval
        standard_docs = self._simple_retrieve(query, k, filters)
        all_results.append(standard_docs)
        
        # 2. HyDE retrieval
        if self.enable_hyde:
            hyde_docs = self._hyde_retrieve(query, k, filters)
            all_results.append(hyde_docs)
        
        # 3. Multi-query retrieval
        multi_query_docs = self._multi_query_retrieve(query, k, filters)
        all_results.append(multi_query_docs)
        
        # 4. Hybrid retrieval if enabled
        if self.enable_hybrid:
            hybrid_docs = self._hybrid_retrieve(query, k, filters)
            all_results.append(hybrid_docs)
        
        # Fuse all results using Reciprocal Rank Fusion
        fused_documents = self.fusion.fuse(all_results)
        
        return fused_documents[:k]
    
    def _hyde_retrieve(
        self,
        query: str,
        k: int,
        filters: Optional[Dict] = None
    ) -> List[Document]:
        """Retrieve using HyDE (Hypothetical Document Embeddings)"""
        hyde_retriever = HyDERetriever(
            vector_store=self.vector_store,
            llm=self.llm
        )
        return hyde_retriever.retrieve(query, k=k, filters=filters)
    
    def _multi_query_retrieve(
        self,
        query: str,
        k: int,
        filters: Optional[Dict] = None
    ) -> List[Document]:
        """Generate multiple query variations and retrieve"""
        try:
            # Create multi-query retriever
            base_retriever = self.vector_store.as_retriever(
                search_kwargs={"k": k // 3, "filter": filters}
            )
            
            multi_query_retriever = MultiQueryRetriever.from_llm(
                retriever=base_retriever,
                llm=self.llm
            )
            
            return multi_query_retriever.get_relevant_documents(query)
            
        except Exception as e:
            logger.warning(f"Multi-query retrieval failed, using simple: {e}")
            return self._simple_retrieve(query, k, filters)
    
    def _filter_by_threshold(self, documents: List[Document]) -> List[Document]:
        """Filter documents by similarity threshold if scores available"""
        # Check if documents have scores in metadata
        filtered = []
        for doc in documents:
            score = doc.metadata.get('score', 1.0)
            if score >= settings.similarity_threshold:
                filtered.append(doc)
        
        return filtered if filtered else documents
    
    def get_retriever_stats(self) -> Dict[str, Any]:
        """Get retriever configuration and statistics"""
        return {
            "enable_hyde": self.enable_hyde,
            "enable_reranking": self.enable_reranking,
            "enable_hybrid": self.enable_hybrid,
            "top_k_retrieval": settings.top_k_retrieval,
            "top_k_final": settings.top_k_final,
            "similarity_threshold": settings.similarity_threshold,
            "rerank_model": settings.rerank_model if self.enable_reranking else None
        }