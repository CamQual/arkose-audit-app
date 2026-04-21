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
    "Pont de Sèvres": "342457aab01481079a6
