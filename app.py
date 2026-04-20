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

st.set_page_config(page_title="Audit Arkose", page_icon="🧗")
st.title("🧗 Audit Qualité Arkose")

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
token = st.secrets["NOTION_TOKEN"]

salle = st.selectbox("Établissement :", list(SALLES_ARKOSE.keys()))
db_id = SALLES_ARKOSE[salle]
audio = st.file_uploader("Audio", type=['mp3', 'm4a', 'wav', 'mp4'])

def push_to_notion(data, database_id, salle_nom):
    url = "https://api.notion.com/v1/pages"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
    date_jour = datetime.now().strftime("%Y-%m-%d")
    
    payload = {
        "parent": {"database_id": database_id},
        "properties": {
            "Nom de la tâche": {"title": [{"text": {"content": str(data.get("nom_de_la_tache", "Sans titre"))}}]},
            "Établissement": {"select": {"name": salle_nom.upper()}},
            "Liste source": {"select": {"name": str(data.get("liste_source", "Accueil"))}},
            "Projet source": {"rich_text": [{"text": {"content": f"Audit interne {salle_nom.upper()}"}}]},
            "Statut": {"status": {"name": str(data.get("statut", "Active"))}},
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

if audio and st.button("🚀 Envoyer"):
    with st.spinner("Analyse intelligente en cours..."):
        try:
            with open("temp.m4a", "wb") as f: f.write(audio.getbuffer())
            f_up = client.files.upload(file="temp.m4a")
            
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
            
            resp = client.models.generate_content(
                model='gemini-flash-latest', 
                contents=[f_up, prompt], 
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            
            data_json = json.loads(resp.text)
            items = data_json if isinstance(data_json, list) else [data_json]

            for item in items:
                r = push_to_notion(item, db_id, salle)
                if r.status_code == 200:
                    st.success(f"✅ Tâche '{item.get('nom_de_la_tache')}' ajoutée avec tous ses détails !")
                else:
                    st.error(f"Erreur : {r.text}")

        except Exception as e:
            st.error(f"Erreur : {e}")
