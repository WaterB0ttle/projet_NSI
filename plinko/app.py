from flask import Flask, request, jsonify, send_from_directory
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

app = Flask(__name__)



class VictoryNode:
    """Nœud pour liste chaînée des victoires PLINKO"""
    def __init__(self, game_type: str, timestamp: str, win_amount: int):
        self.game_type = game_type
        self.timestamp = timestamp
        self.win_amount = win_amount
        self.next: Optional['VictoryNode'] = None

class VictoryLinkedList:
    """Liste chaînée pour les victoires PLINKO"""
    def __init__(self):
        self.head: Optional[VictoryNode] = None
        self.count = 0
    
    def add_victory(self, game_type: str, win_amount: int) -> None:
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
        return self.count
    
    def clear(self) -> None:
        self.head = None
        self.count = 0

class ScoreStack:
    """Pile pour les scores PLINKO"""
    def __init__(self):
        self.items: List[Dict[str, Any]] = []
    
    def push(self, score: int, game_type: str = 'plinko') -> None:
        self.items.append({
            'score': score,
            'game_type': game_type,
            'timestamp': datetime.now().isoformat(),
            'date_display': datetime.now().strftime("%d/%m/%Y %H:%M")
        })
        if len(self.items) > 50:
            self.items = self.items[-50:]
    
    def pop(self) -> Optional[Dict[str, Any]]:
        return self.items.pop() if self.items else None
    
    def peek(self) -> Optional[Dict[str, Any]]:
        return self.items[-1] if self.items else None
    
    def get_all(self) -> List[Dict[str, Any]]:
        return list(reversed(self.items))
    
    def clear(self) -> None:
        self.items = []
    
    def size(self) -> int:
        return len(self.items)
    
    def get_total_score(self) -> int:
        return sum(item['score'] for item in self.items)
    
    def get_current_score(self) -> int:
        return self.get_total_score()

class PlayerData:
    """Données d'un joueur PLINKO"""
    def __init__(self):
        self.score_stack = ScoreStack()
        self.victory_list = VictoryLinkedList()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'score_stack': self.score_stack.get_all(),
            'victory_list': self.victory_list.to_list()
        }
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        if 'score_stack' in data:
            for score_data in data['score_stack']:
                self.score_stack.push(score_data['score'], score_data.get('game_type', 'plinko'))
        
        if 'victory_list' in data:
            for victory_data in data['victory_list']:
                self.victory_list.add_victory(
                    victory_data['game_type'], 
                    victory_data['win_amount']
                )

# Fichier dédié au Plinko
DATA_FILE = 'plinko_scores.json'
players_data: Dict[str, PlayerData] = {}

def load_data():
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
            print("Données Plinko chargées avec succès")
    except Exception as e:
        print(f"Erreur chargement Plinko: {e}")
        players_data = {}

def save_data():
    try:
        data = {}
        for player_id, player_data in players_data.items():
            data[player_id] = player_data.to_dict()
        
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Erreur sauvegarde Plinko: {e}")

load_data()

# Routes PLINKO (mêmes que machine à sous mais port différent)
@app.route('/save_score', methods=['POST'])
def save_score():
    data = request.get_json()
    player_id = data.get('player_id', 'invite')
    score = data.get('score')
    game_type = data.get('game_type', 'plinko')  
    
    if score is None:
        return jsonify({'error': 'Score is required'}), 400

    if player_id not in players_data:
        players_data[player_id] = PlayerData()
    
    players_data[player_id].score_stack.push(score, game_type)
    
    # Dans Plinko, une victoire = score > 0
    if score > 0:
        players_data[player_id].victory_list.add_victory(game_type, score)
    
    save_data()
    
    return jsonify({
        'status': 'success',
        'player_id': player_id,
        'score': score,
        'current_total_score': players_data[player_id].score_stack.get_current_score(),
        'total_victories': players_data[player_id].victory_list.get_total_wins(),
        'message': 'Score Plinko sauvegarde avec succes'
    })

# ... (autres routes identiques à la machine à sous)

if __name__ == '__main__':
    print(" Serveur Plinko démarré!")
    print(" Stockage: Victoires (Liste chaînée) + Scores (Pile)")
    print(" Fichier de données:", DATA_FILE)
    print(" Accessible sur: http://localhost:5001")  
    app.run(debug=True, port=5001)