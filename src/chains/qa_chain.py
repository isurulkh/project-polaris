"""
Question Answering Chain with RAG
"""

import logging
from typing import Dict, Any, List
from langchain.schema import Document
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from src.prompts.query_prompts import QA_PROMPT, QA_WITH_HISTORY_PROMPT

logger = logging.getLogger(__name__)


class QAChain:
    """
    Question answering chain with context from retrieved documents
    """
    
    def __init__(
        self,
        llm,
        retriever,
        enable_sources: bool = True,
        max_context_length: int = 8000
    ):
        """
        Initialize QA chain
        
        Args:
            llm: Language model
            retriever: Document retriever
            enable_sources: Include source documents in response
            max_context_length: Maximum context length in tokens (approximate)
        """
        self.llm = llm
        self.retriever = retriever
        self.enable_sources = enable_sources
        self.max_context_length = max_context_length
        
        # Create chains
        self.qa_chain = LLMChain(
            llm=llm,
            prompt=QA_PROMPT
        )
        
        self.qa_with_history_chain = LLMChain(
            llm=llm,
            prompt=QA_WITH_HISTORY_PROMPT
        )
        
        logger.info("Initialized QA Chain")
    
    def run(
        self,
        query: str,
        documents: List[Document],
        chat_history: List[tuple] = None
    ) -> Dict[str, Any]:
        """
        Run QA chain
        
        Args:
            query: User question
            documents: Retrieved context documents
            chat_history: Optional conversation history [(question, answer), ...]
            
        Returns:
            Dictionary with answer and source documents
        """
        try:
            # Format context from documents
            context = self._format_context(documents)
            
            # Select appropriate chain
            if chat_history and len(chat_history) > 0:
                chain = self.qa_with_history_chain
                history_text = self._format_history(chat_history)
                
                response = chain.invoke({
                    "context": context,
                    "question": query,
                    "chat_history": history_text
                })
            else:
                chain = self.qa_chain
                response = chain.invoke({
                    "context": context,
                    "question": query
                })
            
            answer = response["text"].strip()
            
            # Validate answer quality
            if self._is_low_quality_answer(answer):
                logger.warning("Detected low-quality answer, regenerating...")
                answer = self._regenerate_answer(query, context)
            
            return {
                "answer": answer,
                "source_documents": documents if self.enable_sources else [],
                "context_used": len(context),
                "num_sources": len(documents)
            }
            
        except Exception as e:
            logger.error(f"QA chain execution failed: {e}")
            return {
                "answer": f"I encountered an error while processing your question: {str(e)}",
                "source_documents": [],
                "context_used": 0,
                "num_sources": 0
            }
    
    def _format_context(self, documents: List[Document]) -> str:
        """Format documents into context string"""
        if not documents:
            return "No relevant context found."
        
        context_parts = []
        total_length = 0
        max_chars = self.max_context_length * 4  # Rough approximation
        
        for i, doc in enumerate(documents, 1):
            # Add source information
            filename = doc.metadata.get("filename", "Unknown")
            page = doc.metadata.get("page", "")
            
            source_info = f"[Source {i}: {filename}"
            if page:
                source_info += f", Page {page}"
            source_info += "]\n"
            
            # Add content
            content = doc.page_content.strip()
            
            # Check length
            part_length = len(source_info) + len(content)
            if total_length + part_length > max_chars:
                logger.warning(f"Context truncated at {i} documents due to length limit")
                break
            
            context_parts.append(source_info + content)
            total_length += part_length
        
        return "\n\n".join(context_parts)
    
    def _format_history(self, chat_history: List[tuple]) -> str:
        """Format chat history for context"""
        if not chat_history:
            return ""
        
        history_parts = []
        for question, answer in chat_history[-5:]:  # Last 5 turns
            history_parts.append(f"Human: {question}")
            history_parts.append(f"Assistant: {answer}")
        
        return "\n".join(history_parts)
    
    def _is_low_quality_answer(self, answer: str) -> bool:
        """Detect low-quality or uncertain answers"""
        low_quality_indicators = [
            "i don't know",
            "i cannot find",
            "no information",
            "not sure",
            "unclear",
            "i apologize",
            "sorry, i"
        ]
        
        answer_lower = answer.lower()
        
        # Check for indicators
        for indicator in low_quality_indicators:
            if indicator in answer_lower and len(answer) < 200:
                return True
        
        # Check if answer is too short
        if len(answer.split()) < 10:
            return True
        
        return False
    
    def _regenerate_answer(self, query: str, context: str) -> str:
        """Regenerate answer with stricter prompt"""
        try:
            strict_prompt = f"""Based STRICTLY on the provided context, answer the question. If the context doesn't contain the answer, say "The provided documents don't contain information about this specific question."

Context:
{context}

Question: {query}

Detailed Answer:"""

            response = self.llm.invoke(strict_prompt)
            return response.content.strip()
            
        except Exception as e:
            logger.error(f"Answer regeneration failed: {e}")
            return "I couldn't generate a satisfactory answer from the available documents."