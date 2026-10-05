"""
Database and authentication module for Arkose Dict'Action
"""
import sqlite3
import hashlib

DB_FILE = "utilisateurs.db"

def hash_password(password: str) -> str:
    """Hash un mot de passe en SHA-256."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def get_connection():
    """Crée une connexion SQLite thread-safe."""
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def init_db():
    """Initialise la table des utilisateurs et les administrateurs par défaut."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (email TEXT PRIMARY KEY, role TEXT, password TEXT)')
    
    # Migration si la colonne password manquait
    try:
        c.execute('ALTER TABLE users ADD COLUMN password TEXT')
        conn.commit()
    except sqlite3.OperationalError:
        pass  # Colonne déjà existante
    
    # Initialisation des admins par défaut
    default_password = hash_password("arkose2026")
    admins = [
        ('admin@arkose.com', 'admin', default_password),
        ('camille.g@arkose.com', 'admin', default_password)
    ]
    
    for email, role, password in admins:
        c.execute("INSERT OR IGNORE INTO users (email, role, password) VALUES (?, ?, ?)", (email, role, password))
        c.execute("UPDATE users SET role=? WHERE email=?", (role, email))
        c.execute("UPDATE users SET password=? WHERE email=? AND (password IS NULL OR password='')", (password, email))
    
    conn.commit()
    conn.close()

def authenticate_user(email: str, password: str):
    """
    Vérifie les identifiants d'un utilisateur.
    Retourne (success: bool, role: str or None, message: str)
    """
    email_clean = email.lower().strip()
    hashed_pwd = hash_password(password)
    
    conn = get_connection()
    c = conn.cursor()
    
    c.execute("SELECT role FROM users WHERE email=? AND password=?", (email_clean, hashed_pwd))
    res = c.fetchone()
    
    if res:
        conn.close()
        return True, res[0], "Connexion réussie"
    
    # Vérifier si l'utilisateur existe avec un mauvais mot de passe
    c.execute("SELECT role FROM users WHERE email=?", (email_clean,))
    user_exists = c.fetchone()
    conn.close()
    
    if user_exists:
        return False, None, "Mot de passe incorrect."
    else:
        return False, None, f"Accès refusé pour '{email_clean}'. Ce compte n'existe pas."

def add_user(email: str, role: str, password: str):
    """Ajoute un utilisateur dans la base de données."""
    email_clean = email.lower().strip()
    hashed_pwd = hash_password(password)
    
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (email, role, password) VALUES (?, ?, ?)", (email_clean, role, hashed_pwd))
        conn.commit()
        return True, f"Compte {email_clean} ajouté avec succès !"
    except sqlite3.IntegrityError:
        return False, "Cet email existe déjà dans la base."
    finally:
        conn.close()

def get_all_users():
    """Récupère tous les utilisateurs."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT email, role FROM users ORDER BY email ASC")
    users = c.fetchall()
    conn.close()
    return users

def delete_user(email: str):
    """Supprime un utilisateur."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE email=?", (email,))
    conn.commit()
    conn.close()
