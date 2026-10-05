"""
Configuration and constants for Arkose Dict'Action
"""

# --- CONFIGURATION DES SALLES & DATABASES NOTION ---
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
    "Canal": "342457aab01481d3b6e3d8ad1d1038e3",
    "Strasbourg Saint Denis": "342457aab01481f2aaebd2d9955e73ec",
    "Nanterre": "342457aab01481bd9916f46b3f9ad295",
    "Montmartre": "342457aab01481c2b7e8cdb57558af81",
    "Chevaleret": "342457aab01481fe9d70d2cd7ee136c3",
    "Saint Denis - CAO": "342457aab01481dc8ebbf88df7c120a8"
}

# --- LISTES AUTORISÉES (VIGILE ANTI-INVENTION NOTION) ---
LISTE_SOURCE_OBLIGATOIRE = [
    "EXTERIEUR/TERRASSE", "ACCUEIL", "BAR", "CANTINE", "CUISINE",
    "TOILETTES SALLE", "VESTIAIRES", "VESTIAIRE SEC", "SAUNA", "FITNESS",
    "SALLE GLOBALE", "SALLE PRIVATISABLE", "ZONE DE GRIMPE", "SHOP", "BIEN ETRE"
]

ITEM_OBLIGATOIRE = [
    "ACCUEIL/DISCOURS/EXPE CLIENT", "IMAGE DE MARQUE",
    "PROPRETE/HYGIENE/ENTRETIEN", "PROCESS", "VALORISATION DE L'OFFRE"
]

POLE_OBLIGATOIRE = [
    "EXPLOITATION", "TRAVAUX", "MAINTENANCE", "ESCALADE", "COM&MARKET",
    "DECO", "SUPPORT IT", "RH", "RSE", "PROPERTY"
]

PRISE_EN_CHARGE_OBLIGATOIRE = [
    "LE NIGHT", "MAIL EQUIPE SUPPORT", "STAFF", "ACHAT EXPLOIT",
    "PRESTATAIRE EXTERIEUR", "PLATEFORME SUPPORT"
]

CRITICITE_OBLIGATOIRE = ["FAIBLE", "MOYENNE", "CRITIQUE"]

# --- STATUTS NOTION (AVEC EMOJIS) ---
STATUT_DEFAUT = "👀 A vérifier"
STATUTS_AUTORISES = [
    "👀 A vérifier",
    "🟢 Active",
    "📩 Relance effectuée",
    "🚧 Bloquée",
    "✅ Cloturée"
]

# --- PROMPT SYSTÈME GEMINI ---
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
