import streamlit as st
from google import genai
from google.genai import types
import requests
import json
from datetime import datetime

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

st.set_page_config(page_title="Audit Arkose", page_icon="🧗", layout="centered")

# --- DESIGN & POLICES ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@900&display=swap');

    .stApp {
        background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), 
                    url("https://images.unsplash.com/photo-1550684848-fac1c5b4e853?q=80&w=2070&auto=format&fit=crop");
        background-size: cover;
        background-attachment: fixed;
    }

    /* Titre Roc Grotesk Style */
    h1 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 900 !important;
        text-transform: uppercase;
        color: white !important;
        letter-spacing: -2px;
        line-height: 1;
        margin-bottom: 2rem !important;
    }

    /* Labels Helvetica Neue Gras */
    label p {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif !important;
        color: white !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Harmonisation des onglets et boutons */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: rgba(255,255,255,0.05);
        border-radius: 8px 8px 0px 0px;
        color: white;
        border: 1px solid rgba(132, 27, 243, 0.3);
    }

    .stTabs [aria-selected="true"] {
        background-color: rgba(132, 27, 243, 0.4) !important;
        border-bottom: 3px solid #841bf3 !important;
    }

    /* Bouton principal */
    .stButton>button {
        border: none !important;
        background-color: #841bf3 !important;
        color: white !important;
        font-weight: 800 !important;
        border-radius: 12px;
        padding: 1.2rem;
        text-transform: uppercase;
        width: 100%;
        margin-top: 2rem;
        transition: 0.3s ease;
    }
    
    .stButton>button:hover {
        box-shadow: 0 0 30px rgba(132, 27, 243, 0.8);
        transform: translateY(-2px);
    }

    /* Inputs */
    .stSelectbox div[data-baseweb="select"], .stFileUploader section, .stAudioInput {
        border: 1px solid #841bf3 !important;
        background-color: rgba(0,0,0,0.8) !important;
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)

st.title("Listing Audit Interne -> Notion")

# --- LOGIQUE ---
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
token = st.secrets["NOTION_TOKEN"]

# Sélection de l'établissement
salle_nom = st.selectbox("Établissement :", list(SALLES_ARKOSE.keys()))
db_id = SALLES_ARKOSE[salle_nom]

st.write("") # Espacement

# --- HARMONISATION DES BOUTONS (TABS) ---
tab_micro, tab_file = st.tabs(["🎤 ENREGISTRER", "📂 UPLOADER"])

with tab_micro:
    audio_record = st.audio_input("Capture vocale en direct")

with tab_file:
    audio_file = st.file_uploader("Fichier audio (mp3, m4a...)", type=['mp3', 'm4a', 'wav'])

final_audio = audio_file if audio_file else audio_record

def push_to_notion(data, database_id, name):
    url = "https://api.notion.com/v1/pages"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
    date_jour = datetime.now().strftime("%Y-%m-%d")
    
    payload = {
        "parent": {"database_id": database_id},
        "properties": {
            "Nom de la tâche": {"title": [{"text": {"content": str(data.get("nom_de_la_tache", "Sans titre"))}}]},
            "Établissement": {"select": {"name": name.upper()}},
            "Liste source": {"select": {"name": str(data.get("liste_source", "Accueil"))}},
            "Projet source": {"rich_text": [{"text": {"content": f"Audit {name.upper()}"}}]},
            "Statut": {"status": {"name": "Saisie"}},
            "ITEM": {"select": {"name": str(data.get("item", "Process"))}},
            "Pôle concerné": {"select": {"name": str(data.get("pole_concerne", "Exploitation"))}},
            "Prise en charge": {"select": {"name": str(data.get("prise_en_charge", "Staff"))}},
            "Criticité": {"select": {"name": str(data.get("criticite", "Moyenne"))}},
            "Red flag": {"select": {"name": "Oui" if data.get("red_flag") else "Non"}},
            "Date de créa Notion": {"date": {"start": date_jour}},
            "MAJ tâche NOTION": {"date": {"start": date_jour}},
            "Confiance qualification": {"rich_text": [{"text": {"content": "Camille"}}]}
        }
    }
    return requests.post(url, json=payload, headers=headers)

# Bouton d'envoi unique et centré
if final_audio:
    if st.button("🚀 LANCER L'ANALYSE ARK-IA"):
        with st.spinner("Analyse et synchronisation Notion..."):
            try:
                with open("temp.m4a", "wb") as f:
                    f.write(final_audio.getbuffer())
                
                f_up = client.files.upload(file="temp.m4a")
                prompt = "Expert Arkose. Analyse l'audio. JSON obligatoire: nom_de_la_tache, liste_source, item, pole_concerne, prise_en_charge, criticite, red_flag(bool)."
                
                resp = client.models.generate_content(
                    model='gemini-1.5-flash-latest',
                    contents=[f_up, prompt],
                    config=types.GenerateContentConfig(response_mime_type="application/json")
                )
                
                items = json.loads(resp.text)
                if not isinstance(items, list): items = [items]
                
                for i in items:
                    push_to_notion(i, db_id, salle_nom)
                st.success(f"🔥 Audit synchronisé ! {len(items)} tâche(s) ajoutée(s).")
            except Exception as e:
                st.error(f"Erreur technique : {e}")
