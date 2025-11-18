# Picture Reveal Game (Qix-Style) 🎮

A challenging Python arcade game inspired by classics like *Qix* and *Xonix*. Control a fly to slice up the screen and reveal a hidden picture, while avoiding deadly spiders that patrol the darkness!

## 🎯 Game Objective

Reveal **75%** of the hidden picture. You do this by drawing lines to "slice" sections of the screen away from the spiders. If a spider cannot reach an area because you walled it off, that area becomes revealed and safe!

## 🕹️ How to Play

### Controls
- **Arrow Keys**: Move the fly (UP, DOWN, LEFT, RIGHT)
- **ESC**: Quit the game
- **SPACE**: Restart after game over

### Gameplay Mechanics

1. **Safe Zones vs. The Unknown**:
   - **Revealed Area (The Picture)**: This is "Safe Ground". You are safe here.
   - **Screen Borders**: The edges of the screen are always safe.
   - **Covered Area (Dark Gray)**: This is the "Danger Zone" where spiders live.

2. **Drawing Lines**:
   - Move from a safe area into the danger zone to start drawing a line (Stix).
   - To capture an area, you must connect your line back to **any** safe ground (a border or an already revealed section).
   - Once reconnected, the game calculates which side the spiders are on. The side *without* spiders is instantly revealed!

3. **The Spiders**:
   - Spiders bounce around the covered area.
   - **Game Over** if:
     - A spider touches your fly while you are drawing.
     - A spider touches the line you are currently drawing (before you finish it).
     - You stop moving while drawing (the fuse travels up your line).

4. **Win Condition**: Reveal 75% of the picture to win!

## 🚀 Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Setup Steps

1. **Clone or download this repository**

2. **Install dependencies**:
   ```bash
   pip install pygame

3. Add your background image (optional but recommended):

   Place an image file in the assets/ directory.

   Name it either background.jpg or background.png.

   Recommended size: 800x600 pixels.

   The game will automatically scale your image to fit.

   Note: If you don't add an image, the game will use a generated placeholder pattern.

4. Run the game:

   Bash

   python main.py

### ⚙️ Difficulty Settings
   You can adjust the difficulty by editing the DIFFICULTY variable in game.py (line 100) or passing it to the GameState constructor:

   Easy: 1 spider, slower speed

   Medium: 2 spiders, moderate speed (default)

   Hard: 3 spiders, faster speed

### 🛠️ Technical Details
   This game uses a Grid-based Spatial Partitioning approach rather than complex geometric intersection checks.

#### Core Algorithms
   1.Bresenham's Line Algorithm:

   Used to "rasterize" the player's movement path onto the logic grid. This ensures the walls are watertight with no diagonal gaps that spiders could slip through.

   2.Spider-Centric Flood Fill (BFS):

   Instead of calculating the shape the player drew, the game calculates where the spiders are.

   When a line is finished, the game runs a Breadth-First Search starting from the spiders.

   Any pixels on the grid that the spiders cannot reach are strictly defined as "Captured" and are revealed.

   3.Grid Logic:

   The game runs on a downscaled logic grid (Scale 8:1) for high performance.

   Borders and revealed pixels act as "walls" to the spiders.

### 📁 Project Structure
   picture-reveal-game/
   ├── main.py              # Window management, rendering loop, and input handling
   ├── game.py              # Core logic: BFS algo, Player/Spider physics, Grid state
   ├── assets/              # Place your background image here
   │   └── (background.jpg or background.png)
   └── README.md           # This file
### 🎨 Customization Tips
   Change Window Size: Edit WIDTH and HEIGHT in main.py.

   Adjust Grid Precision: Change self.scale in game.py. Lower numbers (e.g., 4) are more precise but use more CPU; higher numbers (e.g., 10) are faster but blockier.

   Player Speed: Modify speed in the Player class in game.py.

### 🎉 Tips for Success
   Don't be greedy: Try to capture small strips first. Drawing long lines across the screen is risky because the spiders have more time to hit your trail.

   Use the borders: The safest way to play is to stick to the edges and bite off small chunks.

   Trap the spiders: Advanced players can try to create a U-shape to trap a spider in a small area, then close it off!

### 📝 License
   This game is free to use and modify for personal and educational purposes.

### 🙏 Credits
   Built with:

   Python 3

   Pygame - Game development library
