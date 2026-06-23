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
        .stButton>button { width: 100%; background-color: #841bf3 !important; color: white; border-radius: 8px;}
    </style>
    """, unsafe_allow_html=True)
    
    with st.form("login_form", clear_on_submit=False):
        logo_trouve = None
        for fichier in os.listdir('.'):
            if fichier.lower().startswith("logo"):
                logo_trouve = fichier
                break
        
        if logo_trouve:
            st.image(logo_trouve, use_container_width=True)
            
        st.markdown("<p style='text-align: center;'>Connecte toi pour accéder à l'appli !</p>", unsafe_allow_html=True)
        
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
                st.warning("Veuillez entrer un email et un mot de passe.")
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
    "Chevaleret": "342457aab01481fe9d70d2cd7ee136c3",
    "Saint Denis - CAO": "342457aab01481dc8ebbf88df7c120a8"
}

# (Le bloc CSS a été déplacé au début du fichier)

# --- BANNIÈRE ---
banniere_trouvee = None
for fichier in os.listdir('.'):
    if fichier.lower().startswith("banniere"):
        banniere_trouvee = fichier
        break
if banniere_trouvee:
    st.image(banniere_trouvee, use_container_width=True)

st.write(f"Connecté en tant que : **{st.session_state['user_email']}** ({st.session_state['user_role']})") 

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
token = st.secrets["NOTION_TOKEN"]

salle_nom = st.selectbox("Établissement :", list(SALLES_ARKOSE.keys()))
db_id = SALLES_ARKOSE[salle_nom]

st.write("") 

# --- GESTION DES ONGLETS ---
if st.session_state['user_role'] == 'admin':
    onglets = st.tabs(["🎤 Enregistrer", "📂 Uploader", "⚙️ Administration"])
    tab_micro = onglets[0]
    tab_file = onglets[1]
    tab_admin = onglets[2]
else:
    onglets = st.tabs(["🎤 Enregistrer", "📂 Uploader"])
    tab_micro = onglets[0]
    tab_file = onglets[1]

with tab_micro:
    st.write("Clique sur le micro pour parler :")
    audio_record = st.audio_input("Capture vocale en direct")

with tab_file:
    st.write("Sélectionne tes fichiers :")
    audio_files = st.file_uploader("Fichiers audio (mp3, m4a, wav)", type=['mp3', 'm4a', 'wav'], accept_multiple_files=True)

fichiers_a_traiter = []
if audio_files:
    fichiers_a_traiter.extend(audio_files)
if audio_record:
    fichiers_a_traiter.append(audio_record)

if st.session_state['user_role'] == 'admin':
    with tab_admin:
        st.subheader("Gérer les accès à l'application")
        with st.form("add_user_form"):
            new_email = st.text_input("Ajouter un nouvel email autorisé :")
            new_password = st.text_input("Mot de passe de cet utilisateur :", type="password")
            new_role = st.selectbox("Rôle :", ["user", "admin"])
            submit_add = st.form_submit_button("Ajouter l'utilisateur")
            
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
        c.execute("SELECT email, role FROM users")
        utilisateurs = c.fetchall()
        
        for u in utilisateurs:
            col_email, col_role, col_delete = st.columns([3, 1, 1])
            col_email.write(f"👤 {u[0]}")
            col_role.write(f"*{u[1]}*")
            if u[0] != st.session_state['user_email']:
                if col_delete.button("❌ Supprimer", key=f"del_{u[0]}"):
                    c.execute("DELETE FROM users WHERE email=?", (u[0],))
                    conn.commit()
                    st.rerun()

# --- VIGILE ANTI-INVENTION (BLOQUE L'IA SI ELLE INVENTE DES MOTS) ---
def get_valid_option(raw_value, allowed_list, default_value):
    raw_lower = str(raw_value).strip().lower()
    for option in allowed_list:
        if raw_lower == option.lower():
            return option
    return default_value # Si l'IA a inventé un mot, on force la valeur par défaut !

LISTE_SOURCE_OBLIGATOIRE = ["EXTERIEUR/TERRASSE", "ACCUEIL", "BAR", "CANTINE", "CUISINE", "TOILETTES SALLE", "VESTIAIRES", "VESTIAIRE SEC", "SAUNA", "FITNESS", "SALLE GLOBALE", "SALLE PRIVATISABLE", "ZONE DE GRIMPE", "SHOP", "BIEN ETRE"]
ITEM_OBLIGATOIRE = ["ACCUEIL/DISCOURS/EXPE CLIENT", "IMAGE DE MARQUE", "PROPRETE/HYGIENE/ENTRETIEN", "PROCESS", "VALORISATION DE L'OFFRE"]
POLE_OBLIGATOIRE = ["EXPLOITATION", "TRAVAUX", "MAINTENANCE", "ESCALADE", "COM&MARKET", "DECO", "SUPPORT IT", "RH", "RSE", "PROPERTY"]
PRISE_EN_CHARGE_OBLIGATOIRE = ["LE NIGHT", "MAIL EQUIPE SUPPORT", "STAFF", "ACHAT EXPLOIT", "PRESTATAIRE EXTERIEUR", "PLATEFORME SUPPORT"]
CRITICITE_OBLIGATOIRE = ["FAIBLE", "MOYENNE", "CRITIQUE"]

# --- LOGIQUE NOTION ---
def push_to_notion(data, database_id, name):
    url = "https://api.notion.com/v1/pages"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
    date_jour = datetime.now().strftime("%Y-%m-%d")
    
    # Nettoyage implacable : on passe les réponses de l'IA dans notre vigile
    liste_source_clean = get_valid_option(data.get("liste_source"), LISTE_SOURCE_OBLIGATOIRE, "ACCUEIL")
    item_clean = get_valid_option(data.get("item"), ITEM_OBLIGATOIRE, "PROCESS")
    pole_clean = get_valid_option(data.get("pole_concerne"), POLE_OBLIGATOIRE, "EXPLOITATION")
    prise_clean = get_valid_option(data.get("prise_en_charge"), PRISE_EN_CHARGE_OBLIGATOIRE, "STAFF")
    crit_clean = get_valid_option(data.get("criticite"), CRITICITE_OBLIGATOIRE, "MOYENNE")
    auteur_clean = str(data.get("auteur", "Camille"))
    
    payload = {
        "parent": {"database_id": database_id},
        "properties": {
            "Nom de la tâche": {"title": [{"text": {"content": str(data.get("nom_de_la_tache", "Sans titre"))}}]},
            "Établissement": {"select": {"name": name.upper()}},
            "Liste source": {"select": {"name": liste_source_clean}},
            "Projet source": {"rich_text": [{"text": {"content": f"Audit Interne {name.upper()}"}}]},
            "Statut": {"status": {"name": "A vérifier"}},
            "ITEM": {"select": {"name": item_clean}},
            "Pôle concerné": {"select": {"name": pole_clean}},
            "Prise en charge": {"select": {"name": prise_clean}},
            "Criticité": {"select": {"name": crit_clean}},
            "Red flag": {"select": {"name": "Oui" if data.get("red_flag") else "Non"}},
            "Date créa Notion": {"date": {"start": date_jour}},
            "MAJ tâche NOTION": {"date": {"start": date_jour}},
            "Confiance qualification": {"rich_text": [{"text": {"content": f"à vérifier - {auteur_clean}"}}]}
        }
    }
    
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Refus de Notion : {response.text}")
    return response

# --- LE PROMPT EXPERT ---
PROMPT_ARKOSE = """
Tu es un assistant expert en audit qualité d'Arkose, extrêmement rigoureux, bienveillant et concis. 
Ta mission est de transcrire des notes vocales et d'extraire les données pour créer des tâches dans Notion.

RÈGLE D'OR : Pour les champs à choix multiples, tu dois STRICTEMENT utiliser les termes exacts fournis dans les listes ci-dessous. N'INVENTE JAMAIS de nouvelles catégories.

LISTES AUTORISÉES (COPIE EXACTE OBLIGATOIRE) :
- liste_source : "EXTERIEUR/TERRASSE", "ACCUEIL", "BAR", "CANTINE", "CUISINE", "TOILETTES SALLE", "VESTIAIRES", "VESTIAIRE SEC", "SAUNA", "FITNESS", "SALLE GLOBALE", "SALLE PRIVATISABLE", "ZONE DE GRIMPE", "SHOP", "BIEN ETRE"
- item : "ACCUEIL/DISCOURS/EXPE CLIENT", "IMAGE DE MARQUE", "PROPRETE/HYGIENE/ENTRETIEN", "PROCESS", "VALORISATION DE L'OFFRE"
- pole_concerne : "EXPLOITATION", "TRAVAUX", "MAINTENANCE", "ESCALADE", "COM&MARKET", "DECO", "SUPPORT IT", "RH", "RSE", "PROPERTY"
- prise_en_charge : "LE NIGHT", "MAIL EQUIPE SUPPORT", "STAFF", "ACHAT EXPLOIT", "PRESTATAIRE EXTERIEUR", "PLATEFORME SUPPORT"
- criticite : "FAIBLE", "MOYENNE", "CRITIQUE"

RÈGLES D'ANALYSE :
1. Nettoyage et Ton : Supprime les tics de langage et reformule les "abus de langage" pour un rendu professionnel.
2. Reformulation (nom_de_la_tache) : Doit être une phrase COURTE, BIENVEILLANTE, objective et pédagogique apportant la solution.
3. Règle Spécifique VESTIAIRES : Si l'utilisateur mentionne "VESTIAIRES" avec "FEMME" ou "HOMME" :
   - 'liste_source' doit rester "VESTIAIRES".
   - Intègre "FEMME" ou "HOMME" UNIQUEMENT dans le 'nom_de_la_tache' (ex: "Vestiaires femme : [action]").
4. Déduction : Si "Corner" -> "SHOP". Si "Studio" -> "BIEN ETRE".
5. Par défaut : "pole_concerne" = "EXPLOITATION".
6. Auteur : Prénom entendu au début, ou "Camille" par défaut.
7. Criticité : Choisis strictement parmi "FAIBLE", "MOYENNE", "CRITIQUE".

RÉPONSE ATTENDUE (Tableau JSON strict) :
[
  {
    "nom_de_la_tache": "Description résumée",
    "liste_source": "Valeur exacte de la liste",
    "item": "Valeur exacte de la liste",
    "pole_concerne": "Valeur exacte de la liste",
    "prise_en_charge": "Valeur exacte de la liste",
    "criticite": "Valeur exacte de la liste",
    "red_flag": true,
    "auteur": "Camille"
  }
]
"""

if fichiers_a_traiter:
    if st.button("Lancer l'analyse vers Notion"):
        with st.spinner("Analyse et envoi vers Notion..."):
            erreurs_globales = 0
            taches_ajoutees_globalement = 0
            
            for idx, f_audio in enumerate(fichiers_a_traiter):
                nom_fichier = getattr(f_audio, 'name', f'Fichier {idx+1}')
                try:
                    temp_filename = f"temp_{idx}.m4a"
                    with open(temp_filename, "wb") as f:
                        f.write(f_audio.getbuffer())
                    
                    f_up = client.files.upload(file=temp_filename)
                    
                    resp = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=[f_up, PROMPT_ARKOSE],
                        config=types.GenerateContentConfig(response_mime_type="application/json")
                    )
                    
                    items = json.loads(resp.text)
                    
                    if not isinstance(items, list):
                        items = [items]
                    
                    for item in items:
                        try:
                            push_to_notion(item, db_id, salle_nom)
                            taches_ajoutees_globalement += 1
                        except Exception as e:
                            st.error(f"❌ Erreur sur une tâche du fichier '{nom_fichier}' : {e}")
                            erreurs_globales += 1
                    
                    try:
                        os.remove(temp_filename)
                    except:
                        pass
                        
                except Exception as e:
                    st.error(f"Erreur technique de l'IA sur le fichier '{nom_fichier}' : {e}")
                    erreurs_globales += 1
            
            if erreurs_globales == 0 and taches_ajoutees_globalement > 0:
                st.success(f"🔥 Audit synchronisé ! {taches_ajoutees_globalement} tâche(s) ajoutée(s) avec succès depuis {len(fichiers_a_traiter)} fichier(s).")
            elif taches_ajoutees_globalement > 0:
                st.warning(f"⚠️ {taches_ajoutees_globalement} tâches ajoutées, mais il y a eu {erreurs_globales} erreurs.")
            elif erreurs_globales > 0:
                st.error("❌ Échec de la synchronisation. Aucune tâche n'a pu être ajoutée.")
