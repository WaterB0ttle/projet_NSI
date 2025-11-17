/**
 * Setup
 */
const debugEl = document.getElementById('debug'),
      // Mapping des index vers les icônes
      iconMap = ["Banane", "Sept", "Cerise", "Prune", "Orange", "Cloche", "Bar", "Citron", "Pastèque"],
      // Largeur des icônes
      icon_width = 79,	
      // Hauteur d'une icône dans la bande
      icon_height = 79,	
      // Nombre d'icônes dans la bande
      num_icons = 9,	
      // Vitesse max en ms pour animer une icône vers le bas
      time_per_icon = 100,
      // Contient les index des icônes
      indexes = [0, 0, 0];

let score = 0; // Score initial

// Configuration
const SERVER_URL = 'http://localhost:5000';
let PLAYER_ID = localStorage.getItem('playerId') || 'invite';

// Structure de données avancées

// Nœud pour liste chaînée des victoires
class VictoryNode {
    constructor(gameType, timestamp, winAmount) {
        this.gameType = gameType;
        this.timestamp = timestamp;
        this.winAmount = winAmount;
        this.next = null;
    }
}

// Liste chaînée pour les victoires
class VictoryLinkedList {
    constructor() {
        this.head = null;
        this.count = 0;
    }

    addVictory(gameType, winAmount) {
        const newVictory = new VictoryNode(gameType, new Date().toISOString(), winAmount);
        if (!this.head) {
            this.head = newVictory;
        } else {
            let current = this.head;
            while (current.next) {
                current = current.next;
            }
            current.next = newVictory;
        }
        this.count++;
    }

    toArray() {
        const result = [];
        let current = this.head;
        while (current) {
            result.push({
                gameType: current.gameType,
                timestamp: current.timestamp,
                winAmount: current.winAmount
            });
            current = current.next;
        }
        return result;
    }

    getTotalWins() {
        return this.count;
    }
}

// Pile pour les parties individuelles
class GameStack {
    constructor() {
        this.items = [];
    }

    push(gameResult) {
        this.items.push(gameResult);
        // Garde seulement les 50 dernières parties
        if (this.items.length > 50) {
            this.items = this.items.slice(-50);
        }
    }

    pop() {
        return this.items.pop();
    }

    peek() {
        return this.items[this.items.length - 1];
    }

    getAll() {
        return [...this.items].reverse(); // Plus récent en premier
    }

    clear() {
        this.items = [];
    }

    size() {
        return this.items.length;
    }
}

// Gestionnaire de stockage
class GameStorage {
    constructor() {
        this.baseUrl = SERVER_URL;
        this.playerId = PLAYER_ID;
        this.gameStack = new GameStack();
        this.victoryList = new VictoryLinkedList();
        this.loadFromLocalStorage();
    }

    async saveScore(score, gameType = 'slot') {
        try {
            const response = await fetch(`${this.baseUrl}/save_score`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    player_id: this.playerId,
                    score: score,
                    game_type: gameType
                })
            });
            
            const result = await response.json();
            console.log('Score sauvegardé:', result);
            
            // Ajoute à la pile des parties
            this.gameStack.push({
                score: score,
                gameType: gameType,
                timestamp: new Date().toISOString(),
                date: new Date().toLocaleString()
            });
            
            this.saveToLocalStorage();
            return result;
        } catch (error) {
            console.error('Erreur sauvegarde:', error);
            this.saveToLocalStorageFallback(score, gameType);
            return { status: 'success', message: 'Sauvegarde locale' };
        }
    }

    addVictory(gameType, winAmount) {
        this.victoryList.addVictory(gameType, winAmount);
        this.saveToLocalStorage();
    }

    getVictoryStats() {
        return {
            totalWins: this.victoryList.getTotalWins(),
            victories: this.victoryList.toArray()
        };
    }

    getGameHistory() {
        return this.gameStack.getAll();
    }

    clearHistory() {
        this.gameStack.clear();
        this.saveToLocalStorage();
    }

    async getCurrentScore() {
        try {
            const response = await fetch(`${this.baseUrl}/get_scores?player_id=${this.playerId}&limit=1`);
            const data = await response.json();
            if (data.scores && data.scores.length > 0) {
                return data.scores[0].score;
            }
            return 0;
        } catch (error) {
            console.error('Erreur récupération score:', error);
            return this.getScoreFromLocalStorage();
        }
    }

    // Sauvegarde locale
    saveToLocalStorage() {
        const data = {
            gameStack: this.gameStack.getAll(),
            victoryList: this.victoryList.toArray(),
            playerId: this.playerId
        };
        localStorage.setItem(`game_data_${this.playerId}`, JSON.stringify(data));
    }

    loadFromLocalStorage() {
        const key = `game_data_${this.playerId}`;
        const data = JSON.parse(localStorage.getItem(key) || '{}');
        
        if (data.gameStack) {
            data.gameStack.forEach(game => {
                this.gameStack.push(game);
            });
        }
        
        if (data.victoryList) {
            data.victoryList.forEach(victory => {
                this.victoryList.addVictory(victory.gameType, victory.winAmount);
            });
        }
    }

    saveToLocalStorageFallback(score, gameType) {
        this.gameStack.push({
            score: score,
            gameType: gameType,
            timestamp: new Date().toISOString(),
            date: new Date().toLocaleString()
        });
        this.saveToLocalStorage();
    }

    getScoreFromLocalStorage() {
        const history = this.gameStack.getAll();
        if (history.length > 0) {
            return history.reduce((total, game) => total + game.score, 0);
        }
        return 0;
    }

    setPlayerId(id) {
        this.playerId = id;
        PLAYER_ID = id;
        localStorage.setItem('playerId', id);
        this.loadFromLocalStorage();
    }
}

// Initialisation du stockage
const gameStorage = new GameStorage();

// Fonction pour mettre à jour le compteur de victoires
function updateVictoryCounter() {
    const stats = gameStorage.getVictoryStats();
    const victoryCounter = document.querySelector('.victory-number');
    
    if (victoryCounter) {
        victoryCounter.textContent = stats.totalWins;
    }
}

// Fonction pour afficher l'historique des scores
function displayScoreHistory() {
    const history = gameStorage.getGameHistory();
    const historyList = document.getElementById('scoreHistory');
    
    if (historyList) {
        if (history.length === 0) {
            historyList.innerHTML = '<li>Aucune partie enregistrée</li>';
            return;
        }
        
        historyList.innerHTML = history.map(game => `
            <li>
                <span class="game-type">${game.gameType}</span>
                <span class="game-score ${game.score >= 0 ? 'win' : 'lose'}">
                    ${game.score >= 0 ? '+' : ''}${game.score} points
                </span>
                <span class="game-date">${game.date}</span>
            </li>
        `).join('');
    }
}

// Fonction pour afficher le score actuel
async function showCurrentScore() {
    try {
        const currentScore = await gameStorage.getCurrentScore();
        const scoresDisplay = document.getElementById('scoresDisplay');
        
        if (scoresDisplay) {
            scoresDisplay.innerHTML = `
                <div class="current-score">
                    <h3>Score Actuel</h3>
                    <div class="score-value-large">${currentScore} points</div>
                </div>
            `;
        }
    } catch (error) {
        console.error('Erreur affichage score:', error);
    }
}

// Fonction pour rafraîchir l'historique
function refreshHistory() {
    displayScoreHistory();
    showCurrentScore();
    updateVictoryCounter(); // Mettre à jour le compteur de victoires
}

// Fonction pour effacer l'historique
function clearHistory() {
    if (confirm('Êtes-vous sûr de vouloir effacer tout l\'historique des parties ?')) {
        gameStorage.clearHistory();
        refreshHistory();
        alert('Historique effacé !');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const scoreEl = document.getElementById('scoreValue');

    // Fonction pour faire tourner un rouleau
    const roll = (reel, offset = 0) => {
        const delta = (offset + 2) * num_icons + Math.floor(Math.random() * num_icons);

        return new Promise((resolve, reject) => {
            const style = getComputedStyle(reel),
                  backgroundPositionY = parseFloat(style["background-position-y"]),
                  targetBackgroundPositionY = backgroundPositionY + delta * icon_height,
                  normTargetBackgroundPositionY = targetBackgroundPositionY % (num_icons * icon_height);

            setTimeout(() => {
                reel.style.transition = `background-position-y ${(8 + 1 * delta) * time_per_icon}ms cubic-bezier(.41,-0.01,.63,1.09)`;
                reel.style.backgroundPositionY = `${backgroundPositionY + delta * icon_height}px`;
            }, offset * 150);

            setTimeout(() => {
                reel.style.transition = `none`;
                reel.style.backgroundPositionY = `${normTargetBackgroundPositionY}px`;
                resolve(delta % num_icons);
            }, (8 + 1 * delta) * time_per_icon + offset * 150);
        });
    };

    // Fonction pour faire tourner tous les rouleaux
    async function rollAll() {
        debugEl.textContent = 'Rotation...';
        const reelsList = document.querySelectorAll('.slots > .reel');

        // Déduction des points pour chaque partie
        const betAmount = 10;
        score -= betAmount;
        if (scoreEl) scoreEl.textContent = score;

        // Sauvegarde de la perte
        await gameStorage.saveScore(-betAmount, 'machine_a_sous');

        Promise
            .all([...reelsList].map((reel, i) => roll(reel, i)))
            .then(async (deltas) => {
                deltas.forEach((delta, i) => indexes[i] = (indexes[i] + delta) % num_icons);
                debugEl.textContent = indexes.map((i) => iconMap[i]).join(' - ');

                // Vérification des conditions de gain
                let winAmount = 0;
                let isVictory = false;
                
                if (indexes[0] === indexes[1] && indexes[1] === indexes[2]) {
                    // Trois symboles identiques
                    winAmount = 100;
                    isVictory = true;
                    document.querySelector(".slots").classList.add("win2");
                    setTimeout(() => document.querySelector(".slots").classList.remove("win2"), 2000);
                } else if (indexes[0] === indexes[1] || indexes[1] === indexes[2]) {
                    // Deux symboles identiques
                    winAmount = 50;
                    document.querySelector(".slots").classList.add("win1");
                    setTimeout(() => document.querySelector(".slots").classList.remove("win1"), 2000);
                }

                // Si gain, augmentation du score
                if (winAmount > 0) {
                    score += winAmount;
                    if (scoreEl) scoreEl.textContent = score;
                    // Sauvegarde du gain
                    await gameStorage.saveScore(winAmount, 'machine_a_sous');
                    
                    // Ajout aux victoires si trois symboles identiques
                    if (isVictory) {
                        gameStorage.addVictory('machine_a_sous', winAmount);
                        updateVictoryCounter(); // Mise à jour immédiate du compteur
                    }
                }

                // Mise à jour des affichages après la partie
                refreshHistory();
            });
    }

    // Récupération des boutons
    const spinButton = document.getElementById('spinButton');
    const refreshHistoryButton = document.getElementById('refreshHistory');
    const clearHistoryButton = document.getElementById('clearHistory');

    // Écouteur d'événement pour le bouton de rotation
    if (spinButton) {
        spinButton.addEventListener('click', () => {
            rollAll();
        });
    }

    // Écouteur d'événement pour le bouton rafraîchir
    if (refreshHistoryButton) {
        refreshHistoryButton.addEventListener('click', () => {
            refreshHistory();
        });
    }

    // Écouteur d'événement pour le bouton effacer
    if (clearHistoryButton) {
        clearHistoryButton.addEventListener('click', () => {
            clearHistory();
        });
    }

    // Initialisation des affichages
    refreshHistory();
});

// Définition de l'ID joueur
function setPlayerId() {
    const input = document.getElementById('playerId');
    if (!input) return;

    const newId = input.value.trim() || 'invite';
    gameStorage.setPlayerId(newId);
    
    const playerInfo = document.getElementById('playerInfo');
    if (playerInfo) {
        playerInfo.textContent = `Joueur: ${newId}`;
    }
    
    input.value = '';
    
    // Rafraîchissement des affichages avec les nouvelles données
    refreshHistory();
}