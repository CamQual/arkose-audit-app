"""
Google Gemini AI service for transcribing and analyzing audio notes
"""
import os
import json
import tempfile
from google import genai
from google.genai import types
from app_config import PROMPT_ARKOSE

def get_gemini_client(api_key: str) -> genai.Client:
    """Initialise et retourne le client Google Gemini."""
    return genai.Client(api_key=api_key)

def process_audio(client: genai.Client, audio_file_obj, file_label: str = "audio") -> list:
    """
    Traite un fichier audio :
    1. Écrit temporairement le buffer sur disque.
    2. Envoie le fichier à l'API Gemini.
    3. Analyse et extrait la structure JSON demandée.
    4. Supprime les fichiers temporaires.
    5. Retourne une liste de tâches structurées.
    """
    temp_path = None
    uploaded_file = None
    try:
        # Déterminer l'extension
        suffix = ".m4a"
        orig_name = getattr(audio_file_obj, "name", "")
        if orig_name and "." in orig_name:
            suffix = os.path.splitext(orig_name)[1]

        # Création d'un fichier temporaire
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(audio_file_obj.getbuffer())
            temp_path = tmp.name

        # Upload vers Gemini
        uploaded_file = client.files.upload(file=temp_path)

        # Génération structurée
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[uploaded_file, PROMPT_ARKOSE],
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )

        # Parsing JSON
        raw_text = response.text.strip()
        tasks = json.loads(raw_text)

        if not isinstance(tasks, list):
            tasks = [tasks]

        return tasks

    finally:
        # Nettoyage du fichier local
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass
        
        # Nettoyage optionnel du fichier Gemini
        if uploaded_file:
            try:
                client.files.delete(name=uploaded_file.name)
            except Exception:
                pass
