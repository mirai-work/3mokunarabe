import pyxel
import random

try:
    import js
except ImportError:
    class DummyJS:
        def showTitle(self): pass
        def showGame(self): pass
        def showWin(self): pass
        def showLose(self): pass
    js = DummyJS()

class Attack25Game:
    def __init__(self):
        pyxel.init(160, 120, title="PANEL ATTACK 3MOKU")
        pyxel.mouse(True)
        self.state = "TITLE"
        self.level = 1
        self.board = [0] * 25
        self.turn = 1
        self.ai_delay = 0
        self.attack_chance_used = False
        self.flip_effects = []
        self.effect_timer = 0
        self.p_w, self.p_h, self.p_gap = 16, 16, 2
        total_w = 5 * (self.p_w + self.p_gap) - self.p_gap
        total_h = 5 * (self.p_h + self.p_gap) - self.p_gap
        self.start_x = (160 - total_w) // 2
        self.start_y = (120 - total_h) // 2 + 6
        pyxel.run(self.update, self.draw)

    def reset_game(self):
        self.board = [0] * 25
        self.turn = 1
        self.ai_delay = 0
        self.attack_chance_used = False
        self.flip_effects = []
        self.effect_timer = 0
        self.state = "PLAYING"

    def get_flippable(self, idx, color):
        res, opp = [], 3 - color
        r, c = idx // 5, idx % 5
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0: continue
                tmp, nr, nc = [], r + dr, c + dc
                while 0 <= nr < 5 and 0 <= nc < 5 and self.board[nr * 5 + nc] == opp:
                    tmp.append(nr * 5 + nc); nr += dr; nc += dc
                if 0 <= nr < 5 and 0 <= nc < 5 and self.board[nr * 5 + nc] == color:
                    res.extend(tmp)
        return res

    def get_valid_moves(self, color):
        s, a, e = [], [], []
        for i in range(25):
            if self.board[i] != 0: continue
            e.append(i)
            if self.get_flippable(i, color): s.append(i)
            else:
                r, c = i // 5, i % 5
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < 5 and 0 <= nc < 5 and self.board[nr * 5 + nc] == color:
                            a.append(i); break
        return s if s else (a if a else e)

    def process_turn_end(self, color):
        if self.board.count(0) == 5 and not self.attack_chance_used:
            self.state = "ATTACK_CHANCE"; self.attack_chance_used = True; return
        if 0 not in self.board:
            p1, p2 = self.board.count(1), self.board.count(2)
            self.state = "WIN" if p1 > p2 else "LOSE"
            js.showWin() if self.state == "WIN" else js.showLose()
        else: self.turn = 3 - color; self.ai_delay = 0

    def update(self):
        if self.effect_timer > 0: self.effect_timer -= 1; return
        if self.state == "TITLE":
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT): self.reset_game(); js.showGame()
        elif self.state == "PLAYING":
            if self.turn == 1 and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                c, r = (pyxel.mouse_x - self.start_x) // (self.p_w + self.p_gap), (pyxel.mouse_y - self.start_y) // (self.p_h + self.p_gap)
                if 0 <= c < 5 and 0 <= r < 5:
                    idx = r * 5 + c
                    if idx in self.get_valid_moves(1):
                        self.board[idx] = 1
                        for f in self.get_flippable(idx, 1): self.board[f] = 1
                        self.process_turn_end(1)
            elif self.turn == 2:
                self.ai_delay += 1
                if self.ai_delay > 20:
                    moves = self.get_valid_moves(2)
                    idx = random.choice(moves)
                    self.board[idx] = 2
                    for f in self.get_flippable(idx, 2): self.board[f] = 2
                    self.process_turn_end(2)
        elif self.state == "ATTACK_CHANCE":
            if self.turn == 1 and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                c, r = (pyxel.mouse_x - self.start_x) // (self.p_w + self.p_gap), (pyxel.mouse_y - self.start_y) // (self.p_h + self.p_gap)
                idx = r * 5 + c
                if 0 <= idx < 25 and self.board[idx] == 2: self.board[idx] = 1; self.state = "PLAYING"
            elif self.turn == 2:
                opps = [i for i, v in enumerate(self.board) if v == 1]
                if opps: self.board[random.choice(opps)] = 2
                self.state = "PLAYING"
        elif self.state in ["WIN", "LOSE"]:
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT): self.state = "TITLE"; js.showTitle()

    def draw(self):
        if self.state not in ["PLAYING", "ATTACK_CHANCE"]: return
        pyxel.cls(0)
        pyxel.text(5, 5, f"P1:{self.board.count(1)} AI:{self.board.count(2)}", 7)
        if self.state == "ATTACK_CHANCE": pyxel.text(90, 5, "ATTACK!", 10)
        for i in range(25):
            x = self.start_x + (i % 5) * (self.p_w + self.p_gap)
            y = self.start_y + (i // 5) * (self.p_h + self.p_gap)
            pyxel.rect(x, y, self.p_w, self.p_h, 13 if self.board[i]==0 else (11 if self.board[i]==1 else 8))
            pyxel.rectb(x, y, self.p_w, self.p_h, 7)

Attack25Game()
