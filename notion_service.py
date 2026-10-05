"""
Notion API integration and strict schema validation for Arkose Dict'Action
"""
from datetime import datetime
import requests
from app_config import (
    LISTE_SOURCE_OBLIGATOIRE,
    ITEM_OBLIGATOIRE,
    POLE_OBLIGATOIRE,
    PRISE_EN_CHARGE_OBLIGATOIRE,
    CRITICITE_OBLIGATOIRE,
    STATUT_DEFAUT,
    STATUTS_AUTORISES
)

def get_valid_option(raw_value: any, allowed_list: list, default_value: str) -> str:
    """
    Vigile anti-invention : force la sélection d'une option strictement autorisée.
    Si l'IA hallucine ou invente une valeur, la valeur par défaut est assignée.
    """
    if raw_value is None:
        return default_value
    raw_lower = str(raw_value).strip().lower()
    for option in allowed_list:
        if raw_lower == option.lower():
            return option
    return default_value

def push_to_notion(data: dict, database_id: str, salle_name: str, notion_token: str):
    """
    Formate et pousse une tâche analysée vers la base Notion de la salle correspondante.
    """
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    date_jour = datetime.now().strftime("%Y-%m-%d")

    # Nettoyage et sécurisation des données avec le vigile
    liste_source_clean = get_valid_option(data.get("liste_source"), LISTE_SOURCE_OBLIGATOIRE, "ACCUEIL")
    item_clean = get_valid_option(data.get("item"), ITEM_OBLIGATOIRE, "PROCESS")
    pole_clean = get_valid_option(data.get("pole_concerne"), POLE_OBLIGATOIRE, "EXPLOITATION")
    prise_clean = get_valid_option(data.get("prise_en_charge"), PRISE_EN_CHARGE_OBLIGATOIRE, "STAFF")
    crit_clean = get_valid_option(data.get("criticite"), CRITICITE_OBLIGATOIRE, "MOYENNE")
    statut_clean = get_valid_option(data.get("statut"), STATUTS_AUTORISES, STATUT_DEFAUT)
    auteur_clean = str(data.get("auteur", "Camille")).strip()
    nom_tache_clean = str(data.get("nom_de_la_tache", "Sans titre")).strip()
    red_flag = bool(data.get("red_flag", False))

    payload = {
        "parent": {"database_id": database_id},
        "properties": {
            "Nom de la tâche": {"title": [{"text": {"content": nom_tache_clean}}]},
            "Établissement": {"select": {"name": salle_name.upper()}},
            "Liste source": {"select": {"name": liste_source_clean}},
            "Projet source": {"rich_text": [{"text": {"content": f"Audit Interne {salle_name.upper()}"}}]},
            "Statut": {"status": {"name": statut_clean}},
            "ITEM": {"select": {"name": item_clean}},
            "Pôle concerné": {"select": {"name": pole_clean}},
            "Prise en charge": {"select": {"name": prise_clean}},
            "Criticité": {"select": {"name": crit_clean}},
            "Red flag": {"select": {"name": "Oui" if red_flag else "Non"}},
            "Date créa Notion": {"date": {"start": date_jour}},
            "MAJ tâche NOTION": {"date": {"start": date_jour}},
            "Confiance qualification": {"rich_text": [{"text": {"content": f"à vérifier - {auteur_clean}"}}]}
        }
    }

    response = requests.post(url, json=payload, headers=headers, timeout=15)
    if response.status_code not in (200, 201):
        raise RuntimeError(f"Erreur API Notion ({response.status_code}) : {response.text}")
    return response.json()
