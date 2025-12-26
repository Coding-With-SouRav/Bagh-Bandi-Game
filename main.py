import colorsys
import ctypes
import pygame
import sys
import json
import os
import math
import random
import copy
import configparser

if sys.platform == "win32":
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("com.example.BaghBandiGame")
    
# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 900
BOARD_SIZE = 740
BOARD_OFFSET_X = 80
BOARD_OFFSET_Y = 120
GRID_SIZE = 5
CELL_SIZE = BOARD_SIZE // (GRID_SIZE - 1)
# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
MAGENTA = (255, 0, 255)
BLUE = (0, 0, 255)
LIGHT_BLUE = (173, 216, 230)
DARK_GREEN = (0, 100, 0)
YELLOW = (255, 255, 0)
BUTTON_GREEN = (31, 255, 1)
BUTTON_BLUE = (0, 0, 255)
BUTTON_ACTIVE_GREEN = (174, 244, 160)
BUTTON_ACTIVE_BLUE = (150, 200, 255)

def resource_path(relative_path):

    try:
        base_path = sys._MEIPASS

    except Exception:
        base_path = os.path.abspath(".")
    full_path = os.path.join(base_path, relative_path)

    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Resource not found: {full_path}")
    return full_path

class RGBHueRing:
    def __init__(self, radius=22, thickness=4, segments=120, speed=4):
        self.radius = radius
        self.thickness = thickness
        self.segments = segments
        self.speed = speed
        self.hue_offset = 0.0

    def update(self):
        self.hue_offset = (self.hue_offset + self.speed / 360) % 1.0

    def draw(self, surface, center):
        cx, cy = center
        for i in range(self.segments):
            angle = 2 * math.pi * i / self.segments
            hue = (i / self.segments + self.hue_offset) % 1.0

            r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
            color = (int(r * 255), int(g * 255), int(b * 255))

            x = cx + math.cos(angle) * self.radius
            y = cy + math.sin(angle) * self.radius

            pygame.draw.circle(surface, color, (int(x), int(y)), self.thickness)

class Button:
    def __init__(self, x, y, width, height, text, color, active_color, text_color=BLACK, font_size=20):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.active_color = active_color
        self.text_color = text_color
        self.font = pygame.font.SysFont("Arial", font_size)
        self.is_active = False
        
    def draw(self, screen):
        color = self.active_color if self.is_active else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=5)
        
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.is_active = self.rect.collidepoint(pos)
        return self.is_active
        
    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

class Dropdown:
    def __init__(
        self, x, y, width, height, options, default_index=0,
        bg_color=WHITE,
        fg_color=BLACK,
        hover_color=LIGHT_BLUE,
        border_color=BLACK
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.options = options
        self.selected_index = default_index
        self.is_open = False

        self.bg_color = bg_color
        self.fg_color = fg_color
        self.hover_color = hover_color
        self.border_color = border_color

        self.font = pygame.font.SysFont("Arial", 16)
        self.option_rects = []

        
    def draw(self, screen):
        # Main box
        pygame.draw.rect(screen, self.bg_color, self.rect, border_radius=6)
        pygame.draw.rect(screen, self.border_color, self.rect, 2, border_radius=6)

        # Selected text
        selected_text = self.font.render(
            self.options[self.selected_index], True, self.fg_color
        )
        screen.blit(selected_text, (self.rect.x + 8, self.rect.y + 7))

        # Dropdown arrow
        arrow_color = self.fg_color
        points = [
            (self.rect.right - 18, self.rect.centery - 4),
            (self.rect.right - 8, self.rect.centery - 4),
            (self.rect.right - 13, self.rect.centery + 4)
        ]
        pygame.draw.polygon(screen, arrow_color, points)

        # Options
        if self.is_open:
            for i, rect in enumerate(self.option_rects):
                color = self.hover_color if rect.collidepoint(pygame.mouse.get_pos()) else self.bg_color
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, self.border_color, rect, 1)

                option_text = self.font.render(self.options[i], True, self.fg_color)
                screen.blit(option_text, (rect.x + 8, rect.y + 7))
     
    def update_options(self):
        self.option_rects = []
        for i in range(len(self.options)):
            rect = pygame.Rect(
                self.rect.x,
                self.rect.y + self.rect.height * (i + 1),
                self.rect.width,
                self.rect.height
            )
            self.option_rects.append(rect)
            
    def handle_event(self, event):
        pos = pygame.mouse.get_pos()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(pos):
                self.is_open = not self.is_open
                if self.is_open:
                    self.update_options()
                return True
            elif self.is_open:
                for i, rect in enumerate(self.option_rects):
                    if rect.collidepoint(pos):
                        self.selected_index = i
                        self.is_open = False
                        return True
                self.is_open = False
        return False
    
    def get_selected(self):
        return self.options[self.selected_index]

class ImageButton:
    def __init__(self, x, y, image_path, scale=None):
        self.image = pygame.image.load(image_path).convert_alpha()
        if scale:
            self.image = pygame.transform.smoothscale(self.image, scale)
        self.rect = self.image.get_rect(topleft=(x, y))

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def is_clicked(self, pos, event):
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(pos)
        )

class OutlinedLabel:
    def __init__(self, text, font, pos,
                 text_color=(255, 0, 255),   # magenta
                 border_color=(0, 0, 0),     # black
                 border_thickness=1):
        self.text = text
        self.font = font
        self.pos = pos
        self.text_color = text_color
        self.border_color = border_color
        self.border_thickness = border_thickness

    def draw(self, surface):
        x, y = self.pos

        # Draw border (outline)
        for dx in range(-self.border_thickness, self.border_thickness + 1):
            for dy in range(-self.border_thickness, self.border_thickness + 1):
                if dx != 0 or dy != 0:
                    border_surf = self.font.render(self.text, True, self.border_color)
                    surface.blit(border_surf, (x + dx, y + dy))

        # Draw main text
        text_surf = self.font.render(self.text, True, self.text_color)
        surface.blit(text_surf, (x, y))

class BaghChalPygame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Bagh Bandi Game - By SouRav")
        
        icon = pygame.image.load(resource_path("assets/images/icon.png"))
        pygame.display.set_icon(icon)

        # Game state
        self.board = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.selected = None
        self.legal_moves = []
        self.current_player = 'R'
        self.extra_turn_after_capture = False
        self.game_message = None
        self.game_message_active = False
        
        # AI variables
        self.ai_player = None
        self.ai_difficulty = "Easy"
        self.ai_thinking = False
        
        # Game modes
        self.game_mode = "splash"  # splash, mode_select, playing
        self.mode = "Play with Friend"
        self.ai_color = "Green"
        self.show_mode_selection = False  
        
        # UI elements
        self.buttons = {}
        self.dropdowns = {}
        self.create_ui_elements()
        
        # Data directory
        self.data_dir = os.path.join(os.path.expanduser("~"), ".BaghBandiGame")
        os.makedirs(self.data_dir, exist_ok=True)
        self.SAVE_FILE = os.path.join(self.data_dir, "ludo_save.json")
        self.config_file = os.path.join(self.data_dir, "config.ini")
        
        # Initialize game
        self.load_window_geometry()
        self.init_board()
        
        # Load images (placeholder - you'll need to add your actual images)
        self.load_images()
        
        # Check for saved game
        # self.saved_game_exists = os.path.exists(self.SAVE_FILE)
        self.saved_game_exists = self.is_saved_game_playable()
        
        self.selection_ring = RGBHueRing(radius=22, thickness=3, segments=140, speed=6)
        pygame.mixer.init()
        self.load_sounds()
    
    def is_saved_game_playable(self):
        """Return True only if saved game exists AND both players still have pieces"""
        if not os.path.exists(self.SAVE_FILE):
            return False

        try:
            with open(self.SAVE_FILE, "r") as f:
                data = json.load(f)

            board = data.get("board", [])

            red_exists = any('R' in row for row in board)
            green_exists = any('G' in row for row in board)

            return red_exists and green_exists

        except Exception:
            return False

    
    def load_sounds(self):
        try:
            self.sound_friend_capture = pygame.mixer.Sound(
                resource_path("assets/sounds/player_capture.mp3")
            )
            self.sound_ai_capture = pygame.mixer.Sound(
                resource_path("assets/sounds/ai_capture.mp3")
            )
            self.sound_player_capture = pygame.mixer.Sound(
                resource_path("assets/sounds/player_capture.mp3")
            )
        except Exception as e:
            print("Sound load failed:", e)
            self.sound_friend_capture = None
            self.sound_ai_capture = None
            self.sound_player_capture = None

    def load_images(self):
        # Load background image
        try:
            bg_image = pygame.image.load(resource_path("assets/images/back_ground.png"))
            self.bg_image = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except:
            # Create gradient background if image not found
            self.bg_image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.bg_image.fill((240, 240, 255))
            
        try:
            text_image = pygame.image.load(resource_path("assets/images/text.png"))
            self.text_image = pygame.transform.scale(text_image, (500, 130))
        except:
            # Create text surface if image not found
            self.text_image = pygame.Surface((500, 130))
            self.text_image.fill((255, 255, 255))
            font = pygame.font.SysFont("Arial", 70, bold=True)
            text = font.render("BAGH BANDI", True, RED)
            self.text_image.blit(text, (50, 30))
        try:
            self.magenta_coin_img = pygame.image.load(
                resource_path("assets/images/red.png")
            ).convert_alpha()
            self.green_coin_img = pygame.image.load(
                resource_path("assets/images/green.png")
            ).convert_alpha()

            # Scale to match board size
            self.magenta_coin_img = pygame.transform.smoothscale(
                self.magenta_coin_img, (36, 36)
            )
            self.green_coin_img = pygame.transform.smoothscale(
                self.green_coin_img, (36, 36)
            )
        except Exception as e:
            print("Coin image load failed:", e)
            self.magenta_coin_img = None
            self.green_coin_img = None

    
    def create_ui_elements(self):
        # Splash screen buttons
        self.buttons["continue"] = Button(
            SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 40, 
            200, 50, "Continue Game", 
            BUTTON_BLUE, BUTTON_ACTIVE_BLUE, WHITE, 20
        )

        self.buttons["new_game"] = Button(
            SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 20, 
            200, 50, "New Game", 
            BUTTON_GREEN, BUTTON_ACTIVE_GREEN, BLACK, 20
        )

        # ---- VERTICAL MODE SELECTION UI ----
        base_x_label = 220
        base_x_dropdown = 380
        start_y = 220
        gap = 100

        self.dropdowns["mode"] = Dropdown(
            380, 240, 200, 32,
            ["Play with Friend", "Play with AI"],
            bg_color=(30, 30, 30),
            fg_color=(0, 255, 180),
            hover_color=(50, 50, 50),
            border_color=(0, 255, 180)
        )

        self.dropdowns["ai_color"] = Dropdown(
            380, 340, 200, 32,
            ["Red", "Green"], 
            bg_color=(30, 30, 30),
            fg_color=(0, 255, 180),
            hover_color=(50, 50, 50),
            border_color=(0, 255, 180)
        )

        self.dropdowns["difficulty"] = Dropdown(
            380, 440, 200, 32,
            ["Easy", "Medium", "Hard"],
            bg_color=(30, 30, 30),
            fg_color=(0, 255, 180),
            hover_color=(50, 50, 50),
            border_color=(0, 255, 180)
        )

        # Start button (below dropdowns)
        self.buttons["start"] = Button(
            base_x_dropdown, start_y + gap * 3.5 + 10,
            200, 42, "Start Game",
            GREEN, DARK_GREEN, BLACK, 18
        )
        
        self.buttons["back"] = Button(
            base_x_dropdown,
            start_y + gap * 4.2 + 10,   # slightly below Start
            200, 42, "Back",
            BUTTON_BLUE, BUTTON_ACTIVE_BLUE, WHITE, 18
        )

        self.buttons["home"] = ImageButton(
            BOARD_OFFSET_X + BOARD_SIZE - 50,   # top-right of board
            BOARD_OFFSET_Y - 100,                # above board
            resource_path(r"assets/images/home.png"),
            scale=(30, 30)
        )
        
        self.buttons["replay"] = Button(
            SCREEN_WIDTH // 2 - 140,
            SCREEN_HEIGHT // 4 + 120,
            120, 45,
            "Replay",
            BUTTON_GREEN,
            BUTTON_ACTIVE_GREEN,
            BLACK,
            18
        )

        self.buttons["game_home"] = Button(
            SCREEN_WIDTH // 2 + 20,
            SCREEN_HEIGHT // 4 + 120,
            120, 45,
            "Home",
            BUTTON_BLUE,
            BUTTON_ACTIVE_BLUE,
            WHITE,
            18
        )

    def init_board(self):
        idx = 0
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if idx < 10:
                    self.board[r][c] = 'R'
                elif idx >= 15:
                    self.board[r][c] = 'G'
                else:
                    self.board[r][c] = None
                idx += 1
    
    def cell_to_coord(self, r, c):
        x = BOARD_OFFSET_X + c * CELL_SIZE
        y = BOARD_OFFSET_Y + r * CELL_SIZE
        return x, y
    
    def nearest_cell(self, x, y):
        best = None
        best_d = float('inf')
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                cx, cy = self.cell_to_coord(r, c)
                d = math.hypot(cx - x, cy - y)
                if d < best_d:
                    best_d = d
                    best = (r, c)
        if best_d <= 36:  # 2.2 * radius
            return best
        return None
    
    def opponent(self, player):
        return 'G' if player == 'R' else 'R'
    
    def is_inside(self, r, c):
        return 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE
    
    def valid_directions(self, r, c):
        dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        if (r + c) % 2 == 0:
            dirs += [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        return dirs
    
    def can_move_simple(self, sr, sc, dr, dc):
        if not self.is_inside(dr, dc) or self.board[dr][dc] is not None:
            return False
        for d in self.valid_directions(sr, sc):
            if sr + d[0] == dr and sc + d[1] == dc:
                return True
        return False
    
    def can_capture(self, sr, sc, dr, dc):
        if not self.is_inside(dr, dc) or self.board[dr][dc] is not None:
            return False
        for d in self.valid_directions(sr, sc):
            mid_r, mid_c = sr + d[0], sc + d[1]
            end_r, end_c = sr + 2 * d[0], sc + 2 * d[1]
            if (end_r, end_c) == (dr, dc):
                if self.is_inside(mid_r, mid_c) and self.board[mid_r][mid_c] == self.opponent(self.board[sr][sc]):
                    return True
        return False
    
    def find_legal_moves(self, r, c):
        moves = []
        for dr in range(-2, 3):
            for dc in range(-2, 3):
                nr, nc = r + dr, c + dc
                if not self.is_inside(nr, nc) or self.board[nr][nc] is not None:
                    continue
                if max(abs(dr), abs(dc)) == 1 and self.can_move_simple(r, c, nr, nc):
                    moves.append((nr, nc))
                if max(abs(dr), abs(dc)) == 2 and self.can_capture(r, c, nr, nc):
                    moves.append((nr, nc))
        return moves
    
    def find_all_moves_for_player(self, player, board_state):
        moves = []
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if board_state[r][c] == player:
                    for d in self.valid_directions(r, c):
                        nr, nc = r + d[0], c + d[1]
                        if self.is_inside(nr, nc) and board_state[nr][nc] is None:
                            moves.append((r, c, nr, nc, 'move'))
                    for d in self.valid_directions(r, c):
                        nr, nc = r + 2 * d[0], c + 2 * d[1]
                        mr, mc = r + d[0], c + d[1]
                        if self.is_inside(nr, nc) and board_state[nr][nc] is None:
                            if self.is_inside(mr, mc) and board_state[mr][mc] == self.opponent(player):
                                moves.append((r, c, nr, nc, 'capture'))
        return moves
    
    def any_legal_moves_for(self, player):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if self.board[r][c] == player:
                    if self.find_legal_moves(r, c):
                        return True
        return False
    
    def count_pieces(self, player, board_state=None):
        if board_state is None:
            board_state = self.board
        count = 0
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if board_state[r][c] == player:
                    count += 1
        return count
    
    def make_move(self, sr, sc, dr, dc):
        was_capture = False

        if abs(dr - sr) <= 1 and abs(dc - sc) <= 1:
            self.board[dr][dc] = self.board[sr][sc]
            self.board[sr][sc] = None
            self.selected = None
            self.legal_moves = []
            self.current_player = self.opponent(self.current_player)
            self.extra_turn_after_capture = False
        else:
            mid_r = (sr + dr) // 2
            mid_c = (sc + dc) // 2

            captured_piece = self.board[mid_r][mid_c]   # 👈 important
            self.board[mid_r][mid_c] = None
            self.board[dr][dc] = self.board[sr][sc]
            self.board[sr][sc] = None
            was_capture = True

            # 🔊 SOUND LOGIC
            if self.mode == "Play with Friend":
                if self.sound_friend_capture:
                    self.sound_friend_capture.play()

            elif self.mode == "Play with AI":
                # Player captured AI
                if self.current_player != self.ai_player:
                    if self.sound_player_capture:
                        self.sound_player_capture.play()

            self.selected = (dr, dc)
            self.legal_moves = self.find_legal_moves(dr, dc)
            self.extra_turn_after_capture = True

            if not self.legal_moves:
                self.selected = None
                self.extra_turn_after_capture = False
                self.current_player = self.opponent(self.current_player)

        self.post_move_updates()

        if (self.mode == "Play with AI" and 
            self.current_player == self.ai_player and 
            not self.extra_turn_after_capture):
            pygame.time.set_timer(pygame.USEREVENT, 500)  # Trigger AI move after delay
    
    def post_move_updates(self):
        mag_count = self.count_pieces('R')
        green_count = self.count_pieces('G')
        
        if mag_count == 0:
            self.show_message("Green wins!")
            return
        
        if green_count == 0:
            self.show_message("Red wins!")
            return
        
        if not self.any_legal_moves_for(self.current_player):
            if self.extra_turn_after_capture:
                self.current_player = self.opponent(self.current_player)
                self.extra_turn_after_capture = False
                if not self.any_legal_moves_for(self.current_player):
                    winner = "Green" if self.current_player == 'R' else "Red"
                    self.show_message(f"{winner} wins!")
                    return
    
    def draw_game_message(self):
        if not self.game_message_active:
            return

        font = pygame.font.SysFont("Arial", 90, bold=True)
        text = font.render(self.game_message, True, RED)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))

        self.screen.blit(overlay, (0, 0))
        self.screen.blit(text, text_rect)

        # ---- DRAW GAME OVER BUTTONS ----
        mouse_pos = pygame.mouse.get_pos()

        self.buttons["replay"].check_hover(mouse_pos)
        self.buttons["game_home"].check_hover(mouse_pos)

        self.buttons["replay"].draw(self.screen)
        self.buttons["game_home"].draw(self.screen)



    def show_message(self, message):
        self.game_message = message
        self.game_message_active = True
    
    def evaluate_board(self, board_state, maximizing_player):
        if maximizing_player == 'R':
            mag_pieces = self.count_pieces('R', board_state)
            green_pieces = self.count_pieces('G', board_state)
        else:
            mag_pieces = self.count_pieces('G', board_state)
            green_pieces = self.count_pieces('R', board_state)
        
        score = (mag_pieces - green_pieces) * 1000
        
        mag_captures = 0
        green_captures = 0
        
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if board_state[r][c] == 'R':
                    for d in self.valid_directions(r, c):
                        ar, ac = r + d[0], c + d[1]
                        jr, jc = r + 2 * d[0], c + 2 * d[1]
                        if self.is_inside(ar, ac) and self.is_inside(jr, jc):
                            if board_state[ar][ac] == 'G' and board_state[jr][jc] is None:
                                green_captures += 1
                elif board_state[r][c] == 'G':
                    for d in self.valid_directions(r, c):
                        ar, ac = r + d[0], c + d[1]
                        jr, jc = r + 2 * d[0], c + 2 * d[1]
                        if self.is_inside(ar, ac) and self.is_inside(jr, jc):
                            if board_state[ar][ac] == 'R' and board_state[jr][jc] is None:
                                mag_captures += 1
        
        score += (mag_captures - green_captures) * 50
        
        center_positions = [(2, 2), (1, 2), (2, 1), (2, 3), (3, 2)]
        for r, c in center_positions:
            if board_state[r][c] == 'R':
                score += 10
            elif board_state[r][c] == 'G':
                score -= 10
        
        mag_moves = len(self.find_all_moves_for_player('R', board_state))
        green_moves = len(self.find_all_moves_for_player('G', board_state))
        score += (mag_moves - green_moves) * 5
        
        return score if maximizing_player == 'R' else -score
    
    def minimax(self, board_state, depth, alpha, beta, maximizing_player, max_player):
        mag_count = self.count_pieces('R', board_state)
        green_count = self.count_pieces('G', board_state)
        
        if mag_count == 0:
            return -10000 + depth if max_player == 'R' else 10000 - depth
        if green_count == 0:
            return 10000 - depth if max_player == 'R' else -10000 + depth
        
        if depth == 0:
            return self.evaluate_board(board_state, max_player)
        
        current_player_turn = max_player if maximizing_player else self.opponent(max_player)
        moves = self.find_all_moves_for_player(current_player_turn, board_state)
        
        if not moves:
            return -5000 if maximizing_player else 5000
        
        if maximizing_player:
            max_eval = -float('inf')
            for move in moves:
                new_board = copy.deepcopy(board_state)
                sr, sc, dr, dc, move_type = move
                
                if move_type == 'move':
                    new_board[dr][dc] = new_board[sr][sc]
                    new_board[sr][sc] = None
                else:
                    mid_r = (sr + dr) // 2
                    mid_c = (sc + dc) // 2
                    new_board[dr][dc] = new_board[sr][sc]
                    new_board[sr][sc] = None
                    new_board[mid_r][mid_c] = None
                
                eval_score = self.minimax(new_board, depth - 1, alpha, beta, False, max_player)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in moves:
                new_board = copy.deepcopy(board_state)
                sr, sc, dr, dc, move_type = move
                
                if move_type == 'move':
                    new_board[dr][dc] = new_board[sr][sc]
                    new_board[sr][sc] = None
                else:
                    mid_r = (sr + dr) // 2
                    mid_c = (sc + dc) // 2
                    new_board[dr][dc] = new_board[sr][sc]
                    new_board[sr][sc] = None
                    new_board[mid_r][mid_c] = None
                
                eval_score = self.minimax(new_board, depth - 1, alpha, beta, True, max_player)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval
    
    def get_best_move_ai(self, board_state, ai_color, difficulty):
        moves = self.find_all_moves_for_player(ai_color, board_state)
        if not moves:
            return None
        
        if difficulty == "Easy":
            capture_moves = [m for m in moves if m[4] == 'capture']
            if capture_moves:
                return random.choice(capture_moves)
            return random.choice(moves)
        
        elif difficulty == "Medium":
            depth = 2
            best_move = None
            best_value = -float('inf')
            
            for move in moves:
                new_board = copy.deepcopy(board_state)
                sr, sc, dr, dc, move_type = move
                
                if move_type == 'move':
                    new_board[dr][dc] = new_board[sr][sc]
                    new_board[sr][sc] = None
                else:
                    mid_r = (sr + dr) // 2
                    mid_c = (sc + dc) // 2
                    new_board[dr][dc] = new_board[sr][sc]
                    new_board[sr][sc] = None
                    new_board[mid_r][mid_c] = None
                
                move_value = self.minimax(new_board, depth - 1, -float('inf'), float('inf'), False, ai_color)
                
                if move_value > best_value:
                    best_value = move_value
                    best_move = move
            
            return best_move
        
        else:  # Hard
            depth = 4
            best_move = None
            best_value = -float('inf')
            
            for move in moves:
                if move[4] == 'capture':
                    new_board = copy.deepcopy(board_state)
                    sr, sc, dr, dc, move_type = move
                    mid_r = (sr + dr) // 2
                    mid_c = (sc + dc) // 2
                    new_board[dr][dc] = new_board[sr][sc]
                    new_board[sr][sc] = None
                    new_board[mid_r][mid_c] = None
                    
                    opponent_pieces = self.count_pieces(self.opponent(ai_color), new_board)
                    if opponent_pieces == 0:
                        return move
            
            for current_depth in range(1, depth + 1):
                current_best_move = None
                current_best_value = -float('inf')
                
                for move in moves:
                    new_board = copy.deepcopy(board_state)
                    sr, sc, dr, dc, move_type = move
                    
                    if move_type == 'move':
                        new_board[dr][dc] = new_board[sr][sc]
                        new_board[sr][sc] = None
                    else:
                        mid_r = (sr + dr) // 2
                        mid_c = (sc + dc) // 2
                        new_board[dr][dc] = new_board[sr][sc]
                        new_board[sr][sc] = None
                        new_board[mid_r][mid_c] = None
                    
                    move_value = self.minimax(new_board, current_depth - 1, -float('inf'), float('inf'), False, ai_color)
                    
                    if move_value > current_best_value:
                        current_best_value = move_value
                        current_best_move = move
                
                best_move = current_best_move
                best_value = current_best_value
            
            if best_move is None and moves:
                capture_moves = [m for m in moves if m[4] == 'capture']
                if capture_moves:
                    best_move = random.choice(capture_moves)
                else:
                    best_move = random.choice(moves)
            
            return best_move
    
    def ai_move(self):
        if self.ai_thinking or self.current_player != self.ai_player:
            return
        
        self.ai_thinking = True
        
        best_move = self.get_best_move_ai(self.board, self.ai_player, self.ai_difficulty)
        
        if best_move:
            sr, sc, dr, dc, move_type = best_move
            was_capture = (move_type == 'capture')
            
            if move_type == 'move':
                self.board[dr][dc] = self.board[sr][sc]
                self.board[sr][sc] = None
            else:
                mid_r = (sr + dr) // 2
                mid_c = (sc + dc) // 2

                self.board[mid_r][mid_c] = None
                self.board[dr][dc] = self.board[sr][sc]
                self.board[sr][sc] = None

                # 🔊 AI captured player
                if self.sound_ai_capture:
                    self.sound_ai_capture.play()

            
            if was_capture:
                self.extra_turn_after_capture = True
            else:
                self.current_player = self.opponent(self.ai_player)
                self.extra_turn_after_capture = False
            
            self.post_move_updates()
            
            if self.extra_turn_after_capture and self.current_player == self.ai_player:
                pygame.time.set_timer(pygame.USEREVENT, 500)
            elif self.mode == "Play with AI" and self.current_player == self.ai_player:
                pygame.time.set_timer(pygame.USEREVENT, 500)
        
        self.ai_thinking = False
    
    def draw_board(self):
       # Draw grid lines
        for i in range(GRID_SIZE):
            # Vertical lines
            x = BOARD_OFFSET_X + i * CELL_SIZE
            pygame.draw.line(self.screen, BLACK, 
                           (x, BOARD_OFFSET_Y), 
                           (x, BOARD_OFFSET_Y + BOARD_SIZE), 3)
            # Horizontal lines
            y = BOARD_OFFSET_Y + i * CELL_SIZE
            pygame.draw.line(self.screen, BLACK, 
                           (BOARD_OFFSET_X, y), 
                           (BOARD_OFFSET_X + BOARD_SIZE, y), 3)
        
        # Draw diagonal lines
        pygame.draw.line(self.screen, BLACK,
                        (BOARD_OFFSET_X, BOARD_OFFSET_Y),
                        (BOARD_OFFSET_X + BOARD_SIZE, BOARD_OFFSET_Y + BOARD_SIZE), 3)
        pygame.draw.line(self.screen, BLACK,
                        (BOARD_OFFSET_X, BOARD_OFFSET_Y + BOARD_SIZE),
                        (BOARD_OFFSET_X + BOARD_SIZE, BOARD_OFFSET_Y), 3)
        
        # Draw center lines
        center_x = BOARD_OFFSET_X + 2 * CELL_SIZE
        center_y = BOARD_OFFSET_Y + 2 * CELL_SIZE
        points = [
            [(BOARD_OFFSET_X, center_y), (center_x, BOARD_OFFSET_Y)],
            [(center_x, BOARD_OFFSET_Y), (BOARD_OFFSET_X + BOARD_SIZE, center_y)],
            [(BOARD_OFFSET_X + BOARD_SIZE, center_y), (center_x, BOARD_OFFSET_Y + BOARD_SIZE)],
            [(center_x, BOARD_OFFSET_Y + BOARD_SIZE), (BOARD_OFFSET_X, center_y)]
        ]
        for p1, p2 in points:
            pygame.draw.line(self.screen, BLACK, p1, p2, 3)
        
        # Draw grid points
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                x, y = self.cell_to_coord(r, c)
                pygame.draw.circle(self.screen, BLACK, (int(x), int(y)), 4)
        
        # Draw legal moves
        for mr, mc in self.legal_moves:
            x, y = self.cell_to_coord(mr, mc)
            pygame.draw.circle(self.screen, BLUE, (int(x), int(y)), 10, 2)
        
        # Draw pieces
        # Draw pieces (IMAGE BASED)
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                p = self.board[r][c]
                if p is not None:
                    x, y = self.cell_to_coord(r, c)

                    if p == 'R' and self.magenta_coin_img:
                        rect = self.magenta_coin_img.get_rect(center=(int(x), int(y)))
                        self.screen.blit(self.magenta_coin_img, rect)

                    elif p == 'G' and self.green_coin_img:
                        rect = self.green_coin_img.get_rect(center=(int(x), int(y)))
                        self.screen.blit(self.green_coin_img, rect)

        # Draw selection highlight
        if self.selected:
            sr, sc = self.selected
            x, y = self.cell_to_coord(sr, sc)
            # pygame.draw.circle(self.screen, RED, (int(x), int(y)), 22, 4)
            if self.selected:
                sr, sc = self.selected
                x, y = self.cell_to_coord(sr, sc)
                self.selection_ring.draw(self.screen, (int(x), int(y)))
    
    def home_to_splash(self):
        self.save_game_state()
        self.game_mode = "splash"
        self.show_mode_selection = False
        self.selected = None
        self.legal_moves = []
        # self.current_player = 'R'
        # self.extra_turn_after_capture = False
        self.ai_thinking = False
        # self.init_board()
        
    def draw_splash_screen(self):
        self.screen.blit(self.bg_image, (0, 0))
        self.screen.blit(self.text_image, (200, 0))
        
        if not self.show_mode_selection:
            # Draw splash buttons
            mouse_pos = pygame.mouse.get_pos()
            self.buttons["continue"].check_hover(mouse_pos)
            self.buttons["new_game"].check_hover(mouse_pos)
            
            self.buttons["continue"].draw(self.screen)
            self.buttons["new_game"].draw(self.screen)
            
            # Show continue button only if saved game exists
            if not self.saved_game_exists:
                overlay = pygame.Surface((200, 50), pygame.SRCALPHA)
                overlay.fill((128, 128, 128, 128))
                self.screen.blit(overlay, self.buttons["continue"].rect.topleft)
        else:
            # Draw mode selection UI
            self.draw_mode_selection_on_splash()
    
    def draw_mode_selection_on_splash(self):
        font = pygame.font.SysFont("Arial", 40, bold=True)

        start_y = 220
        gap = 100
        label_x = 220

        # ---- MODE LABEL (always shown) ----
        mode_label = OutlinedLabel(
            text="Mode:",
            font=font,
            pos=(label_x, start_y + 6),
            text_color=(255, 0, 255),
            border_color=(0, 0, 0),
            border_thickness=3
        )
        mode_label.draw(self.screen)

        # ---- MODE DROPDOWN ----
        self.dropdowns["mode"].draw(self.screen)

        # ---- AI OPTIONS (only if Play with AI) ----
        if self.dropdowns["mode"].get_selected() == "Play with AI":

            ai_color_label = OutlinedLabel(
                text="AI Color:",
                font=font,
                pos=(label_x, start_y + gap + 6),
                text_color=(255, 0, 255),
                border_color=(0, 0, 0),
                border_thickness=3
            )
            ai_color_label.draw(self.screen)

            difficulty_label = OutlinedLabel(
                text="Difficulty:",
                font=font,
                pos=(label_x, start_y + gap * 2 + 6),
                text_color=(255, 0, 255),
                border_color=(0, 0, 0),
                border_thickness=3
            )
            difficulty_label.draw(self.screen)

            self.dropdowns["ai_color"].draw(self.screen)
            self.dropdowns["difficulty"].draw(self.screen)

        # ---- START BUTTON ----
        mouse_pos = pygame.mouse.get_pos()
        self.buttons["start"].check_hover(mouse_pos)
        self.buttons["start"].draw(self.screen)
        self.buttons["back"].check_hover(mouse_pos)
        self.buttons["back"].draw(self.screen)
        
    def draw_game_mode_screen(self):
        self.screen.fill((240, 240, 255))
        
        # Draw labels
        font = pygame.font.SysFont("Arial", 20)
        labels = ["Mode:", "AI Color:", "AI Difficulty:"]
        positions = [70, 270, 470]
        
        for label, x in zip(labels, positions):
            text = font.render(label, True, BLACK)
            self.screen.blit(text, (x, 25))
        
        # Draw dropdowns
        for dropdown in self.dropdowns.values():
            dropdown.draw(self.screen)
        
        # Draw start button
        mouse_pos = pygame.mouse.get_pos()
        self.buttons["start"].check_hover(mouse_pos)
        self.buttons["start"].draw(self.screen)
    
    def draw_game_screen(self):
        self.screen.fill((240, 240, 255))
        
        # Draw top panel with game info
        font = pygame.font.SysFont("Arial", 20, bold=True)
        
        # Draw mode info
        mode_text = f"Mode: {self.mode}"
        if self.mode == "Play with AI":
            mode_text += f" | AI: {self.ai_color} ({self.ai_difficulty})"
        text = font.render(mode_text, True, BLACK)
        self.screen.blit(text, (20, 10))
        
        # Draw player turn
        player_text = f"Turn: {'Red' if self.current_player == 'R' else 'Green'}"
        if self.extra_turn_after_capture:
            player_text += " (Extra Turn after Capture!)"
        text = font.render(player_text, True, BLACK)
        self.screen.blit(text, (20, 35))
        
        # Draw piece counts
        mag_count = self.count_pieces('R')
        green_count = self.count_pieces('G')
        count_text = f"Red: {mag_count} | Green: {green_count}"
        text = font.render(count_text, True, BLACK)
        self.screen.blit(text, (20, 60))
        
        # Draw board
        self.draw_board()
        # Draw home button
        self.buttons["home"].draw(self.screen)
        
        # Draw AI thinking indicator
        if self.ai_thinking:
            font = pygame.font.SysFont("Arial", 24)
            text = font.render("AI is thinking...", True, RED)
            self.screen.blit(text, (SCREEN_WIDTH//2 - 80, SCREEN_HEIGHT - 40))
        self.draw_game_message() 
    
    def load_game_state(self):
        if not os.path.exists(self.SAVE_FILE):
            return False
        
        try:
            with open(self.SAVE_FILE, "r") as f:
                data = json.load(f)
            
            self.board = data["board"]
            self.current_player = data["current_player"]
            self.selected = tuple(data["selected"]) if data["selected"] else None
            self.legal_moves = [tuple(m) for m in data["legal_moves"]]
            self.extra_turn_after_capture = data["extra_turn_after_capture"]
            
            self.mode = data["mode"]
            self.ai_color = data["ai_color"]
            self.ai_difficulty = data["ai_difficulty"]
            self.ai_player = data["ai_player"]
            
            self.game_mode = "playing"
            return True
            
        except Exception as e:
            print(f"Load failed: {e}")
            return False
    
    def save_game_state(self):
        try:
            data = {
                "board": self.board,
                "current_player": self.current_player,
                "selected": self.selected,
                "legal_moves": self.legal_moves,
                "extra_turn_after_capture": self.extra_turn_after_capture,
                "mode": self.mode,
                "ai_color": self.ai_color,
                "ai_difficulty": self.ai_difficulty,
                "ai_player": self.ai_player,
            }
            
            with open(self.SAVE_FILE, "w") as f:
                json.dump(data, f, indent=4)
            
            self.saved_game_exists = True  
            print("Game state saved")
            
        except Exception as e:
            print(f"Failed to save game: {e}")
    
    def load_window_geometry(self):
        if os.path.exists(self.config_file):
            config = configparser.ConfigParser()
            config.read(self.config_file)
            
            if "Geometry" in config:
                geometry = config["Geometry"].get("size", "")
                if geometry:
                    # Handle different formats: "widthxheight" or "widthxheight+x+y"
                    # We only need the width and height parts
                    if 'x' in geometry and '+' in geometry:
                        # Format: "widthxheight+x+y"
                        # Split by '+' first, then take the first part
                        size_part = geometry.split('+')[0]
                        w, h = map(int, size_part.split('x'))
                    elif 'x' in geometry:
                        # Format: "widthxheight"
                        w, h = map(int, geometry.split('x'))
                    else:
                        # Invalid format, use defaults
                        w, h = SCREEN_WIDTH, SCREEN_HEIGHT
                    
                    self.screen = pygame.display.set_mode((w, h))
                    
    def save_window_geometry(self):
        config = configparser.ConfigParser()
        
        if os.path.exists(self.config_file):
            config.read(self.config_file)
        
        if not config.has_section("Geometry"):
            config.add_section("Geometry")
        
        w, h = self.screen.get_size()
        # Only save the size, not the position
        config["Geometry"]["size"] = f"{w}x{h}"
        
        with open(self.config_file, "w") as f:
            config.write(f)
            
    def start_game(self):
        self.mode = self.dropdowns["mode"].get_selected()

        if self.mode == "Play with AI":
            self.ai_color = self.dropdowns["ai_color"].get_selected()
            self.ai_difficulty = self.dropdowns["difficulty"].get_selected()
            self.ai_player = 'R' if self.ai_color == "Red" else 'G'
        else:
            self.ai_color = None
            self.ai_difficulty = None
            self.ai_player = None

        self.init_board()
        self.selected = None
        self.legal_moves = []
        self.current_player = 'R'
        self.extra_turn_after_capture = False
        self.ai_thinking = False

        self.game_mode = "playing"
        self.show_mode_selection = False

        if self.mode == "Play with AI" and self.current_player == self.ai_player:
            pygame.time.set_timer(pygame.USEREVENT, 500)

    
    def restart_current_game(self):
        """Restart game using the SAME mode & AI settings"""

        # Reset board only
        self.init_board()
        self.selected = None
        self.legal_moves = []
        self.current_player = 'R'
        self.extra_turn_after_capture = False
        self.ai_thinking = False

        # Keep SAME mode
        if self.mode == "Play with AI":
            self.ai_player = 'R' if self.ai_color == "Red" else 'G'
        else:
            self.ai_player = None

        self.game_message_active = False
        self.game_message = None
        self.game_mode = "playing"

        # AI starts if needed
        if self.mode == "Play with AI" and self.current_player == self.ai_player:
            pygame.time.set_timer(pygame.USEREVENT, 500)


    def home_game(self):
        self.selected = None
        self.legal_moves = []
        self.current_player = 'R'
        self.extra_turn_after_capture = False
        self.ai_thinking = False
        self.init_board()
    
    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if self.game_mode == "playing":
                        self.save_game_state()   # ✅ only save real games
                    self.save_window_geometry()
                    running = False
                elif event.type == pygame.USEREVENT:
                    pygame.time.set_timer(pygame.USEREVENT, 0)  # Clear timer
                    self.ai_move()
                
                # In the event handling section
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # ================= GAME OVER STATE =================
                    if self.game_message_active:
                        if self.buttons["replay"].is_clicked(mouse_pos, event):
                            self.game_message_active = False
                            # self.start_game()   # restart game
                            self.restart_current_game()

                        elif self.buttons["game_home"].is_clicked(mouse_pos, event):
                            self.game_message_active = False
                            self.home_to_splash()

                        continue  # 🚫 block all other clicks

                    # ================= SPLASH SCREEN =================
                    if self.game_mode == "splash" and not self.show_mode_selection:
                        if self.saved_game_exists and self.buttons["continue"].is_clicked(mouse_pos, event):
                            if self.load_game_state():
                                self.game_mode = "playing"
                        elif self.buttons["new_game"].is_clicked(mouse_pos, event):
                            self.show_mode_selection = True

                    elif self.game_mode == "splash" and self.show_mode_selection:
                        self.dropdowns["mode"].handle_event(event)

                        if self.dropdowns["mode"].get_selected() == "Play with AI":
                            self.dropdowns["ai_color"].handle_event(event)
                            self.dropdowns["difficulty"].handle_event(event)

                        if self.buttons["start"].is_clicked(mouse_pos, event):
                            self.start_game()

                        elif self.buttons["back"].is_clicked(mouse_pos, event):
                            self.show_mode_selection = False

                    # ================= GAME PLAYING =================
                    elif self.game_mode == "playing":
                        if self.buttons["home"].is_clicked(mouse_pos, event):
                            self.home_to_splash()
                            continue

                        if self.mode == "Play with AI" and self.current_player == self.ai_player:
                            continue

                        if self.ai_thinking:
                            continue

                        cell = self.nearest_cell(mouse_pos[0], mouse_pos[1])
                        if cell is not None:
                            r, c = cell
                            piece = self.board[r][c]

                            if self.selected is None:
                                if piece == self.current_player:
                                    self.selected = (r, c)
                                    self.legal_moves = self.find_legal_moves(r, c)
                            else:
                                sr, sc = self.selected
                                if (r, c) == (sr, sc):
                                    self.selected = None
                                    self.legal_moves = []
                                elif (r, c) in self.legal_moves:
                                    self.make_move(sr, sc, r, c)
                                elif piece == self.current_player:
                                    self.selected = (r, c)
                                    self.legal_moves = self.find_legal_moves(r, c)

            self.selection_ring.update()          
            # Draw current screen
            if self.game_mode == "splash":
                self.draw_splash_screen()
            elif self.game_mode == "mode_select":
                self.draw_game_mode_screen()
            elif self.game_mode == "playing":
                self.draw_game_screen()
            
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(2)
    except:
        pass
    game = BaghChalPygame()
    game.run()
