# example_usage.py
"""
Script d'exemple pour tester le système multi-agent
"""
import asyncio
import requests
import json
from orchestrator import orchestrator

async def test_orchestrator_direct():
    """Test direct de l'orchestrateur sans passer par l'API"""
    print("🧪 Test direct de l'orchestrateur")
    print("=" * 50)
    
    # Test avec différents styles
    test_queries = [
        ("Intelligence artificielle générative", "académique"),
        ("Changement climatique 2024", "journalistique"),
        ("Blockchain et cryptomonnaies", "vulgarisation")
    ]
    
    for query, style in test_queries:
        print(f"\n📝 Test: '{query}' (style: {style})")
        print("-" * 30)
        
        try:
            result = await orchestrator.process_research_request(query, style)
            
            if result.final_result:
                print("✅ Succès!")
                print(f"📊 Résultats trouvés: {len(result.search_results) if result.search_results else 0}")
                print(f"✍️ Contenu final: {result.final_result[:200]}...")
                print(f"👤 Validé: {'Oui' if result.validation_approved else 'Non'}")
                print(f"💬 Feedback: {result.feedback}")
            else:
                print(f"❌ Erreur: {result.error_message}")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
        
        await asyncio.sleep(1)  # Pause entre les tests

def test_api_endpoints():
    """Test des endpoints de l'API"""
    print("\n🌐 Test des endpoints API")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test de santé
    print("\n🏥 Test endpoint /health")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
    
    # Test de recherche
    print("\n🔍 Test endpoint /research")
    try:
        payload = {
            "query": "Machine Learning tendances 2024",
            "style": "académique",
            "max_results": 3
        }
        
        response = requests.post(f"{base_url}/research", json=payload)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Succès!")
            print(f"Query: {result['query']}")
            print(f"Résultats: {len(result['search_results'])}")
            print(f"Temps de traitement: {result['processing_time']}s")
            print(f"Validé: {result['validation_status']}")
        else:
            print(f"❌ Erreur: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    # Test mémoire
    print("\n🧠 Test endpoint /memory")
    try:
        response = requests.get(f"{base_url}/memory")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            memory = response.json()
            history_count = len(memory.get('research_history', []))
            print(f"✅ Historique récupéré: {history_count} entrées")
        else:
            print(f"❌ Erreur: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    # Test statistiques
    print("\n📊 Test endpoint /memory/stats")
    try:
        response = requests.get(f"{base_url}/memory/stats")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Statistiques:")
            print(f"   Total recherches: {stats.get('total_searches', 0)}")
            print(f"   Taux d'approbation: {stats.get('approval_rate', 0)}%")
            print(f"   Styles utilisés: {stats.get('styles_used', {})}")
        else:
            print(f"❌ Erreur: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

async def demo_complete_workflow():
    """Démonstration complète du workflow"""
    print("\n🎯 Démonstration complète du workflow")
    print("=" * 50)
    
    demo_query = "Impact de l'IA sur l'emploi en 2024"
    demo_style = "journalistique"
    
    print(f"📝 Requête: {demo_query}")
    print(f"🎨 Style: {demo_style}")
    print("\n⏳ Traitement en cours...")
    
    try:
        result = await orchestrator.process_research_request(demo_query, demo_style)
        
        print("\n📋 RÉSULTATS DÉTAILLÉS:")
        print("=" * 30)
        
        if result.search_results:
            print(f"🔍 Sources trouvées: {len(result.search_results)}")
            for i, source in enumerate(result.search_results[:3], 1):
                print(f"   {i}. {source['title'][:60]}...")
        
        if result.summary:
            print(f"\n📄 Résumé ({len(result.summary)} caractères):")
            print(result.summary[:300] + "..." if len(result.summary) > 300 else result.summary)
        
        if result.edited_content:
            print(f"\n✍️ Contenu édité ({len(result.edited_content)} caractères):")
            print(result.edited_content[:300] + "..." if len(result.edited_content) > 300 else result.edited_content)
        
        print(f"\n✅ Validation: {'Approuvé' if result.validation_approved else 'Rejeté'}")
        print(f"💬 Feedback: {result.feedback}")
        print(f"💾 Sauvegardé: {'Oui' if result.saved_to_memory else 'Non'}")
        
        if result.error_message:
            print(f"\n❌ Erreurs: {result.error_message}")
            
    except Exception as e:
        print(f"❌ Erreur durant la démonstration: {str(e)}")

def display_memory_content():
    """Affiche le contenu de la mémoire"""
    print("\n🧠 Contenu de la mémoire")
    print("=" * 50)
    
    try:
        memory = orchestrator.get_memory_history()
        
        if 'error' in memory:
            print(f"❌ Erreur: {memory['error']}")
            return
        
        history = memory.get('research_history', [])
        
        if not history:
            print("📝 Aucune recherche en mémoire")
            return
        
        print(f"📊 Total: {len(history)} recherches")
        print("\n📝 Dernières recherches:")
        
        for i, entry in enumerate(history[-3:], 1):  # 3 dernières
            print(f"\n{i}. Query: {entry['query']}")
            print(f"   Style: {entry['style']}")
            print(f"   Date: {entry['timestamp'][:19]}")
            print(f"   Validé: {'✅' if entry['validation_approved'] else '❌'}")
            print(f"   Feedback: {entry['feedback'][:50]}..." if entry['feedback'] else "   Feedback: Aucun")
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")

async def main():
    """Fonction principale pour exécuter tous les tests"""
    print("🚀 SYSTÈME MULTI-AGENT - TESTS COMPLETS")
    print("=" * 60)
    
    # Variables d'environnement nécessaires
    import os
    if not os.getenv("GEMINI_API_KEY"):
        print("⚠️  Attention: GEMINI_API_KEY non définie")
    if not os.getenv("TAVILY_API_KEY"):
        print("⚠️  Attention: TAVILY_API_KEY non définie")
    
    print("\n" + "=" * 60)
    
    # 1. Test direct de l'orchestrateur
    await test_orchestrator_direct()
    
    # 2. Démonstration complète
    await demo_complete_workflow()
    
    # 3. Affichage de la mémoire
    display_memory_content()
    
    # 4. Tests API (nécessite que le serveur soit en cours d'exécution)
    print(f"\n{'='*60}")
    print("ℹ️  Pour tester les endpoints API, lancez d'abord:")
    print("   python main.py")
    print("   puis dans un autre terminal:")
    print("   python -c \"from example_usage import test_api_endpoints; test_api_endpoints()\"")
    
    print(f"\n{'='*60}")
    print("✅ Tests terminés!")

if __name__ == "__main__":
    # Exécution des tests
    asyncio.run(main())