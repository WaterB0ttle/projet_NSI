# simple_scores_db.py
import sqlite3
import contextlib
from datetime import datetime

DATABASE = 'scores.db'

@contextlib.contextmanager
def get_db():
    """Context manager pour gérer automatiquement la connexion BD"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    """Initialise la base de données pour les scores simples"""
    with get_db() as db:
        # Table des scores sans player_id
        db.execute('''
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                score INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Index pour optimiser les requêtes
        db.execute('CREATE INDEX IF NOT EXISTS idx_score ON scores(score)')
        db.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON scores(timestamp)')

def save_score(score):
    """
    Sauvegarde un score anonyme
    
    Args:
        score (int): Score à sauvegarder
    
    Returns:
        int: ID du score inséré
    """
    with get_db() as db:
        cursor = db.execute('INSERT INTO scores (score) VALUES (?)', (score,))
        return cursor.lastrowid

def get_all_scores(limit=100, sort_by='timestamp', order='DESC'):
    """
    Récupère tous les scores avec options de tri
    
    Args:
        limit (int): Nombre maximum de scores
        sort_by (str): Colonne de tri ('id', 'score', 'timestamp')
        order (str): Ordre de tri ('ASC' ou 'DESC')
    
    Returns:
        list: Liste de tous les scores
    """
    valid_sorts = ['id', 'score', 'timestamp']
    if sort_by not in valid_sorts:
        sort_by = 'timestamp'
    
    order = 'DESC' if order.upper() == 'DESC' else 'ASC'
    
    with get_db() as db:
        query = f'SELECT * FROM scores ORDER BY {sort_by} {order} LIMIT ?'
        scores = db.execute(query, (limit,)).fetchall()
        
        return [dict(score) for score in scores]

def get_score_by_id(score_id):
    """
    Récupère un score spécifique par son ID
    
    Args:
        score_id (int): ID du score à récupérer
    
    Returns:
        dict: Données du score ou None si non trouvé
    """
    with get_db() as db:
        score = db.execute('SELECT * FROM scores WHERE id = ?', (score_id,)).fetchone()
        return dict(score) if score else None

def get_stats():
    """
    Récupère les statistiques globales des scores
    
    Returns:
        dict: Statistiques complètes
    """
    with get_db() as db:
        stats = db.execute('''
            SELECT 
                COUNT(*) as total_scores,
                MAX(score) as highest_score,
                MIN(score) as lowest_score,
                AVG(score) as average_score,
                MAX(timestamp) as last_score_date,
                MIN(timestamp) as first_score_date
            FROM scores
        ''').fetchone()
        
        return dict(stats)

def get_recent_scores(limit=10):
    """
    Récupère les scores les plus récents
    
    Args:
        limit (int): Nombre de scores récents à retourner
    
    Returns:
        list: Scores les plus récents
    """
    return get_all_scores(limit=limit, sort_by='timestamp', order='DESC')

def get_top_scores(limit=10):
    """
    Récupère les meilleurs scores
    
    Args:
        limit (int): Nombre de meilleurs scores à retourner
    
    Returns:
        list: Meilleurs scores
    """
    return get_all_scores(limit=limit, sort_by='score', order='DESC')

def delete_score(score_id):
    """
    Supprime un score spécifique
    
    Args:
        score_id (int): ID du score à supprimer
    
    Returns:
        bool: True si suppression réussie, False sinon
    """
    with get_db() as db:
        cursor = db.execute('DELETE FROM scores WHERE id = ?', (score_id,))
        return cursor.rowcount > 0

def get_scores_count():
    """
    Retourne le nombre total de scores enregistrés
    
    Returns:
        int: Nombre total de scores
    """
    with get_db() as db:
        result = db.execute('SELECT COUNT(*) as count FROM scores').fetchone()
        return result['count']

def get_score_range(min_score=None, max_score=None, limit=100):
    """
    Récupère les scores dans une plage spécifique
    
    Args:
        min_score (int): Score minimum
        max_score (int): Score maximum
        limit (int): Nombre maximum de résultats
    
    Returns:
        list: Scores dans la plage spécifiée
    """
    query = 'SELECT * FROM scores'
    params = []
    
    if min_score is not None and max_score is not None:
        query += ' WHERE score BETWEEN ? AND ?'
        params.extend([min_score, max_score])
    elif min_score is not None:
        query += ' WHERE score >= ?'
        params.append(min_score)
    elif max_score is not None:
        query += ' WHERE score <= ?'
        params.append(max_score)
    
    query += ' ORDER BY score DESC LIMIT ?'
    params.append(limit)
    
    with get_db() as db:
        scores = db.execute(query, params).fetchall()
        return [dict(score) for score in scores]

# Test et démonstration
if __name__ == '__main__':
    # Initialisation
    init_db()
    print("✅ Base de données scores simples initialisée")
    
    # Données de test
    test_scores = [1500, 2300, 1800, 1900, 2700, 1200, 2100, 2500, 2200, 3000]
    
    # Insertion des données de test
    for score in test_scores:
        save_score(score)
    print("✅ Données de test insérées")
    
    # Affichage des statistiques
    print(f"\n📊 Statistiques:")
    stats = get_stats()
    print(f"   Total scores: {stats['total_scores']}")
    print(f"   Meilleur score: {stats['highest_score']}")
    print(f"   Pire score: {stats['lowest_score']}")
    print(f"   Score moyen: {stats['average_score']:.2f}")
    print(f"   Premier score: {stats['first_score_date']}")
    print(f"   Dernier score: {stats['last_score_date']}")
    
    print(f"\n🕒 5 derniers scores:")
    recent = get_recent_scores(limit=5)
    for score in recent:
        print(f"   #{score['id']}: {score['score']} pts - {score['timestamp']}")
    
    print(f"\n🏆 5 meilleurs scores:")
    top = get_top_scores(limit=5)
    for i, score in enumerate(top, 1):
        print(f"   {i}. {score['score']} pts (#{score['id']})")
    
    print(f"\n🎯 Scores entre 2000 et 2500:")
    range_scores = get_score_range(min_score=2000, max_score=2500, limit=5)
    for score in range_scores:
        print(f"   {score['score']} pts (#{score['id']})")