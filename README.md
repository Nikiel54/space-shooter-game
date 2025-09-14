# 🚀 Space Shooter Game  

An **arcade-style 2D shooter** built with [PyGame](https://www.pygame.org/), compiled to **WebAssembly** using [pygbag](https://pypi.org/project/pygbag/), and deployed automatically to **GitHub Pages** via CI/CD.  

🎮 **[Play the Game Online!](https://nikiel54.github.io/space-shooter-game/)**  

---

## ✨ Features
- 🛸 **Arcade gameplay** – control your spaceship, dodge asteroids, and blast enemies.  
- 🎯 **Dynamic difficulty scaling** – the game gets harder as you progress.  
- 💥 **Collision detection system** – responsive interactions between lasers, asteroids, and player.  
- 🌍 **Runs in the browser** – thanks to WebAssembly, no installation needed.  
- ⚙️ **CI/CD pipeline** – automated builds with GitHub Actions + pygbag.  

---

## 🛠️ Tech Stack
- **Language:** Python (PyGame CE)  
- **Frameworks/Tools:**  
  - [PyGame CE](https://pyga.me/) – for core game engine  
  - [pygbag](https://pypi.org/project/pygbag/) – Python → WebAssembly compiler  
  - [GitHub Actions](https://docs.github.com/en/actions) – CI/CD automation  
  - [GitHub Pages](https://pages.github.com/) – web deployment  

---

## 🎮 How to Play
- Use **Arrow Keys / WASD** to move your spaceship.  
- Press **Spacebar** to shoot lasers.  
- Destroy asteroids and avoid collisions.  
- Survive as long as possible while scoring points!  

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
