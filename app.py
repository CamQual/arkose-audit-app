import streamlit as st
from google import genai
from google.genai import types
import requests
import json
from datetime import datetime
import base64
import os
import sqlite3

# --- INITIALISATION DE LA BASE DE DONNÉES UTILISATEURS ---
conn = sqlite3.connect('utilisateurs.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS users (email TEXT PRIMARY KEY, role TEXT)')

c.execute('SELECT count(*) FROM users')
if c.fetchone()[0] == 0:
    c.execute("INSERT INTO users VALUES ('admin@arkose.com', 'admin')")
    conn.commit()

# --- INITIALISATION DE LA SESSION ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_email' not in st.session_state:
    st.session_state['user_email'] = ""
if 'user_role' not in st.session_state:
    st.session_state['user_role'] = ""

st.set_page_config(page_title="Audit Arkose", page_icon="🧗", layout="centered")

# --- PAGE DE CONNEXION ---
if not st.session_state['logged_in']:
    st.markdown("""
    <style>
        .login-box {
            background-color: #121212; padding: 40px; border-radius: 15px; 
            border: 2px solid #841bf3; text-align: center; margin-top: 50px;
        }
        .stButton>button { width: 100%; background-color: #841bf3 !important; color: white; border-radius: 8px;}
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.title("🧗 Arkose Audit")
    st.write("Veuillez vous identifier pour accéder à l'application.")
    
    email_input = st.text_input("Adresse email (Google Connect simulé) :", placeholder="ex: jean.dupont@arkose.com")
    
    if st.button("Se connecter"):
        if email_input:
            c.execute("SELECT role FROM users WHERE email=?", (email_input.lower().strip(),))
            result = c.fetchone()
            if result:
                st.session_state['logged_in'] = True
                st.session_state['user_email'] = email_input.lower().strip()
                st.session_state['user_role'] = result[0]
                st.rerun()
            else:
                st.error("⛔ Accès refusé. Ce compte n'est pas autorisé.")
        else:
            st.warning("Veuillez entrer un email.")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- DÉCONNEXION ---
col_vide, col_logout = st.columns([4, 1])
with col_logout:
    if st.button("Déconnexion"):
        st.session_state['logged_in'] = False
        st.session_state['user_email'] = ""
        st.session_state['user_role'] = ""
        st.rerun()

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

# --- GESTION DE L'IMAGE DE FOND ---
bg_css_rule = ""
dossier_script = os.path.dirname(os.path.abspath(__file__))
target_bg = "adobestock_271556185"
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
    .stApp {{
        background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), 
                    url("data:image/jpeg;base64,{encoded_string}") !important;
        background-size: cover !important;
        background-attachment: fixed !important;
    }}
    </style>
    """
else:
    bg_css_rule = "<style>.stApp { background-color: #121212; }</style>"

# --- DESIGN ET POLICES ---
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

    .stSelectbox div[data-baseweb="select"], .stFileUploader section {
        border: 1px solid #841bf3 !important; background-color: rgba(0,0,0,0.8) !important; border-radius: 12px;
    }
    .stFileUploader section { padding: 20px !important; }
    .stFileUploader button { border-radius: 8px !important; }

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

# --- BANNIÈRE ---
banniere_trouvee = None
for fichier in os.listdir('.'):
    if fichier.lower().startswith("banniere"):
        banniere_trouvee = fichier
        break
if banniere_trouvee:
    st.image(banniere_trouvee, use_container_width
