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

# On s'assure que Camille et l'admin par défaut existent avec le bon rôle
admins = [('admin@arkose.com', 'admin'), ('camille.g@arkose.com', 'admin')]
for email, role in admins:
    c.execute("INSERT OR IGNORE INTO users VALUES (?, ?)", (email, role))
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
if not st.session_state['logged_in']:
    st.markdown("""
    <style>
        .login-box {
            background-color: #121212; padding: 40px; border-radius: 15px; 
            border: 2px solid #841bf3; text-align: center; margin-top: 50px;
        [data-testid="stForm"] {
            background-color: #121212 !important; 
            padding: 40px !important; 
            border-radius: 15px !important; 
            border: 2px solid #841bf3 !important; 
            margin-top: 50px;
        }
        .stButton>button { width: 100%; background-color: #841bf3 !important; color: white; border-radius: 8px;}
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.title("🧗 Arkose Audit")
    st.write("Veuillez vous identifier pour accéder à l'application.")
    
    email_input = st.text_input("Adresse email :", placeholder="ex: camille.g@arkose.com")
    
    if st.button("Se connecter"):
        if email_input:
            email_clean = email_input.lower().strip()
            c.execute("SELECT role FROM users WHERE email=?", (email_clean,))
            result = c.fetchone()
            if result:
                st.session_state['logged_in'] = True
                st.session_state['user_email'] = email_clean
                st.session_state['user_role'] = result[0]
                st.rerun()
    with st.form("login_form", clear_on_submit=False):
        st.markdown("<h1 style='text-align: center;'>🧗 Arkose Audit</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>Veuillez vous identifier pour accéder à l'application.</p>", unsafe_allow_html=True)
        
        email_input = st.text_input("Adresse email :", placeholder="ex: camille.g@arkose.com")
        password_input = st.text_input("Mot de passe :", type="password")
        
        submit_btn = st.form_submit_button("Se connecter")
        
        if submit_btn:
            if email_input and password_input:
                email_clean = email_input.lower().strip()
                hashed_pwd = hash_password(password_input)
                
                c.execute("SELECT role FROM users WHERE email=? AND password=?", (email_clean, hashed_pwd))
                result = c.fetchone()
                if result:
                    st.session_state['logged_in'] = True
                    st.session_state['user_email'] = email_clean
                    st.session_state['user_role'] = result[0]
                    st.rerun()
                else:
                    # Vérifions si l'email existe pour donner un message précis
                    c.execute("SELECT role FROM users WHERE email=?", (email_clean,))
                    if c.fetchone():
                        st.error("⛔ Mot de passe incorrect.")
                    else:
                        st.error(f"⛔ Accès refusé pour '{email_clean}'. Ce compte n'existe pas.")
            else:
                st.error(f"⛔ Accès refusé pour '{email_clean}'. Ce compte n'est pas autorisé.")
                # Liste des emails autorisés pour debug
                c.execute("SELECT email FROM users")
                all_users = [row[0] for row in c.fetchall()]
                st.write(f"Emails en base : {all_users}")
        else:
            st.warning("Veuillez entrer un email.")
    st.markdown('</div>', unsafe_allow_html=True)
                st.warning("Veuillez entrer un email et un mot de passe.")
    st.stop()

# --- DÉCONNEXION ---
        st.subheader("Gérer les accès à l'application")
        with st.form("add_user_form"):
            new_email = st.text_input("Ajouter un nouvel email autorisé :")
            new_password = st.text_input("Mot de passe de cet utilisateur :", type="password")
            new_role = st.selectbox("Rôle :", ["user", "admin"])
            submit_add = st.form_submit_button("Ajouter l'utilisateur")
            
            if submit_add and new_email:
                try:
                    c.execute("INSERT INTO users VALUES (?, ?)", (new_email.lower().strip(), new_role))
                    conn.commit()
                    st.success(f"Compte {new_email} ajouté avec succès !")
                except sqlite3.IntegrityError:
                    st.error("Cet email existe déjà dans la base.")
            if submit_add:
                if new_email and new_password:
                    try:
                        hashed_new_pwd = hash_password(new_password)
                        c.execute("INSERT INTO users (email, role, password) VALUES (?, ?, ?)", (new_email.lower().strip(), new_role, hashed_new_pwd))
                        conn.commit()
                        st.success(f"Compte {new_email} ajouté avec succès !")
                    except sqlite3.IntegrityError:
                        st.error("Cet email existe déjà dans la base.")
                else:
                    st.warning("L'email et le mot de passe sont obligatoires.")

        st.write("---")
        st.write("### Liste des utilisateurs")
                    
            except Exception as e:
                st.error(f"Erreur technique de l'IA : {e}")
