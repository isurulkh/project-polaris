"""
Summary API Endpoints
"""

import logging
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter()


class SummaryRequest(BaseModel):
    """Summary request model"""
    query: str = Field(..., description="Topic or focus for summary")
    summary_type: str = Field(
        default="comprehensive",
        description="Type of summary: brief, comprehensive, executive"
    )
    max_docs: int = Field(default=10, ge=1, le=50, description="Maximum documents to analyze")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Metadata filters")


class SummaryResponse(BaseModel):
    """Summary response model"""
    success: bool
    summary: str
    key_points: List[str]
    insights: List[str]
    num_documents_analyzed: int
    document_sources: List[Dict[str, str]]
    metadata: Dict[str, Any]


class CompareRequest(BaseModel):
    """Request model for document comparison"""
    query: str = Field(..., description="Comparison topic")
    filters: Optional[List[Dict[str, Any]]] = Field(default=None, description="Metadata filters")


@router.post("/summarize", response_model=SummaryResponse)
async def summarize_documents(
    request: SummaryRequest,
    polaris=Depends(lambda: __import__('src.api.main', fromlist=['polaris']).polaris)
):
    """
    Generate a summary from relevant documents
    
    This endpoint:
    1. Retrieves documents related to the query/topic
    2. Generates a comprehensive summary using Gemini Pro
    3. Extracts key points and insights
    4. Provides source attribution
    
    Summary types:
    - brief: Short, concise summary (3-5 sentences)
    - comprehensive: Detailed analysis with multiple paragraphs
    - executive: Business-focused summary for stakeholders
    """
    try:
        logger.info(f"Generating {request.summary_type} summary for: {request.query[:100]}...")
        
        # Execute summary agent
        result = polaris.summary_agent.execute({
            "query": request.query,
            "summary_type": request.summary_type,
            "max_docs": request.max_docs,
            "filters": request.filters
        })
        
        if not result.success:
            raise HTTPException(status_code=500, detail=result.error)
        
        data = result.data
        
        return SummaryResponse(
            success=True,
            summary=data["summary"],
            key_points=data["key_points"],
            insights=data["insights"],
            num_documents_analyzed=data["num_documents_analyzed"],
            document_sources=data["document_sources"],
            metadata={
                "summary_type": data["summary_type"],
                "execution_time": result.metadata.get("execution_time"),
                "summary_length": result.metadata.get("summary_length")
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Summarization failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare")
async def compare_documents(
    request: CompareRequest,
    polaris=Depends(lambda: __import__('src.api.main', fromlist=['polaris']).polaris)
):
    """
    Compare documents on a specific topic
    
    Performs comparative analysis across multiple document sets
    """
    try:
        result = polaris.summary_agent.compare_documents(
            query=request.query,
            filters=request.filters
        )
        
        return {
            "success": True,
            "comparison": result
        }
        
    except Exception as e:
        logger.error(f"Comparison failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_summary_stats(
    polaris=Depends(lambda: __import__('src.api.main', fromlist=['polaris']).polaris)
):
    """Get summary agent statistics"""
    try:
        return {
            "success": True,
            "agent_stats": polaris.summary_agent.get_stats()
        }
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))