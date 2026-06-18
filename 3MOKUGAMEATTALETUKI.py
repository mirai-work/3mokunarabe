import pyxel

try:
    import js
except ImportError:
    js = None

CELL_SIZE = 9
BOARD_SIZE = 5
SCREEN_SIZE = CELL_SIZE * BOARD_SIZE + 1

DIRECTIONS = [
    (-1,-1),(0,-1),(1,-1),
    (-1,0),        (1,0),
    (-1,1),(0,1),(1,1)
]

CHARACTER_LIST = [(0, 128), (0, 136)]

class Othello25:
    def __init__(self):
        pyxel.init(SCREEN_SIZE, SCREEN_SIZE, title="ATTACK 3MOKU")
        
        # Safe load for testing
        try:
            pyxel.load("KAIYOU.pyxres")
            self.has_res = True
        except FileNotFoundError:
            self.has_res = False

        pyxel.mouse(True)
        self.scene = "TITLE"
        self.difficulty = 3
        self.reset_game()
        pyxel.run(self.update, self.draw)

    # =========================
    # 初期化 (Initialization)
    # =========================
    def reset_game(self):
        self.grids = [[0] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.grids[1][1] = 2
        self.grids[2][2] = 2
        self.grids[1][2] = 1
        self.grids[2][1] = 1

        self.turn = 1
        self.scene = "TITLE"
        pyxel.stop()

        if js:
            try: js.showTitle()
            except: pass

    def start_game(self):
        self.scene = "GAME"
        if js:
            try: js.showGame()
            except: pass
        pyxel.playm(0, loop=True)

    # =========================
    # 勝敗判定 (Game Over Check)
    # =========================
    def check_game_over(self):
        p1 = sum(row.count(1) for row in self.grids)
        cpu = sum(row.count(2) for row in self.grids)
        
        self.status = 1 if p1 > cpu else (2 if cpu > p1 else 3)
        self.scene = "RESULT"

        if js:
            try:
                if self.status == 1: js.showWin()
                elif self.status == 2: js.showLose()
                else: js.showTitle()
            except: pass

        pyxel.stop()
        # pyxel.play(3, 2 if self.status == 1 else 3) # Uncomment if you have sound

    # =========================
    # 更新処理 (Update Loop)
    # =========================
    def update(self):
        # ---------- TITLE ----------
        if self.scene == "TITLE":
            if pyxel.btnp(pyxel.KEY_1):
                self.difficulty = 1
                self.start_game()
            elif pyxel.btnp(pyxel.KEY_2):
                self.difficulty = 2
                self.start_game()
            elif pyxel.btnp(pyxel.KEY_3):
                self.difficulty = 3
                self.start_game()

        # ---------- GAME ----------
        elif self.scene == "GAME":
            # 1. Check if ANYONE can move. If not, the game is over.
            if not self.has_valid_moves(1) and not self.has_valid_moves(2):
                self.check_game_over()
                return

            # 2. Player 1's Turn
            if self.turn == 1:
                if not self.has_valid_moves(1):
                    self.turn = 2 # Pass turn
                elif pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                    mx = pyxel.mouse_x // CELL_SIZE
                    my = pyxel.mouse_y // CELL_SIZE

                    if 0 <= mx < BOARD_SIZE and 0 <= my < BOARD_SIZE:
                        flips = self.get_flips(mx, my, 1)
                        if flips:
                            self.grids[my][mx] = 1
                            for fx, fy in flips:
                                self.grids[fy][fx] = 1
                            self.turn = 2

            # 3. CPU's Turn
            elif self.turn == 2:
                if not self.has_valid_moves(2):
                    self.turn = 1 # Pass turn
                else:
                    self.cpu_move()
                    self.turn = 1

        # ---------- RESULT ----------
        elif self.scene == "RESULT":
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.reset_game()

    # =========================
    # Valid Move Helper
    # =========================
    def has_valid_moves(self, player):
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                if self.get_flips(x, y, player):
                    return True
        return False

    # =========================
    # フリップ判定 (Get Flips)
    # =========================
    def get_flips(self, x, y, player):
        if self.grids[y][x] != 0:
            return []

        opponent = 3 - player
        flips = []

        for dx, dy in DIRECTIONS:
            nx, ny = x + dx, y + dy
            temp = []

            while 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and self.grids[ny][nx] == opponent:
                temp.append((nx, ny))
                nx += dx
                ny += dy

            if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and self.grids[ny][nx] == player:
                flips.extend(temp)

        return flips

    # =========================
    # CPU
    # =========================
    def cpu_move(self):
        moves = []
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                flips = self.get_flips(x, y, 2)
                if flips:
                    # Store move with how many pieces it flips
                    moves.append((x, y, flips, len(flips)))

        if not moves:
            return

        # TODO: Implement self.difficulty logic here!
        # For now, it just picks the first valid move.
        # Example for difficulty 3: moves.sort(key=lambda m: m[3], reverse=True)
        
        x, y, flips, _ = moves[0]

        self.grids[y][x] = 2
        for fx, fy in flips:
            self.grids[fy][fx] = 2


    # =========================
    # 描画 (Draw)
    # =========================
    def draw(self):
        pyxel.cls(0)

        if self.scene == "TITLE":
            pyxel.text(1, 10, "ATTACK 3MOKU", 7)
            pyxel.text(1, 20, "PRESS 1/2/3", 7)

        else:
            # Draw Grid
            for i in range(BOARD_SIZE + 1):
                pyxel.line(i * CELL_SIZE, 0, i * CELL_SIZE, BOARD_SIZE * CELL_SIZE, 1)
                pyxel.line(0, i * CELL_SIZE, BOARD_SIZE * CELL_SIZE, i * CELL_SIZE, 1)

            # Draw Pieces
            for y in range(BOARD_SIZE):
                for x in range(BOARD_SIZE):
                    if self.grids[y][x]:
                        if self.has_res:
                            # Draw from pyxres file
                            u, v = CHARACTER_LIST[self.grids[y][x]-1]
                            pyxel.blt(x*CELL_SIZE+1, y*CELL_SIZE+1, 0, u, v, 8, 8, 0)
                        else:
                            # Fallback shapes if res is missing
                            color = 8 if self.grids[y][x] == 1 else 10
                            pyxel.circ(x * CELL_SIZE + 4, y * CELL_SIZE + 4, 3, color)

            if self.scene == "RESULT":
                # Determine winner text
                msg = "P1 WIN" if self.status == 1 else ("CPU WIN" if self.status == 2 else "DRAW")
                pyxel.text(6, 20, "RESULT", 7)
                pyxel.text(6, 30, msg, 8 if self.status == 1 else 10)

Othello25()
