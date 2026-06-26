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
    .stTabs [aria-selected="true"] { background-color: rgba(132, 27, 24
