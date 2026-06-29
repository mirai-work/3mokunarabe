import pyxel
import random
import copy
import math

try:
    import js
except:
    js = None

CELL_SIZE = 9
BOARD_SIZE = 5
SCREEN_SIZE = CELL_SIZE * BOARD_SIZE + 1
VIEW_HEIGHT = SCREEN_SIZE + 10 
DIRECTIONS = [(-1,-1), (0,-1), (1,-1), (-1,0), (1,0), (-1,1), (0,1), (1,1)]
CHARACTER_LIST = [(0, 128), (0, 136)]

class Othello25:
    def __init__(self):
        pyxel.init(SCREEN_SIZE, VIEW_HEIGHT, title="ATTACK3MOKU")
        try:
            pyxel.load("KAIYOU.pyxres")
        except:
            pass
        self.init_sound()
        pyxel.mouse(True)
        self.reset_game()
        pyxel.run(self.update, self.draw)

    def call_js(self, func_name):
        if js and hasattr(js, func_name):
            try: getattr(js, func_name)()
            except: pass

    def is_decision_pressed(self):
        return pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A) or pyxel.btnp(pyxel.KEY_SPACE)

    def init_sound(self):
        # ... (初期化処理は同じ) ...
        pyxel.sound(0).set("e2e2", "n", "7", "f", 5)
        pyxel.sound(1).set("g3g3 c4", "p", "7", "v", 10)
        pyxel.sound(2).set("c4e4g4 c4 r c4", "p", "7", "v", 10)
        pyxel.sound(10).set("c3 e3 g3 c4  e3 g3 c4 e4", "t", "4", "n", 25)
        pyxel.sound(11).set("c2 g2 c2 g2  c2 g2 c2 g2", "s", "4", "n", 25)
        pyxel.music(0).set([10], [11], [], [])
        # ... 以下省略(元のコードと同様) ...
        pyxel.sound(12).set("a2 c3 e3 a3  g2 b2 d3 g3", "t", "5", "n", 25)
        pyxel.sound(13).set("a1 e2 a1 e2  g1 d2 g1 d2", "p", "5", "n", 25)
        pyxel.music(1).set([12], [13], [], [])
        pyxel.sound(16).set("c3 e3 g3 c4 g3 e3 c3 e3", "t", "5", "n", 20)
        pyxel.sound(17).set("c2 g2 c2 g2 c2 g2 c2 g2", "p", "5", "n", 20)
        pyxel.music(4).set([16], [17], [], [])
        pyxel.sound(18).set("e3 e3 g3 e3 a3 g3 e3 d3", "t", "6", "n", 15)
        pyxel.sound(19).set("e2 e2 e2 e2 e2 e2 e2 e2", "n", "5", "f", 15)
        pyxel.music(5).set([18], [19], [], [])
        pyxel.sound(14).set("c3 e3 g3 c4 e4 c4 e4 g4 c4 r r r", "p", "6", "n", 25)
        pyxel.music(2).set([14], [], [], [])
        pyxel.sound(15).set("c3 g2 d#2 c2 g1 d#1 c1 r r r", "s", "6", "f", 25)
        pyxel.music(3).set([15], [], [], [])

    def reset_game(self):
        self.grids = [[0] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.grids[1][1] = 2; self.grids[2][2] = 2
        self.grids[1][2] = 1; self.grids[2][1] = 1
        self.turn = 1; self.status = 0; self.wait_timer = 0
        self.pass_timer = 0; self.attack_chance_available = True
        self.difficulty = 2
        # ステージを「背景表示中」に設定
        self.scene = "TITLE_WAIT" 
        self.title_wait_timer = 30 # 背景が表示されるのを待つ時間
        self.cursor_x = 2; self.cursor_y = 2
        pyxel.stop()
        self.call_js("showTitleBG")

    def start_game(self, difficulty_level, music_id):
        self.difficulty = difficulty_level
        self.scene = "GAME"
        pyxel.playm(music_id, loop=True)
        self.call_js("clearBG")

    # ... (get_flips, apply_move_logic, evaluate_board, minimax, check_valid, cpu_move, check_attack_chance_trigger, cpu_attack, change_turn, check_game_over は元のまま) ...
    def get_flips(self, x, y, p):
        if self.grids[y][x] != 0: return []
        flips = []
        opp = 3 - p
        for dx, dy in DIRECTIONS:
            nx, ny = x + dx, y + dy
            temp = []
            while 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and self.grids[ny][nx] == opp:
                temp.append((nx, ny)); nx += dx; ny += dy
            if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and self.grids[ny][nx] == p:
                flips.extend(temp)
        return flips

    def apply_move_logic(self, board, x, y, p):
        board[y][x] = p
        opp = 3 - p
        for dx, dy in DIRECTIONS:
            nx, ny = x + dx, y + dy
            temp = []
            while 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and board[ny][nx] == opp:
                temp.append((nx, ny)); nx += dx; ny += dy
            if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and board[ny][nx] == p:
                for fx, fy in temp: board[fy][fx] = p

    def evaluate_board(self, board, player):
        score = 0
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                w = 10 if (x in [0, BOARD_SIZE-1] and y in [0, BOARD_SIZE-1]) else 1
                if board[y][x] == player: score += w
                elif board[y][x] != 0: score -= w
        return score

    def minimax(self, board, depth, player, alpha, beta):
        if depth == 0: return self.evaluate_board(board, 2)
        moves = [(x, y) for y in range(BOARD_SIZE) for x in range(BOARD_SIZE) if self.check_valid(board, x, y, player)]
        if not moves: return self.evaluate_board(board, 2)
        if player == 2:
            val = -math.inf
            for mx, my in moves:
                b = copy.deepcopy(board); self.apply_move_logic(b, mx, my, 2)
                val = max(val, self.minimax(b, depth-1, 1, alpha, beta)); alpha = max(alpha, val)
                if beta <= alpha: break
            return val
        else:
            val = math.inf
            for mx, my in moves:
                b = copy.deepcopy(board); self.apply_move_logic(b, mx, my, 1)
                val = min(val, self.minimax(b, depth-1, 2, alpha, beta)); beta = min(beta, val)
                if beta <= alpha: break
            return val

    def check_valid(self, board, x, y, p):
        if board[y][x] != 0: return False
        opp = 3 - p
        for dx, dy in DIRECTIONS:
            nx, ny = x + dx, y + dy
            found = False
            while 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and board[ny][nx] == opp:
                nx += dx; ny += dy; found = True
            if found and 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and board[ny][nx] == p: return True
        return False

    def cpu_move(self):
        moves = [(x, y) for y in range(BOARD_SIZE) for x in range(BOARD_SIZE) if self.get_flips(x, y, 2)]
        if not moves: self.change_turn(); return
        depth = 1 if self.difficulty == 1 else 3 if self.difficulty == 2 else 5
        best = -math.inf; best_move = moves[0]
        for mx, my in moves:
            b = copy.deepcopy(self.grids); self.apply_move_logic(b, mx, my, 2)
            score = self.minimax(b, depth, 1, -math.inf, math.inf)
            if score > best: best = score; best_move = (mx, my)
        self.apply_move_logic(self.grids, best_move[0], best_move[1], 2)
        pyxel.play(3, 0); self.check_attack_chance_trigger()

    def check_attack_chance_trigger(self):
        empty_count = sum(row.count(0) for row in self.grids)
        if self.attack_chance_available and empty_count <= 8:
            self.scene = "ATTACK_CHANCE"; self.attack_chance_available = False
            pyxel.play(3, 2)
            if self.turn == 2: self.wait_timer = 20
        else: self.change_turn()

    def cpu_attack(self):
        targets = [(x, y) for y in range(BOARD_SIZE) for x in range(BOARD_SIZE) if self.grids[y][x] == 1]
        if targets:
            tx, ty = random.choice(targets); self.grids[ty][tx] = 0; pyxel.play(3, 1)
        self.scene = "GAME"; self.change_turn()

    def change_turn(self):
        next_turn = 3 - self.turn
        can_next = any(len(self.get_flips(x,y,next_turn))>0 for y in range(BOARD_SIZE) for x in range(BOARD_SIZE))
        if can_next:
            self.turn = next_turn
            if self.turn == 2: self.wait_timer = 20
        else:
            can_me = any(len(self.get_flips(x,y,self.turn))>0 for y in range(BOARD_SIZE) for x in range(BOARD_SIZE))
            if not can_me: self.check_game_over()
            else: self.pass_timer = 30

    def check_game_over(self):
        p1 = sum(row.count(1) for row in self.grids); cpu = sum(row.count(2) for row in self.grids)
        self.status = 1 if p1 > cpu else 2 if cpu > p1 else 3
        self.scene = "RESULT_START"
        self.transition_timer = 90
        pyxel.stop(); pyxel.playm(2 if self.status == 1 else 3, loop=False)
        if self.status == 1: self.call_js("showWinBG")
        elif self.status == 2: self.call_js("showLoseBG")

    def update(self):
        if self.pass_timer > 0: self.pass_timer -= 1
        if pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_UP): self.cursor_y = max(0, self.cursor_y - 1)
        if pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN): self.cursor_y = min(BOARD_SIZE - 1, self.cursor_y + 1)
        if pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT): self.cursor_x = max(0, self.cursor_x - 1)
        if pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT): self.cursor_x = min(BOARD_SIZE - 1, self.cursor_x + 1)
        
        # タイトル待機フェーズ
        if self.scene == "TITLE_WAIT":
            self.title_wait_timer -= 1
            if self.title_wait_timer <= 0:
                self.scene = "TITLE_MENU"
        
        # タイトルメニューフェーズ
        elif self.scene == "TITLE_MENU":
            if pyxel.btnp(pyxel.KEY_1): self.start_game(1, 1)
            elif pyxel.btnp(pyxel.KEY_2): self.start_game(2, 4)
            elif pyxel.btnp(pyxel.KEY_3): self.start_game(3, 5)
            elif self.is_decision_pressed(): self.start_game(2, 4)

        elif self.scene == "GAME":
            if self.turn == 1 and self.is_decision_pressed():
                mx, my = (pyxel.mouse_x // CELL_SIZE, pyxel.mouse_y // CELL_SIZE) if pyxel.mouse_x >= 0 else (self.cursor_x, self.cursor_y)
                if 0 <= mx < BOARD_SIZE and 0 <= my < BOARD_SIZE and self.get_flips(mx, my, 1):
                    self.apply_move_logic(self.grids, mx, my, 1); pyxel.play(3, 0); self.check_attack_chance_trigger()
            elif self.turn == 2:
                if self.wait_timer > 0: self.wait_timer -= 1
                else: self.cpu_move()
        elif self.scene == "ATTACK_CHANCE":
            if self.turn == 1 and self.is_decision_pressed():
                mx, my = (pyxel.mouse_x // CELL_SIZE, pyxel.mouse_y // CELL_SIZE) if pyxel.mouse_x >= 0 else (self.cursor_x, self.cursor_y)
                if 0 <= mx < BOARD_SIZE and 0 <= my < BOARD_SIZE and self.grids[my][mx] == 2:
                    self.grids[my][mx] = 0; pyxel.play(3, 1); self.scene = "GAME"; self.change_turn()
            elif self.turn == 2:
                if self.wait_timer > 0: self.wait_timer -= 1
                else: self.cpu_attack()
        elif self.scene == "RESULT_START":
            self.transition_timer -= 1
            if self.transition_timer <= 0:
                self.reset_game()

    def draw(self):
        # 起動直後の数フレームは描画をスキップ
        if pyxel.frame_count < 10: return

        # タイトル画面（WAITまたはMENU）の時は画面をクリアしない（背景を表示させるため）
        if self.scene != "TITLE_WAIT" and self.scene != "TITLE_MENU":
            pyxel.cls(0)
        
        # タイトルメニューの時だけ文字を描画
        if self.scene == "TITLE_MENU":
            pyxel.text(5, 18, "LV1 (Press 1)", 11)
            pyxel.text(5, 26, "LV2 (Press 2)", 10)
            pyxel.text(5, 34, "LV3 (Press 3)", 8)
            
        elif self.scene == "GAME" or self.scene == "ATTACK_CHANCE" or self.scene == "RESULT_START":
            for i in range(BOARD_SIZE + 1):
                pyxel.line(i * CELL_SIZE, 0, i * CELL_SIZE, BOARD_SIZE * CELL_SIZE, 1)
                pyxel.line(0, i * CELL_SIZE, BOARD_SIZE * CELL_SIZE, i * CELL_SIZE, 1)
            for y in range(BOARD_SIZE):
                for x in range(BOARD_SIZE):
                    if self.grids[y][x]:
                        u, v = CHARACTER_LIST[self.grids[y][x] - 1]
                        pyxel.blt(x * CELL_SIZE + 1, y * CELL_SIZE + 1, 0, u, v, 8, 8, 0)
            if self.turn == 1: pyxel.rectb(self.cursor_x * CELL_SIZE, self.cursor_y * CELL_SIZE, CELL_SIZE + 1, CELL_SIZE + 1, 11)
            
            if self.scene == "RESULT_START":
                if self.status == 3:
                    pyxel.circ(23, 23, 8, 7); pyxel.line(19, 20, 21, 22, 0); pyxel.line(25, 20, 27, 22, 0); pyxel.line(20, 27, 26, 27, 0)
                    c = 7 if pyxel.frame_count % 10 < 5 else 0
                    pyxel.text(10, 35, "DRAW!", c)
            else:
                p1 = sum(row.count(1) for row in self.grids); cpu = sum(row.count(2) for row in self.grids)
                y_pos = SCREEN_SIZE + 2
                pyxel.text(2, y_pos, f"YOU:{p1}", 11)
                pyxel.text(25, y_pos, f"CPU:{cpu}", 10)
                if self.pass_timer > 0: pyxel.rect(5, 15, 35, 10, 0); pyxel.rectb(5, 15, 35, 10, 7); pyxel.text(12, 18, "PASS", 7)
                if self.scene == "ATTACK_CHANCE":
                    c = 10 if pyxel.frame_count % 10 < 5 else 7
                    pyxel.rectb(0, 0, SCREEN_SIZE, SCREEN_SIZE, c); pyxel.text(2, 20, "ATTACK!", 10)

Othello25()
