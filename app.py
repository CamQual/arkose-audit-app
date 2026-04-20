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

# --- STYLISATION PERSONNALISÉE (CSS ARKOSE NOIR GRAIN) ---
def local_css(file_name):
    # Charge l'image de fond et l'applique au conteneur principal
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("app/static/arkose_noir_grain.jpg");
            background-size: cover;
            background-position: center;
        }}
        
        /* Titres : Roc Grotesk medium */
        h1 {{
            font-family: 'Roc Grotesk medium', sans-serif !important;
            color: white !important;
            text-shadow: 1px 1px 2px black;
            font-size: 2.5rem;
        }}
        
        /* Corps de texte : Helvetica Neue */
        p, .stSelectbox label, .stFileUploader label, .stMarkdown, .stButton label {{
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif !important;
            color: #d1d1d1 !important;
        }}
        
        /* Boutons avec contour violet Arkose #841bf3 */
        .stButton>button {{
            border: 2px solid #841bf3;
            border-radius: 5px;
            background-color: transparent;
            color: #841bf3;
            font-weight: bold;
            transition: all 0.3s ease;
        }}
        .stButton>button:hover {{
            background-color: #841bf3;
            color: white;
            border: 2px solid #841bf3;
        }}
        
        /* Champ Uploader avec contour violet */
        .stFileUploader {{
            border: 2px solid #841bf3 !important;
            border-radius: 5px;
            background-color: rgba(255, 255, 255, 0.05); /* Léger fond transparent */
        }
        .stFileUploader label {{
            color: #841bf3 !important;
        }

        /* Champ Selectbox */
        .stSelectbox>div {{
            border: 2px solid #841bf3;
            border-radius: 5px;
            background-color: rgba(255, 255, 255, 0.05);
        }
        
        /* Sécurité supplémentaire : rendre le conteneur du bouton transparent */
        .stButton {{
            background-color: transparent !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# --- INTERFACE STREAMLIT ---
st.set_page_config(page_title="Audit Qualité Arkose - Noir Grain", page_icon="🧗", layout="centered")

# Application du CSS personnalisé
local_css("style.css")

# --- TITRE PRINCIPAL ---
st.title("🧗 Audit Qualité Arkose")

# Vérification des secrets
if "GEMINI_API_KEY" not in st.secrets or "NOTION_TOKEN" not in st.secrets:
    st.error("⚠️ Configurer les secrets GEMINI_API_KEY et NOTION_TOKEN.")
    st.stop()

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
NOTION_TOKEN = st.secrets["NOTION_TOKEN"]

# --- SÉLECTION DE LA SALLE ---
salle_selectionnee = st.selectbox("Dans quel établissement es-tu ?", list(SALLES_ARKOSE.keys()))
db_id = SALLES_ARKOSE[salle_selectionnee]

# --- CHARGEMENT DE L'AUDIO ---
st.write("") # Espace
audio_file = st.file_uploader("Audio d'audit", type=['mp3', 'm4a', 'wav', 'mp4'], help="Enregistre ou dépose ton audio")

def push_to_notion(data, database_id, salle):
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
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
    return requests.post(url, json=payload, headers=headers)

if audio_file and st.button("🚀 Analyser et envoyer à Notion"):
    with st.spinner("Analyse et envoi intelligente en cours..."):
        try:
            with open("temp_audio.m4a", "wb") as f:
                f.write(audio_file.getbuffer())
            
            uploaded_file = client.files.upload(file="temp_audio.m4a")
            
            prompt = """Tu es l'expert audit Arkose. Analyse l'audio et génère un JSON pour chaque tâche détectée.
            OPTIONS POUR LES CHAMPS (respecte l'orthographe) :
            - liste_source: Extérieur/terrasse, Accueil, Bar, Cantine, Cuisine, Toilettes Salle, Vestiaire, Fitness, Salle globale, shop, bien être.
            - item: Accueil/Discours/Expé client, Image de marque, Propreté/hygiène/entretien, Process, Valorisation de l'offre.
            - pole_concerne: Exploitation, Travaux/Maintenance, Escalade, Com&Market, Déco, Support IT, RH.
            - prise_en_charge: Le night, Mail équipe support, Staff, Achat exploit, Prestataire extérieur.
            - criticite: Faible (confort/esthétique), Moyenne (impact image/qualité), Critique (urgence).
            - statut: Active, Cloturée.
            
            Format JSON: {"nom_de_la_tache": "...", "liste_source": "...", "item": "...", "pole_concerne": "...", "prise_en_charge": "...", "criticite": "...", "red_flag": true/false, "statut": "Active", "confiance_qualification": "Camille"}
            """

            response = client.models.generate_content(
                model='gemini-flash-latest',
                contents=[uploaded_file, prompt],
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )

            res_text = response.text.replace('```json', '').replace('```', '').strip()
            data_json = json.loads(res_text)

            items_to_push = data_json if isinstance(data_json, list) else [data_json]

            for item in items_to_push:
                push_to_notion(item, db_id, salle_selectionnee)
            
            st.success("✅ Tâche(s) envoyée(s) à Notion !")
            
        except Exception as e:
            st.error(f"⚠️ Erreur : {e}")
