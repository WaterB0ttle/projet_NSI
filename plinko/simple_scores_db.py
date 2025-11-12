from flask import Flask, request, jsonify
import sqlite3
import contextlib
from datetime import datetime

app = Flask(__name__)

# Database setup
DATABASE = 'scores.db'

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
                score INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

init_db()

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Gestionnaire de Scores</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
            .form-group { margin: 20px 0; }
            input, button { padding: 12px; margin: 5px; border: 1px solid #ddd; border-radius: 5px; }
            button { background: #007bff; color: white; cursor: pointer; }
            button:hover { background: #0056b3; }
            .scores { margin-top: 30px; }
            .score-item { padding: 10px; border-bottom: 1px solid #eee; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏆 Gestionnaire de Scores</h1>
            
            <div class="form-group">
                <h3>Ajouter un Score</h3>
                <input type="number" id="score" placeholder="Entrez un score" value="100">
                <button onclick="saveScore()">Enregistrer le Score</button>
            </div>

            <div class="form-group">
                <h3>Actions</h3>
                <button onclick="getScores()">Voir Tous les Scores</button>
                <button onclick="getStats()">Statistiques</button>
            </div>

            <div id="results" class="scores"></div>
        </div>

        <script>
            async function saveScore() {
                const score = document.getElementById('score').value;

                const response = await fetch('/save_score', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ score: parseInt(score) })
                });

                const result = await response.json();
                showMessage(result.message || 'Erreur: ' + result.error);
            }

            async function getScores() {
                const response = await fetch('/get_scores');
                const data = await response.json();
                
                let html = '<h3>📊 Tous les Scores:</h3>';
                data.scores.forEach(score => {
                    const date = new Date(score.timestamp).toLocaleString();
                    html += `<div class="score-item">#${score.id} - ${score.score} points (${date})</div>`;
                });
                html += `<p><strong>Total: ${data.count} scores</strong></p>`;
                
                document.getElementById('results').innerHTML = html;
            }

            async function getStats() {
                const response = await fetch('/stats');
                const stats = await response.json();
                
                let html = '<h3>📈 Statistiques:</h3>';
                if (stats.message) {
                    html += `<p>${stats.message}</p>`;
                } else {
                    html += `
                        <p><strong>Total scores:</strong> ${stats.total_scores}</p>
                        <p><strong>Meilleur score:</strong> ${stats.highest_score}</p>
                        <p><strong>Score moyen:</strong> ${Math.round(stats.average_score)}</p>
                        <p><strong>Plus récent:</strong> ${new Date(stats.last_score_date).toLocaleString()}</p>
                    `;
                }
                
                document.getElementById('results').innerHTML = html;
            }

            function showMessage(message) {
                document.getElementById('results').innerHTML = `<p>${message}</p>`;
            }
        </script>
    </body>
    </html>
    '''

@app.route('/save_score', methods=['POST'])
def save_score():
    data = request.get_json()
    score = data.get('score')

    if score is None:
        return jsonify({'error': 'Score is required'}), 400

    try:
        score = int(score)
        if score < 0:
            return jsonify({'error': 'Score must be positive'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': 'Score must be a valid integer'}), 400

    try:
        with get_db() as db:
            cursor = db.execute('INSERT INTO scores (score) VALUES (?)', (score,))
        return jsonify({'message': 'Score saved successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_scores', methods=['GET'])
def get_scores():
    try:
        limit = min(int(request.args.get('limit', 100)), 1000)
    except ValueError:
        limit = 100

    try:
        with get_db() as db:
            scores = db.execute('SELECT * FROM scores ORDER BY id DESC LIMIT ?', (limit,)).fetchall()
        
        return jsonify({
            'scores': [dict(score) for score in scores],
            'count': len(scores)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    try:
        with get_db() as db:
            stats = db.execute('''
                SELECT 
                    COUNT(*) as total_scores,
                    MAX(score) as highest_score,
                    AVG(score) as average_score,
                    MAX(timestamp) as last_score_date
                FROM scores
            ''').fetchone()
        
        if stats['total_scores'] == 0:
            return jsonify({'message': 'No scores available yet'})
        
        return jsonify(dict(stats))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)