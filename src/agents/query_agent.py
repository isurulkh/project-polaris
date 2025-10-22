"""
Query Agent - Information Retrieval and Question Answering
"""

import logging
import time
from typing import Dict, Any, List, Optional
from langchain.schema import Document
from src.agents.base_agent import BaseAgent, AgentResult
from src.rag.retriever import AdvancedRAGRetriever
from src.chains.qa_chain import QAChain

logger = logging.getLogger(__name__)


class QueryAgent(BaseAgent):
    """
    Query agent for information retrieval and question answering
    Uses advanced RAG pipeline for accurate responses
    """
    
    def __init__(
        self,
        llm,
        retriever: AdvancedRAGRetriever,
        enable_sources: bool = True,
        enable_followup: bool = True,
        **kwargs
    ):
        """
        Initialize query agent
        
        Args:
            llm: Language model instance
            retriever: Advanced RAG retriever
            enable_sources: Include source citations
            enable_followup: Enable follow-up question suggestions
            **kwargs: Additional configuration
        """
        super().__init__(
            name="QueryAgent",
            description="Retrieves and answers questions from document knowledge base",
            llm=llm,
            **kwargs
        )
        
        self.retriever = retriever
        self.enable_sources = enable_sources
        self.enable_followup = enable_followup
        
        # Initialize QA chain
        self.qa_chain = QAChain(
            llm=llm,
            retriever=retriever,
            enable_sources=enable_sources
        )
        
        logger.info("Initialized QueryAgent with advanced RAG")
    
    def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute query retrieval and answering
        
        Args:
            input_data: Dictionary with:
                - query: User question
                - chat_history: Optional conversation history
                - filters: Optional metadata filters
                
        Returns:
            AgentResult with answer and sources
        """
        start_time = time.time()
        
        query = input_data.get("query", "")
        chat_history = input_data.get("chat_history", [])
        filters = input_data.get("filters")
        
        if not query:
            return AgentResult(
                success=False,
                data=None,
                agent_name=self.name,
                error="No query provided"
            )
        
        try:
            # Retrieve relevant documents
            logger.info(f"Processing query: {query[:100]}...")
            documents = self.retriever.retrieve(
                query=query,
                filters=filters
            )
            
            if not documents:
                return self._handle_no_results(query)
            
            # Generate answer using QA chain
            result = self.qa_chain.run(
                query=query,
                documents=documents,
                chat_history=chat_history
            )
            
            # Extract answer and sources
            answer = result.get("answer", "")
            source_documents = result.get("source_documents", [])
            
            # Generate follow-up questions if enabled
            followup_questions = []
            if self.enable_followup and answer:
                followup_questions = self._generate_followup_questions(
                    query, answer, documents
                )
            
            # Prepare result data
            result_data = {
                "answer": answer,
                "sources": self._format_sources(source_documents) if self.enable_sources else [],
                "num_sources": len(source_documents),
                "followup_questions": followup_questions,
                "query": query
            }
            
            # Log execution
            execution_time = time.time() - start_time
            self._log_execution(input_data, result_data, execution_time)
            
            logger.info(
                f"Query answered with {len(source_documents)} sources "
                f"in {execution_time:.3f}s"
            )
            
            return AgentResult(
                success=True,
                data=result_data,
                agent_name=self.name,
                metadata={
                    "execution_time": execution_time,
                    "num_documents_retrieved": len(documents),
                    "num_sources_used": len(source_documents)
                }
            )
            
        except Exception as e:
            logger.error(f"Query execution failed: {e}", exc_info=True)
            return AgentResult(
                success=False,
                data=None,
                agent_name=self.name,
                error=str(e)
            )
    
    def _handle_no_results(self, query: str) -> AgentResult:
        """Handle case when no relevant documents found"""
        logger.warning(f"No relevant documents found for query: {query}")
        
        return AgentResult(
            success=True,
            data={
                "answer": (
                    "I couldn't find any relevant information in the document "
                    "knowledge base to answer your question. This could mean:\n\n"
                    "1. The information isn't available in the indexed documents\n"
                    "2. The query might need to be rephrased\n"
                    "3. The relevant documents haven't been processed yet\n\n"
                    "Try rephrasing your question or check if the relevant "
                    "documents have been uploaded to the system."
                ),
                "sources": [],
                "num_sources": 0,
                "followup_questions": [],
                "query": query
            },
            agent_name=self.name,
            metadata={"no_results": True}
        )
    
    def _format_sources(self, documents: List[Document]) -> List[Dict[str, Any]]:
        """Format source documents for response"""
        sources = []
        
        for i, doc in enumerate(documents, 1):
            source = {
                "index": i,
                "content": doc.page_content[:500],  # First 500 chars
                "metadata": {
                    "filename": doc.metadata.get("filename", "Unknown"),
                    "page": doc.metadata.get("page", "N/A"),
                    "source": doc.metadata.get("source", "Unknown")
                }
            }
            
            # Add relevance scores if available
            if "rerank_score" in doc.metadata:
                source["relevance_score"] = round(doc.metadata["rerank_score"], 3)
            elif "score" in doc.metadata:
                source["relevance_score"] = round(doc.metadata["score"], 3)
            
            sources.append(source)
        
        return sources
    
    def _generate_followup_questions(
        self,
        query: str,
        answer: str,
        documents: List[Document]
    ) -> List[str]:
        """Generate relevant follow-up questions"""
        try:
            prompt = f"""Based on this Q&A interaction, suggest 3 relevant follow-up questions the user might want to ask:

Question: {query}
Answer: {answer[:500]}...

Generate 3 specific, relevant follow-up questions. Return ONLY the questions, one per line, without numbering."""

            response = self.llm.invoke(prompt)
            questions = [
                q.strip().lstrip("1234567890.-) ")
                for q in response.content.strip().split('\n')
                if q.strip()
            ]
            
            return questions[:3]
            
        except Exception as e:
            logger.error(f"Failed to generate follow-up questions: {e}")
            return []
    
    def search_documents(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict] = None
    ) -> List[Document]:
        """
        Direct document search without answer generation
        
        Args:
            query: Search query
            top_k: Number of documents
            filters: Metadata filters
            
        Returns:
            List of relevant documents
        """
        return self.retriever.retrieve(
            query=query,
            top_k=top_k,
            filters=filters
        )