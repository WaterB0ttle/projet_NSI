from flask import Flask, request, jsonify
import json
import os
from datetime import datetime
from typing import Dict, List, Any

app = Flask(__name__)

# Dictionnaire pour la sauvegarde locale
DATA_FILE = 'game_scores.json'
game_scores: Dict[str, List[Dict[str, Any]]] = {}

def load_scores():
    """Charge les scores depuis le fichier JSON"""
    global game_scores
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                game_scores = json.load(f)
            print("Scores charges avec succes")
    except Exception as e:
        print(f"Erreur lors du chargement: {e}")
        game_scores = {}

def save_scores():
    """Sauvegarde les scores dans le fichier JSON"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(game_scores, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Erreur lors de la sauvegarde: {e}")

# Charge au démarrage
load_scores()

@app.route('/save_score', methods=['POST'])
def save_score():
    data = request.get_json()
    player_id = data.get('player_id', 'guest')
    score = data.get('score')
    
    if score is None:
        return jsonify({'error': 'Score is required'}), 400

    # Sauvegarde dans le dictionnaire
    if player_id not in game_scores:
        game_scores[player_id] = []
    
    score_data = {
        'score': score,
        'timestamp': datetime.now().isoformat(),
        'date_display': datetime.now().strftime("%d/%m/%Y %H:%M"),
        'id': len(game_scores[player_id]) + 1
    }
    
    game_scores[player_id].append(score_data)
    save_scores()
    
    return jsonify({
        'status': 'success',
        'player_id': player_id,
        'score_data': score_data,
        'total_games': len(game_scores[player_id]),
        'message': 'Score sauvegarde avec succes'
    })

@app.route('/get_scores', methods=['GET'])
def get_scores():
    player_id = request.args.get('player_id', 'guest')
    limit = int(request.args.get('limit', 10))
    
    if player_id not in game_scores:
        return jsonify({'scores': [], 'player_id': player_id})
    
    scores = game_scores[player_id][-limit:]
    scores.reverse()
    
    return jsonify({
        'player_id': player_id,
        'scores': scores,
        'total_count': len(scores)
    })

@app.route('/get_leaderboard', methods=['GET'])
def get_leaderboard():
    leaderboard = []
    
    for player_id, scores in game_scores.items():
        if scores:
            total_score = sum(score['score'] for score in scores)
            best_score = max(score['score'] for score in scores)
            games_played = len(scores)
            
            leaderboard.append({
                'player_id': player_id,
                'total_score': total_score,
                'best_score': best_score,
                'games_played': games_played,
                'last_play': scores[-1]['timestamp'] if scores else None
            })
    
    leaderboard.sort(key=lambda x: x['total_score'], reverse=True)
    
    return jsonify({
        'leaderboard': leaderboard[:10],
        'generated_at': datetime.now().isoformat()
    })

@app.route('/get_player_stats', methods=['GET'])
def get_player_stats():
    player_id = request.args.get('player_id', 'guest')
    
    if player_id not in game_scores or not game_scores[player_id]:
        return jsonify({'error': 'Aucun score trouve pour ce joueur'}), 404
    
    scores = game_scores[player_id]
    score_values = [score['score'] for score in scores]
    
    stats = {
        'player_id': player_id,
        'total_games': len(scores),
        'total_score': sum(score_values),
        'average_score': round(sum(score_values) / len(scores), 2),
        'best_score': max(score_values),
        'worst_score': min(score_values),
        'last_game': scores[-1] if scores else None,
        'first_game': scores[0] if scores else None
    }
    
    return jsonify(stats)

@app.route('/get_all_players', methods=['GET'])
def get_all_players():
    players = list(game_scores.keys())
    return jsonify({
        'players': players,
        'total_players': len(players)
    })

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'total_players': len(game_scores),
        'total_games': sum(len(scores) for scores in game_scores.values()),
        'storage': 'dictionary',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("Serveur demarre sur http://localhost:5000")
    app.run(debug=True, port=5000)