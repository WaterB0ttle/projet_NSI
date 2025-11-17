/* | functions| */
let start = false;
const SERVER_URL = 'http://localhost:5001';
let PLAYER_ID = localStorage.getItem('playerId') || 'invite';

// Structure de données avancées pour le Plinko

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
        if (this.items.length > 50) {
            this.items = this.items.slice(-50);
        }
    }

    pop() {
        return this.items.pop();
    }

    getAll() {
        return [...this.items].reverse();
    }

    clear() {
        this.items = [];
    }

    size() {
        return this.items.length;
    }
}

// Gestionnaire de stockage Plinko
class PlinkoStorage {
    constructor() {
        this.baseUrl = SERVER_URL;
        this.playerId = PLAYER_ID;
        this.gameStack = new GameStack();
        this.victoryList = new VictoryLinkedList();
        this.loadFromLocalStorage();
    }

    async saveScore(score, gameType = 'plinko') {
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
            console.error('Erreur sauvegarde plinko:', error);
            this.saveToLocalStorageFallback(score, gameType);
            return { status: 'success', message: 'Sauvegarde locale' };
        }
    }

    addVictory(winAmount) {
        this.victoryList.addVictory('plinko', winAmount);
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

    // Sauvegarde locale
    saveToLocalStorage() {
        const data = {
            gameStack: this.gameStack.getAll(),
            victoryList: this.victoryList.toArray(),
            playerId: this.playerId
        };
        localStorage.setItem(`plinko_data_${this.playerId}`, JSON.stringify(data));
    }

    loadFromLocalStorage() {
        const key = `plinko_data_${this.playerId}`;
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

    setPlayerId(id) {
        this.playerId = id;
        PLAYER_ID = id;
        localStorage.setItem('playerId', id);
        this.loadFromLocalStorage();
    }
}

// Initialisation du stockage
const plinkoStorage = new PlinkoStorage();

// Fonction pour mettre à jour le compteur de victoires
function updateVictoryCounter() {
    const stats = plinkoStorage.getVictoryStats();
    const victoryCounter = document.querySelector('.victory-number');
    
    if (victoryCounter) {
        victoryCounter.textContent = stats.totalWins;
    }
}

// Fonction pour afficher l'historique des scores
function displayScoreHistory() {
    const history = plinkoStorage.getGameHistory();
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

// Fonction pour mettre à jour l'affichage
function updateDisplay() {
    displayScoreHistory();
    updateVictoryCounter();
}

// Fonction pour effacer l'historique
function clearHistory() {
    if (confirm('Êtes-vous sûr de vouloir effacer tout l\'historique des parties ?')) {
        plinkoStorage.clearHistory();
        updateDisplay();
        alert('Historique effacé !');
    }
}

/* Variables et fonctions du jeu Plinko */
function randomSign(a){
    if(Math.random()>0.5) return -a;
    else return a;
}

function DistanceTo(x1, y1, x2, y2){
    return Math.sqrt((x2-x1)**2 + (y2-y1)**2);
}

function normalise(x1, y1, x2, y2, char){
    let dist = DistanceTo(x1, y1, x2, y2);
    let X1X2 = x2-x1; let Y1Y2 = y2-y1;
    if(char=='x') return X1X2 / dist;
    else if(char=='y') return Y1Y2 / dist;
    else throw new Error('Error')
}

function getPoints(x) {
    let a = canvassize/5;
    if(x < a || x > a * 4) return 4
    else if(x > a * 2 && x < a * 3) return 0
    else if((x > a && x < a * 2 ) || (x > a * 3 && x < a * 4)) return 1
}

/* ||||||||||||||||||||||||||||||var declarations||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| */
let screensize = (screen.availHeight+ screen.availWidth)/2 - screen.availWidth/5
let canvassize = screensize/2;
let dist_contact; let dist;  
var scoredPoint = false;

var MainBallPosSize = [(Math.random()*canvassize/3) + canvassize/3, canvassize/10, screensize/50, 0.1, 0.001, 0.02];
var MainBallDir = [randomSign(Math.random()+1)*3, Math.random()];
let speed = 2
var vec = [0,1];
let ball2radius = screensize/65;
var possx = []; var possy = []
var colorArray = ["red","black","red","black","red"]
let points = [4,1,0,1,4]
var finalPoints = 0;
var finalfinalPoints = 0;

/* Création des obstacles */
let obstacles_nombre = 40;
let nb_lignes = 5;           
let obstaclesParLigne = (obstacles_nombre / nb_lignes);
let grad_nb_obstacles = Math.ceil(obstaclesParLigne / 2);

for(var y=1; y<=nb_lignes ; y++) {
    for(var i=1; i<=grad_nb_obstacles; i++ ){ 
        possx.push((canvassize/(grad_nb_obstacles+1))*i);
        possy.push((canvassize/(nb_lignes+1))*y)
    }
    grad_nb_obstacles+=2;
}

/* Fonctions principales */
let replay = false;

function myFunction() {
    start = true;
    var button = document.getElementById("launchBallButton");
    button.style.animation = "none";
    button.style.boxShadow = "none";
    document.getElementById("sketch").style.animationPlayState = "running";
}

function Replay(){
    document.getElementById("replayButton").style.animation = "none";
    document.getElementById("replayButton").style.boxShadow = "none";
    scoredPoint = false;
    document.getElementById("sketch").style.animation = "pulsate 1s ease-out infinite";
    replay = true;
}

function setup() {
    var cns = createCanvas(canvassize,canvassize);
    cns.parent('sketch');
}

function draw() {
    background(125,0,0);
    
    if(replay) {
        MainBallPosSize = [(Math.random()*canvassize/3) + canvassize/3, canvassize/10, screensize/50, 0.1, 0.001, 0.02];
        MainBallDir = [randomSign(Math.random()+1)*3, Math.random()];
    }

    if(start){
        if(MainBallPosSize[0] < MainBallPosSize[2]/2|| MainBallPosSize[0] > canvassize - (MainBallPosSize[2]/2)) {
            MainBallDir[0] = -MainBallDir[0];
        }

        dist_contact = (MainBallPosSize[2]+ball2radius)/2;
        
        for(var i=0; i < obstacles_nombre; i++) { 
            dist = DistanceTo(MainBallPosSize[0], MainBallPosSize[1], possx[i], possy[i]);

            if( dist <= dist_contact ) {
                vec[0] = normalise(MainBallPosSize[0], MainBallPosSize[1], possx[i], possy[i] , 'x');
                vec[1] = normalise(MainBallPosSize[0], MainBallPosSize[1], possx[i], possy[i] , 'y');
            
                MainBallDir[0] = -vec[0];  
                MainBallDir[1] = -vec[1];
            
                MainBallPosSize[3] *= 0.5;
                MainBallPosSize[5] += 0.005;
                break;        
            }
        }
    
        MainBallPosSize[3] += MainBallPosSize[5];
        MainBallPosSize[0] += MainBallDir[0];     
        MainBallPosSize[1] += MainBallDir[1] + MainBallPosSize[3];
        
        if ( MainBallPosSize[1] > (canvassize - MainBallPosSize[2] / 2)) {
            MainBallPosSize[4] *= MainBallPosSize[5]
            MainBallPosSize[1] = (canvassize - MainBallPosSize[2] / 2)
            MainBallDir[0] = 0

            document.getElementById("sketch").style.animation = "none";
            document.getElementById("sketch").style.boxShadow = "none";
            
            document.getElementById("replayButton").style.animationPlayState = "running";
            document.getElementById("replayButton").style.animation = "pulsate 1s ease-out infinite";

            if(!scoredPoint) {
                const pointsWon = getPoints(MainBallPosSize[0]);
                finalPoints += pointsWon;
                scoredPoint = true;

                // Sauvegarde du score
                plinkoStorage.saveScore(pointsWon, 'plinko');

                // Ajout aux victoires si score positif
                if (pointsWon > 0) {
                    plinkoStorage.addVictory(pointsWon);
                }

                // Mise à jour automatique de l'affichage
                updateDisplay();
            }
        }
    }

    // Dessin des zones de score
    for(var i=0; i < 5; i++) {
        rect((canvassize/5)*i,canvassize-50,canvassize/5, 50)
        text(points[i],((canvassize/5)*i)+(0.5*(canvassize/5)),canvassize-25)
    }

    ellipse(MainBallPosSize[0],MainBallPosSize[1],MainBallPosSize[2]);

    for(var i=0; i < obstacles_nombre; i++) { 
        ellipse(possx[i], possy[i], ball2radius);
    }

    finalfinalPoints = finalPoints;
    document.getElementById("scoreValue").textContent = finalfinalPoints;
    replay = false;
}

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    // Écouteur d'événement pour le bouton effacer
    const clearHistoryButton = document.getElementById('clearHistory');
    if (clearHistoryButton) {
        clearHistoryButton.addEventListener('click', () => {
            clearHistory();
        });
    }

    // Initialisation des affichages
    updateDisplay();
});

// Définition de l'ID joueur
function setPlayerId() {
    const input = document.getElementById('playerId');
    if (!input) return;

    const newId = input.value.trim() || 'invite';
    plinkoStorage.setPlayerId(newId);
    
    const playerInfo = document.getElementById('playerInfo');
    if (playerInfo) {
        playerInfo.textContent = `Joueur: ${newId}`;
    }
    
    input.value = '';
    
    // Mise à jour des affichages avec les nouvelles données
    updateDisplay();
}