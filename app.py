import streamlit as st
from google import genai
from google.genai import types
import requests
import json
from datetime import datetime
import base64
import os
import sqlite3
import hashlib

# --- INITIALISATION DE LA BASE DE DONNÉES UTILISATEURS ---
conn = sqlite3.connect('utilisateurs.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS users (email TEXT PRIMARY KEY, role TEXT)')

# Ajout de la colonne password si elle n'existe pas
try:
    c.execute('ALTER TABLE users ADD COLUMN password TEXT')
    conn.commit()
except sqlite3.OperationalError:
    pass # La colonne existe déjà

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# On s'assure que Camille et l'admin par défaut existent avec le bon rôle et un mot de passe
default_password = hash_password("arkose2026")
admins = [('admin@arkose.com', 'admin', default_password), ('camille.g@arkose.com', 'admin', default_password)]
for email, role, password in admins:
    c.execute("INSERT OR IGNORE INTO users (email, role, password) VALUES (?, ?, ?)", (email, role, password))
    c.execute("UPDATE users SET role=? WHERE email=?", (role, email))
    c.execute("UPDATE users SET password=? WHERE email=? AND (password IS NULL OR password='')", (password, email))
conn.commit()

# --- INITIALISATION DE LA SESSION ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_email' not in st.session_state:
    st.session_state['user_email'] = ""
if 'user_role' not in st.session_state:
    st.session_state['user_role'] = ""

st.set_page_config(page_title="Arkose Dict'Action", page_icon="🧗", layout="centered")

# --- GESTION DE L'IMAGE DE FOND ---
bg_css_rule = ""
dossier_script = os.path.dirname(os.path.abspath(__file__))
target_bg = "background"
fond_trouve = None

for fichier in os.listdir('.'):
    if fichier.lower().startswith(target_bg):
        fond_trouve = fichier
        break

if fond_trouve:
    with open(fond_trouve, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    bg_css_rule = f"""
    <style>
    .stApp, [data-testid="stAppViewContainer"] {{
        background: url("data:image/jpeg;base64,{encoded_string}") !important;
        background-size: cover !important;
        background-attachment: fixed !important;
        background-position: center !important;
    }}
    </style>
    """
else:
    bg_css_rule = "<style>.stApp, [data-testid='stAppViewContainer'] { background-color: #121212; }</style>"

css_base = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@900&display=swap');
    p, label, span, div, .stMarkdown, button { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif !important; }
    label p { color: white !important; font-weight: 700 !important; font-size: 1.1rem !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 15px; }
    .stTabs [data-baseweb="tab"] {
        height: auto !important; padding: 12px 20px !important; 
        background-color: rgba(255,255,255,0.05); border-radius: 8px 8px 0px 0px;
        color: white !important; border: 1px solid rgba(132, 27, 243, 0.2); white-space: nowrap; 
    }
    .stTabs [aria-selected="true"] { background-color: rgba(132, 27, 243, 0.3) !important; border-bottom: 3px solid #841bf3 !important; }
    
    /* --- CORRECTION STYLE FILE UPLOADER --- */
    .stSelectbox div[data-baseweb="select"], .stFileUploader section {
        border: 1px solid #841bf3 !important; background-color: rgba(0,0,0,0.8) !important; border-radius: 12px;
    }
    .stFileUploader section { padding: 20px !important; }
    
    /* Ciblage precis du bouton pour eviter le doublon de texte */
    .stFileUploader [data-testid="stBaseButton-secondary"] { 
        border-radius: 8px !important; 
        background-color: #841bf3 !important;
        border: none !important;
        padding: 8px 16px !important;
    }
    .stFileUploader [data-testid="stBaseButton-secondary"] p {
        color: white !important;
        font-weight: bold !important;
    }
    .stFileUploader [data-testid="stBaseButton-secondary"]:hover { 
        box-shadow: 0 0 15px rgba(132, 27, 243, 0.5) !important; 
    }
    .stFileUploader [data-testid="stBaseButton-secondary"] svg { 
        display: none !important; 
    }
    /* -------------------------------------- */

    .stAudioInput {
        margin-top: 20px; padding: 15px; border: 1px solid #841bf3 !important;
        border-radius: 12px; background-color: rgba(0,0,0,0.6);
    }
    .stButton>button {
        border: none !important; background-color: #841bf3 !important; color: white !important;
        font-weight: 700 !important; border-radius: 12px; padding: 1.2rem; width: 100%; margin-top: 1rem;
    }
    .stButton>button:hover { box-shadow: 0 0 30px rgba(132, 27, 243, 0.7); }
</style>
"""
st.markdown(bg_css_rule + css_base, unsafe_allow_html=True)

# --- PAGE DE CONNEXION ---
if not st.session_state['logged_in']:
    st.markdown("""
    <style>
        [data-testid="stForm"] {
            background-color: rgba(132, 27, 243, 0.75) !important; 
            padding: 40px !important; 
            border-radius: 15px !important; 
            border: 2px solid #841bf3 !important; 
            margin-top: 50px;
        }
        .stButton
