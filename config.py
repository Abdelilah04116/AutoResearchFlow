# config.py
import os
from typing import Optional

class Config:
    """Configuration centralisée pour le système multi-agent"""
    
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
    def get_gemini_api_key(cls) -> Optional[str]:
        import os
        return os.getenv("GEMINI_API_KEY")

    @classmethod
    def get_tavily_api_key(cls) -> Optional[str]:
        import os
        return os.getenv("TAVILY_API_KEY")

    @classmethod
    def validate(cls) -> bool:
        if not cls.get_gemini_api_key():
            raise ValueError("GEMINI_API_KEY n'est pas définie")
        if not cls.get_tavily_api_key():
            raise ValueError("TAVILY_API_KEY n'est pas définie")
        return True