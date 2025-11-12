/* |||||||||||||||||||||||||||||| functions||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| */
let start      = false;

// function hideTopBar() {
//   document.getElementsByClassName("header").style.
// }



function myFunction() {
  start = true;
  // document.getElementById("launchBallButton").style.animationPlayState = "paused";
  var button = document.getElementById("launchBallButton");
  button.style.animation = "none";  // Arrête l'animation
  button.style.boxShadow = "none";  // Supprime l'effet d'ombre

  document.getElementById("sketch").style.animationPlayState = "running";


}

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

var MainBallPosSize = [(Math.random()*canvassize/3) + canvassize/3, canvassize/10    ,   screensize/50   ,      0.1      ,  0.001 , 0.02  ];
//                    [position x                                 ,  position y      , taille , acceleration  , rebond , vitesse d'acceleration]
var MainBallDir     = [randomSign(Math.random()+1)*3, Math.random()];
//                    [direction x  , direction y  ]
let speed = 2

var vec             = [0,1];
let ball2radius     = screensize/65;

var possx = []; var possy = []

var colorArray = ["red","black","red","black","red" ]
let points = [4,1,0,1,4]
var finalPoints = 0;
var finalfinalPoints = 0;

/* |||||||||||||||||||||||||||||||create wanted number of balls |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| */


let obstacles_nombre  = 40;
let nb_lignes         = 5;           

let obstaclesParLigne = (obstacles_nombre / nb_lignes);

let grad_nb_obstacles = Math.ceil(obstaclesParLigne / 2);

for(var y=1; y<=nb_lignes ; y++) {
  for(var i=1; i<=grad_nb_obstacles; i++ ){ 
    possx.push((canvassize/(grad_nb_obstacles+1))*i);
    possy.push((canvassize/(nb_lignes+1))*y)
  }
  grad_nb_obstacles+=2;
}


/* ||||||||||||||||||||||||||||||||||||main functions|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| */
let replay = false;
function Replay(){
  document.getElementById("replayButton").style.animation = "none";  // Arrête l'animation
  document.getElementById("replayButton").style.boxShadow = "none";  // Supprime l'effet d'ombre
  
  scoredPoint=false;

  document.getElementById("sketch").style.animation = "pulsate 1s ease-out infinite";
  
  replay=true;
}

function setup() {
  var cns = createCanvas(canvassize,canvassize);
  cns.parent('sketch');
}

function draw() {
  background(125,0,0);
  
  if(replay) {
     MainBallPosSize = [(Math.random()*canvassize/3) + canvassize/3, canvassize/10    ,   screensize/50   ,      0.1      ,  0.001 , 0.02  ];
//                    [position x                                 ,  position y      , taille , acceleration  , rebond , vitesse d'acceleration]
     MainBallDir     = [randomSign(Math.random()+1)*3, Math.random()];
//                    [direction x  , direction y  ]
  }

  if(start){

    if(MainBallPosSize[0] < MainBallPosSize[2]/2|| MainBallPosSize[0] > canvassize - (MainBallPosSize[2]/2)) {
      MainBallDir[0] = -MainBallDir[0];
    }

    dist_contact = (MainBallPosSize[2]+ball2radius)/2;
    
    for(var i=0; i < obstacles_nombre; i++) { 
      dist         = DistanceTo(MainBallPosSize[0], MainBallPosSize[1], possx[i], possy[i]);

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
    MainBallPosSize[0] += MainBallDir[0] ;     
    MainBallPosSize[1] += MainBallDir[1] + MainBallPosSize[3];
    
    if ( MainBallPosSize[1] > (canvassize - MainBallPosSize[2] / 2)) {
      MainBallPosSize[4] *= MainBallPosSize[5]
      MainBallPosSize[1] = (canvassize - MainBallPosSize[2] / 2)
      MainBallDir[0] = 0


      document.getElementById("sketch").style.animation = "none";  // Arrête l'animation
      document.getElementById("sketch").style.boxShadow = "none";  // Supprime l'effet d'ombre
      
      document.getElementById("replayButton").style.animationPlayState = "running";
      document.getElementById("replayButton").style.animation = "pulsate 1s ease-out infinite";


      if(!scoredPoint) {
        finalPoints += getPoints(MainBallPosSize[0]);
        // finalfinalPoints += finalPoints;
        scoredPoint= true;
      }
      

    } 
    if (this.posY > (canvassize - this.size / 2)) {
      this.bounce *= this.speed;
      this.posY = canvassize - this.size / 2;
      this.dirX = 0;
    
      if (!this.scored) {
        finalPoints += getPoints(this.posX);
        this.scored = true;
    
        // Save the score when the ball lands
        saveScore(finalPoints);
      }
    }
  }


  for(var i=0; i < 5; i++) {
    rect((canvassize/5)*i,canvassize-50,canvassize/5, 50)
    text(points[i],((canvassize/5)*i)+(0.5*(canvassize/5)),canvassize-25,)
  }

  ellipse(MainBallPosSize[0],MainBallPosSize[1],MainBallPosSize[2]);

  for(var i=0; i < obstacles_nombre; i++) { 
    ellipse(possx[i], possy[i], ball2radius);
  }

  // if(replay) finalfinalPoints += finalPoints;
  finalfinalPoints = finalPoints;
  // text("points " + finalPoints , 750, 50)
  document.getElementById("scoreValue").textContent = finalfinalPoints;
  // if (finalPoints < 0) document.getElementById("launchBallButton").style.visibility = "visible";
  // if (finalPoints > 0) {
  //   document.getElementById("replayButton").style.visibility = "hidden";
  //   document.getElementById("launchBallButton").style.visibility = "visible";
  // }
  replay= !true;

  function saveScore(user_id, score) {
    fetch('http://127.0.0.1:5000/save_score', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ user_id: user_id, score: score }),
    })
      .then(response => response.json())
      .then(data => {
        console.log('Score saved:', data);
      })
      .catch((error) => {
        console.error('Error:', error);
      });
  }

  function getScores() {
    fetch('http://127.0.0.1:5000/get_scores')
      .then(response => response.json())
      .then(data => {
        let scoresDisplay = document.getElementById('scoresDisplay');
        scoresDisplay.innerHTML = '<h3>Previous Scores:</h3>';
        data.forEach(score => {
          scoresDisplay.innerHTML += `<p>Score: ${score.score}</p>`;
        });
      })
      .catch((error) => {
        console.error('Error:', error);
      });
  }



/* ||||||||||||||||||||||||||||||||||||||||debug||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| */

  // text("vecx " + vec[0] , 50, 50)
  // text("vecy " + vec[1] , 50, 75)
  // text("wtf " + dist , 50, 100)
  
  // text("wtf " + dist_contact , 50, 125)

  // text("posx " + MainBallPosSize[0] , 50, 150)
  // text("posy " + MainBallPosSize[1] , 50, 175)
  // text("distt  " + (canvassize - MainBallPosSize[1]) , 50, 200)

  
}

  
  

