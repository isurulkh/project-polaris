"""
Summary Agent - Document Summarization and Synthesis
"""

import logging
import time
from typing import Dict, Any, List, Optional
from langchain.schema import Document
from src.agents.base_agent import BaseAgent, AgentResult
from src.rag.retriever import AdvancedRAGRetriever
from src.chains.summary_chain import SummaryChain

logger = logging.getLogger(__name__)


class SummaryAgent(BaseAgent):
    """
    Summary agent for document summarization and synthesis
    Uses Gemini Pro model for high-quality summaries
    """
    
    def __init__(
        self,
        llm,
        retriever: AdvancedRAGRetriever,
        summary_type: str = "comprehensive",
        **kwargs
    ):
        """
        Initialize summary agent
        
        Args:
            llm: Language model instance (should be Pro model)
            retriever: Advanced RAG retriever
            summary_type: Type of summary (brief, comprehensive, executive)
            **kwargs: Additional configuration
        """
        super().__init__(
            name="SummaryAgent",
            description="Generates summaries and synthesizes information from documents",
            llm=llm,
            **kwargs
        )
        
        self.retriever = retriever
        self.summary_type = summary_type
        
        # Initialize summary chain
        self.summary_chain = SummaryChain(
            llm=llm,
            summary_type=summary_type
        )
        
        logger.info(f"Initialized SummaryAgent with {summary_type} mode")
    
    def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute document summarization
        
        Args:
            input_data: Dictionary with:
                - query: Summary request or topic
                - summary_type: Optional override (brief/comprehensive/executive)
                - max_docs: Maximum documents to summarize
                - filters: Optional metadata filters
                
        Returns:
            AgentResult with summary and key points
        """
        start_time = time.time()
        
        query = input_data.get("query", "")
        summary_type = input_data.get("summary_type", self.summary_type)
        max_docs = input_data.get("max_docs", 10)
        filters = input_data.get("filters")
        
        if not query:
            return AgentResult(
                success=False,
                data=None,
                agent_name=self.name,
                error="No query provided"
            )
        
        try:
            logger.info(f"Generating {summary_type} summary for: {query[:100]}...")
            
            # Retrieve relevant documents
            documents = self.retriever.retrieve(
                query=query,
                top_k=max_docs,
                filters=filters
            )
            
            if not documents:
                return self._handle_no_documents(query)
            
            # Generate summary
            result = self.summary_chain.run(
                documents=documents,
                query=query,
                summary_type=summary_type
            )
            
            # Extract summary components
            summary = result.get("summary", "")
            key_points = result.get("key_points", [])
            insights = result.get("insights", [])
            
            # Prepare result data
            result_data = {
                "summary": summary,
                "key_points": key_points,
                "insights": insights,
                "num_documents_analyzed": len(documents),
                "summary_type": summary_type,
                "query": query,
                "document_sources": self._get_document_sources(documents)
            }
            
            # Log execution
            execution_time = time.time() - start_time
            self._log_execution(input_data, result_data, execution_time)
            
            logger.info(
                f"Generated {summary_type} summary from {len(documents)} documents "
                f"in {execution_time:.3f}s"
            )
            
            return AgentResult(
                success=True,
                data=result_data,
                agent_name=self.name,
                metadata={
                    "execution_time": execution_time,
                    "num_documents": len(documents),
                    "summary_length": len(summary.split())
                }
            )
            
        except Exception as e:
            logger.error(f"Summary generation failed: {e}", exc_info=True)
            return AgentResult(
                success=False,
                data=None,
                agent_name=self.name,
                error=str(e)
            )
    
    def summarize_documents(
        self,
        documents: List[Document],
        summary_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Directly summarize provided documents
        
        Args:
            documents: List of documents to summarize
            summary_type: Type of summary
            
        Returns:
            Summary result dictionary
        """
        if not documents:
            return {
                "summary": "No documents provided to summarize.",
                "key_points": [],
                "insights": []
            }
        
        return self.summary_chain.run(
            documents=documents,
            query="Summarize these documents",
            summary_type=summary_type
        )
    
    def compare_documents(
        self,
        query: str,
        filters: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Compare multiple documents on a topic
        
        Args:
            query: Comparison query
            filters: List of filter dicts for different document sets
            
        Returns:
            Comparison analysis
        """
        try:
            if not filters or len(filters) < 2:
                # Simple comparison without filters
                documents = self.retriever.retrieve(query=query, top_k=10)
                
                comparison_prompt = f"""Compare and contrast the information in these documents about: {query}

Provide:
1. Common themes and agreements
2. Key differences or contradictions
3. Unique insights from different sources
4. Overall synthesis"""

                result = self.summary_chain.run(
                    documents=documents,
                    query=comparison_prompt,
                    summary_type="analysis"
                )
                
                return result
            
            # Multi-group comparison
            document_groups = []
            for filter_dict in filters:
                docs = self.retriever.retrieve(
                    query=query,
                    top_k=5,
                    filters=filter_dict
                )
                document_groups.append(docs)
            
            # Combine and compare
            all_docs = [doc for group in document_groups for doc in group]
            
            return self.summary_chain.run(
                documents=all_docs,
                query=f"Compare information about: {query}",
                summary_type="comparative"
            )
            
        except Exception as e:
            logger.error(f"Document comparison failed: {e}")
            return {
                "summary": f"Comparison failed: {str(e)}",
                "key_points": [],
                "insights": []
            }
    
    def _handle_no_documents(self, query: str) -> AgentResult:
        """Handle case when no documents found"""
        logger.warning(f"No documents found for summarization: {query}")
        
        return AgentResult(
            success=True,
            data={
                "summary": (
                    "No relevant documents were found to summarize for this query. "
                    "Please ensure the relevant documents have been uploaded and "
                    "processed by the system."
                ),
                "key_points": [],
                "insights": [],
                "num_documents_analyzed": 0,
                "query": query,
                "summary_type": "comprehensive",
                "document_sources": []
            },
            agent_name=self.name,
            metadata={"no_documents": True}
        )
    
    def _get_document_sources(self, documents: List[Document]) -> List[Dict[str, str]]:
        """Extract unique document sources"""
        sources = {}
        
        for doc in documents:
            filename = doc.metadata.get("filename", "Unknown")
            if filename not in sources:
                sources[filename] = {
                    "filename": filename,
                    "type": doc.metadata.get("mimeType", "Unknown"),
                    "id": doc.metadata.get("id", "")
                }
        
        return list(sources.values())