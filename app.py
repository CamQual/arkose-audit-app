import streamlit as st
from google import genai
from google.genai import types
import requests
import json
from datetime import datetime
import re

# --- CONFIGURATION ---
SALLES_ARKOSE = {
    "Montreuil": "342457aab0148128933fe069f5899250",
    "Bordeaux": "342457aab01481c29bb2f231d970f528",
    "Massy": "342457aab01481aab2f8ca7fdd3404ae",
    "Nation": "343457aab014812292f3d2c5aff2cf64",
    "Prado": "342457aab01481beb7f5f07a1771bb30",
    "Genevois": "342457aab0148130af0dd6d81b5a6a70",
    "Tours": "342457aab01481e29cecdaa9e1d5bd21",
    "Pantin Voie": "342457aab0148154b194c85d6bf37a7d",
    "Pantin Bloc": "342457aab01481beb4daff69b0a3da36",
    "Issy Voie": "342457aab01481ccbed0d0a7be05e28a",
    "Issy Bloc": "342457aab01481328b8bda542d61eef1",
    "Rouen": "342457aab01481b29b72f4ed445a9562",
    "Toulouse": "342457aab0148160b0fee34a57bb484e",
    "Nice": "342457aab014814cb575d3498d0242ac",
    "Lille": "342457aab0148143a99dc43e8f4b7d22",
    "Didot": "342457aab01481a19896f3223db047ed",
    "Pont de Sèvres": "342457aab01481079a62d519a238706a",
    "Canal": "342457aab01480f1bc09d89e923aee6e",
    "Strasbourg Saint Denis": "342457aab01481f2aaebd2d9955e73ec",
    "Nanterre": "342457aab01481bd9916f46b3f9ad295",
    "Montmartre": "342457aab01481c2b7e8cdb57558af81",
    "Chevaleret": "342457aab01480db94d7d49ebb5472a3",
    "Saint Denis - CAO": "342457aab01481dc8ebbf88df7c120a8"
}

st.set_page_config(page_title="Audit Arkose", page_icon="🧗", layout="centered")

# --- STYLE ARKOSE ---
st.markdown("""
    <style>
    /* Import d'une police proche de Roc Grotesk si non installée */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Helvetica Neue', 'Helvetica', 'Arial', sans-serif;
    }
    
    h1, h2, h3 {
        font-family: 'Roc Grotesk', 'Outfit', sans-serif !important;
        font-weight: 500;
        color: #1a1a1a;
    }
    
    /* Style des boutons avec le contour violet Arkose */
    div.stButton > button {
        border: 2px solid #841bf3 !important;
        border-radius: 12px !important;
        padding: 0.5rem 2rem !important;
        color: #841bf3 !important;
        background-color: transparent !important;
        font-weight: 600 !important;
        transition: all 0.3s ease;
    }
    
    div.stButton > button:hover {
        background-color: #841bf3 !important;
        color: white !important;
        border-color: #841bf3 !important;
    }

    /* Style de l'upload */
    .stFileUploader {
        border: 1px dashed #841bf3;
        border-radius: 10px;
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.image("arkose_header.png", use_container_width=True)
st.title("🧗 Audit Qualité Arkose")

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
token = st.secrets["NOTION_TOKEN"]

# --- INTERFACE ---
col1, col2 = st.columns([1, 1])
with col1:
    salle_selectionnee = st.selectbox("Établissement :", list(SALLES_ARKOSE.keys()))
with col2:
    audio = st.file_uploader("Enregistrement audio", type=['mp3', 'm4a', 'wav', 'mp4'])

db_id = SALLES_ARKOSE[salle_selectionnee]

def push_to_notion(data, database_id, salle_nom):
    url = "https://api.notion.com/v1/pages"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
    date_jour = datetime.now().strftime("%Y-%m-%d")
    
    payload = {
        "parent": {"database_id": database_id},
        "properties": {
            "Nom de la tâche": {"title": [{"text": {"content": str(data.get("nom_de_la_tache", "Sans titre"))}}]},
            "Établissement": {"select": {"name": salle_nom}},
            "La liste source": {"select": {"name": str(data.get("liste_source", "Accueil"))}},
            "Projet source": {"rich_text": [{"text": {"content": f"Audit Interne {salle_nom.upper()}"}}]},
            "Statut": {"status": {"name": "Saisie"}},
            "ITEM": {"select": {"name": str(data.get("item", "Process"))}},
            "Pole concerné": {"select": {"name": str(data.get("pole_concerne", "Exploitation"))}},
            "La prise en charge": {"select": {"name": str(data.get("prise_en_charge", "Staff"))}},
            "criticité": {"select": {"name": str(data.get("criticite", "Moyenne"))}},
            "Red flag": {"select": {"name": "Oui" if data.get("red_flag") else "Non"}},
            "Date de créa Notion": {"date": {"start": date_jour}},
            "MAJ tâche NOTION": {"date": {"start": date_jour}},
            "confiance qualification": {"rich_text": [{"text": {"content": str(data.get("confiance_qualification", "Camille"))}}]}
        }
    }
    return requests.post(url, json=payload, headers=headers)

if audio and st.button("🚀 Lancer l'analyse"):
    with st.spinner("L'IA analyse l'audio et prépare les fiches..."):
        try:
            with open("temp.m4a", "wb") as f: 
                f.write(audio.getbuffer())
            
            f_up = client.files.upload(file="temp.m4a")
            
            prompt_systeme = f"""Tu es l'assistant expert en audit qualité d'Arkose. 
Analyse l'audio pour l'établissement {salle_selectionnee}. 
Structure le résultat en JSON pour Notion.

### RÈGLES :
1. Nettoyage : Supprime les tics de langage.
2. Reformulation : Le "nom_de_la_tache" doit être court et pédagogique.
3. Vocabulaire : "Corner" -> "shop", "Studio" -> "bien être".
4. Pôle par défaut : "Exploitation".

### JSON ATTENDU (Minuscules) :
{{
  "nom_de_la_tache": "...",
  "liste_source": "...",
  "item": "...",
  "pole_concerne": "...",
  "prise_en_charge": "...",
  "criticite": "...",
  "red_flag": boolean,
  "confiance_qualification": "..."
}}"""

            # Utilisation de Gemini 2.5 Flash pour une analyse optimale
            resp = client.models.generate_content(
                model='gemini-2.5-flash', 
                contents=[f_up, "Analyse cet audit."], 
                config=types.GenerateContentConfig(
                    system_instruction=prompt_systeme,
                    response_mime_type="application/json"
                )
            )
            
            data_json = json.loads(resp.text)
            items = data_json if isinstance(data_json, list) else [data_json]

            for item in items:
                push_to_notion(item, db_id, salle_selectionnee)
            
            st.balloons()
            st.success(f"✅ {len(items)} audit(s) envoyé(s) avec succès pour {salle_selectionnee} !")

        except Exception as e:
            st.error(f"Erreur lors de l'analyse : {e}")
