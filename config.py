# config.py
import os
from typing import Optional

class Config:
    """Configuration centralisée pour le système multi-agent"""
    
    # API Keys
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    TAVILY_API_KEY: Optional[str] = os.getenv("TAVILY_API_KEY")
    
    # Paramètres des modèles
    GEMINI_MODEL: str = "gemini-2.0-flash-exp"
    GEMINI_TEMPERATURE: float = 0.7
    GEMINI_MAX_TOKENS: int = 4000
    
    # Paramètres de recherche
    TAVILY_MAX_RESULTS: int = 5
    TAVILY_SEARCH_DEPTH: str = "advanced"
    
    # Chemins des fichiers
    MEMORY_FILE: str = "research_memory.json"
    
    @classmethod
    def validate(cls) -> bool:
        """Valide que toutes les clés API sont configurées"""
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY n'est pas définie")
        if not cls.TAVILY_API_KEY:
            raise ValueError("TAVILY_API_KEY n'est pas définie")
        return True