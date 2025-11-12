from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
import contextlib

app = Flask(__name__)

# Database setup
DATABASE = 'slot_scores.db'

@contextlib.contextmanager
def get_db():
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
    with get_db() as db:
        db.execute('''
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id TEXT NOT NULL,
                score INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        db.execute('CREATE INDEX IF NOT EXISTS idx_player_id ON scores(player_id)')

init_db()

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Machine à Sous - Scores</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            .form-group { margin: 20px 0; }
            input, button { padding: 10px; margin: 5px; }
            .scores { margin-top: 30px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎰 Machine à Sous - Gestion des Scores</h1>
            
            <div class="form-group">
                <h3>Enregistrer un Score</h3>
                <input type="text" id="player_id" placeholder="ID du joueur" value="joueur1">
                <input type="number" id="score" placeholder="Score" value="1000">
                <button onclick="saveScore()">Sauvegarder le Score</button>
            </div>

            <div class="form-group">
                <h3>Voir les Scores</h3>
                <input type="text" id="get_player_id" placeholder="ID du joueur" value="joueur1">
                <button onclick="getScores()">Voir les Scores</button>
            </div>

            <div id="results" class="scores"></div>
        </div>

        <script>
            async function saveScore() {
                const player_id = document.getElementById('player_id').value;
                const score = document.getElementById('score').value;

                const response = await fetch('/save_score', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ player_id, score: parseInt(score) })
                });

                const result = await response.json();
                document.getElementById('results').innerHTML = 
                    `<p>✅ ${result.status === 'success' ? 'Score sauvegardé !' : 'Erreur: ' + result.error}</p>`;
            }

            async function getScores() {
                const player_id = document.getElementById('get_player_id').value;
                
                const response = await fetch(`/get_scores?player_id=${player_id}&limit=10`);
                const scores = await response.json();
                
                let html = '<h3>Derniers Scores:</h3><ul>';
                scores.forEach(score => {
                    html += `<li>${score.score} points - ${new Date(score.timestamp).toLocaleString()}</li>`;
                });
                html += '</ul>';
                
                document.getElementById('results').innerHTML = html;
            }
        </script>
    </body>
    </html>
    '''

@app.route('/save_score', methods=['POST'])
def save_score():
    data = request.get_json()
    player_id = data.get('player_id', 'guest')
    score = data.get('score')
    
    if score is None:
        return jsonify({'error': 'Score is required'}), 400

    try:
        with get_db() as db:
            db.execute('INSERT INTO scores (player_id, score) VALUES (?, ?)', (player_id, score))
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_scores', methods=['GET'])
def get_scores():
    player_id = request.args.get('player_id', 'guest')
    limit = min(int(request.args.get('limit', 10)), 100)  # Limite à 100 max
    
    try:
        with get_db() as db:
            scores = db.execute('''
                SELECT score, timestamp 
                FROM scores 
                WHERE player_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (player_id, limit)).fetchall()
        
        return jsonify([dict(score) for score in scores])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)