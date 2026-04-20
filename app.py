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

# --- INTERFACE STREAMLIT ---
st.set_page_config(page_title="Arkose Quality Audit", page_icon="🧗")
st.title("🧗 Audit Qualité Arkose")

# Secrets (À configurer sur Streamlit Cloud plus tard)
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
NOTION_TOKEN = st.secrets["NOTION_TOKEN"]

client = genai.Client(api_key=GEMINI_API_KEY)

# 1. Choix de la salle
salle_selectionnee = st.selectbox("Dans quel établissement es-tu ?", list(SALLES_ARKOSE.keys()))
db_id = SALLES_ARKOSE[salle_selectionnee]

# 2. Enregistrement / Upload
audio_file = st.file_uploader("Enregistre ou dépose ton audio d'audit", type=['mp3', 'm4a', 'wav', 'mp4'])

if audio_file and st.button("🚀 Analyser et envoyer à Notion"):
    with st.spinner("L'IA écoute et prépare les fiches Notion..."):
        try:
            # Sauvegarde temporaire pour l'IA
            with open("temp_audio.m4a", "wb") as f:
                f.write(audio_file.getbuffer())
            
            # Analyse Gemini
            uploaded_file = client.files.upload(file="temp_audio.m4a")
            
            # TON PROMPT (Intégré ici)
            prompt_systeme = f"""Tu es l'assistant expert Arkose. Analyse l'audio pour l'établissement {salle_selectionnee}. 
            Structure en JSON pour Notion. (Insérer ici tout ton prompt détaillé précédent)"""

            response = client.models.generate_content(
                model='gemini-flash-latest',
                contents=[uploaded_file, "Analyse cet audit."],
                config=types.GenerateContentConfig(system_instruction=prompt_systeme)
            )

            # Nettoyage JSON
            res_text = response.text.replace('```json', '').replace('```', '').strip()
            data_json = json.loads(res_text)

            # Envoi vers Notion
            def push_to_notion(data, database_id):
                url = "https://api.notion.com/v1/pages"
                headers = {
                    "Authorization": f"Bearer {NOTION_TOKEN}",
                    "Content-Type": "application/json",
                    "Notion-Version": "2022-06-28"
                }
                # On ne met que les colonnes non-automatiques
                payload = {
                    "parent": {"database_id": database_id},
                    "properties": {
                        "Nom de la tâche": {"title": [{"text": {"content": data.get("nom_de_la_tache", "Sans titre")}}]},
                        "L'établissement": {"select": {"name": salle_selectionnee}},
                        "La liste source": {"select": {"name": data.get("liste_source")}},
                        "Projet source": {"rich_text": [{"text": {"content": f"Audit Interne {salle_selectionnee.upper()}"}}]},
                        "ITEM": {"select": {"name": data.get("item")}},
                        "Pole concerné": {"select": {"name": data.get("pole_concerne", "Exploitation")}},
                        "La prise en charge": {"select": {"name": data.get("prise_en_charge")}},
                        "criticité": {"select": {"name": data.get("criticite")}},
                        "Red flag": {"select": {"name": "Oui" if data.get("red_flag") else "Non"}},
                        "confiance qualification": {"rich_text": [{"text": {"content": data.get("confiance_qualification", "à vérifier - Camille")}}]}
                    }
                }
                return requests.post(url, json=payload, headers=headers)

            if isinstance(data_json, list):
                for item in data_json:
                    push_to_notion(item, db_id)
            else:
                push_to_notion(data_json, db_id)

            st.success(f"✅ Audit terminé pour {salle_selectionnee} ! Les fiches sont sur Notion.")
            
        except Exception as e:
            st.error(f"Oups, une erreur : {e}")