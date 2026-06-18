import pyxel
import random

try:
    import js
except:
    js = None

CELL_SIZE = 9
BOARD_SIZE = 5
SCREEN_SIZE = CELL_SIZE * BOARD_SIZE + 1
DIRECTIONS = [(-1,-1), (0,-1), (1,-1), (-1,0), (1,0), (-1,1), (0,1), (1,1)]
CHARACTER_LIST = [(0, 128), (0, 136)]

class Othello25:
    def __init__(self):
        pyxel.init(SCREEN_SIZE, SCREEN_SIZE, title="ATTACK 3MOKU")
        pyxel.load("KAIYOU.pyxres")
        self.init_sound()
        pyxel.mouse(True)
        self.reset_game()
        pyxel.run(self.update, self.draw)

    def init_sound(self):
        pyxel.sound(0).set("e1e1", "n", "7", "f", 5)
        pyxel.sound(1).set("g2g2 c3", "p", "7", "v", 10)
        pyxel.sound(2).set("c3e3g3 c4 e3g3c4 e4", "p", "6", "v", 15)
        pyxel.sound(3).set("c2g1c1", "n", "6", "f", 20)
        pyxel.sound(6).set("c3e3g3 c4 r c4", "p", "7", "v", 10)
        pyxel.sound(4).set("c3 c3 g2 g2 c3 c3 e3 d3", "p", "5", "v", 20)
        pyxel.sound(5).set("c2 r c2 r g1 r g1 r", "s", "4", "v", 20)
        pyxel.music(0).set([4], [5], [], [])

    def reset_game(self):
        self.grids = [[0] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.grids[1][1] = 2; self.grids[2][2] = 2
        self.grids[1][2] = 1; self.grids[2][1] = 1
        self.turn = 1; self.status = 0; self.wait_timer = 0
        self.pass_timer = 0; self.attack_chance_available = True
        self.scene = "TITLE_START"
        self.transition_timer = 150
        pyxel.stop()
        if js:
            try: js.showTitleBG()
            except: pass

    def get_flips(self, x, y, player_turn):
        if self.grids[y][x] != 0: return []
        flips = []
        opponent = 3 - player_turn
        for dx, dy in DIRECTIONS:
            nx, ny = x + dx, y + dy
            temp = []
            while 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and self.grids[ny][nx] == opponent:
                temp.append((nx, ny)); nx += dx; ny += dy
            if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and self.grids[ny][nx] == player_turn:
                flips.extend(temp)
        return flips

    def cpu_move(self):
        valid_moves = []
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                flips = self.get_flips(x, y, 2)
                if flips:
                    score = self.evaluate_move(x, y, len(flips))
                    valid_moves.append((x, y, flips, score))
        if not valid_moves: self.change_turn(); return
        valid_moves.sort(key=lambda x: x[3], reverse=True)
        move = random.choice(valid_moves) if self.difficulty == 1 else (random.choice(valid_moves[:2]) if self.difficulty == 2 else valid_moves[0])
        bx, by, bflips, _ = move
        self.grids[by][bx] = 2
        for fx, fy in bflips: self.grids[fy][fx] = 2
        pyxel.play(3, 0)
        self.check_attack_chance_trigger()

    def evaluate_move(self, x, y, flips_count):
        score = flips_count
        if (x, y) in [(0,0), (0,4), (4,0), (4,4)]: return 1000
        if (x, y) in [(1,1), (0,1), (1,0), (3,0), (4,1), (3,1), (0,3), (1,4), (1,3), (4,3), (3,4), (3,3)]:
            score -= 20
        return score

    def check_attack_chance_trigger(self):
        empty_count = sum(row.count(0) for row in self.grids)
        if self.attack_chance_available and empty_count <= 8:
            self.scene = "ATTACK_CHANCE"
            self.attack_chance_available = False
            pyxel.play(3, 6)
            if self.turn == 2: self.wait_timer = 20
        else: self.change_turn()

    def cpu_attack(self):
        targets = [(x, y) for y in range(BOARD_SIZE) for x in range(BOARD_SIZE) if self.grids[y][x] == 1]
        if targets:
            tx, ty = random.choice(targets)
            self.grids[ty][tx] = 0
            pyxel.play(3, 1)
        self.scene = "GAME"
        self.change_turn()

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
        p1 = sum(row.count(1) for row in self.grids)
        cpu = sum(row.count(2) for row in self.grids)
        self.status = 1 if p1 > cpu else (2 if cpu > p1 else 3)
        self.scene = "RESULT_START"
        self.transition_timer = 150
        if js:
            try:
                if self.status == 1: js.showWinBG()
                elif self.status == 2: js.showLoseBG()
            except: pass
        pyxel.stop()
        pyxel.play(3, 2 if self.status == 1 else 3)

    def update(self):
        if self.pass_timer > 0: self.pass_timer -= 1
        if self.scene == "TITLE_START":
            self.transition_timer -= 1
            if self.transition_timer <= 0:
                self.scene = "TITLE"
                if js:
                    try: js.clearBG()
                    except: pass
            return
        elif self.scene == "RESULT_START":
            self.transition_timer -= 1
            if self.transition_timer <= 0: self.reset_game()
            return
        if self.scene == "TITLE":
            if pyxel.btnp(pyxel.KEY_1) or pyxel.btnp(pyxel.KEY_2) or pyxel.btnp(pyxel.KEY_3) or pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.scene = "GAME"
                if js:
                    try: js.clearBG()
                    except: pass
                pyxel.playm(0, loop=True)
        elif self.scene == "GAME":
            if self.turn == 1 and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                mx, my = pyxel.mouse_x // CELL_SIZE, pyxel.mouse_y // CELL_SIZE
                if 0 <= mx < BOARD_SIZE and 0 <= my < BOARD_SIZE:
                    flips = self.get_flips(mx, my, 1)
                    if flips:
                        self.grids[my][mx] = 1
                        for fx, fy in flips: self.grids[fy][fx] = 1
                        pyxel.play(3, 0)
                        self.check_attack_chance_trigger()
            elif self.turn == 2:
                if self.wait_timer > 0: self.wait_timer -= 1
                else: self.cpu_move()
        elif self.scene == "ATTACK_CHANCE":
            if self.turn == 1:
                if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                    mx, my = pyxel.mouse_x // CELL_SIZE, pyxel.mouse_y // CELL_SIZE
                    if 0 <= mx < BOARD_SIZE and 0 <= my < BOARD_SIZE and self.grids[my][mx] == 2:
                        self.grids[my][mx] = 0
                        pyxel.play(3, 1)
                        self.scene = "GAME"
                        self.change_turn()
            elif self.turn == 2:
                if self.wait_timer > 0: self.wait_timer -= 1
                else: self.cpu_attack()

    def draw(self):
        pyxel.cls(0)
        if self.scene in ["TITLE_START", "RESULT_START"]: return
        if self.scene == "TITLE":
            pyxel.text(2, 5, "ATTACK 3MOKU", pyxel.frame_count % 16)
            return
        for i in range(BOARD_SIZE + 1):
            pyxel.line(i * CELL_SIZE, 0, i * CELL_SIZE, BOARD_SIZE * CELL_SIZE, 1)
            pyxel.line(0, i * CELL_SIZE, BOARD_SIZE * CELL_SIZE, i * CELL_SIZE, 1)
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                if self.grids[y][x]:
                    u, v = CHARACTER_LIST[self.grids[y][x] - 1]
                    pyxel.blt(x * CELL_SIZE + 1, y * CELL_SIZE + 1, 0, u, v, 8, 8, 0)
        pyxel.text(2, SCREEN_SIZE - 8, "YOU" if self.turn == 1 else "CPU", 7)
        if self.pass_timer > 0:
            pyxel.rect(5, 15, 35, 10, 0); pyxel.rectb(5, 15, 35, 10, 7); pyxel.text(12, 18, "PASS", 7)
        if self.scene == "ATTACK_CHANCE":
            c = 10 if pyxel.frame_count % 10 < 5 else 7
            pyxel.rectb(0, 0, SCREEN_SIZE, SCREEN_SIZE, c)
            pyxel.text(2, 20, "ATTACK!", 10)

Othello25()
