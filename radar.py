from google import genai

# Remplace par ta vraie clé en variable d'environnement ou secrets
GEMINI_API_KEY = "VOTRE_CLE_GEMINI"

client = genai.Client(api_key=GEMINI_API_KEY)

print("📡 Recherche des modèles autorisés pour ton compte...")
for model in client.models.list():
    print("-", model.name)