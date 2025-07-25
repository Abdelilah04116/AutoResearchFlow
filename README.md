# 🤖 Assistant de Recherche Multi-Agent

Un système multi-agent intelligent orchestré avec **LangGraph** pour la recherche et l'analyse d'informations. Ce projet utilise plusieurs agents spécialisés qui collaborent pour produire des analyses de haute qualité.

## 🏗️ Architecture

Le système est composé de **7 agents spécialisés** :

1. **🔎 Research Agent** : Effectue des recherches web via l'API Tavily
2. **📝 Summarizer Agent** : Résume les résultats avec Gemini 2.0 Flash
3. **✍️ Editor Agent** : Reformule et adapte le style du contenu
4. **✅ Human Validator Agent** : Simule une validation humaine
5. **📥 Feedback Agent** : Collecte des retours utilisateur
6. **💾 Memory Agent** : Sauvegarde les résultats en JSON
7. **🧠 Orchestrator Agent** : Coordonne tous les agents via LangGraph

## 🚀 Installation

### Prérequis

- Python 3.11+
- Clés API :
  - [Google Gemini API](https://makersuite.google.com/app/apikey)
  - [Tavily API](https://tavily.com/)

### Installation locale

```bash
# Cloner le projet
git clone <votre-repo>
cd assistant-recherche-multi-agent

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Éditez .env avec vos clés API
```

### Installation avec Docker

```bash
# Configurer les variables d'environnement
cp .env.example .env
# Éditez .env avec vos clés API

# Lancer avec Docker Compose
docker-compose up --build
```

## 🔧 Configuration

Créez un fichier `.env` avec vos clés API :

```bash
GEMINI_API_KEY=your_gemini_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

## 🎯 Utilisation

### Démarrage du serveur

```bash
python main.py
```

Le serveur sera accessible sur `http://localhost:8000`

### Interface API

- **Documentation** : `http://localhost:8000/docs`
- **Interface Redoc** : `http://localhost:8000/redoc`

### Endpoints principaux

#### 🔍 Recherche
```bash
POST /research
```

Exemple de requête :
```json
{
  "query": "Intelligence artificielle générative en 2024",
  "style": "académique",
  "max_results": 5
}
```

#### 🧠 Mémoire
```bash
GET /memory          # Récupérer l'historique
GET /memory/stats    # Statistiques
DELETE /memory       # Effacer l'historique
```

#### 🏥 Santé
```bash
GET /health          # État du système
```

## 🧪 Tests

### Tests directs

```bash
# Tester l'orchestrateur directement
python example_usage.py
```

### Tests API

```bash
# Démarrer le serveur dans un terminal
python main.py

# Dans un autre terminal, tester les endpoints
python -c "from example_usage import test_api_endpoints; test_api_endpoints()"
```

## 📁 Structure du projet

```
assistant-recherche-multi-agent/
├── main.py              # Point d'entrée FastAPI
├── orchestrator.py      # Orchestrateur LangGraph
├── agents.py           # Tous les agents spécialisés
├── models.py           # Modèles Pydantic
├── config.py           # Configuration centralisée
├── example_usage.py    # Scripts de test et exemples
├── requirements.txt    # Dépendances Python
├── Dockerfile         # Configuration Docker
├── docker-compose.yml # Orchestration Docker
├── .env.example       # Exemple de configuration
└── README.md          # Documentation
```

## 🔄 Workflow

Le système suit ce flux orchestré par LangGraph :

```
Requête → Research → Summarize → Edit → Validate
                                          ↓
                     Memory ← Feedback ← [Approved]
                                          ↓
                                    [Rejected] → Edit
```

## 🎨 Styles disponibles

- **académique** : Langage précis, références, structure claire
- **journalistique** : Accessible, titres accrocheurs
- **technique** : Terminologie spécialisée, précision
- **vulgarisation** : Concepts simplifiés, exemples

## 📊 Fonctionnalités

### ✨ Points forts

- **Architecture modulaire** : Chaque agent a une responsabilité claire
- **Orchestration intelligente** : LangGraph gère les flux complexes
- **Validation automatique** : Contrôle qualité intégré
- **Mémoire persistante** : Historique des recherches
- **API complète** : Interface REST documentée
- **Docker ready** : Déploiement simplifié

### 🔧 Personnalisation

- **Agents extensibles** : Ajoutez facilement de nouveaux agents
- **Styles configurables** : Définissez vos propres styles d'écriture
- **Paramètres ajustables** : Configuration via `config.py`

## 📈 Monitoring

Le système enregistre :
- Historique des recherches
- Temps de traitement
- Taux d'approbation
- Statistiques d'utilisation

Accédez aux métriques via `/memory/stats`

## 🚨 Gestion d'erreurs

- Validation des entrées
- Gestion des timeouts API
- Récupération automatique des erreurs
- Logs détaillés pour le débogage

## 🔒 Sécurité

- Variables d'environnement pour les API keys
- Validation des données d'entrée
- Rate limiting (configurable)
- Utilisateur non-root dans Docker

## 🤝 Contribution

1. Fork le projet
2. Créez une branche feature (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Committez vos changements (`git commit -am 'Ajout nouvelle fonctionnalité'`)
4. Push vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Créez une Pull Request

## 📝 License

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🆘 Support

- **Issues** : Utilisez GitHub Issues pour signaler des bugs
- **Documentation** : Consultez `/docs` pour l'API complète
- **Exemples** : Voir `example_usage.py` pour des cas d'usage

---

**Développé avec ❤️ en utilisant LangGraph, FastAPI et Gemini 2.0**