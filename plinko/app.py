from flask import Flask, request, jsonify, send_from_directory
import json
import os
from datetime import datetime
from typing import Dict, List, Any

app = Flask(__name__)

# Dictionnaire pour la sauvegarde locale
DATA_FILE = 'plinko_scores.json'
plinko_scores: Dict[str, List[Dict[str, Any]]] = {}

def load_scores():
    """Charge les scores depuis le fichier JSON"""
    global plinko_scores
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                plinko_scores = json.load(f)
            print("Scores plinko chargés avec succès")
    except Exception as e:
        print(f"Erreur lors du chargement: {e}")
        plinko_scores = {}

def save_scores():
    """Sauvegarde les scores dans le fichier JSON"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(plinko_scores, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Erreur lors de la sauvegarde: {e}")

# Charge au démarrage
load_scores()

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/save_score', methods=['POST'])
def save_score():
    data = request.get_json()
    player_id = data.get('player_id', 'invite')
    score = data.get('score')
    
    if score is None:
        return jsonify({'error': 'Score is required'}), 400

    # Sauvegarde dans le dictionnaire
    if player_id not in plinko_scores:
        plinko_scores[player_id] = []
    
    score_data = {
        'score': score,
        'timestamp': datetime.now().isoformat(),
        'date_display': datetime.now().strftime("%d/%m/%Y %H:%M"),
        'id': len(plinko_scores[player_id]) + 1,
        'game_type': 'plinko'
    }
    
    plinko_scores[player_id].append(score_data)
    save_scores()
    
    return jsonify({
        'status': 'success',
        'player_id': player_id,
        'score_data': score_data,
        'total_games': len(plinko_scores[player_id]),
        'message': 'Score plinko sauvegarde avec succes'
    })

@app.route('/get_scores', methods=['GET'])
def get_scores():
    player_id = request.args.get('player_id', 'invite')
    limit = int(request.args.get('limit', 10))
    
    if player_id not in plinko_scores:
        return jsonify({'scores': [], 'player_id': player_id})
    
    scores = plinko_scores[player_id][-limit:]
    scores.reverse()
    
    return jsonify({
        'player_id': player_id,
        'scores': scores,
        'total_count': len(scores)
    })

@app.route('/get_leaderboard', methods=['GET'])
def get_leaderboard():
    leaderboard = []
    
    for player_id, scores in plinko_scores.items():
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
    player_id = request.args.get('player_id', 'invite')
    
    if player_id not in plinko_scores or not plinko_scores[player_id]:
        return jsonify({'error': 'Aucun score trouve pour ce joueur'}), 404
    
    scores = plinko_scores[player_id]
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

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'total_players': len(plinko_scores),
        'total_games': sum(len(scores) for scores in plinko_scores.values()),
        'storage': 'dictionary',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("Serveur Plinko demarre sur http://localhost:5001")
    app.run(debug=True, port=5001)