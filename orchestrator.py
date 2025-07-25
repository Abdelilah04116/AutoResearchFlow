# orchestrator.py
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from agents import (
    ResearchAgent, SummarizerAgent, EditorAgent, 
    HumanValidatorAgent, FeedbackAgent, MemoryAgent
)
from models import AgentState
from datetime import datetime

class MultiAgentOrchestrator:
    """Orchestrateur principal utilisant LangGraph"""
    
    def __init__(self):
        self.research_agent = ResearchAgent()
        self.summarizer_agent = SummarizerAgent()
        self.editor_agent = EditorAgent()
        self.validator_agent = HumanValidatorAgent()
        self.feedback_agent = FeedbackAgent()
        self.memory_agent = MemoryAgent()
        
        # Construction du graphe LangGraph
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Construit le workflow avec LangGraph"""
        
        # Création du graphe d'état
        workflow = StateGraph(AgentState)
        
        # Ajout des nœuds (agents)
        workflow.add_node("research", self._research_node)
        workflow.add_node("summarize", self._summarize_node)
        workflow.add_node("edit", self._edit_node)
        workflow.add_node("validate", self._validate_node)
        workflow.add_node("feedback_node", self._feedback_node)
        workflow.add_node("memory", self._memory_node)
        workflow.add_node("finalize", self._finalize_node)
        
        # Définition du flux
        workflow.set_entry_point("research")
        
        # Flux principal
        workflow.add_edge("research", "summarize")
        workflow.add_edge("summarize", "edit")
        workflow.add_edge("edit", "validate")
        
        # Branchement conditionnel après validation
        workflow.add_conditional_edges(
            "validate",
            self._should_continue_after_validation,
            {
                "approved": "feedback_node",
                "rejected": "edit",  # Retour à l'édition
                "error": END
            }
        )
        
        workflow.add_edge("feedback_node", "memory")
        workflow.add_edge("memory", "finalize")
        workflow.add_edge("finalize", END)
        
        return workflow.compile()
    
    def _research_node(self, state: AgentState) -> dict:
        """Nœud de recherche"""
        return self.research_agent.execute(state).__dict__
    
    def _summarize_node(self, state: AgentState) -> dict:
        """Nœud de résumé"""
        return self.summarizer_agent.execute(state).__dict__
    
    def _edit_node(self, state: dict) -> dict:
        """Nœud d'édition avec instructions humaines si présentes"""
        human_instructions = state.get("human_instructions")
        # Reconstruire AgentState si besoin
        from models import AgentState
        agent_state = AgentState(**state)
        return self.editor_agent.execute(agent_state, human_instructions).__dict__
    
    def _validate_node(self, state: AgentState) -> dict:
        """Nœud de validation"""
        return self.validator_agent.execute(state).__dict__
    
    def _feedback_node(self, state: AgentState) -> dict:
        """Nœud de feedback"""
        return self.feedback_agent.execute(state).__dict__
    
    def _memory_node(self, state: AgentState) -> dict:
        """Nœud de mémorisation"""
        return self.memory_agent.execute(state).__dict__
    
    def _finalize_node(self, state: AgentState) -> dict:
        """Nœud de finalisation"""
        if state.edited_content and state.validation_approved:
            state.final_result = state.edited_content
        else:
            state.final_result = "Traitement incomplet ou rejeté"
        return state.__dict__
    
    def _should_continue_after_validation(self, state) -> str:
        """Fonction de décision après validation"""
        if state.get("error_message"):
            return "error"
        elif state.get("validation_approved"):
            return "approved"
        else:
            return "rejected"
    
    async def process_research_request(self, query: str, style: str = "académique") -> dict:
        """Traite une demande de recherche complète"""
        
        # État initial sous forme de dictionnaire avec timestamp
        initial_state = {
            "query": query,
            "style": style,
            "timestamp": datetime.now()
        }
        
        print(f"🚀 Démarrage du processus de recherche pour: '{query}'")
        print(f"📝 Style demandé: {style}")
        print("-" * 50)
        
        # Exécution du workflow
        try:
            final_state = await self.workflow.ainvoke(initial_state)
            
            print("-" * 50)
            if final_state.get("final_result"):
                print("✅ Processus terminé avec succès!")
            elif final_state.get("error_message"):
                print(f"❌ Erreur dans l'orchestration: {final_state.get('error_message')}")
            else:
                print("❌ Processus terminé avec des erreurs")
            
            return final_state
            
        except Exception as e:
            print(f"❌ Erreur dans l'orchestration: {str(e)}")
            initial_state["error_message"] = f"Erreur d'orchestration: {str(e)}"
            return initial_state
    
    def get_memory_history(self) -> Dict[str, Any]:
        """Récupère l'historique des recherches"""
        try:
            import json
            from config import Config
            
            with open(Config.MEMORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {'research_history': []}
        except Exception as e:
            return {'error': f"Erreur de lecture mémoire: {str(e)}"}

# Instance globale de l'orchestrateur
orchestrator = MultiAgentOrchestrator()