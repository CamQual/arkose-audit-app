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

# Récupération des clés sécurisées
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    NOTION_TOKEN = st.secrets["NOTION_TOKEN"]
except:
    st.error("Clés API manquantes dans les Secrets de Streamlit.")
    st.stop()

client = genai.Client(api_key=GEMINI_API_KEY)

# 1. Choix de la salle
salle_selectionnee = st.selectbox("Dans quel établissement es-tu ?", list(SALLES_ARKOSE.keys()))
db_id = SALLES_ARKOSE[salle_selectionnee]

# 2. Enregistrement / Upload
audio_file = st.file_uploader("Enregistre ou dépose ton audio d'audit", type=['mp3', 'm4a', 'wav', 'mp4'])

if audio_file and st.button("🚀 Analyser et envoyer à Notion"):
    with st.spinner("L'IA écoute et prépare les fiches Notion..."):
        try:
            # Sauvegarde temporaire
            with open("temp_audio.m4a", "wb") as f:
                f.write(audio_file.getbuffer())
            
            # Analyse Gemini
            uploaded_file = client.files.upload(file="temp_audio.m4a")
