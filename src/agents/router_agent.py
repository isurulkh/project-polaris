"""
Router Agent - Query Intent Classification and Agent Routing
"""

import logging
import time
from typing import Dict, Any
from langchain.prompts import PromptTemplate
from src.agents.base_agent import BaseAgent, AgentResult

logger = logging.getLogger(__name__)


class RouterAgent(BaseAgent):
    """
    Router agent that classifies query intent and routes to appropriate agent
    """
    
    ROUTING_PROMPT = """You are an intelligent query router for a document management system. Analyze the user's query and classify it into ONE of these categories:

**Categories:**
1. **QUERY** - Information retrieval questions about documents
   Examples: "What does the report say about...?", "Find information on...", "What are the key points...?"

2. **SUMMARY** - Requests for summaries or overviews
   Examples: "Summarize the document...", "Give me an overview of...", "What are the main takeaways...?"

3. **ANALYSIS** - Deep analysis or comparison requests
   Examples: "Compare these documents...", "Analyze the trends in...", "What patterns emerge from...?"

4. **METADATA** - Questions about document properties
   Examples: "How many documents...?", "Which files contain...?", "List all documents about...?"

5. **GENERAL** - General chat, greetings, or unclear intent
   Examples: "Hello", "How are you?", "Can you help me?"

User Query: {query}

Respond ONLY with the category name (QUERY, SUMMARY, ANALYSIS, METADATA, or GENERAL) and a brief reasoning (1 line).

Format:
Category: [CATEGORY]
Reason: [one line explanation]"""
    
    # Agent mapping
    AGENT_MAP = {
        "QUERY": "query_agent",
        "SUMMARY": "summary_agent",
        "ANALYSIS": "summary_agent",  # Use summary agent for analysis
        "METADATA": "tool_agent",
        "GENERAL": "query_agent",  # Default to query agent
    }
    
    def __init__(self, llm, **kwargs):
        """Initialize router agent"""
        super().__init__(
            name="RouterAgent",
            description="Routes queries to appropriate specialized agents",
            llm=llm,
            **kwargs
        )
        
        self.prompt = PromptTemplate(
            template=self.ROUTING_PROMPT,
            input_variables=["query"]
        )
    
    def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Route query to appropriate agent
        
        Args:
            input_data: Dictionary with 'query' key
            
        Returns:
            AgentResult with routing decision
        """
        start_time = time.time()
        query = input_data.get("query", "")
        
        if not query:
            return AgentResult(
                success=False,
                data=None,
                agent_name=self.name,
                error="No query provided"
            )
        
        try:
            # Classify query
            category, reasoning = self._classify_query(query)
            
            # Get target agent
            target_agent = self.AGENT_MAP.get(category, "query_agent")
            
            # Prepare result
            result_data = {
                "category": category,
                "target_agent": target_agent,
                "reasoning": reasoning,
                "original_query": query
            }
            
            # Log execution
            execution_time = time.time() - start_time
            self._log_execution(input_data, result_data, execution_time)
            
            logger.info(
                f"Routed query to {target_agent} "
                f"(category: {category}) in {execution_time:.3f}s"
            )
            
            return AgentResult(
                success=True,
                data=result_data,
                agent_name=self.name,
                metadata={"execution_time": execution_time}
            )
            
        except Exception as e:
            logger.error(f"Routing failed: {e}")
            return AgentResult(
                success=False,
                data={"target_agent": "query_agent"},  # Default fallback
                agent_name=self.name,
                error=str(e)
            )
    
    def _classify_query(self, query: str) -> tuple[str, str]:
        """
        Classify query into category
        
        Returns:
            Tuple of (category, reasoning)
        """
        try:
            # Generate classification
            response = self.llm.invoke(
                self.prompt.format(query=query)
            )
            
            content = response.content.strip()
            
            # Parse response
            category = "QUERY"  # Default
            reasoning = "Default routing"
            
            for line in content.split('\n'):
                if line.startswith("Category:"):
                    category = line.replace("Category:", "").strip().upper()
                elif line.startswith("Reason:"):
                    reasoning = line.replace("Reason:", "").strip()
            
            # Validate category
            if category not in self.AGENT_MAP:
                logger.warning(f"Invalid category {category}, defaulting to QUERY")
                category = "QUERY"
            
            return category, reasoning
            
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            return "QUERY", "Fallback routing due to classification error"
    
    def get_routing_stats(self) -> Dict[str, Any]:
        """Get routing statistics"""
        if not self.execution_history:
            return {"total_routes": 0, "category_distribution": {}}
        
        category_counts = {}
        for record in self.execution_history:
            category = record.get("output", {}).get("category", "UNKNOWN")
            category_counts[category] = category_counts.get(category, 0) + 1
        
        return {
            "total_routes": len(self.execution_history),
            "category_distribution": category_counts,
            "agent_targets": {
                cat: self.AGENT_MAP.get(cat, "unknown")
                for cat in category_counts.keys()
            }
        }