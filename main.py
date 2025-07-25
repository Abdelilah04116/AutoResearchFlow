# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import time
from datetime import datetime

from orchestrator import orchestrator
from models import ResearchRequest, ResearchOutput, SearchResult, AgentState
from config import Config

from dotenv import load_dotenv
load_dotenv()

from config import Config
Config.validate()

import os
print("GEMINI_API_KEY =", os.getenv("GEMINI_API_KEY"))

# Configuration de l'application FastAPI
app = FastAPI(
    title="Assistant de Recherche Multi-Agent",
    description="Système multi-agent orchestré avec LangGraph pour la recherche intelligente",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    agents_available: bool

class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None
    timestamp: datetime

@app.get("/", response_model=Dict[str, str])
async def root():
    """Point d'entrée de l'API"""
    return {
        "message": "Assistant de Recherche Multi-Agent",
        "version": "1.0.0",
        "status": "operational",
        "documentation": "/docs"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Vérification de l'état de santé du système"""
    try:
        Config.validate()
        agents_available = True
    except Exception:
        agents_available = False
    
    return HealthResponse(
        status="healthy" if agents_available else "degraded",
        timestamp=datetime.now(),
        agents_available=agents_available
    )

@app.post("/research", response_model=ResearchOutput)
async def research(request: ResearchRequest):
    """
    Endpoint principal pour effectuer une recherche avec le système multi-agent
    
    Args:
        request: Requête de recherche contenant la query et les paramètres
    
    Returns:
        ResearchOutput: Résultat complet de la recherche
    """
    start_time = time.time()
    
    try:
        # Validation des paramètres
        if not request.query.strip():
            raise HTTPException(
                status_code=400, 
                detail="La requête de recherche ne peut pas être vide"
            )
        
        # Traitement par le système multi-agent
        result_state = await orchestrator.process_research_request(
            query=request.query,
            style=request.style
        )
        
        # Vérification des erreurs
        if result_state.error_message:
            raise HTTPException(
                status_code=500,
                detail=f"Erreur du système multi-agent: {result_state.error_message}"
            )
        
        # Construction de la réponse
        search_results = []
        if result_state.search_results:
            for result in result_state.search_results:
                search_results.append(SearchResult(
                    title=result.get('title', ''),
                    url=result.get('url', ''),
                    content=result.get('content', ''),
                    score=result.get('score')
                ))
        
        processing_time = time.time() - start_time
        
        output = ResearchOutput(
            query=result_state.query,
            final_content=result_state.final_result or "Contenu non disponible",
            search_results=search_results,
            summary=result_state.summary or "Résumé non disponible",
            edited_content=result_state.edited_content or "Contenu édité non disponible",
            validation_status=result_state.validation_approved or False,
            feedback=result_state.feedback,
            timestamp=result_state.timestamp,
            processing_time=round(processing_time, 2)
        )
        
        return output
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur interne du serveur: {str(e)}"
        )

@app.get("/memory", response_model=Dict[str, Any])
async def get_memory():
    """
    Récupère l'historique des recherches stockées en mémoire
    
    Returns:
        Dict contenant l'historique des recherches
    """
    try:
        memory_data = orchestrator.get_memory_history()
        return memory_data
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération de la mémoire: {str(e)}"
        )

@app.get("/memory/stats", response_model=Dict[str, Any])
async def get_memory_stats():
    """
    Récupère les statistiques de l'historique des recherches
    
    Returns:
        Dict contenant les statistiques
    """
    try:
        memory_data = orchestrator.get_memory_history()
        
        if 'error' in memory_data:
            return memory_data
        
        history = memory_data.get('research_history', [])
        
        # Calcul des statistiques
        total_searches = len(history)
        approved_searches = sum(1 for item in history if item.get('validation_approved', False))
        
        styles_used = {}
        for item in history:
            style = item.get('style', 'unknown')
            styles_used[style] = styles_used.get(style, 0) + 1
        
        stats = {
            'total_searches': total_searches,
            'approved_searches': approved_searches,
            'approval_rate': round(approved_searches / total_searches * 100, 2) if total_searches > 0 else 0,
            'styles_used': styles_used,
            'last_search': history[-1]['timestamp'] if history else None
        }
        
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du calcul des statistiques: {str(e)}"
        )

@app.delete("/memory", response_model=Dict[str, str])
async def clear_memory():
    """
    Efface l'historique des recherches
    
    Returns:
        Message de confirmation
    """
    try:
        import os
        from config import Config
        
        if os.path.exists(Config.MEMORY_FILE):
            os.remove(Config.MEMORY_FILE)
            return {"message": "Mémoire effacée avec succès"}
        else:
            return {"message": "Aucune mémoire à effacer"}
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'effacement de la mémoire: {str(e)}"
        )

# Point d'entrée pour le développement
if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Démarrage de l'Assistant de Recherche Multi-Agent")
    print("📋 Configuration:")
    print(f"   - Modèle Gemini: {Config.GEMINI_MODEL}")
    print(f"   - Fichier mémoire: {Config.MEMORY_FILE}")
    print(f"   - Max résultats Tavily: {Config.TAVILY_MAX_RESULTS}")
    print("=" * 50)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )