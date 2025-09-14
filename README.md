# 🚀 SPACE DEFENDERS  

An **arcade-style 2D shooter** developed with PyGame, compiled to **WebAssembly** using pygbag, and deployed automatically to **GitHub Pages** via CI/CD.  
Play as a lone space explorer who has to defend their base from an onslaught of incoming asteroids.  


🕹️ **[Play the Game Online!](https://nikiel54.github.io/space-shooter-game/)**  

Aim of the game is to collect powerups, beatdown asteroids and survive as long as possible.  
It takes ~10 seconds to load in any suitable browser.  
Try your best to beat my personal high score of 587 points. Good Luck! 


## 🎮 How to Play
- Use **WASD** to move your spaceship.  
- Press **Left CLick** to shoot lasers.  
- Destroy all asteroids and avoid collisions.  
- Survive as long as possible while scoring points!  


## ✨ Features
- 🛸 **Arcade gameplay** – control your spaceship, dodge asteroids, and blast enemies.  
- 🎯 **Dynamic difficulty scaling** – the game gets harder as you progress.  
- 💥 **Collision detection system** – responsive interactions between lasers, asteroids, and player.  
- 🌍 **Runs in the browser** – thanks to WebAssembly, no installation needed.  

---

## 💻 Run Locally
Clone the repository and install dependencies:  


```bash
git clone https://github.com/Nikiel54/space-shooter-game.git
cd space-shooter-game

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate   # (Linux/Mac)
venv\Scripts\activate      # (Windows)

# Install pygame-ce and pygbag
pip install pygame-ce pygbag
