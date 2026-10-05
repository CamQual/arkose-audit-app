"""
UI styling, CSS injection, and asset management for Arkose Dict'Action
"""
import os
import base64
import streamlit as st

def get_base64_image(image_path: str) -> str:
    """Encode une image en base64 pour injection CSS."""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def find_asset(prefix: str):
    """Recherche un fichier asset par préfixe dans le dossier courant."""
    for file in os.listdir("."):
        if file.lower().startswith(prefix.lower()):
            return file
    return None

def apply_custom_styles():
    """Injecte le thème CSS personnalisé et l'image de fond."""
    bg_file = find_asset("background")
    if bg_file:
        encoded_bg = get_base64_image(bg_file)
        bg_css = f"""
        <style>
        .stApp, [data-testid="stAppViewContainer"] {{
            background: url("data:image/jpeg;base64,{encoded_bg}") !important;
            background-size: cover !important;
            background-attachment: fixed !important;
            background-position: center !important;
        }}
        </style>
        """
    else:
        bg_css = "<style>.stApp, [data-testid='stAppViewContainer'] { background-color: #121212; }</style>"

    css_base = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@900&display=swap');
        
        /* Typographie ciblée pour ne pas casser les polices d'icônes Streamlit */
        body, p, label, .stMarkdown p, h1, h2, h3, h4, h5, h6 { 
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif !important; 
        }
        label p { color: white !important; font-weight: 700 !important; font-size: 1.1rem !important; }
        
        /* Onglets */
        .stTabs [data-baseweb="tab-list"] { gap: 15px; }
        .stTabs [data-baseweb="tab"] {
            height: auto !important; padding: 12px 20px !important; 
            background-color: rgba(255,255,255,0.05); border-radius: 8px 8px 0px 0px;
            color: white !important; border: 1px solid rgba(132, 27, 243, 0.2); white-space: nowrap; 
        }
        .stTabs [aria-selected="true"] { background-color: rgba(132, 27, 243, 0.3) !important; border-bottom: 3px solid #841bf3 !important; }
        
        /* Sélecteurs et Zone d'upload */
        .stSelectbox div[data-baseweb="select"], .stFileUploader section {
            border: 1px solid #841bf3 !important; background-color: rgba(0,0,0,0.8) !important; border-radius: 12px;
        }
        .stFileUploader section { padding: 20px !important; }
        .stFileUploader button { 
            border-radius: 8px !important; 
            background-color: #841bf3 !important;
            color: white !important;
            border: none !important;
            font-weight: 700 !important;
        }
        .stFileUploader button:hover { box-shadow: 0 0 15px rgba(132, 27, 243, 0.5); }
        
        /* Audio Input */
        .stAudioInput {
            margin-top: 20px; padding: 15px; border: 1px solid #841bf3 !important;
            border-radius: 12px; background-color: rgba(0,0,0,0.6);
        }
        
        /* Boutons principaux */
        .stButton>button {
            border: none !important; background-color: #841bf3 !important; color: white !important;
            font-weight: 700 !important; border-radius: 12px; padding: 1.2rem; width: 100%; margin-top: 1rem;
        }
        .stButton>button:hover { box-shadow: 0 0 30px rgba(132, 27, 243, 0.7); }
    </style>
    """
    st.markdown(bg_css + css_base, unsafe_allow_html=True)

def apply_login_styles():
    """Injecte les styles spécifiques au formulaire de login."""
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

def apply_main_container_styles():
    """Injecte les styles pour le conteneur principal après connexion."""
    st.markdown("""
    <style>
        .block-container {
            background-color: rgba(132, 27, 243, 0.75) !important; 
            padding: 40px !important; 
            border-radius: 15px !important; 
            border: 2px solid #841bf3 !important; 
            margin-top: 20px !important;
            margin-bottom: 20px !important;
        }
    </style>
    """, unsafe_allow_html=True)

def render_logo():
    """Affiche le logo s'il existe."""
    logo = find_asset("logo")
    if logo:
        st.image(logo, use_container_width=True)

def render_banner():
    """Affiche la bannière d'en-tête si elle existe."""
    banner = find_asset("arkose_header") or find_asset("banniere")
    if banner:
        st.image(banner, use_container_width=True)
