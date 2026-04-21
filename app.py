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
    st.write("Sélectionne ton fichier :")
    audio_file = st.file_uploader("Fichier audio (mp3, m4a, wav)", type=['mp3', 'm4a', 'wav'])

final_audio = audio_file if audio_file else audio_record

if st.session_state['user_role'] == 'admin':
    with tab_admin:
        st.subheader("Gérer les accès à l'application")
        with st.form("add_user_form"):
            new_email = st.text_input("Ajouter un nouvel email autorisé :")
            new_role = st.selectbox("Rôle :", ["user", "admin"])
            submit_add = st.form_submit_button("Ajouter l'utilisateur")
            
            if submit_add and new_email:
                try:
                    c.execute("INSERT INTO users VALUES (?, ?)", (new_email.lower().strip(), new_role))
                    conn.commit()
                    st.success(f"Compte {new_email} ajouté avec succès !")
                except sqlite3.IntegrityError:
                    st.error("Cet email existe déjà dans la base.")

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

# --- LOGIQUE NOTION & IA ---
def push_to_notion(data, database_id, name):
    url = "https://api.notion.com/v1/pages"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
    date_jour = datetime.now().strftime("%Y-%m-%d")
    
    # Nettoyage automatique des virgules pour éviter le bug Notion
    liste_source_clean = str(data.get("liste_source", "Accueil")).replace(",", " -")
    item_clean = str(data.get("item", "Process")).replace(",", " -")
    pole_clean = str(data.get("pole_concerne", "Exploitation")).replace(",", " -")
    prise_clean = str(data.get("prise_en_charge", "Staff")).replace(",", " -")
    crit_clean = str(data.get("criticite", "Moyenne")).replace(",", " -")
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
            "Date de créa Notion": {"date": {"start": date_jour}},
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
Tu es l'assistant expert en audit qualité d'Arkose. 
Ta mission est de transcrire des notes vocales prises lors d'audits en établissements par Camille (Responsable Qualité) ou d'autres collaborateurs, et de les structurer en JSON pour une base de données Notion.

### RÈGLES DE TRAITEMENT :
1. Nettoyage : Supprime les tics de langage ("euh", "bah", répétitions, vulgarité, familiarité).
2. Reformulation : Le "nom_de_la_tache" doit être résumé en une phrase courte, objective et pédagogique pour les équipes, et qui donne la solution et non souligne le problème.
3. Déduction intelligente et Vocabulaire :
   - Si l'utilisateur dit "Corner", traduis par "shop" dans le champ 'liste_source'.
   - Si l'utilisateur dit "Studio", traduis par "bien être" dans le champ 'liste_source'.
   - Si le nom "Issy" est prononcé seul, associe-le à "Issy Bloc" ou "Issy Voie" si l'un de ces deux a déjà été explicitement mentionné plus tôt.
   - Par défaut, si non précisé, le 'pole_concerne' est "Exploitation".
4. Identification de l'auteur : Écoute attentivement le début de l'audio. Si la personne se présente (ex: "Salut, c'est Thomas..."), mémorise son prénom. Si personne ne se présente, considère par défaut qu'il s'agit de Camille.

### STRUCTURE DE SORTIE (JSON STRICT) :
Tu dois répondre UNIQUEMENT avec une liste d'objets JSON respectant scrupuleusement ces propriétés :
[
  {
    "nom_de_la_tache": "Résumé pédagogique et objectif de la tâche",
    "liste_source": "Choisir STRICTEMENT parmi : Extérieur/terrasse, Accueil, Bar, Cantine, Cuisine, Toilettes Salle, Vestiaire, vestiaire sec, Sauna, Fitness (espace étirement), Salle globale (espace chill), salle privatisable, zone de grimpe, shop, bien être",
    "item": "Choisir STRICTEMENT parmi : Accueil/Discours/Expé client, Image de marque, Propreté/hygiène/entretien, Process, Valorisation de l'offre",
    "pole_concerne": "Choisir STRICTEMENT parmi : Exploitation, Travaux/Maintenance, Escalade, Com&Market, Déco, Support IT, RH, RSE, Property",
    "prise_en_charge": "Choisir STRICTEMENT parmi : Le night, Mail équipe support, Staff, Achat exploit, Prestataire extérieur, Plateforme support",
    "criticite": "Faible (confort/esthétique), Moyenne (impact image/qualité à terme), ou Critique (urgence/dégradation/hygiène grave)",
    "red_flag": true ou false,
    "auteur": "Prénom identifié dans l'audio ou Camille"
  }
]

INTERDICTION ABSOLUE d'utiliser des virgules (,) dans tes réponses pour les choix de listes, utilise des tirets (-) à la place si besoin.
"""

if final_audio:
    if st.button("Lancer l'analyse vers Notion"):
        with st.spinner("Analyse et envoi vers Notion..."):
            try:
                with open("temp.m4a", "wb") as f:
                    f.write(final_audio.getbuffer())
                
                f_up = client.files.upload(file="temp.m4a")
                
                resp = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[f_up, PROMPT_ARKOSE],
                    config=types.GenerateContentConfig(response_mime_type="application/json")
                )
                
                items = json.loads(resp.text)
                
                if not isinstance(items, list):
                    items = [items]
                
                erreurs = 0
                for i in items:
                    try:
                        push_to_notion(i, db_id, salle_nom)
                    except Exception as e:
                        st.error(f"❌ Erreur sur une tâche : {e}")
                        erreurs += 1
                
                if erreurs == 0:
                    st.success(f"🔥 Audit synchronisé ! {len(items)} tâche(s) ajoutée(s) avec succès.")
                else:
                    st.warning(f"⚠️ {len(items) - erreurs} tâches ajoutées, mais {erreurs} ont été refusées par Notion.")
                    
            except Exception as e:
                st.error(f"Erreur technique de l'IA : {e}")
