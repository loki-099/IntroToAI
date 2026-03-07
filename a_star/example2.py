"""
    R - new maze & re-run
    Q - quit
"""

import random
import tkinter as tk
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

# ── Config ────────────────────────────────────────────────────────────────────

ROWS, COLS    = 25, 35
CELL          = 24
EXPLORE_DELAY = 12     # ms per explored-cell step
PATH_DELAY    = 55     # ms per path-cell step

# Wall density: 0.0 = open field, 1.0 = all walls
# ~0.25 gives a nice open maze with scattered obstacles
WALL_DENSITY  = 0.25

C_BG       = "#0f111a"
C_WALL     = "#c8c8d8"
C_OPEN     = "#1a1d2e"
C_EXPLORED = "#2a4a8a"
C_PATH     = "#00ddcc"
C_START    = "#44dd44"
C_GOAL     = "#dd4444"
C_TEXT     = "#c0c0d0"


# ── Maze generation ───────────────────────────────────────────────────────────

def generate_matrix(rows, cols, wall_density=WALL_DENSITY):
    matrix = [[1] * cols for _ in range(rows)]

    # Scatter random walls
    for r in range(rows):
        for c in range(cols):
            if random.random() < wall_density:
                matrix[r][c] = 0

    # Guaranteed corridor so A* always finds a path
    for c in range(cols):
        matrix[0][c] = 1
    for r in range(rows):
        matrix[r][cols - 1] = 1

    # Force start and goal open
    matrix[0][0]           = 1
    matrix[rows-1][cols-1] = 1

    return matrix


# ── A* via pathfinding library ────────────────────────────────────────────────

def run_astar(matrix):
    grid  = Grid(matrix=matrix)
    start = grid.node(0, 0)               # node(col, row)
    end   = grid.node(COLS - 1, ROWS - 1)

    finder = AStarFinder(
        diagonal_movement=DiagonalMovement.only_when_no_obstacle,
    )
    path, _ = finder.find_path(start, end, grid)

    # Collect every node the finder touched
    explored_nodes = []
    for r in range(ROWS):
        for c in range(COLS):
            node = grid.node(c, r)
            if node.closed or node.opened:
                explored_nodes.append(node)

    # Sort by g so animation fans outward from start correctly
    explored_nodes.sort(key=lambda n: n.g)
    explored = [(n.y, n.x) for n in explored_nodes]  # (row, col)

    # path is a list of Node objects → convert to (row, col)
    path_rc = [(node.y, node.x) for node in path]

    return path_rc, explored


# ── Tkinter App ───────────────────────────────────────────────────────────────

class AStarApp:
    def __init__(self, root):
        self.root = root
        self.root.title("A* Diagonal — pathfinding + tkinter")
        self.root.configure(bg=C_BG)
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(
            root,
            width=COLS * CELL,
            height=ROWS * CELL,
            bg=C_BG,
            highlightthickness=0,
        )
        self.canvas.pack()

        self.hud_var = tk.StringVar()
        tk.Label(
            root, textvariable=self.hud_var,
            bg=C_BG, fg=C_TEXT,
            font=("Consolas", 11), pady=4,
        ).pack()

        btn_frame = tk.Frame(root, bg=C_BG)
        btn_frame.pack(pady=(0, 8))
        for text, cmd in [("New Maze  (R)", self.new_run),
                            ("Quit  (Q)",     root.destroy)]:
            tk.Button(
                btn_frame, text=text, command=cmd,
                bg="#252838", fg=C_TEXT, activebackground="#353a50",
                relief="flat", padx=12, pady=4, font=("Consolas", 10),
            ).pack(side="left", padx=6)

        root.bind("<r>", lambda e: self.new_run())
        root.bind("<R>", lambda e: self.new_run())
        root.bind("<q>", lambda e: root.destroy())
        root.bind("<Q>", lambda e: root.destroy())

        self.rects    = {}
        self.after_id = None
        self.matrix   = None
        self.path     = []
        self.explored = []

        self._build_canvas()
        self.new_run()

    # ── Canvas ────────────────────────────────────────────────────────────────

    def _build_canvas(self):
        self.canvas.delete("all")
        self.rects = {}
        for r in range(ROWS):
            for c in range(COLS):
                x1, y1 = c * CELL,          r * CELL
                x2, y2 = x1 + CELL - 1,     y1 + CELL - 1  # 1px gap = grid lines
                item = self.canvas.create_rectangle(
                    x1, y1, x2, y2, fill=C_OPEN, outline="",
                )
                self.rects[(r, c)] = item

    def _colour(self, r, c, color):
        self.canvas.itemconfig(self.rects[(r, c)], fill=color)

    def _draw_maze(self):
        for r in range(ROWS):
            for c in range(COLS):
                self._colour(r, c, C_WALL if self.matrix[r][c] == 0 else C_OPEN)

    def _draw_markers(self):
        self.canvas.delete("marker")
        for (r, c), color in [((0, 0), C_START),
                                ((ROWS-1, COLS-1), C_GOAL)]:
            pad = CELL // 5
            x1  = c * CELL + pad
            y1  = r * CELL + pad
            self.canvas.create_oval(
                x1, y1,
                x1 + CELL - 2*pad,
                y1 + CELL - 2*pad,
                fill=color, outline="", tags="marker",
            )

    # ── Run ───────────────────────────────────────────────────────────────────

    def new_run(self):
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None

        self.matrix              = generate_matrix(ROWS, COLS)
        self.path, self.explored = run_astar(self.matrix)

        self._build_canvas()
        self._draw_maze()
        self._draw_markers()

        steps = len(self.path) - 1 if self.path else 0
        self.hud_var.set(
            f"Path steps: {steps}   |   Cells explored: {len(self.explored)}   "
            f"|   Diagonal: ✓  (no corner-cutting)"
        )

        self._animate_explore(0)

    # ── Animation ─────────────────────────────────────────────────────────────

    def _animate_explore(self, idx):
        if idx < len(self.explored):
            r, c = self.explored[idx]
            if self.matrix[r][c] == 1:
                self._colour(r, c, C_EXPLORED)
            self.after_id = self.root.after(
                EXPLORE_DELAY, self._animate_explore, idx + 1
            )
        else:
            self._draw_markers()
            self.after_id = self.root.after(200, self._animate_path, 0)

    def _animate_path(self, idx):
        if idx < len(self.path):
            r, c = self.path[idx]
            self._colour(r, c, C_PATH)
            self._draw_markers()
            self.after_id = self.root.after(
                PATH_DELAY, self._animate_path, idx + 1
            )
        else:
            self.after_id = None


# ── Entry ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    AStarApp(root)
    root.mainloop()