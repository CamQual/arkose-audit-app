import streamlit as st
from google import genai
from google.genai import types
import requests
import json
from datetime import datetime
import re

# --- CONFIGURATION DES SALLES ---
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

# --- INTERFACE ET DESIGN ---
st.set_page_config(page_title="Audit Qualité Arkose", page_icon="🧗")

# CSS sans f-string pour éviter les conflits d'accolades
st.markdown(
    """
    <style>
    .stApp {
        background-image: url("https://images.adobe.com/content/dam/cc/us/en/creative-cloud/stock/stock-home/AdobeStock_271556185.jpg");
        background-size: cover;
        background-position: center;
    }
    
    h1 {
        font-family: 'Roc Grotesk medium', sans-serif !important;
        color: white !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.7);
    }
    
    p, label, .stMarkdown {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif !important;
        color: #f0f0f0 !important;
        font-weight: 500;
    }
    
    .stButton>button {
        border: 2px solid #841bf3 !important;
        background-color: rgba(132, 27, 243, 0.1) !important;
        color: white !important;
        font-weight: bold;
        border-radius: 8px;
        backdrop-filter: blur(5px);
    }

    .stSelectbox div[data-baseweb="select"], .stFileUploader section {
        border: 2px solid #841bf3 !important;
        background-color: rgba(0,0,0,0.6) !important;
        border-radius: 8px;
        color: white !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🧗 Audit Qualité Arkose")

# --- LOGIQUE ---
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Clé API manquante dans les secrets.")
    st.stop()

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
NOTION_TOKEN = st.secrets["NOTION_TOKEN"]

salle_selectionnee = st.selectbox("Établissement :", list(SALLES_ARKOSE.keys()))
db_id = SALLES_ARKOSE[salle_selectionnee]
audio_file = st.file_uploader("Audio d'audit", type=['mp3', 'm4a', 'wav', 'mp4'])

def push_to_notion(data, database_id, salle):
    url = "https://api.notion.com/v1/pages"
    headers = {"Authorization": f"Bearer {NOTION_TOKEN}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
    date_jour = datetime.now().strftime("%Y-%m-%d")
    
    payload = {
        "parent": {"database_id": database_id},
        "properties": {
            "Nom de la tâche": {"title": [{"text": {"content": str(data.get("nom_de_la_tache", "Sans titre"))}}]},
            "Établissement": {"select": {"name": salle.upper()}},
            "Liste source": {"select": {"name": str(data.get("liste_source", "Accueil"))}},
            "Projet source": {"rich_text": [{"text": {"content": f"Audit interne {salle.upper()}"}}]},
            "Statut": {"status": {"name": "Saisie"}},
            "ITEM": {"select": {"name": str(data.get("item", "Process"))}},
            "Pôle concerné": {"select": {"name": str(data.get("pole_concerne", "Exploitation"))}},
            "Prise en charge": {"select": {"name": str(data.get("prise_en_charge", "Staff"))}},
            "Criticité": {"select": {"name": str(data.get("criticite", "Moyenne"))}},
            "Red flag": {"select": {"name": "Oui" if data.get("red_flag") else "Non"}},
            "Date de créa Notion": {"date": {"start": date_jour}},
            "MAJ tâche NOTION": {"date": {"start": date_jour}},
            "Confiance qualification": {"rich_text": [{"text": {"content": str(data.get("confiance_qualification", "Camille"))}}]}
        }
    }
    return requests.post(url,
