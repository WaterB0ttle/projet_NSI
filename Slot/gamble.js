/**
 * Setup
 */
const debugEl = document.getElementById('debug'),
      // Mapping of indexes to icons: start from banana in the middle of the initial position and then upwards
      iconMap = ["Banane", "Sept", "Cerise", "Prune", "Orange", "Cloche", "Bar", "Citron", "Pastèque"],
      // Width of the icons
      icon_width = 79,	
      // Height of one icon in the strip
      icon_height = 79,	
      // Number of icons in the strip
      num_icons = 9,	
      // Max-speed in ms for animating one icon down
      time_per_icon = 100,
      // Holds icon indexes
      indexes = [0, 0, 0];

let score = 0; // Initialize score variable

document.addEventListener('DOMContentLoaded', () => {
    const scoreEl = document.getElementById('scoreValue'); // Corrected score display element

    // Function to roll a reel
    const roll = (reel, offset = 0) => {
        // Minimum of 2 + the reel offset rounds
        const delta = (offset + 2) * num_icons + Math.round(Math.random() * num_icons); 

        // Return promise so we can wait for all reels to finish
        return new Promise((resolve, reject) => {
            const style = getComputedStyle(reel),
                  // Current background position
                  backgroundPositionY = parseFloat(style["background-position-y"]),
                  // Target background position
                  targetBackgroundPositionY = backgroundPositionY + delta * icon_height,
                  // Normalized background position, for reset
                  normTargetBackgroundPositionY = targetBackgroundPositionY % (num_icons * icon_height);

            // Delay animation with timeout, for some reason a delay in the animation property causes stutter
            setTimeout(() => {
                // Set transition properties ==> https://cubic-bezier.com/#.41,-0.01,.63,1.09
                reel.style.transition = `background-position-y ${(8 + 1 * delta) * time_per_icon}ms cubic-bezier(.41,-0.01,.63,1.09)`;
                // Set background position
                reel.style.backgroundPositionY = `${backgroundPositionY + delta * icon_height}px`;
            }, offset * 150);

            // After animation
            setTimeout(() => {
                // Reset position, so that it doesn't get higher without limit
                reel.style.transition = `none`;
                reel.style.backgroundPositionY = `${normTargetBackgroundPositionY}px`;
                // Resolve this promise
                resolve(delta % num_icons);
            }, (8 + 1 * delta) * time_per_icon + offset * 150);
        });
    };

    // Function to roll all reels
    function rollAll() {
        debugEl.textContent = 'rolling...';
        const reelsList = document.querySelectorAll('.slots > .reel');

        Promise
            .all([...reelsList].map((reel, i) => roll(reel, i)))
            .then((deltas) => {
                deltas.forEach((delta, i) => indexes[i] = (indexes[i] + delta) % num_icons);
                debugEl.textContent = indexes.map((i) => iconMap[i]).join(' - ');

                // Deduct points for each play
                score -= 10; // Removes 10 points for each play
                scoreEl.textContent = score; // Update score display

                // Check for win conditions
                if (indexes[0] === indexes[1] || indexes[1] === indexes[2]) {
                    const winCls = indexes[0] === indexes[2] ? "win2" : "win1";
                    document.querySelector(".slots").classList.add(winCls);
                    setTimeout(() => document.querySelector(".slots").classList.remove(winCls), 2000);

                    // If it's a win, increase score
                    score += 50; // Add 50 points for a win
                    scoreEl.textContent = score; // Update score display
                }
            });
    }

    // Get the button element
    const spinButton = document.getElementById('spinButton');

    // Add click event listener to the button
    spinButton.addEventListener('click', () => {
        // Trigger the roll when the button is clicked
        rollAll();
    });
});

function saveSlotScore(user_id, score) {
    fetch('http://127.0.0.1:5000/save_slot_score', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ user_id: user_id, score: score }),
    })
      .then(response => response.json())
      .then(data => {
        console.log('Slot score saved:', data);
      })
      .catch((error) => {
        console.error('Error:', error);
      });
  }

  function getSlotScores(user_id) {
    fetch(`http://127.0.0.1:5000/get_slot_scores?user_id=${user_id}`)
      .then(response => response.json())
      .then(data => {
        let scoresDisplay = document.getElementById('scoresDisplay');
        scoresDisplay.innerHTML = '<h3>Previous Slot Scores:</h3>';
        data.forEach(score => {
          scoresDisplay.innerHTML += `<p>Score: ${score.score}</p>`;
        });
      })
      .catch((error) => {
        console.error('Error:', error);
      });
  }

// Configuration
const SERVER_URL = 'http://localhost:5000';
const PLAYER_ID = 'player_1'; // Change to dynamic ID later

// Save score to backend
async function saveScore(score) {
    try {
        const response = await fetch(`${SERVER_URL}/save_score`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                player_id: PLAYER_ID,
                score: score
            })
        });
        console.log('Score saved:', await response.json());
    } catch (error) {
        console.error('Failed to save:', error);
    }
}

// Load score history
async function loadScoreHistory() {
    try {
        const response = await fetch(`${SERVER_URL}/get_scores?player_id=${PLAYER_ID}`);
        const history = await response.json();
        
        const historyList = document.getElementById('scoreHistory');
        historyList.innerHTML = history.map(item => `
            <li>${item.score} pts (${new Date(item.timestamp).toLocaleString()})</li>
        `).join('');
    } catch (error) {
        console.error('Failed to load history:', error);
    }
}

// Modify your existing spin function
function rollAll() {
    // ... existing spin logic ...
    
    // After updating score:
    saveScore(currentScore);  // Add this line
}