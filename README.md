# 🎮 Python Maze Game

An interactive, feature-rich 2D Maze Game built using **Python**, **Pygame**, and **Tkinter**. Featuring modern and colorful UI menus, pathfinding algorithms, an Escape Room mode with keys and breakable walls, dynamic torchlight fog of war, and persistent SQLite score tracking.

---

## 🌟 Key Features

- **🎨 Clean, Colorful UI**:
  - Smooth card-based menus with categorized color accents (Start, High Scores, Settings, Exit).
  - Full mouse support (hover highlights & click) alongside classic keyboard navigation (Arrow keys / Enter / Esc).
  - Seamless single-window transitions (no screen flicker or window teardown).

- **🕹️ Two Game Modes**:
  - **Classic Mode**: Race against the clock to navigate the labyrinth from start to the glowing goal portal.
  - **Escape Mode**: Collect scattered golden keys and smash breakable walls to unlock the path to freedom.

- **🔦 Dynamic Torchlight (Fog of War)**:
  - Toggle fog of war on or off at any time during gameplay by pressing **`T`** or enabling it in Settings.
  - Illuminates a warm radial radius around the player while the rest of the maze remains shrouded in darkness.

- **🤖 Pathfinding & Generation**:
  - Randomized maze generation using Graph-based depth-first search (DFS) with recursive backtracking.
  - Built-in **A\* Search Algorithm** solver for optimal path analysis.

- **🏆 High Score Tracking & Accounts**:
  - User authentication and registration system with password visibility toggle.
  - Local **SQLite** database (`maze_scores.db`) tracking top times, ranks, grid dimensions, and timestamps.
  - Medal badges (🥇 Gold, 🥈 Silver, 🥉 Bronze) for top rankers.

- **⚙️ In-Game Settings**:
  - Configurable maze grid size (10x10 up to 30x30).
  - Adjustable wall thickness and path dimensions.
  - Interactive steppers (`[-]` / `[+]` or Arrow keys).

---

## ⌨️ Controls

| Action | Control |
| :--- | :--- |
| **Move Player** | `W` / `A` / `S` / `D` or Arrow Keys (`↑` `←` `↓` `→`) |
| **Break Wall (Escape Mode)** | Walk into a breakable wall (requires keys) |
| **Toggle Torchlight** | `T` |
| **Pause / Return to Menu** | `ESC` |
| **Select / Confirm** | `ENTER` or Left Mouse Click |
| **Navigate Menus** | Up/Down Arrow keys or Mouse Hover |

---

## 🚀 Getting Started

### Prerequisites

Ensure you have Python 3.8+ installed:
```bash
python --version
```

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/AnuragJha100706/python-maze-game-with-tkinter.git
   cd python-maze-game-with-tkinter
   ```

2. **Install required dependencies:**
   ```bash
   pip install pygame
   ```
   *(Note: `tkinter` and `sqlite3` are part of Python's standard library).*

### Running the Game

- **Start with User Login / Register:**
  ```bash
  python login.py
  ```

- **Or launch directly into the Game Menu:**
  ```bash
  python main.py
  ```

---

## 📂 Project Structure

```text
├── astar.py           # A* pathfinding algorithm implementation
├── character.py       # Player rendering, key popups, and movement logic
├── graph.py           # Graph data structure & maze generation algorithms
├── login.py           # Modern Tkinter login and user registration window
├── main.py            # Main game loop, display management, HUD & torchlight
├── score_db.py        # SQLite database operations for player scores
├── score_tracker.py   # High score record keeper
├── ui_file.py         # Pygame menus (Main Menu, Settings, Leaderboards, Victory)
├── .gitignore         # Git ignore rules for Python bytecode & local databases
└── README.md          # Project documentation
```

---

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
