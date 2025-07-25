from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from orchestrator import orchestrator
from models import ResearchRequest
import asyncio

st.set_page_config(page_title="Assistant de Recherche Multi-Agent", layout="wide")
st.title("🤖 Assistant de Recherche Multi-Agent (SMA)")

# --- Sidebar ---
st.sidebar.header("Paramètres de la recherche")
query = st.sidebar.text_area("Votre requête de recherche", "Qu'est-ce que l'intelligence artificielle ?")
style = st.sidebar.selectbox(
    "Style de rédaction",
    ["académique", "journalistique", "technique", "vulgarisation"]
)
launch = st.sidebar.button("Lancer la recherche multi-agent 🚀")

# --- Tabs ---
tabs = st.tabs(["Recherche", "Historique", "Statistiques", "Mémoire"])

# --- Gestion de l'état du workflow ---
if 'step' not in st.session_state:
    st.session_state.step = 0
if 'result_state' not in st.session_state:
    st.session_state.result_state = None
if 'edited_summary' not in st.session_state:
    st.session_state.edited_summary = ''
if 'user_feedback' not in st.session_state:
    st.session_state.user_feedback = ''

# --- Lancer la recherche multi-agent (jusqu'au résumé) ---
if launch:
    with st.spinner("Traitement en cours..."):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        request = ResearchRequest(query=query, style=style)
        # Lance le workflow jusqu'à l'étape résumé
        result_state = loop.run_until_complete(
            orchestrator.process_research_request(query=request.query, style=request.style)
        )
        loop.close()
    st.session_state.result_state = result_state
    st.session_state.step = 1
    st.session_state.edited_summary = result_state.get("summary") or ""
    st.session_state.user_feedback = ""

# --- Etape 1 : Affichage recherche et résumé modifiable ---
if st.session_state.step == 1 and st.session_state.result_state:
    with tabs[0]:
        st.subheader("1️⃣ Résultats de la recherche web")
        if st.session_state.result_state.get("search_results"):
            for r in st.session_state.result_state.get("search_results"):
                st.markdown(f"**{r['title']}**\n{r['url']}\n{r['content'][:300]}...")
        else:
            st.info("Aucun résultat trouvé.")

        st.subheader("2️⃣ Résumé généré")
        st.write(st.session_state.result_state.get("summary") or "Résumé non disponible")

        st.subheader("3️⃣ Instructions de modification pour l'agent d'édition")
        st.session_state.human_instructions = st.text_area(
            "Écrivez ici vos instructions pour modifier le texte édité (ex: remplacer X par Y, supprimer le paragraphe 2, etc.) :",
            getattr(st.session_state, 'human_instructions', ''),
            height=120
        )
        if st.button("Appliquer les instructions humaines"):
            # Ajoute les instructions à l'état et relance l'édition
            st.session_state.result_state["human_instructions"] = st.session_state.human_instructions
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            # Appelle uniquement le nœud d'édition avec instructions
            from orchestrator import orchestrator
            edited_state = orchestrator._edit_node(st.session_state.result_state)
            loop.close()
            st.session_state.result_state.update(edited_state)
            st.session_state.step = 2

# --- Etape 2 : Affichage du texte édité par l'agent après instructions humaines ---
if st.session_state.step == 2:
    with tabs[0]:
        st.subheader("4️⃣ Texte édité par l'agent après instructions humaines")
        st.write(st.session_state.result_state.get("edited_content") or "Contenu édité non disponible")
        valider = st.button("✅ Valider le contenu édité")
        rejeter = st.button("❌ Rejeter le contenu édité")
        if valider or rejeter:
            st.session_state.result_state["validation_approved"] = valider
            st.session_state.step = 3

# --- Etape 3 : Feedback utilisateur ---
if st.session_state.step == 3:
    with tabs[0]:
        st.subheader("4️⃣ Feedback utilisateur (manuel)")
        st.session_state.user_feedback = st.text_area(
            "Votre feedback sur le contenu :",
            st.session_state.user_feedback,
            height=100
        )
        if st.button("Envoyer le feedback et finaliser"):
            st.session_state.result_state["feedback"] = st.session_state.user_feedback
            st.session_state.step = 4

# --- Etape 4 : Sauvegarde et affichage final ---
if st.session_state.step == 4:
    with tabs[0]:
        st.subheader("5️⃣ Sauvegarde en mémoire et résultat final")
        # Simule la sauvegarde en mémoire (appelle le MemoryAgent si besoin)
        st.session_state.result_state["saved_to_memory"] = True
        st.session_state.result_state["final_result"] = st.session_state.result_state.get("edited_content")
        st.success("Résultat sauvegardé en mémoire.")
        st.write("Résultat final :")
        st.write(st.session_state.result_state.get("final_result") or "Non disponible")
        if st.button("Nouvelle recherche"):
            st.session_state.step = 0
            st.session_state.result_state = None
            st.session_state.edited_summary = ''
            st.session_state.user_feedback = ''

# --- Historique ---
with tabs[1]:
    st.subheader("Historique des recherches")
    memory = orchestrator.get_memory_history()
    history = memory.get('research_history', [])
    if history:
        for item in reversed(history):
            st.markdown(f"**{item['timestamp']}** | *{item['style']}* | {item['query']}")
            st.write(item['final_content'][:300] + "...")
            st.write(f"Validation : {'✅' if item.get('validation_approved') else '❌'} | Feedback : {item.get('feedback', '')}")
            st.markdown("---")
    else:
        st.info("Aucune recherche en mémoire.")

# --- Statistiques ---
with tabs[2]:
    st.subheader("Statistiques d'utilisation")
    stats = orchestrator.get_memory_history()
    history = stats.get('research_history', [])
    total = len(history)
    approved = sum(1 for h in history if h.get('validation_approved'))
    st.metric("Total recherches", total)
    st.metric("Recherches validées", approved)
    st.metric("Taux de validation", f"{(approved/total*100) if total else 0:.1f}%")
    styles = {}
    for h in history:
        s = h.get('style', 'inconnu')
        styles[s] = styles.get(s, 0) + 1
    st.write("Styles utilisés :", styles)

# --- Mémoire (reset) ---
with tabs[3]:
    st.subheader("Gestion de la mémoire")
    if st.button("Effacer la mémoire des recherches"):
        import os
        from config import Config
        if os.path.exists(Config.MEMORY_FILE):
            os.remove(Config.MEMORY_FILE)
            st.success("Mémoire effacée !")
        else:
            st.info("Aucune mémoire à effacer.")
    else:
        st.info("Utilisez ce bouton pour réinitialiser l'historique des recherches.") 