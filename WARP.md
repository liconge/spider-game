# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

A Python/Pygame arcade game where players control a fly to reveal a hidden picture by drawing rectangles while avoiding deadly spiders and their trailing webs. The game uses flood-fill algorithms for area detection and CCW (Counter-Clockwise) algorithms for collision detection.

## Development Commands

### Running the Game
```bash
python main.py
```

### Installing Dependencies
```bash
pip install -r requirements.txt
```

### Environment Setup
If using a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
pip install -r requirements.txt
```

## Architecture

### Code Organization

The codebase follows a **Model-View separation pattern** with two main modules:

**`game.py`** - Core game logic (Model)
- `Player` class: Manages fly position, movement constraints (horizontal/vertical only), and path tracking for rectangle detection
- `Spider` class: Enemy AI with random directional movement, edge-bouncing behavior, and trailing deque-based line tracking
- `GameState` class: Central orchestrator that manages collision detection, area revelation via flood-fill, win condition checking, and overall game state

**`main.py`** - Game loop and rendering (View)
- `GameRenderer` class: Handles all pygame rendering including background loading, mask-based reveal effects, and UI overlays
- Main game loop: Processes input, updates game state, and manages game over/restart flow

### Key Algorithms

**Line Segment Intersection** (`_segments_intersect` in GameState)
- Uses CCW (Counter-Clockwise) test to detect when player's path crosses spider trails
- Includes bounding box optimization for performance

**Flood Fill for Area Detection** (`_flood_fill_outside` in GameState)
- Inverse flood fill approach: fills exterior first, then interior = enclosed area
- Only triggers when player path has 10+ points and enclosed area exceeds 100 pixels
- Revealed areas tracked as a set of (x, y) coordinates

**Difficulty Scaling** (GameState initialization)
- Easy: 1 spider @ 1.5 speed
- Medium: 2 spiders @ 2.0 speed (default)
- Hard: 3 spiders @ 2.5 speed

### Configuration Points

**Game Settings** (main.py, line 192-195):
- `WIDTH, HEIGHT`: Window dimensions (default: 800x600)
- `FPS`: Frame rate (default: 60)
- `DIFFICULTY`: "easy", "medium", or "hard"

**Player Speed** (game.py, line 107):
- `Player(10, 10, speed=4)` - Controls fly movement speed

**Win Condition** (game.py, line 241):
- `reveal_percentage >= 0.75` - 75% of picture must be revealed to win

**Background Image** (main.py, line 46-49):
- Looks for `assets/background.jpg` or `assets/background.png`
- Falls back to colorful tile pattern if no image found

### Movement and Collision System

**Movement Constraints**:
- Player can only move horizontally OR vertically (no diagonal), enforced in `Player.move()`
- Position clamped to screen boundaries

**Collision Detection**:
- Player vs Spider: Euclidean distance check with 15-pixel collision radius
- Player Path vs Spider Trail: Segment-to-segment intersection tests using CCW algorithm

**Path Tracking**:
- Player's `current_path` accumulates positions until rectangle is completed
- Spider's `trail` uses fixed-length deque (60 positions max) for memory efficiency

### Rendering Details

**Reveal Mechanism**:
- Creates a mask surface filled with dark gray
- Sets revealed pixel positions to transparent
- Blits mask over background with `BLEND_MULT` for selective reveal effect

**Spider Visual**:
- Red body with 8 radiating legs drawn at 45° intervals
- Trail rendered as connected line segments from deque

## Testing

No automated tests exist. To verify changes manually:
1. Run the game and test basic movement with arrow keys
2. Verify spider collision triggers game over
3. Test rectangle completion and area reveal
4. Confirm win condition at 75% reveal
