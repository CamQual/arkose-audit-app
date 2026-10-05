"""
Arkose Dict'Action - Main Streamlit Application
"""
import streamlit as st
import app_config
import database
import styles
import notion_service
import ai_service

# 1. Configuration de la page Streamlit
st.set_page_config(
    page_title="Arkose Dict'Action",
    page_icon="🧗",
    layout="centered"
)

# 2. Initialisation de la base de données SQLite
database.init_db()

# 3. Initialisation de l'état de session
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_email' not in st.session_state:
    st.session_state['user_email'] = ""
if 'user_role' not in st.session_state:
    st.session_state['user_role'] = ""

# 4. Application des styles globaux
styles.apply_custom_styles()

# -------------------------------------------------------------
# PAGE DE CONNEXION
# -------------------------------------------------------------
if not st.session_state['logged_in']:
    styles.apply_login_styles()
    
    with st.form("login_form", clear_on_submit=False):
        styles.render_logo()
        st.markdown("<p style='text-align: center;'>Connecte-toi pour accéder à l'application !</p>", unsafe_allow_html=True)
        
        email_input = st.text_input("Adresse email :", placeholder="ex: camille.g@arkose.com")
        password_input = st.text_input("Mot de passe :", type="password")
        
        submit_btn = st.form_submit_button("Se connecter")
        
        if submit_btn:
            if email_input and password_input:
                success, role, msg = database.authenticate_user(email_input, password_input)
                if success:
                    st.session_state['logged_in'] = True
                    st.session_state['user_email'] = email_input.lower().strip()
                    st.session_state['user_role'] = role
                    st.rerun()
                else:
                    st.error(f"⛔ {msg}")
            else:
                st.warning("Veuillez entrer un email et un mot de passe.")
    st.stop()

# -------------------------------------------------------------
# APPLICATION PRINCIPALE (UTILISATEUR AUTHENTIFIÉ)
# -------------------------------------------------------------
styles.apply_main_container_styles()

# Barre supérieure : Déconnexion
col_info, col_logout = st.columns([4, 1])
with col_logout:
    if st.button("Déconnexion"):
        st.session_state['logged_in'] = False
        st.session_state['user_email'] = ""
        st.session_state['user_role'] = ""
        st.rerun()

# Bannière d'en-tête
styles.render_banner()

st.write(f"Connecté en tant que : **{st.session_state['user_email']}** (*{st.session_state['user_role']}*)")

# Vérification des secrets de configuration
if "GEMINI_API_KEY" not in st.secrets or "NOTION_TOKEN" not in st.secrets:
    st.error("⚠️ Clés API manquantes dans les Secrets Streamlit (GEMINI_API_KEY ou NOTION_TOKEN).")
    st.stop()

gemini_api_key = st.secrets["GEMINI_API_KEY"]
notion_token = st.secrets["NOTION_TOKEN"]

# Client Gemini
try:
    gemini_client = ai_service.get_gemini_client(gemini_api_key)
except Exception as e:
    st.error(f"Erreur d'initialisation Gemini : {e}")
    st.stop()

# Sélection de la salle Arkose
salle_nom = st.selectbox("Établissement :", list(app_config.SALLES_ARKOSE.keys()))
db_id = app_config.SALLES_ARKOSE[salle_nom]

st.write("")

# Onglets d'action
if st.session_state['user_role'] == 'admin':
    onglets = st.tabs(["🎤 Enregistrer", "📂 Télécharger", "⚙️ Administration"])
    tab_micro = onglets[0]
    tab_file = onglets[1]
    tab_admin = onglets[2]
else:
    onglets = st.tabs(["🎤 Enregistrer", "📂 Télécharger"])
    tab_micro = onglets[0]
    tab_file = onglets[1]
    tab_admin = None

with tab_micro:
    st.write("Clique sur le micro pour parler :")
    audio_record = st.audio_input("Capture vocale en direct")

with tab_file:
    st.write("Sélectionne tes fichiers :")
    audio_files = st.file_uploader(
        "Fichiers audio (mp3, m4a, wav)",
        type=['mp3', 'm4a', 'wav'],
        accept_multiple_files=True
    )

# Gestion de l'administration (comptes utilisateurs)
if tab_admin and st.session_state['user_role'] == 'admin':
    with tab_admin:
        st.subheader("Gérer les accès à l'application")
        with st.form("add_user_form"):
            new_email = st.text_input("Ajouter un nouvel email autorisé :")
            new_password = st.text_input("Mot de passe de cet utilisateur :", type="password")
            new_role = st.selectbox("Rôle :", ["user", "admin"])
            submit_add = st.form_submit_button("Ajouter l'utilisateur")
            
            if submit_add:
                if new_email and new_password:
                    ok, msg = database.add_user(new_email, new_role, new_password)
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)
                else:
                    st.warning("L'email et le mot de passe sont obligatoires.")

        st.write("---")
        st.write("### Liste des utilisateurs")
        utilisateurs = database.get_all_users()
        
        for u in utilisateurs:
            col_u_email, col_u_role, col_u_delete = st.columns([3, 1, 1])
            col_u_email.write(f"👤 {u[0]}")
            col_u_role.write(f"*{u[1]}*")
            if u[0] != st.session_state['user_email']:
                if col_u_delete.button("❌ Supprimer", key=f"del_{u[0]}"):
                    database.delete_user(u[0])
                    st.rerun()

# Rassemblement des fichiers audio à traiter
fichiers_a_traiter = []
if audio_files:
    fichiers_a_traiter.extend(audio_files)
if audio_record:
    fichiers_a_traiter.append(audio_record)

# Traitement IA et envoi Notion
if fichiers_a_traiter:
    if st.button("Lancer l'analyse vers Notion"):
        with st.spinner("Analyse avec Gemini 2.5 Flash et envoi vers Notion..."):
            erreurs_globales = 0
            taches_ajoutees_globalement = 0
            
            for idx, f_audio in enumerate(fichiers_a_traiter):
                nom_fichier = getattr(f_audio, 'name', f'Capture micro #{idx+1}')
                try:
                    # 1. Analyse audio par l'IA Gemini
                    items = ai_service.process_audio(gemini_client, f_audio, file_label=nom_fichier)
                    
                    # 2. Envoi de chaque tâche vers Notion
                    for item in items:
                        try:
                            notion_service.push_to_notion(item, db_id, salle_nom, notion_token)
                            taches_ajoutees_globalement += 1
                        except Exception as e:
                            st.error(f"❌ Erreur sur une tâche de '{nom_fichier}' : {e}")
                            erreurs_globales += 1
                            
                except Exception as e:
                    st.error(f"❌ Erreur technique de l'IA sur '{nom_fichier}' : {e}")
                    erreurs_globales += 1
            
            if erreurs_globales == 0 and taches_ajoutees_globalement > 0:
                st.success(f"🔥 Audit synchronisé ! {taches_ajoutees_globalement} tâche(s) ajoutée(s) avec succès dans Notion depuis {len(fichiers_a_traiter)} enregistrement(s).")
            elif taches_ajoutees_globalement > 0:
                st.warning(f"⚠️ {taches_ajoutees_globalement} tâche(s) ajoutée(s), mais {erreurs_globales} erreur(s) détectée(s).")
            elif erreurs_globales > 0:
                st.error("❌ Échec de la synchronisation. Aucune tâche n'a pu être ajoutée.")