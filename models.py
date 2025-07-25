# models.py
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class AgentType(str, Enum):
    RESEARCH = "research"
    SUMMARIZER = "summarizer"
    EDITOR = "editor"
    VALIDATOR = "validator"
    FEEDBACK = "feedback"
    MEMORY = "memory"
    ORCHESTRATOR = "orchestrator"

class ResearchRequest(BaseModel):
    query: str = Field(..., description="Requête de recherche")
    style: Optional[str] = Field("académique", description="Style de sortie souhaité")
    max_results: Optional[int] = Field(5, description="Nombre maximum de résultats")

class AgentState(BaseModel):
    """État global partagé entre tous les agents"""
    query: str
    style: str = "académique"
    
    # Résultats de chaque agent
    search_results: Optional[List[Dict[str, Any]]] = None
    summary: Optional[str] = None
    edited_content: Optional[str] = None
    validation_approved: Optional[bool] = None
    feedback: Optional[str] = None
    saved_to_memory: Optional[bool] = None
    
    # Métadonnées
    timestamp: datetime = Field(default_factory=datetime.now)
    current_agent: Optional[str] = None
    error_message: Optional[str] = None
    final_result: Optional[str] = None

class SearchResult(BaseModel):
    title: str
    url: str
    content: str
    score: Optional[float] = None

class ResearchOutput(BaseModel):
    query: str
    final_content: str
    search_results: List[SearchResult]
    summary: str
    edited_content: str
    validation_status: bool
    feedback: Optional[str]
    timestamp: datetime
    processing_time: Optional[float] = None