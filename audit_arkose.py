import requests
import json
from datetime import datetime
from google import genai
from google.genai import types

# === 1. TES CLÉS SECRÈTES (A définir en variables d'environnement) ===
GEMINI_API_KEY = "VOTRE_CLE_GEMINI" 
NOTION_TOKEN = "VOTRE_TOKEN_NOTION" 
DATABASE_ID = "342457aab0148128933fe069f5899250"

# Initialisation du client Google
client = genai.Client(api_key=GEMINI_API_KEY)

def envoyer_a_notion(data):
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    payload = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Nom de la tâche": {"title": [{"text": {"content": data.get("nom_de_la_tache", "Sans titre")}}]},
            "L'établissement": {"select": {"name": data.get("etablissement")}},
            "La liste source": {"select": {"name": data.get("liste_source")}},
            "Projet source": {"rich_text": [{"text": {"content": data.get("projet_source", "")}}]},
            "Statut": {"select": {"name": data.get("statut")}},
            "ITEM": {"select": {"name": data.get("item")}},
            "Pole concerné": {"select": {"name": data.get("pole_concerne")}},
            "La prise en charge": {"select": {"name": data.get("prise_en_charge")}},
            "criticité": {"select": {"name": data.get("criticite")}},
            "Red flag": {"checkbox": data.get("red_flag", False)},
            "Date de créa Notion": {"date": {"start": datetime.now().strftime("%Y-%m-%d")}},
            "MAJ tâche NOTION": {"date": {"start": datetime.now().strftime("%Y-%m-%d")}},
            "confiance qualification": {"rich_text": [{"text": {"content": data.get("confiance_qualification", "à vérifier - Camille")}}]}
        }
    }
    
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        print("✅ Succès ! La tâche a été ajoutée à Notion.")
    else:
        print(f"❌ Erreur Notion: {response.status_code}")
        print(response.text)

def transcrire_et_analyser(audio_path):
    mon_prompt = """Tu es l'assistant expert en audit qualité d'Arkose."""
    print("Écoute et analyse de l'audio par l'IA...")
    audio_file = client.files.upload(file=audio_path)
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[audio_file, "Analyse cet audit et renvoie uniquement le JSON strict."],
        config=types.GenerateContentConfig(
            system_instruction=mon_prompt,
        )
    )
    json_text = response.text.replace('```json', '').replace('```', '').strip()
    return json.loads(json_text)