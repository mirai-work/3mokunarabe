import pyxel

try:
    import js
except:
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
        pyxel.load("KAIYOU.pyxres")

        pyxel.mouse(True)

        self.scene = "TITLE"
        self.difficulty = 3

        self.reset_game()

        pyxel.run(self.update, self.draw)

    # =========================
    # 初期化
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

        # ★タイトル背景
        if js:
            try:
                js.showTitle()
            except:
                pass

    # =========================
    # ゲーム開始
    # =========================
    def start_game(self):
        self.scene = "GAME"

        if js:
            try:
                js.showGame()
            except:
                pass

        pyxel.playm(0, loop=True)

    # =========================
    # 勝敗判定
    # =========================
    def check_game_over(self):

        p1 = sum(row.count(1) for row in self.grids)
        cpu = sum(row.count(2) for row in self.grids)

        self.status = 1 if p1 > cpu else (2 if cpu > p1 else 3)

        self.scene = "RESULT"

        if js:
            try:
                if self.status == 1:
                    js.showWin()
                elif self.status == 2:
                    js.showLose()
                else:
                    js.showTitle()
            except:
                pass

        pyxel.stop()

        pyxel.play(3, 2 if self.status == 1 else 3)

    # =========================
    # 更新処理
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

            if self.turn == 1 and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                mx = pyxel.mouse_x // CELL_SIZE
                my = pyxel.mouse_y // CELL_SIZE

                if 0 <= mx < BOARD_SIZE and 0 <= my < BOARD_SIZE:
                    flips = self.get_flips(mx, my, 1)

                    if flips:
                        self.grids[my][mx] = 1
                        for fx, fy in flips:
                            self.grids[fy][fx] = 1

                        self.change_turn()

            elif self.turn == 2:
                self.cpu_move()

        # ---------- RESULT ----------
        elif self.scene == "RESULT":

            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.reset_game()

    # =========================
    # フリップ判定
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
    # ターン変更
    # =========================
    def change_turn(self):
        self.turn = 3 - self.turn

        if self.turn == 2:
            self.cpu_move()

        # ここで勝敗チェック
        self.check_game_over()

    # =========================
    # CPU
    # =========================
    def cpu_move(self):

        moves = []

        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                flips = self.get_flips(x, y, 2)
                if flips:
                    moves.append((x, y, flips))

        if not moves:
            self.change_turn()
            return

        x, y, flips = moves[0]

        self.grids[y][x] = 2

        for fx, fy in flips:
            self.grids[fy][fx] = 2

        self.change_turn()

    # =========================
    # 描画
    # =========================
    def draw(self):
        pyxel.cls(0)

        if self.scene == "TITLE":
            pyxel.text(10, 10, "ATTACK 3MOKU", 7)
            pyxel.text(10, 20, "PRESS 1 / 2 / 3", 7)

        else:
            # グリッド
            for i in range(BOARD_SIZE + 1):
                pyxel.line(i * CELL_SIZE, 0,
                           i * CELL_SIZE, BOARD_SIZE * CELL_SIZE, 1)

                pyxel.line(0, i * CELL_SIZE,
                           BOARD_SIZE * CELL_SIZE, i * CELL_SIZE, 1)

            # 駒
            for y in range(BOARD_SIZE):
                for x in range(BOARD_SIZE):
                    if self.grids[y][x]:
                        u, v = CHARACTER_LIST[self.grids[y][x]-1]
                        pyxel.blt(x*CELL_SIZE+1, y*CELL_SIZE+1,
                                  0, u, v, 8, 8, 0)

            if self.scene == "RESULT":
                pyxel.text(10, 10, "RESULT", 7)


Othello25()
