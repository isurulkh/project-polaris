"""
Base Agent Class for Multi-Agent Architecture
"""

import logging
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from datetime import datetime

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the system
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        llm,
        **kwargs
    ):
        """
        Initialize base agent
        
        Args:
            name: Agent name
            description: Agent description
            llm: Language model instance
            **kwargs: Additional configuration
        """
        self.name = name
        self.description = description
        self.llm = llm
        self.config = kwargs
        self.execution_history: List[Dict] = []
        
        logger.info(f"Initialized agent: {name}")
    
    @abstractmethod
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute agent's main functionality
        
        Args:
            input_data: Input dictionary with query and context
            
        Returns:
            Result dictionary
        """
        pass
    
    def _log_execution(
        self,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        execution_time: float
    ):
        """Log agent execution for monitoring"""
        execution_record = {
            "timestamp": datetime.now().isoformat(),
            "agent": self.name,
            "input": input_data,
            "output": output_data,
            "execution_time": execution_time,
        }
        self.execution_history.append(execution_record)
        
        # Keep only last 100 executions
        if len(self.execution_history) > 100:
            self.execution_history = self.execution_history[-100:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics"""
        return {
            "name": self.name,
            "description": self.description,
            "total_executions": len(self.execution_history),
            "config": self.config
        }
    
    def reset_history(self):
        """Clear execution history"""
        self.execution_history = []


class AgentResult:
    """
    Standardized agent result format
    """
    
    def __init__(
        self,
        success: bool,
        data: Any,
        agent_name: str,
        metadata: Optional[Dict] = None,
        error: Optional[str] = None
    ):
        """
        Initialize agent result
        
        Args:
            success: Whether execution was successful
            data: Result data
            agent_name: Name of executing agent
            metadata: Additional metadata
            error: Error message if failed
        """
        self.success = success
        self.data = data
        self.agent_name = agent_name
        self.metadata = metadata or {}
        self.error = error
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "success": self.success,
            "data": self.data,
            "agent_name": self.agent_name,
            "metadata": self.metadata,
            "error": self.error,
            "timestamp": self.timestamp.isoformat()
        }
    
    def __repr__(self) -> str:
        status = "SUCCESS" if self.success else "FAILED"
        return f"AgentResult({status}, agent={self.agent_name})"