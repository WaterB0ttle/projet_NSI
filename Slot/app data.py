# slot_machine_db.py
import sqlite3
import contextlib
from datetime import datetime

DATABASE = 'slot_scores.db'

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
    """Initialise la base de données pour la machine à sous"""
    with get_db() as db:
        # Table des scores avec player_id
        db.execute('''
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id TEXT NOT NULL,
                score INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Index pour optimiser les recherches par joueur
        db.execute('CREATE INDEX IF NOT EXISTS idx_player_id ON scores(player_id)')
        db.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON scores(timestamp)')

def save_score(player_id, score):
    """
    Sauvegarde un score pour un joueur spécifique
    
    Args:
        player_id (str): Identifiant du joueur
        score (int): Score à sauvegarder
    
    Returns:
        int: ID du score inséré
    """
    with get_db() as db:
        cursor = db.execute(
            'INSERT INTO scores (player_id, score) VALUES (?, ?)', 
            (player_id, score)
        )
        return cursor.lastrowid

def get_player_scores(player_id, limit=10):
    """
    Récupère les scores d'un joueur spécifique
    
    Args:
        player_id (str): Identifiant du joueur
        limit (int): Nombre maximum de scores à retourner
    
    Returns:
        list: Liste des scores avec timestamp
    """
    with get_db() as db:
        scores = db.execute('''
            SELECT score, timestamp 
            FROM scores 
            WHERE player_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (player_id, limit)).fetchall()
        
        return [dict(score) for score in scores]

def get_all_players():
    """
    Récupère la liste de tous les joueurs uniques
    
    Returns:
        list: Liste des IDs des joueurs
    """
    with get_db() as db:
        players = db.execute('''
            SELECT DISTINCT player_id 
            FROM scores 
            ORDER BY player_id
        ''').fetchall()
        
        return [player['player_id'] for player in players]

def get_player_stats(player_id):
    """
    Récupère les statistiques d'un joueur spécifique
    
    Args:
        player_id (str): Identifiant du joueur
    
    Returns:
        dict: Statistiques du joueur
    """
    with get_db() as db:
        stats = db.execute('''
            SELECT 
                COUNT(*) as total_games,
                MAX(score) as best_score,
                AVG(score) as average_score,
                MIN(score) as worst_score,
                MAX(timestamp) as last_played
            FROM scores 
            WHERE player_id = ?
        ''', (player_id,)).fetchone()
        
        return dict(stats) if stats else None

def get_global_stats():
    """
    Récupère les statistiques globales de tous les joueurs
    
    Returns:
        dict: Statistiques globales
    """
    with get_db() as db:
        stats = db.execute('''
            SELECT 
                COUNT(*) as total_scores,
                COUNT(DISTINCT player_id) as total_players,
                MAX(score) as global_best_score,
                AVG(score) as global_average_score
            FROM scores
        ''').fetchone()
        
        return dict(stats)

def get_leaderboard(limit=10):
    """
    Récupère le classement des meilleurs scores
    
    Args:
        limit (int): Nombre de joueurs à afficher
    
    Returns:
        list: Classement des meilleurs scores
    """
    with get_db() as db:
        leaderboard = db.execute('''
            SELECT 
                player_id,
                MAX(score) as best_score,
                COUNT(score) as games_played
            FROM scores 
            GROUP BY player_id
            ORDER BY best_score DESC
            LIMIT ?
        ''', (limit,)).fetchall()
        
        return [dict(row) for row in leaderboard]

def delete_player_scores(player_id):
    """
    Supprime tous les scores d'un joueur
    
    Args:
        player_id (str): Identifiant du joueur
    
    Returns:
        int: Nombre de scores supprimés
    """
    with get_db() as db:
        cursor = db.execute('DELETE FROM scores WHERE player_id = ?', (player_id,))
        return cursor.rowcount

# Test et démonstration
if __name__ == '__main__':
    # Initialisation
    init_db()
    print("✅ Base de données machine à sous initialisée")
    
    # Données de test
    test_data = [
        ('john', 1500),
        ('alice', 2300),
        ('bob', 1800),
        ('john', 1900),
        ('alice', 2700),
        ('bob', 2200),
        ('charlie', 1200),
        ('alice', 2500),
        ('john', 2100),
        ('diana', 3000)
    ]
    
    # Insertion des données de test
    for player_id, score in test_data:
        save_score(player_id, score)
    print("✅ Données de test insérées")
    
    # Affichage des statistiques
    print(f"\n📊 Statistiques globales:")
    global_stats = get_global_stats()
    print(f"   Total scores: {global_stats['total_scores']}")
    print(f"   Joueurs uniques: {global_stats['total_players']}")
    print(f"   Meilleur score global: {global_stats['global_best_score']}")
    print(f"   Score moyen global: {global_stats['global_average_score']:.2f}")
    
    # Test pour un joueur spécifique
    player = 'alice'
    print(f"\n🎯 Scores de {player}:")
    scores = get_player_scores(player, limit=5)
    for score in scores:
        print(f"   {score['score']} pts - {score['timestamp']}")
    
    print(f"\n📈 Statistiques de {player}:")
    stats = get_player_stats(player)
    if stats:
        print(f"   Parties jouées: {stats['total_games']}")
        print(f"   Meilleur score: {stats['best_score']}")
        print(f"   Score moyen: {stats['average_score']:.2f}")
        print(f"   Dernière partie: {stats['last_played']}")
    
    print(f"\n🏆 Classement:")
    leaderboard = get_leaderboard(limit=5)
    for i, player in enumerate(leaderboard, 1):
        print(f"   {i}. {player['player_id']}: {player['best_score']} pts ({player['games_played']} parties)")