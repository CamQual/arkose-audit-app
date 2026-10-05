# 🧗 Arkose Dict'Action

Application Streamlit d'audit qualité vocal pour les établissements Arkose. L'audio est retranscrit et analysé par **Google Gemini 2.5 Flash**, puis automatiquement synchronisé sous forme de tâches qualifiées dans les bases de données **Notion**.

---

## 📁 Architecture du Projet

Le projet a été fractionné en modules indépendants pour une maintenance simplifiée et des performances optimales :

- **`app.py`** : Point d'entrée principal de l'application Streamlit (authentification, sélection des salles, enregistrement / upload audio, onglet admin).
- **`app_config.py`** : Centralisation des configurations (liste des salles Arkose, IDs Notion, catégories imposées, prompt système).
- **`database.py`** : Gestion de la base SQLite locale, hachage des mots de passe (SHA-256) et gestion des rôles/utilisateurs.
- **`styles.py`** : Gestion du thème graphique Arkose (CSS personnalisé, fond d'écran dynamique, logo, bannière).
- **`notion_service.py`** : Communication avec l'API Notion et vigile strict anti-hallucination.
- **`ai_service.py`** : Traitement audio via Google Gemini 2.5 Flash et extraction de données structurées.
- **`requirements.txt`** : Dépendances Python requises pour le déploiement.
- **`.gitignore`** : Fichiers ignorés par Git (secrets, caches, fichiers temporaires).

---

## 🚀 Déploiement et Synchronisation Automatique (GitHub ➡️ Streamlit Cloud)

Streamlit Community Cloud se synchronise directement avec votre dépôt GitHub : à chaque `git push`, votre application est mise à jour instantanément en ligne.

### Étape 1 : Initialiser et publier le dépôt sur GitHub

1. Ouvrez un terminal dans le dossier du projet :
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Architecture modulaire Arkose Dict'Action"
   ```

2. Créez un nouveau dépôt sur [GitHub](https://github.com/new) (par exemple nommé `arkose-dictaction`).

3. Liez votre dossier local au dépôt GitHub et poussez vos fichiers :
   ```bash
   git remote add origin https://github.com/VOTRE_COMPTE/arkose-dictaction.git
   git branch -M main
   git push -u origin main
   ```

### Étape 2 : Connecter l'application à Streamlit Cloud

1. Rendez-vous sur [share.streamlit.io](https://share.streamlit.io) et connectez-vous avec votre compte GitHub.
2. Cliquez sur **"Create app"** (ou "New app").
3. Sélectionnez votre dépôt (`arkose-dictaction`), la branche `main` et le fichier principal `app.py`.
4. Cliquez sur **"Advanced settings"** > **"Secrets"** et collez vos clés d'API :
   ```toml
   GEMINI_API_KEY = "votre_cle_gemini"
   NOTION_TOKEN = "votre_token_notion"
   ```
5. Cliquez sur **"Deploy"**.

### Étape 3 : Mises à jour automatiques en direct

Dès que vous modifiez le code ou ajoutez une fonctionnalité, il vous suffit de faire :
```bash
git add .
git commit -m "Mise à jour de l'application"
git push
```
Streamlit Cloud détectera automatiquement le commit et mettra à jour votre application en quelques secondes !

---

## 🔑 Identifiants par défaut

- **Admin** : `admin@arkose.com` (mot de passe : `arkose2026`)
- **Camille** : `camille.g@arkose.com` (mot de passe : `arkose2026`)
