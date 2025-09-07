# Bagh Bandi Game

## Overview
Bagh Bandi is a strategic board game implementation with a polished graphical interface built using Python's tkinter and PyGame libraries. The game features two players (Red and Green) on a 5x5 board with diagonal movement capabilities.

## User Interface Components

### 1. Welcome Screen
- Clean, centered panel with dark blue background (#0F0895)
- "BAGH BANDI" title in large white bold font
- Three action buttons:
  - New Game: Starts a fresh game
  - Continue: Loads previous game (if available)
  - Quit: Exits the application

### 2. Main Game Interface
- **Game Board**: 600x600 pixel canvas with dark blue background (#071029)
- **Side Panel**: Right-side panel with purple background (#241BA4) containing:
  - Game title "BAGH BANDI"
  - Current player turn indicator (cyan text)
  - Game status message (light green text)
  - Restart Game button (light green)
  - Quit button (red)
  - AI toggle with on/off icons
  - AI difficulty dropdown (Easy, Medium, Hard, Expert)

### 3. Visual Elements
- **Board**: 5x5 grid with connecting lines and intersection points
- **Pieces**: Custom red and green icons (35x35 pixels)
- **Selection Animation**: Pulsating colored arc around selected piece with rainbow color cycle
- **Valid Moves**: Green circles indicate possible moves
- **Valid Captures**: Red circles indicate capture opportunities

### 4. Game Over Screen
- Centered overlay panel with blue background (#081996)
- "Game Over" message in large red text
- Winner announcement
- Play Again and Quit buttons

## Key Features

### 1. Game Mechanics
- Traditional Bagh Bandi rules implementation
- Piece movement in all 8 directions (orthogonal and diagonal)
- Capture mechanics by jumping over opponent pieces
- Win conditions:
  - Red wins by eliminating all Green pieces
  - Green wins by trapping all Red pieces (no valid moves)

### 2. AI Opponent
- Configurable difficulty levels (Easy, Medium, Hard, Expert)
- Minimax algorithm with alpha-beta pruning
- Strategic evaluation considering:
  - Material count (piece advantage)
  - Mobility (available moves and captures)
  - Center control (board positioning)
- Performance optimization through memoization

### 3. Audio Features
- Custom sound effects for captures (red_cut.mp3, green_cut.mp3)
- PyGame-based audio system

### 4. Persistence
- Automatic saving of game state and window geometry
- Config file storage in user directory (~/.BaghBandiGame/)
- Ability to continue interrupted games

### 5. Visual Effects
- Animated piece selection with rotating rainbow arc
- Smooth transitions between game states
- Themed color scheme throughout the application

### 6. Customization Options
- Toggle AI opponent on/off
- Four difficulty levels for AI
- Responsive window that remembers size and position

### 7. Technical Implementation
- Resource path handling for both development and packaged versions
- Proper application ID setting for Windows platform
- Exception handling for missing resources
- Multi-threading for AI computation to prevent UI freezing

The game offers a complete implementation of Bagh Bandi with an attractive interface, intelligent AI opponent, and polished user experience suitable for both new and experienced players.

## Demo images
<img width="1123" height="845" alt="Screenshot 2025-09-07 193826" src="https://github.com/user-attachments/assets/963e936f-62a5-4e5a-8b53-40b10edcf6c2" />

<img width="1127" height="842" alt="Screenshot 2025-09-07 193844" src="https://github.com/user-attachments/assets/6a1e9e51-8ef0-4967-a563-a582920f47d2" />
<img width="1130" height="853" alt="Screenshot 2025-09-07 193933" src="https://github.com/user-attachments/assets/d523115d-bcc4-4a18-be5a-759d4e06775a" />
