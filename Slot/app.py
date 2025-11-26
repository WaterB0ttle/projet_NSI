from flask import Flask, request, jsonify, send_from_directory
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

app = Flask(__name__)

# Structure de données avancées

class VictoryNode:
    """Nœud pour liste chaînée des victoires"""
    def __init__(self, game_type: str, timestamp: str, win_amount: int):
        self.game_type = game_type
        self.timestamp = timestamp
        self.win_amount = win_amount
        self.next: Optional['VictoryNode'] = None

class VictoryLinkedList:
    """Liste chaînée pour les victoires"""
    def __init__(self):
        self.head: Optional[VictoryNode] = None
        self.count = 0
    
    def add_victory(self, game_type: str, win_amount: int) -> None:
        """Ajoute une victoire à la liste chaînée"""
        new_node = VictoryNode(game_type, datetime.now().isoformat(), win_amount)
        if not self.head:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node
        self.count += 1
    
    def to_list(self) -> List[Dict[str, Any]]:
        """Convertit la liste chaînée en liste Python"""
        result = []
        current = self.head
        while current:
            result.append({
                'game_type': current.game_type,
                'timestamp': current.timestamp,
                'win_amount': current.win_amount
            })
            current = current.next
        return result
    
    def get_total_wins(self) -> int:
        """Retourne le nombre total de victoires"""
        return self.count
    
    def clear(self) -> None:
        """Vide la liste chaînée"""
        self.head = None
        self.count = 0

class ScoreStack:
    """Pile pour les scores individuels"""
    def __init__(self):
        self.items: List[Dict[str, Any]] = []
    
    def push(self, score: int, game_type: str = 'slot') -> None:
        """Empile un score"""
        self.items.append({
            'score': score,
            'game_type': game_type,
            'timestamp': datetime.now().isoformat(),
            'date_display': datetime.now().strftime("%d/%m/%Y %H:%M")
        })
        # Garde seulement les 50 derniers scores
        if len(self.items) > 50:
            self.items = self.items[-50:]
    
    def pop(self) -> Optional[Dict[str, Any]]:
        """Dépile un score"""
        return self.items.pop() if self.items else None
    
    def peek(self) -> Optional[Dict[str, Any]]:
        """Regarde le score au sommet"""
        return self.items[-1] if self.items else None
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Retourne tous les scores (plus récent en premier)"""
        return list(reversed(self.items))
    
    def clear(self) -> None:
        """Vide la pile"""
        self.items = []
    
    def size(self) -> int:
        """Retourne la taille de la pile"""
        return len(self.items)
    
    def get_total_score(self) -> int:
        """Calcule le score total"""
        return sum(item['score'] for item in self.items)
    
    def get_current_score(self) -> int:
        """Retourne le score actuel (total)"""
        return self.get_total_score()

class PlayerData:
    """Données d'un joueur avec structures avancées"""
    def __init__(self):
        self.score_stack = ScoreStack()
        self.victory_list = VictoryLinkedList()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire pour JSON"""
        return {
            'score_stack': self.score_stack.get_all(),
            'victory_list': self.victory_list.to_list()
        }
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Reconstruit depuis un dictionnaire"""
        if 'score_stack' in data:
            for score_data in data['score_stack']:
                self.score_stack.push(score_data['score'], score_data.get('game_type', 'slot'))
        
        if 'victory_list' in data:
            for victory_data in data['victory_list']:
                self.victory_list.add_victory(
                    victory_data['game_type'], 
                    victory_data['win_amount']
                )

# Dictionnaire global pour la sauvegarde
DATA_FILE = 'slot_scores.json'
players_data: Dict[str, PlayerData] = {}

def load_data():
    """Charge les données depuis le fichier JSON"""
    global players_data
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                players_data = {}
                for player_id, player_data in data.items():
                    player = PlayerData()
                    player.from_dict(player_data)
                    players_data[player_id] = player
            print("Données chargées avec succès")
    except Exception as e:
        print(f"Erreur lors du chargement: {e}")
        players_data = {}

def save_data():
    """Sauvegarde les données dans le fichier JSON"""
    try:
        data = {}
        for player_id, player_data in players_data.items():
            data[player_id] = player_data.to_dict()
        
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Erreur lors de la sauvegarde: {e}")

# Charge au démarrage
load_data()

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/save_score', methods=['POST'])
def save_score():
    data = request.get_json()
    player_id = data.get('player_id', 'invite')
    score = data.get('score')
    game_type = data.get('game_type', 'slot')
    
    if score is None:
        return jsonify({'error': 'Score is required'}), 400

    # Initialise le joueur si nécessaire
    if player_id not in players_data:
        players_data[player_id] = PlayerData()
    
    # Sauvegarde dans la pile des scores
    players_data[player_id].score_stack.push(score, game_type)
    
    # Si c'est une victoire (score positif), ajoute à la liste chaînée
    if score > 0:
        players_data[player_id].victory_list.add_victory(game_type, score)
    
    save_data()
    
    return jsonify({
        'status': 'success',
        'player_id': player_id,
        'score': score,
        'current_total_score': players_data[player_id].score_stack.get_current_score(),
        'total_victories': players_data[player_id].victory_list.get_total_wins(),
        'message': 'Score sauvegarde avec succes'
    })

@app.route('/get_scores', methods=['GET'])
def get_scores():
    player_id = request.args.get('player_id', 'invite')
    limit = int(request.args.get('limit', 10))
    
    if player_id not in players_data:
        return jsonify({'scores': [], 'player_id': player_id})
    
    scores = players_data[player_id].score_stack.get_all()[:limit]
    
    return jsonify({
        'player_id': player_id,
        'scores': scores,
        'current_total_score': players_data[player_id].score_stack.get_current_score(),
        'total_count': len(scores)
    })

@app.route('/get_victories', methods=['GET'])
def get_victories():
    player_id = request.args.get('player_id', 'invite')
    
    if player_id not in players_data:
        return jsonify({'victories': [], 'player_id': player_id})
    
    victories = players_data[player_id].victory_list.to_list()
    
    return jsonify({
        'player_id': player_id,
        'victories': victories,
        'total_victories': players_data[player_id].victory_list.get_total_wins()
    })

@app.route('/reset_scores', methods=['POST'])
def reset_scores():
    """Réinitialise seulement les scores (garde les victoires)"""
    data = request.get_json()
    player_id = data.get('player_id', 'invite')
    
    if player_id not in players_data:
        return jsonify({'error': 'Joueur non trouve'}), 404
    
    # Sauvegarde le nombre de victoires avant reset
    total_victories = players_data[player_id].victory_list.get_total_wins()
    
    # Réinitialise seulement les scores
    players_data[player_id].score_stack.clear()
    save_data()
    
    return jsonify({
        'status': 'success',
        'player_id': player_id,
        'score_reset_to': 0,
        'victories_preserved': total_victories,
        'message': 'Scores reinitialises, victoires conservees'
    })

@app.route('/reset_all', methods=['POST'])
def reset_all():
    """Réinitialise complètement (scores et victoires)"""
    data = request.get_json()
    player_id = data.get('player_id', 'invite')
    
    if player_id not in players_data:
        return jsonify({'error': 'Joueur non trouve'}), 404
    
    # Réinitialise tout
    players_data[player_id].score_stack.clear()
    players_data[player_id].victory_list.clear()
    save_data()
    
    return jsonify({
        'status': 'success',
        'player_id': player_id,
        'score_reset_to': 0,
        'victories_reset_to': 0,
        'message': 'Scores et victoires reinitialises'
    })

@app.route('/get_player_stats', methods=['GET'])
def get_player_stats():
    player_id = request.args.get('player_id', 'invite')
    
    if player_id not in players_data:
        return jsonify({'error': 'Joueur non trouve'}), 404
    
    player_data = players_data[player_id]
    scores = player_data.score_stack.get_all()
    
    if not scores:
        return jsonify({
            'player_id': player_id,
            'current_score': 0,
            'total_victories': player_data.victory_list.get_total_wins(),
            'total_games': 0,
            'average_score': 0,
            'best_score': 0
        })
    
    score_values = [score['score'] for score in scores]
    
    return jsonify({
        'player_id': player_id,
        'current_score': player_data.score_stack.get_current_score(),
        'total_victories': player_data.victory_list.get_total_wins(),
        'total_games': len(scores),
        'average_score': round(sum(score_values) / len(scores), 2),
        'best_score': max(score_values),
        'worst_score': min(score_values)
    })

@app.route('/get_leaderboard', methods=['GET'])
def get_leaderboard():
    leaderboard = []
    
    for player_id, player_data in players_data.items():
        current_score = player_data.score_stack.get_current_score()
        total_victories = player_data.victory_list.get_total_wins()
        
        leaderboard.append({
            'player_id': player_id,
            'total_score': current_score,
            'total_victories': total_victories,
            'games_played': player_data.score_stack.size(),
            'last_play': player_data.score_stack.peek()['timestamp'] if player_data.score_stack.peek() else None
        })
    
    leaderboard.sort(key=lambda x: x['total_score'], reverse=True)
    
    return jsonify({
        'leaderboard': leaderboard[:10],
        'generated_at': datetime.now().isoformat()
    })

@app.route('/health', methods=['GET'])
def health_check():
    total_players = len(players_data)
    total_games = sum(player_data.score_stack.size() for player_data in players_data.values())
    total_victories = sum(player_data.victory_list.get_total_wins() for player_data in players_data.values())
    
    return jsonify({
        'status': 'healthy',
        'total_players': total_players,
        'total_games': total_games,
        'total_victories': total_victories,
        'storage': 'victoires_liste_chainee + scores_pile',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print(" Serveur Slot Machine démarré!")
    print(" Stockage: Victoires (Liste chaînée) + Scores (Pile)")
    print(" Fichier de données:", DATA_FILE)
    print(" Accessible sur: http://localhost:5000")
    app.run(debug=True, port=5000)