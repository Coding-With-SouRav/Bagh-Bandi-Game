import configparser
import ctypes
import os
import sys
import threading
import tkinter as tk
from tkinter import StringVar, IntVar, ttk
from PIL import Image, ImageTk
import random
import colorsys
import math
import pygame
from pygame.locals import *

if sys.platform == "win32":
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("com.example.BaghBandiGame")

def resource_path(relative_path):

    try:
        base_path = sys._MEIPASS

    except Exception:
        base_path = os.path.abspath(".")
    full_path = os.path.join(base_path, relative_path)

    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Resource not found: {full_path}")
    return full_path
CANVAS_SIZE = 600
BOARD_SIZE = 5
MARGIN = 50
CELL = (CANVAS_SIZE - 2 * MARGIN) // (BOARD_SIZE - 1)
LINE_WIDTH = 2
POINT_RADIUS = 16
RED = "T"
GREEN = "G"
EMPTY = "."
BG_DARK = "#071029"
BG_PANEL = "#241BA4"
FG_TEXT = "white"

class GameState:

    def __init__(self):
        self.grid = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.current_player = RED
        for r in range(2):
            for c in range(BOARD_SIZE):
                self.grid[r][c] = RED
        for r in range(BOARD_SIZE - 2, BOARD_SIZE):
            for c in range(BOARD_SIZE):
                self.grid[r][c] = GREEN

    def neighbors(self, r, c):
        dirs = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]
        for dr, dc in dirs:
            nr, nc = r+dr, c+dc

            if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                yield nr, nc

    def valid_moves(self, r, c):
        moves, captures = [], []
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
            nr, nc = r+dr, c+dc

            if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:

                if self.grid[nr][nc] == EMPTY:
                    moves.append((nr,nc))
                elif self.grid[nr][nc] != self.current_player:
                    jr, jc = nr+dr, nc+dc

                    if 0 <= jr < BOARD_SIZE and 0 <= jc < BOARD_SIZE and self.grid[jr][jc] == EMPTY:
                        captures.append(((nr,nc),(jr,jc)))
        return moves, captures

    def count_pieces(self, piece):
        return sum(cell == piece for row in self.grid for cell in row)

    def is_red_win(self):
        return self.count_pieces(GREEN) == 0

    def is_green_win(self):
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):

                if self.grid[r][c] == RED:
                    moves, captures = self.valid_moves(r,c)

                    if moves or captures:
                        return False
        return True

class BaghBandiUI:

    def __init__(self, root):
        self.root = root
        self.root.title("Bagh Bandi — By SouRav Bhattacharya")
        self.root.geometry("900x650")
        self.root.configure(bg=BG_DARK)
        self.root.resizable(False, False)
        pygame.init()
        pygame.mixer.init()

        try:
            self.root.iconbitmap(resource_path(r"icons/icon.ico"))

        except:
            pass
        self.data_dir = os.path.join(os.path.expanduser("~"), ".BaghBandiGame")
        os.makedirs(self.data_dir, exist_ok=True)
        self.config_file = os.path.join(self.data_dir, "config.ini")
        self.ai_enabled = False
        self.controllar_frame = None
        self.game_over = False
        self.angle = 0
        self.hue = 0
        self.animation_running = False
        self.animation_items = {}
        self.main_frame = tk.Frame(root, bg=BG_DARK)
        self.main_frame.pack(fill="both", expand=True)
        self.canvas_frame = tk.Frame(self.main_frame, bg="#40477A")
        self.canvas = tk.Canvas(self.canvas_frame, width=CANVAS_SIZE, height=CANVAS_SIZE,
                                bg=BG_DARK, highlightthickness=0)
        self.canvas.pack(padx=15, pady=15)
        self.sidebar = tk.Frame(self.main_frame, bg=BG_PANEL)
        tk.Label(self.sidebar, text="BAGH BANDI", font=("Segoe UI", 25, "bold"),
                 fg="white", bg=BG_PANEL).pack(pady=10)
        ttk.Separator(self.sidebar, orient="horizontal").pack(fill="x", pady=5)
        self.info_var = StringVar()
        self.status_var = StringVar()
        tk.Label(self.sidebar, textvariable=self.info_var, font=("Segoe UI", 14, "bold"),
                 fg="cyan", bg=BG_PANEL).pack(pady=10)
        tk.Label(self.sidebar, textvariable=self.status_var, font=("Segoe UI", 12, "bold"),
                 fg="lightgreen", bg=BG_PANEL).pack(pady=10)
        tk.Button(self.sidebar, text="Restart Game", font=("Segoe UI", 12, "bold"),
                  fg="black",bd=0, bg="lightgreen", activebackground="#05E335", command=self.restart_game).pack(pady=10)
        tk.Button(self.sidebar, text="Quit", font=("Segoe UI", 12, "bold"),
                  fg="white",bd=0, bg="red", activebackground="red", command=self.on_closing).pack(pady=10)
        toggle_on_img = Image.open(resource_path(r"icons/toggle_on.png")).resize((80, 40))
        self.toggle_on_icon = ImageTk.PhotoImage(toggle_on_img)
        toggle_off_img = Image.open(resource_path(r"icons/toggle_off.png")).resize((80, 40))
        self.toggle_off_icon = ImageTk.PhotoImage(toggle_off_img)

        def toggle_ai_button():
            self.ai_enabled = not self.ai_enabled
            self.ai_btn.config(image=(self.toggle_on_icon if self.ai_enabled else self.toggle_off_icon))

            if self.ai_enabled and self.state.current_player == RED:
                self.root.after(500, self.ai_move)
        tk.Label(self.sidebar, text="PLAY WITH COMPUTER", font=("Segoe UI", 14, "bold"),
                 fg="cyan", bg=BG_PANEL).pack(pady=(50,5))
        self.ai_btn = tk.Button(self.sidebar, image=self.toggle_off_icon,
                           bg=BG_PANEL, bd=0, activebackground=BG_PANEL,
                           command=toggle_ai_button)
        self.ai_btn.pack(pady=(0,50))
        self.difficulty = StringVar(value="Medium")
        tk.Label(self.sidebar, text="AI Difficulty:", font=("Segoe UI", 12, "bold"),
                 fg="cyan", bg=BG_PANEL).pack(pady=5)
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "TCombobox",
            fieldbackground="red",
            background="#12E5F0",
            foreground="black",
            bordercolor="red",
            lightcolor="black",
            darkcolor="pink",
            arrowcolor="blue",
            selectbackground="lightblue",
            selectforeground="black"
        )
        self.sidebar.option_add('*TCombobox*Listbox.background', "#262372")
        self.sidebar.option_add('*TCombobox*Listbox.foreground', 'white')
        self.sidebar.option_add('*TCombobox*Listbox.selectBackground', "#5A7DE5")
        self.sidebar.option_add('*TCombobox*Listbox.selectForeground', 'black')
        self.sidebar.option_add('*TCombobox*Listbox.font', 'SegoeUI 11')
        self.difficulty_dropdown = ttk.Combobox(self.sidebar, textvariable=self.difficulty,
                                    values=["Easy", "Medium", "Hard", "Expert"],
                                    font=("Segoe UI", 12), state="readonly")
        self.difficulty_dropdown.pack(pady=5)
        self.state = GameState()
        self.selected = None
        self.valid_moves = []
        self.valid_captures = []
        red_img = Image.open(resource_path(r"icons/red.png")).resize((35, 35))
        self.red_piece = ImageTk.PhotoImage(red_img)
        green_img = Image.open(resource_path(r"icons/green.png")).resize((35, 35))
        self.green_piece = ImageTk.PhotoImage(green_img)
        self.cut_sound1 = pygame.mixer.Sound(resource_path(r"icons/red_cut.mp3"))
        self.cut_sound2 = pygame.mixer.Sound(resource_path(r"icons/green_cut.mp3"))
        self.canvas.bind("<Button-1>", self.on_click)
        self.load_window_geometry()
        self.show_welcome_screen()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _handle_post_ai_move_capture(self, captured):

        if captured:
            self.cut_sound1.play()
            self.status_var.set("CUT!")
            self.draw_board()
            self.root.after(800, self.draw_board)
        else:
            self.draw_board()

    def animate_selection(self):

        if not self.selected or self.game_over:
            self.animation_running = False
            return
        for item_id in self.animation_items.values():
            self.canvas.delete(item_id)
        self.animation_items.clear()
        self.angle = (self.angle + 3) % 360
        self.hue += 0.01

        if self.hue > 1:
            self.hue = 0
        r, g, b = colorsys.hsv_to_rgb(self.hue, 1, 1)
        hex_color = f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
        sr, sc = self.selected
        x, y = self.coord_to_pixel(sr, sc)
        arc_radius = POINT_RADIUS + 6
        arc_id = self.canvas.create_arc(
            x - arc_radius, y - arc_radius,
            x + arc_radius, y + arc_radius,
            start=self.angle, extent=210,
            style="arc", outline=hex_color, width=3
        )
        self.animation_items[(sr, sc)] = arc_id

        if self.selected:
            self.root.after(5, self.animate_selection)
        else:
            self.animation_running = False

    def on_closing(self):
        self.save_game_state()
        self.save_window_geometry()
        self.root.destroy()

    def load_window_geometry(self):

        if os.path.exists(self.config_file):
            config = configparser.ConfigParser()
            config.read(self.config_file)

            if "Geometry" in config:
                geometry = config["Geometry"].get("size", "")
                state = config["Geometry"].get("state", "normal")

                if geometry:
                    self.root.geometry(geometry)
                    self.root.update_idletasks()
                    self.root.update()

                if state == "zoomed":
                    self.root.state("zoomed")
                elif state == "iconic":
                    self.root.iconify()

    def save_window_geometry(self):
        config = configparser.ConfigParser()

        if os.path.exists(self.config_file):
            config.read(self.config_file)

        if not config.has_section("Geometry"):
            config.add_section("Geometry")
        config["Geometry"]["size"] = self.root.geometry()
        config["Geometry"]["state"] = self.root.state()

        with open(self.config_file, "w") as f:
            config.write(f)

    def toggle_ai(self):

        if self.ai_enabled and self.state.current_player == RED:
            self.root.after(500, self.ai_move)

    def restart_game(self):
        self.state = GameState()

        if self.controllar_frame is not None:

            try:
                self.controllar_frame.place_forget()
                self.controllar_frame.destroy()

            except:
                pass
            self.controllar_frame = None
        self.game_over = False
        self.main_frame.pack(fill="both", expand=True)
        self.selected = None
        self.valid_moves = []
        self.valid_captures = []
        self.draw_board()

        if self.ai_enabled and self.state.current_player == RED:
            self.root.after(500, self.ai_move)

    def coord_to_pixel(self, r, c):
        x = MARGIN + c * CELL
        y = MARGIN + r * CELL
        return x, y

    def pixel_to_coord(self, x, y):
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                px, py = self.coord_to_pixel(r,c)

                if (x-px)**2 + (y-py)**2 <= 20**2:
                    return r,c
        return None

    def draw_board(self):

        if getattr(self, "game_over", False):
            return
        self.canvas.delete("all")
        self.canvas.create_rectangle(18, 18, CANVAS_SIZE - 18, CANVAS_SIZE - 18,
                                     fill='#071029', outline='')
        for i in range(BOARD_SIZE):
            x1, y = self.coord_to_pixel(i, 0)
            x2, _ = self.coord_to_pixel(i, BOARD_SIZE - 1)
            self.canvas.create_line(MARGIN, y, CANVAS_SIZE - MARGIN, y,
                                    width=LINE_WIDTH, fill='#2b3948')
            x, y1 = self.coord_to_pixel(0, i)
            _, y2 = self.coord_to_pixel(BOARD_SIZE - 1, i)
            self.canvas.create_line(x, MARGIN, x, CANVAS_SIZE - MARGIN,
                                    width=LINE_WIDTH, fill='#2b3948')
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                x, y = self.coord_to_pixel(r, c)
                for nr, nc in self.state.neighbors(r, c):
                    x2, y2 = self.coord_to_pixel(nr, nc)

                    if nr > r or (nr == r and nc > c):
                        self.canvas.create_line(x, y, x2, y2,
                                                width=1.5, fill='#233041')
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                x, y = self.coord_to_pixel(r, c)
                self.canvas.create_oval(x - 6, y - 6, x + 6, y + 6,
                                        fill='#0b1220', outline='#1f2a36')
                piece = self.state.grid[r][c]

                if piece == RED:
                    self.canvas.create_image(x, y, image=self.red_piece)
                elif piece == GREEN:
                    self.canvas.create_image(x, y, image=self.green_piece)

        if self.selected:
            sr, sc = self.selected
            x, y = self.coord_to_pixel(sr, sc)

            if not self.animation_running:
                self.animation_running = True
                self.animate_selection()
            for (mr, mc) in self.valid_moves:
                mx, my = self.coord_to_pixel(mr, mc)
                self.canvas.create_oval(mx - 8, my - 8, mx + 8, my + 8,
                                        outline="#7ee787", width=2)
            for (_, (jr, jc)) in self.valid_captures:
                mx, my = self.coord_to_pixel(jr, jc)
                self.canvas.create_oval(mx - 10, my - 10, mx + 10, my + 10,
                                        outline="red", width=2)
        self.info_var.set(f"{'RED' if self.state.current_player == RED else 'GREEN'}'s turn")
        red_count = self.state.count_pieces(RED)
        green_count = self.state.count_pieces(GREEN)

        if green_count == 0:
            self.game_over_window("RED WINS!!")
            return

        if red_count == 0:
            self.game_over_window("GREEN WINS!!")
            return

        if self.state.is_red_win():
            self.game_over_window("RED WINS!!")
        elif self.state.is_green_win():
            self.game_over_window("GREEN WINS!!")
        else:
            self.status_var.set("Game in progress...")

    def game_over_window(self, message):

        if getattr(self, "game_over", False):
            return
        self.game_over = True
        self.animation_running = False

        try:
            self.main_frame.pack_forget()

        except:
            pass

        if self.controllar_frame is not None:

            try:
                self.controllar_frame.destroy()

            except:
                pass
            self.controllar_frame = None
        self.controllar_frame = tk.Frame(self.root,width=400, height=400, bg="#081996")
        self.controllar_frame.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(self.controllar_frame, text="Game Over", font=("Arial", 40, "bold"), fg="red", bg="#081996").pack(pady=10, padx=30)
        tk.Label(self.controllar_frame, text=message, font=("Arial", 20), fg="#82eef0", bg="#081996").pack(pady=10)
        tk.Button(self.controllar_frame, text="Play Again", command=self.restart_game, bg="#0AAB22", fg="white", bd=0, activebackground="#0CF067", font=("Segoe UI", 12, "bold"), width=12).pack(pady=10)
        tk.Button(self.controllar_frame, text="Quit", command=self.on_closing, bg="#FF0808", fg="white", bd=0, activebackground="#EF4545", font=("Segoe UI", 12, "bold"), width=12).pack(pady=(10,30))

    def on_click(self, event):

        if self.state.current_player == RED and self.ai_enabled:
            return

        if getattr(self, "game_over", False):
            return
        cell = self.pixel_to_coord(event.x, event.y)

        if not cell:
            return
        r, c = cell
        piece = self.state.grid[r][c]

        if self.selected is None:

            if piece == self.state.current_player:
                self.selected = (r, c)
                self.valid_moves, self.valid_captures = self.state.valid_moves(r, c)
                self.animation_running = True
                self.animate_selection()
        else:
            sr, sc = self.selected
            capture_made = False
            for (enemy, (jr, jc)) in self.valid_captures:

                if (r, c) == (jr, jc):
                    er, ec = enemy
                    self.state.grid[jr][jc] = self.state.grid[sr][sc]
                    self.state.grid[sr][sc] = EMPTY
                    self.state.grid[er][ec] = EMPTY
                    capture_made = True
                    self.selected = (jr, jc)
                    self.valid_moves, self.valid_captures = self.state.valid_moves(jr, jc)
                    self.draw_board()
                    self.cut_sound2.play()
                    self.status_var.set("CUT!")
                    self.root.after(800, self.draw_board)

                    if self.valid_captures and self.state.current_player == GREEN:
                        return
                    else:
                        self.state.current_player = GREEN if self.state.current_player == RED else RED
                    break

            if not capture_made:

                if (r, c) in self.valid_moves:
                    self.state.grid[r][c] = self.state.grid[sr][sc]
                    self.state.grid[sr][sc] = EMPTY
                    self.state.current_player = GREEN if self.state.current_player == RED else RED
                self.selected = None
                self.animation_running = False
                for item_id in self.animation_items.values():
                    self.canvas.delete(item_id)
                self.animation_items.clear()
        self.draw_board()

        if self.ai_enabled and self.state.current_player == RED:
            self.root.after(500, self.ai_move)

    def evaluate(self):
        green_count = sum(cell == GREEN for row in self.state.grid for cell in row)
        red_count = sum(cell == RED for row in self.state.grid for cell in row)
        material_score = (10 - green_count) * 50 - (8 - red_count) * 30
        red_moves = 0
        red_captures = 0
        green_moves = 0
        green_captures = 0
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):

                if self.state.grid[r][c] == RED:
                    moves, caps = self.state.valid_moves(r, c)
                    red_moves += len(moves)
                    red_captures += len(caps) * 3
                elif self.state.grid[r][c] == GREEN:
                    moves, caps = self.state.valid_moves(r, c)
                    green_moves += len(moves)
                    green_captures += len(caps) * 3
        mobility_score = (red_moves + red_captures * 5) - (green_moves + green_captures * 4)
        center_control = 0
        key_positions = [(1, 1), (1, 3), (3, 1), (3, 3)]
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):

                if self.state.grid[r][c] == RED:
                    distance_to_center = abs(r - 2) + abs(c - 2)
                    center_control += (4 - distance_to_center) * 2

                    if (r, c) in key_positions:
                        center_control += 10

        if self.state.is_red_win():
            return 10000 + material_score

        if self.state.is_green_win():
            return -10000 - material_score
        return material_score + mobility_score + center_control

    def board_key(self):
        return tuple(tuple(row) for row in self.state.grid), self.state.current_player

    def minimax(self, depth, is_red_turn, alpha=-float('inf'), beta=float('inf'), memo=None):

        if memo is None:
            memo = {}
        board_key = self.board_key()
        key = (board_key, depth, is_red_turn)

        if key in memo:
            return memo[key]

        if depth == 0 or self.state.is_red_win() or self.state.is_green_win():
            score = self.evaluate()
            memo[key] = (score, None)
            return score, None
        best_move = None

        if is_red_turn:
            max_eval = -float('inf')
            all_moves = []
            for r in range(BOARD_SIZE):
                for c in range(BOARD_SIZE):

                    if self.state.grid[r][c] == RED:
                        moves, caps = self.state.valid_moves(r, c)
                        for move in moves:
                            all_moves.append(((r, c), move, None))
                        for (enemy, dest) in caps:
                            all_moves.append(((r, c), dest, enemy))
            all_moves.sort(
                key=lambda x: (
                    x[2] is not None,
                    -(abs(x[1][0] - 2) + abs(x[1][1] - 2))
                ),
                reverse=True
            )
            for move in all_moves:
                (sr, sc), (jr, jc), enemy = move
                backup = [row[:] for row in self.state.grid]
                self.state.grid[jr][jc] = RED
                self.state.grid[sr][sc] = EMPTY

                if enemy:
                    er, ec = enemy
                    self.state.grid[er][ec] = EMPTY
                eval_score, _ = self.minimax(depth - 1, False, alpha, beta, memo)
                self.state.grid = backup

                if eval_score > max_eval:
                    max_eval, best_move = eval_score, move
                alpha = max(alpha, eval_score)

                if beta <= alpha:
                    break
            memo[key] = (max_eval, best_move)
            return max_eval, best_move
        else:
            min_eval = float('inf')
            all_moves = []
            for r in range(BOARD_SIZE):
                for c in range(BOARD_SIZE):

                    if self.state.grid[r][c] == GREEN:
                        moves, caps = self.state.valid_moves(r, c)
                        for move in moves:
                            all_moves.append(((r, c), move, None))
                        for (enemy, dest) in caps:
                            all_moves.append(((r, c), dest, enemy))
            all_moves.sort(
                key=lambda x: (
                    x[2] is not None,
                    (abs(x[1][0] - 2) + abs(x[1][1] - 2))
                ),
                reverse=True
            )
            for move in all_moves:
                (sr, sc), (jr, jc), enemy = move
                backup = [row[:] for row in self.state.grid]
                self.state.grid[jr][jc] = GREEN
                self.state.grid[sr][sc] = EMPTY

                if enemy:
                    er, ec = enemy
                    self.state.grid[er][ec] = EMPTY
                eval_score, _ = self.minimax(depth - 1, True, alpha, beta, memo)
                self.state.grid = backup

                if eval_score < min_eval:
                    min_eval, best_move = eval_score, move
                beta = min(beta, eval_score)

                if beta <= alpha:
                    break
            memo[key] = (min_eval, best_move)
            return min_eval, best_move

    def _apply_ai_move(self, best_move, captured):

        if best_move:
            (sr, sc), (jr, jc), enemy = best_move
            self.state.grid[jr][jc] = self.state.grid[sr][sc]
            self.state.grid[sr][sc] = EMPTY

            if enemy:
                er, ec = enemy
                self.state.grid[er][ec] = EMPTY
        self.state.current_player = GREEN
        self.selected = None
        self.valid_moves = []
        self.valid_captures = []
        self._handle_post_ai_move_capture(captured)

    def ai_move(self):

        if self.state.current_player != RED:
            return

        def think():
            level = self.difficulty.get()

            if level == "Easy":
                depth = 1

                if random.random() < 0.3:
                    red_pieces = []
                    for r in range(BOARD_SIZE):
                        for c in range(BOARD_SIZE):

                            if self.state.grid[r][c] == RED:
                                moves, captures = self.state.valid_moves(r, c)

                                if moves or captures:
                                    red_pieces.append((r, c))

                    if red_pieces:
                        sr, sc = random.choice(red_pieces)
                        moves, captures = self.state.valid_moves(sr, sc)
                        all_moves = [(m, None) for m in moves] + [(dest, enemy) for enemy, dest in captures]

                        if all_moves:
                            m, enemy = random.choice(all_moves)
                            best_move = ((sr, sc), m, enemy)
                            captured = bool(enemy)
                            self.root.after(0, lambda bm=best_move, cap=captured: self._apply_ai_move(bm, cap))
                            return
                depth = 1
            elif level == "Medium":
                depth = 2
            elif level == "Hard":
                depth = 3
            else:
                depth = 4
            _, best_move = self.minimax(depth, True)

            if not best_move:
                red_pieces = []
                for r in range(BOARD_SIZE):
                    for c in range(BOARD_SIZE):

                        if self.state.grid[r][c] == RED:
                            moves, captures = self.state.valid_moves(r, c)

                            if moves or captures:
                                red_pieces.append((r, c))

                if red_pieces:
                    sr, sc = random.choice(red_pieces)
                    moves, captures = self.state.valid_moves(sr, sc)
                    all_moves = [(m, None) for m in moves] + [(dest, enemy) for enemy, dest in captures]

                    if all_moves:
                        m, enemy = random.choice(all_moves)
                        best_move = ((sr, sc), m, enemy)
            captured = bool(best_move and best_move[2])
            self.root.after(0, lambda bm=best_move, cap=captured: self._apply_ai_move(bm, cap))
        threading.Thread(target=think, daemon=True).start()

    def save_game_state(self):
        config = configparser.ConfigParser()

        if os.path.exists(self.config_file):
            config.read(self.config_file)

        if not config.has_section("GameState"):
            config.add_section("GameState")
        grid_str = ''.join(''.join(row) for row in self.state.grid)
        config["GameState"]["grid"] = grid_str
        config["GameState"]["current_player"] = self.state.current_player
        config["GameState"]["ai_enabled"] = str(self.ai_enabled)
        config["GameState"]["difficulty"] = self.difficulty.get()

        with open(self.config_file, "w") as f:
            config.write(f)

    def load_game_state(self):

        if not os.path.exists(self.config_file):
            return False
        config = configparser.ConfigParser()
        config.read(self.config_file)

        if "GameState" not in config:
            return False

        try:
            grid_str = config["GameState"]["grid"]
            for i in range(BOARD_SIZE):
                for j in range(BOARD_SIZE):
                    self.state.grid[i][j] = grid_str[i * BOARD_SIZE + j]
            self.state.current_player = config["GameState"]["current_player"]
            self.ai_enabled = config["GameState"].getboolean("ai_enabled")
            self.difficulty.set(config["GameState"]["difficulty"])

            if hasattr(self, 'ai_btn'):
                self.ai_btn.config(
                    image=(self.toggle_on_icon if self.ai_enabled else self.toggle_off_icon)
                )
            return True

        except:
            return False

    def show_welcome_screen(self):
        self.welcome_frame = tk.Frame(self.root,  width=350, background="#0F0895")
        self.welcome_frame.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(self.welcome_frame, text="BAGH BANDI",
                font=("Segoe UI", 30, "bold"), fg="white", bg="#0F0895").pack(pady=20, padx=30)
        tk.Button(self.welcome_frame, text="New Game",
                command=self.start_new_game, bg="#0AAB22", fg="white", bd=0, activebackground="#0CF067",
                font=("Segoe UI", 12, "bold"), width=15).pack(pady=10)
        has_saved_game = os.path.exists(self.config_file)
        self.continue_btn = tk.Button(self.welcome_frame, text="Continue", bd=0, activebackground="#3073F7",
                                    command=self.continue_game, bg="blue", fg="white",
                                    font=("Segoe UI", 12, "bold"),
                                    width=15, state="normal" if has_saved_game else "disabled")
        self.continue_btn.pack(pady=10)
        tk.Button(self.welcome_frame, text="Quit", bd=0, activebackground="#F94B4B",
                command=self.on_closing, bg="red", fg="white",
                font=("Segoe UI", 12, "bold"), width=15).pack(pady=(10,20))

    def start_new_game(self):
        self.welcome_frame.destroy()
        self.state = GameState()
        self.selected = None
        self.valid_moves = []
        self.valid_captures = []
        self.game_over = False
        self.draw_board()
        self.canvas_frame.pack(side="left", padx=10, pady=10)
        self.sidebar.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        if self.ai_enabled and self.state.current_player == RED:
            self.root.after(500, self.ai_move)

    def continue_game(self):

        if self.load_game_state():
            self.welcome_frame.destroy()
            self.selected = None
            self.valid_moves = []
            self.valid_captures = []
            self.game_over = False
            self.draw_board()
            self.canvas_frame.pack(side="left", padx=10, pady=10)
            self.sidebar.pack(side="left", fill="both", expand=True, padx=10, pady=10)

            if self.ai_enabled and self.state.current_player == RED:
                self.root.after(500, self.ai_move)

if __name__ == "__main__":
    root = tk.Tk()
    app = BaghBandiUI(root)
    root.mainloop()
