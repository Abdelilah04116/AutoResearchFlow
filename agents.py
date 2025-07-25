# agents.py
import json
import random
import google.generativeai as genai
from tavily import TavilyClient
from typing import Dict, Any, List
from datetime import datetime
from config import Config
from models import AgentState, SearchResult

class BaseAgent:
    """Classe de base pour tous les agents"""
    
    def __init__(self, name: str):
        self.name = name
        Config.validate()
    
    def log(self, message: str):
        print(f"[{self.name}] {message}")

class ResearchAgent(BaseAgent):
    """Agent de recherche utilisant l'API Tavily"""
    
    def __init__(self):
        super().__init__("Research Agent")
        self.client = TavilyClient(api_key=Config.TAVILY_API_KEY)
    
    def execute(self, state: AgentState) -> AgentState:
        """Effectue une recherche web sur la requête"""
        self.log(f"Recherche pour: {state.query}")
        
        try:
            response = self.client.search(
                query=state.query,
                max_results=Config.TAVILY_MAX_RESULTS,
                search_depth=Config.TAVILY_SEARCH_DEPTH,
                include_answer=True,
                include_raw_content=True
            )
            
            search_results = []
            for result in response.get('results', []):
                search_results.append({
                    'title': result.get('title', ''),
                    'url': result.get('url', ''),
                    'content': result.get('content', ''),
                    'score': result.get('score', 0.0)
                })
            
            state.search_results = search_results
            state.current_agent = self.name
            self.log(f"Trouvé {len(search_results)} résultats")
            
        except Exception as e:
            state.error_message = f"Erreur de recherche: {str(e)}"
            self.log(f"Erreur: {state.error_message}")
        
        return state

class SummarizerAgent(BaseAgent):
    """Agent de résumé utilisant Gemini"""
    
    def __init__(self):
        super().__init__("Summarizer Agent")
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(Config.GEMINI_MODEL)
    
    def execute(self, state: AgentState) -> AgentState:
        """Résume les résultats de recherche"""
        if not state.search_results:
            state.error_message = "Aucun résultat de recherche à résumer"
            return state
        
        self.log("Génération du résumé...")
        
        try:
            # Prépare le contenu pour le résumé
            content = f"Requête: {state.query}\n\n"
            for i, result in enumerate(state.search_results, 1):
                content += f"Source {i}: {result['title']}\n{result['content']}\n\n"
            
            prompt = f"""
            Tu es un expert en synthèse d'information. Résume les informations suivantes de manière claire et structurée.
            
            {content}
            
            Instructions:
            - Crée un résumé cohérent et informatif
            - Organise les informations par thèmes principaux
            - Cite les sources importantes
            - Garde un ton objectif et professionnel
            - Limite à 500 mots maximum
            """
            
            response = self.model.generate_content(prompt)
            state.summary = response.text
            state.current_agent = self.name
            self.log("Résumé généré avec succès")
            
        except Exception as e:
            state.error_message = f"Erreur de résumé: {str(e)}"
            self.log(f"Erreur: {state.error_message}")
        
        return state

class EditorAgent(BaseAgent):
    """Agent d'édition utilisant Gemini"""
    
    def __init__(self):
        super().__init__("Editor Agent")
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(Config.GEMINI_MODEL)
    
    def execute(self, state: AgentState) -> AgentState:
        """Édite et reformule le contenu selon le style demandé"""
        if not state.summary:
            state.error_message = "Aucun résumé à éditer"
            return state
        
        self.log(f"Édition dans le style: {state.style}")
        
        try:
            prompt = f"""
            Tu es un rédacteur expert. Reformule le texte suivant dans un style {state.style}.
            
            Texte original:
            {state.summary}
            
            Instructions pour le style '{state.style}':
            - Si académique: utilise un langage précis, des références, une structure claire
            - Si journalistique: rends le texte accessible, utilise des titres accrocheurs
            - Si technique: utilise la terminologie appropriée, sois précis
            - Si vulgarisation: simplifie les concepts, utilise des exemples
            
            Conserve toute l'information importante tout en adaptant le style.
            """
            
            response = self.model.generate_content(prompt)
            state.edited_content = response.text
            state.current_agent = self.name
            self.log("Édition terminée avec succès")
            
        except Exception as e:
            state.error_message = f"Erreur d'édition: {str(e)}"
            self.log(f"Erreur: {state.error_message}")
        
        return state

class HumanValidatorAgent(BaseAgent):
    """Agent de validation humaine (simulée)"""
    
    def __init__(self):
        super().__init__("Human Validator Agent")
    
    def execute(self, state: AgentState) -> AgentState:
        """Simule une validation humaine"""
        if not state.edited_content:
            state.error_message = "Aucun contenu à valider"
            return state
        
        self.log("Validation du contenu...")
        
        # Simulation simple: 90% de chance d'approbation
        # En production, ceci serait une interface utilisateur
        approval_chance = 0.9
        state.validation_approved = random.random() < approval_chance
        
        state.current_agent = self.name
        
        if state.validation_approved:
            self.log("✅ Contenu approuvé")
        else:
            self.log("❌ Contenu rejeté - révision nécessaire")
        
        return state

class FeedbackAgent(BaseAgent):
    """Agent de collecte de feedback"""
    
    def __init__(self):
        super().__init__("Feedback Agent")
    
    def execute(self, state: AgentState) -> AgentState:
        """Collecte des feedbacks (simulés)"""
        self.log("Collecte des feedbacks...")
        
        # Simulation de feedbacks variés
        positive_feedback = [
            "Excellente synthèse, très claire et complète",
            "Bon travail sur la structuration de l'information",
            "Les sources sont pertinentes et bien utilisées"
        ]
        
        negative_feedback = [
            "Le contenu pourrait être plus détaillé",
            "Certaines informations semblent manquer",
            "Le style pourrait être amélioré"
        ]
        
        if state.validation_approved:
            state.feedback = random.choice(positive_feedback)
        else:
            state.feedback = random.choice(negative_feedback)
        
        state.current_agent = self.name
        self.log(f"Feedback collecté: {state.feedback}")
        
        return state

class MemoryAgent(BaseAgent):
    """Agent de mémorisation"""
    
    def __init__(self):
        super().__init__("Memory Agent")
    
    def execute(self, state: AgentState) -> AgentState:
        """Sauvegarde les résultats dans un fichier JSON"""
        if not state.edited_content:
            state.error_message = "Aucun contenu à sauvegarder"
            return state
        
        self.log("Sauvegarde en mémoire...")
        
        try:
            # Prépare les données à sauvegarder
            memory_data = {
                'timestamp': state.timestamp.isoformat(),
                'query': state.query,
                'style': state.style,
                'final_content': state.edited_content,
                'validation_approved': state.validation_approved,
                'feedback': state.feedback,
                'search_count': len(state.search_results) if state.search_results else 0
            }
            
            # Charge la mémoire existante
            try:
                with open(Config.MEMORY_FILE, 'r', encoding='utf-8') as f:
                    memory = json.load(f)
            except FileNotFoundError:
                memory = {'research_history': []}
            
            # Ajoute la nouvelle entrée
            memory['research_history'].append(memory_data)
            
            # Sauvegarde
            with open(Config.MEMORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(memory, f, ensure_ascii=False, indent=2)
            
            state.saved_to_memory = True
            state.current_agent = self.name
            self.log(f"Sauvegardé dans {Config.MEMORY_FILE}")
            
        except Exception as e:
            state.error_message = f"Erreur de sauvegarde: {str(e)}"
            self.log(f"Erreur: {state.error_message}")
        
        return state