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
    st.session_state['user_role
