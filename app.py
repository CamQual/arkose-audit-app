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

st.set_page_config(page_title="Arkose Quality Audit", page_icon="🧗")
st.title("🧗 Audit Qualité Arkose")

if "GEMINI_API_KEY" not in st.secrets or "NOTION_TOKEN" not in st.secrets:
    st.error("⚠️ Secrets manquants.")
    st.stop()

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
NOTION_TOKEN = st.secrets["NOTION_TOKEN"]

salle_selectionnee = st.selectbox("Établissement :", list(SALLES_ARKOSE.keys()))
db_id = SALLES_ARKOSE[salle_selectionnee]
audio_file = st.file_uploader("Audio d'audit", type=['mp3', 'm4a', 'wav', 'mp4'])

def push_to_notion(data, database_id, salle):
    url = "https://api.notion.com/v1/pages"
    headers = {"Authorization": f"Bearer {NOTION_TOKEN}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
    
    payload = {
        "parent": {"database_id": database_id},
        "properties": {
            "Nom de la tâche": {"title": [{"text": {"content": str(data.get("nom_de_la_tache", "Sans titre"))}}]},
            "Établissement": {"select": {"name": salle}},
            "Liste source": {"select": {"name": str(data.get("liste_source", "Accueil"))}},
            "Projet source": {"rich_text": [{"text": {"content": f"Audit Interne {salle.upper()}"}}]},
            "ITEM": {"select": {"name": str(data.get("item", "Process"))}},
            "Pôle concerné": {"select": {"name": str(data.get("pole_concerne", "Exploitation"))}},
            "Prise en charge": {"select": {"name": str(data.get("prise_en_charge", "Staff"))}},
            "Criticité": {"select": {"name": str(data.get("criticite", "Moyenne"))}},
            "Red flag": {"select": {"name": "Oui" if data.get("red_flag") == True else "Non"}},
            "confiance qualification": {"rich_text": [{"text": {"content": str(data.get("confiance_qualification", "Camille"))}}]}
        }
    }
    return requests.post(url, json=payload, headers=headers)

if audio_file and st.button("🚀 Analyser et envoyer"):
    with st.spinner("Analyse Gemini en cours..."):
        try:
            with open("temp_audio.m4a", "wb") as f:
                f.write(audio_file.getbuffer())
            
            uploaded_file = client.files.upload(file="temp_audio.m4a")
            
            prompt = f"""Tu es l'expert Arkose pour la salle {salle_selectionnee}.
            Analyse l'audio et extrais les tâches.
            Règles : Corner -> shop, Studio -> bien être.
            Renvoie un JSON avec : nom_de_la_tache, liste_source, item, pole_concerne, prise_en_charge, criticite, red_flag (booléen), confiance_qualification."""

            response = client.models.generate_content(
                model='gemini-1.5-flash', # On passe sur le tout dernier modèle dispo
                contents=[uploaded_file, prompt],
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )

            # Extraction robuste du JSON
            raw_text = response.text.strip()
            # On cherche le premier [ ou { pour ignorer le texte avant
            match = re.search(r'[\{\[]', raw_text)
            if match:
                data_json = json.loads(raw_text[match.start():])
            else:
                data_json = json.loads(raw_text)

            if isinstance(data_json, list):
                for item in data_json:
                    push_to_notion(item, db_id, salle_selectionnee)
            else:
                push_to_notion(data_json, db_id, salle_selectionnee)

            st.success("✅ Données envoyées à Notion !")
            
        except Exception as e:
            st.error(f"Erreur : {e}")
            st.write("Réponse brute de l'IA (pour debug) :", response.text if 'response' in locals() else "Pas de réponse")
