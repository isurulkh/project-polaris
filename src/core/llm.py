"""
Google Gemini 2.5 LLM Wrapper
Production-ready LLM initialization with error handling
"""

import logging
from typing import Optional, List, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.callbacks.base import BaseCallbackHandler
from config.settings import settings, get_gemini_config

logger = logging.getLogger(__name__)


class TokenCounterCallback(BaseCallbackHandler):
    """Callback to track token usage"""
    
    def __init__(self):
        self.total_tokens = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0
    
    def on_llm_end(self, response, **kwargs):
        """Track tokens after LLM completion"""
        if hasattr(response, 'llm_output') and response.llm_output:
            token_usage = response.llm_output.get('token_usage', {})
            self.prompt_tokens += token_usage.get('prompt_tokens', 0)
            self.completion_tokens += token_usage.get('completion_tokens', 0)
            self.total_tokens += token_usage.get('total_tokens', 0)
    
    def reset(self):
        """Reset counter"""
        self.total_tokens = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0


class GeminiLLM:
    """
    Gemini 2.5 LLM wrapper with model selection and configuration
    """
    
    def __init__(self):
        """Initialize Gemini LLM instances"""
        self.flash_model = self._create_llm("flash")
        self.pro_model = self._create_llm("pro")
        self.token_callback = TokenCounterCallback()
        
        logger.info("Initialized Gemini LLM models")
    
    def _create_llm(
        self,
        model_type: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        callbacks: Optional[List[BaseCallbackHandler]] = None
    ) -> ChatGoogleGenerativeAI:
        """
        Create Gemini LLM instance
        
        Args:
            model_type: "flash" for fast queries, "pro" for complex tasks
            temperature: Override default temperature
            max_tokens: Override default max tokens
            callbacks: List of callback handlers
            
        Returns:
            ChatGoogleGenerativeAI instance
        """
        try:
            config = get_gemini_config(model_type)
            
            if temperature is not None:
                config["temperature"] = temperature
            if max_tokens is not None:
                config["max_output_tokens"] = max_tokens
            
            # Add callbacks
            config["callbacks"] = callbacks or []
            
            # Additional safety and generation settings - removed as they cause validation errors
            # Safety settings should be configured differently in newer versions
            
            llm = ChatGoogleGenerativeAI(**config)
            
            logger.info(f"Created {model_type} model: {config['model']}")
            return llm
            
        except Exception as e:
            logger.error(f"Failed to create {model_type} LLM: {e}")
            raise
    
    def get_flash_model(
        self,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> ChatGoogleGenerativeAI:
        """
        Get Gemini Flash model (fast, efficient)
        Best for: Quick queries, routing, classification
        
        Args:
            temperature: Override temperature
            max_tokens: Override max tokens
            
        Returns:
            ChatGoogleGenerativeAI instance
        """
        if temperature is not None or max_tokens is not None:
            return self._create_llm(
                "flash",
                temperature=temperature,
                max_tokens=max_tokens,
                callbacks=[self.token_callback]
            )
        return self.flash_model
    
    def get_pro_model(
        self,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> ChatGoogleGenerativeAI:
        """
        Get Gemini Pro model (powerful, high-quality)
        Best for: Summaries, complex analysis, detailed responses
        
        Args:
            temperature: Override temperature
            max_tokens: Override max tokens
            
        Returns:
            ChatGoogleGenerativeAI instance
        """
        if temperature is not None or max_tokens is not None:
            return self._create_llm(
                "pro",
                temperature=temperature,
                max_tokens=max_tokens,
                callbacks=[self.token_callback]
            )
        return self.pro_model
    
    def get_model(
        self,
        task_type: str = "query",
        **kwargs
    ) -> ChatGoogleGenerativeAI:
        """
        Get appropriate model based on task type
        
        Args:
            task_type: Type of task (query, summary, analysis, routing)
            **kwargs: Additional configuration
            
        Returns:
            Appropriate ChatGoogleGenerativeAI instance
        """
        task_model_map = {
            "query": "flash",
            "routing": "flash",
            "classification": "flash",
            "extraction": "flash",
            "summary": "pro",
            "analysis": "pro",
            "synthesis": "pro",
            "creative": "pro",
        }
        
        model_type = task_model_map.get(task_type, "flash")
        
        if model_type == "pro":
            return self.get_pro_model(**kwargs)
        else:
            return self.get_flash_model(**kwargs)
    
    def get_token_usage(self) -> Dict[str, int]:
        """Get current token usage statistics"""
        return {
            "total_tokens": self.token_callback.total_tokens,
            "prompt_tokens": self.token_callback.prompt_tokens,
            "completion_tokens": self.token_callback.completion_tokens,
        }
    
    def reset_token_counter(self):
        """Reset token usage counter"""
        self.token_callback.reset()


# Global LLM instance
_gemini_llm = None


def get_gemini_llm() -> GeminiLLM:
    """Get or create global Gemini LLM instance"""
    global _gemini_llm
    if _gemini_llm is None:
        _gemini_llm = GeminiLLM()
    return _gemini_llm