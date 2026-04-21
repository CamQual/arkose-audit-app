import streamlit as st
from google import genai
from google.genai import types
import requests
import json
from datetime import datetime
import base64
import os

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

# --- GESTION DE L'IMAGE DE FOND ---
bg_css_rule = ""
dossier_script = os.path.dirname(os.path.abspath(__file__))
chemin_image = os.path.join(dossier_script, "AdobeStock_271556185.jpg")

if os.path.exists(chemin_image):
    with open(chemin_image, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    bg_css_rule = f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), 
                    url("data:image/jpeg;base64,{encoded_string}");
        background-size: cover;
        background-attachment: fixed;
    }}
    </style>
    """
else:
    bg_css_rule = "<style>.stApp { background-color: #121212; }</style>"

# --- DESIGN ET POLICES ---
css_base = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@900&display=swap');

    html, body, [class*="st-"] {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif !important;
    }

    label p {
        color: white !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
    }

    .stTabs [data-baseweb="tab-list"] { 
        gap: 15px; 
    }
    .st
