"""
Document Summarization Chain with Multiple Strategies
"""

import logging
from typing import Dict, Any, List
from langchain.schema import Document
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate
from src.prompts.summary_prompts import (
    BRIEF_SUMMARY_PROMPT,
    COMPREHENSIVE_SUMMARY_PROMPT,
    EXECUTIVE_SUMMARY_PROMPT,
    MAP_REDUCE_MAP_PROMPT,
    MAP_REDUCE_COMBINE_PROMPT
)

logger = logging.getLogger(__name__)


class SummaryChain:
    """
    Flexible summarization chain supporting multiple summary types
    """
    
    def __init__(
        self,
        llm,
        summary_type: str = "comprehensive",
        use_map_reduce: bool = True
    ):
        """
        Initialize summary chain
        
        Args:
            llm: Language model
            summary_type: Type of summary (brief, comprehensive, executive)
            use_map_reduce: Use map-reduce for long documents
        """
        self.llm = llm
        self.summary_type = summary_type
        self.use_map_reduce = use_map_reduce
        
        # Prompt selection
        self.prompts = {
            "brief": BRIEF_SUMMARY_PROMPT,
            "comprehensive": COMPREHENSIVE_SUMMARY_PROMPT,
            "executive": EXECUTIVE_SUMMARY_PROMPT,
            "analysis": COMPREHENSIVE_SUMMARY_PROMPT,
            "comparative": COMPREHENSIVE_SUMMARY_PROMPT
        }
        
        logger.info(f"Initialized Summary Chain with {summary_type} mode")
    
    def run(
        self,
        documents: List[Document],
        query: str = "",
        summary_type: str = None
    ) -> Dict[str, Any]:
        """
        Generate summary from documents
        
        Args:
            documents: List of documents to summarize
            query: Optional specific question or focus
            summary_type: Override default summary type
            
        Returns:
            Dictionary with summary, key points, and insights
        """
        summary_type = summary_type or self.summary_type
        
        try:
            # Choose strategy based on document count and length
            total_length = sum(len(doc.page_content) for doc in documents)
            
            if len(documents) > 10 or total_length > 30000:
                logger.info("Using map-reduce strategy for large document set")
                return self._map_reduce_summarize(documents, query, summary_type)
            else:
                logger.info("Using direct summarization strategy")
                return self._direct_summarize(documents, query, summary_type)
                
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            return {
                "summary": f"Failed to generate summary: {str(e)}",
                "key_points": [],
                "insights": []
            }
    
    def _direct_summarize(
        self,
        documents: List[Document],
        query: str,
        summary_type: str
    ) -> Dict[str, Any]:
        """Direct summarization for smaller document sets"""
        
        # Combine document content
        combined_text = self._combine_documents(documents)
        
        # Select prompt
        prompt_template = self.prompts.get(summary_type, COMPREHENSIVE_SUMMARY_PROMPT)
        
        # Add query context if provided
        if query:
            context_addition = f"\n\nSpecific Focus: {query}"
            combined_text += context_addition
        
        # Generate summary
        prompt = prompt_template.format(text=combined_text)
        response = self.llm.invoke(prompt)
        summary_text = response.content.strip()
        
        # Parse structured output
        parsed = self._parse_summary_output(summary_text)
        
        return {
            "summary": parsed["summary"],
            "key_points": parsed["key_points"],
            "insights": parsed["insights"],
            "num_documents": len(documents)
        }
    
    def _map_reduce_summarize(
        self,
        documents: List[Document],
        query: str,
        summary_type: str
    ) -> Dict[str, Any]:
        """Map-reduce summarization for large document sets"""
        
        try:
            # Use LangChain's map-reduce chain
            chain = load_summarize_chain(
                llm=self.llm,
                chain_type="map_reduce",
                map_prompt=MAP_REDUCE_MAP_PROMPT,
                combine_prompt=MAP_REDUCE_COMBINE_PROMPT,
                verbose=False
            )
            
            # Run chain
            result = chain.invoke({"input_documents": documents})
            summary_text = result["output_text"]
            
            # Parse output
            parsed = self._parse_summary_output(summary_text)
            
            # Extract key points from individual documents
            key_points = self._extract_key_points_from_docs(documents)
            
            return {
                "summary": parsed["summary"],
                "key_points": key_points[:10],  # Top 10 points
                "insights": parsed["insights"],
                "num_documents": len(documents)
            }
            
        except Exception as e:
            logger.error(f"Map-reduce summarization failed: {e}")
            # Fallback to direct with sampling
            sampled_docs = documents[:10]  # Take first 10
            return self._direct_summarize(sampled_docs, query, summary_type)
    
    def _combine_documents(self, documents: List[Document]) -> str:
        """Combine document contents with source attribution"""
        parts = []
        
        for i, doc in enumerate(documents, 1):
            filename = doc.metadata.get("filename", "Unknown")
            content = doc.page_content.strip()
            
            parts.append(f"[Document {i}: {filename}]\n{content}")
        
        return "\n\n".join(parts)
    
    def _parse_summary_output(self, summary_text: str) -> Dict[str, Any]:
        """Parse structured summary output"""
        
        # Initialize result
        result = {
            "summary": summary_text,
            "key_points": [],
            "insights": []
        }
        
        # Try to extract structured sections
        lines = summary_text.split('\n')
        current_section = "summary"
        summary_lines = []
        key_points = []
        insights = []
        
        for line in lines:
            line_lower = line.lower().strip()
            
            if "key points:" in line_lower or "main points:" in line_lower:
                current_section = "key_points"
                continue
            elif "insights:" in line_lower or "key insights:" in line_lower:
                current_section = "insights"
                continue
            elif "summary:" in line_lower:
                current_section = "summary"
                continue
            
            # Add to appropriate section
            if current_section == "summary" and line.strip():
                summary_lines.append(line)
            elif current_section == "key_points" and line.strip():
                # Remove bullet points and numbering
                clean_line = line.strip().lstrip("•-*1234567890. ")
                if clean_line:
                    key_points.append(clean_line)
            elif current_section == "insights" and line.strip():
                clean_line = line.strip().lstrip("•-*1234567890. ")
                if clean_line:
                    insights.append(clean_line)
        
        # Update result
        if summary_lines:
            result["summary"] = "\n".join(summary_lines)
        if key_points:
            result["key_points"] = key_points
        if insights:
            result["insights"] = insights
        
        return result
    
    def _extract_key_points_from_docs(self, documents: List[Document]) -> List[str]:
        """Extract key points from individual documents"""
        key_points = []
        
        try:
            # Sample documents for key point extraction
            sample_size = min(5, len(documents))
            sampled = documents[:sample_size]
            
            for doc in sampled:
                # Get first few sentences as potential key point
                sentences = doc.page_content.split('.')[:2]
                point = '. '.join(sentences).strip()
                if point and len(point) > 20:
                    key_points.append(point + '.')
            
        except Exception as e:
            logger.error(f"Key point extraction failed: {e}")
        
        return key_points