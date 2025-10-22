"""
HyDE (Hypothetical Document Embeddings) Implementation
Generates hypothetical answers to improve retrieval
"""

import logging
from typing import List, Dict, Any, Optional
from langchain.schema import Document
from langchain.prompts import PromptTemplate

logger = logging.getLogger(__name__)


class HyDERetriever:
    """
    HyDE retriever that generates hypothetical documents
    to improve semantic search accuracy
    """
    
    HYDE_PROMPT = """You are an expert consultant creating a hypothetical document excerpt that would perfectly answer the following question. 

Generate a detailed, informative paragraph (150-200 words) that directly answers this question as if it came from a high-quality consulting report or industry document. Include specific details, metrics, and professional terminology.

Question: {query}

Hypothetical Document Excerpt:"""
    
    def __init__(self, vector_store, llm, num_hypotheses: int = 3):
        """
        Initialize HyDE retriever
        
        Args:
            vector_store: Vector store instance
            llm: Language model for hypothesis generation
            num_hypotheses: Number of hypothetical documents to generate
        """
        self.vector_store = vector_store
        self.llm = llm
        self.num_hypotheses = num_hypotheses
        
        self.prompt = PromptTemplate(
            template=self.HYDE_PROMPT,
            input_variables=["query"]
        )
        
        logger.info(f"Initialized HyDE retriever with {num_hypotheses} hypotheses")
    
    def retrieve(
        self,
        query: str,
        k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        Retrieve documents using HyDE
        
        Args:
            query: User query
            k: Number of documents to retrieve
            filters: Metadata filters
            
        Returns:
            List of relevant documents
        """
        try:
            # Generate hypothetical documents
            hypotheses = self._generate_hypotheses(query)
            
            # Search with each hypothesis
            all_documents = []
            for hypothesis in hypotheses:
                docs = self.vector_store.similarity_search(
                    query=hypothesis,
                    k=k,
                    filter=filters
                )
                all_documents.extend(docs)
            
            # Deduplicate and rank
            unique_docs = self._deduplicate_documents(all_documents)
            
            return unique_docs[:k]
            
        except Exception as e:
            logger.error(f"HyDE retrieval failed: {e}")
            # Fallback to regular search
            return self.vector_store.similarity_search(query, k=k, filter=filters)
    
    def _generate_hypotheses(self, query: str) -> List[str]:
        """Generate hypothetical document excerpts"""
        hypotheses = []
        
        try:
            for i in range(self.num_hypotheses):
                # Generate hypothesis with slight temperature variation
                temperature = 0.3 + (i * 0.2)  # 0.3, 0.5, 0.7
                
                response = self.llm.invoke(
                    self.prompt.format(query=query),
                    temperature=temperature
                )
                
                hypothesis = response.content.strip()
                if hypothesis:
                    hypotheses.append(hypothesis)
                    logger.debug(f"Generated hypothesis {i+1}: {hypothesis[:100]}...")
            
        except Exception as e:
            logger.error(f"Failed to generate hypotheses: {e}")
            # Return original query as fallback
            hypotheses = [query]
        
        return hypotheses or [query]
    
    def _deduplicate_documents(self, documents: List[Document]) -> List[Document]:
        """Remove duplicate documents while preserving order"""
        seen = set()
        unique_docs = []
        
        for doc in documents:
            # Use content hash for deduplication
            doc_hash = hash(doc.page_content)
            
            if doc_hash not in seen:
                seen.add(doc_hash)
                unique_docs.append(doc)
        
        return unique_docs