import pyxel
import random

# Web環境（Pyodide）のJavaScript環境を安全にインポート
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
        pyxel.init(160, 120, title="PANEL ATTACK 25")
        pyxel.mouse(True)
        
        self.state = "TITLE"
        self.level = 1
        
        self.board = [0] * 25
        self.turn = 1          
        self.ai_delay = 0      
        
        self.attack_chance_used = False
        self.flip_effects = []
        self.effect_timer = 0
        
        self.p_width = 16
        self.p_height = 16
        self.p_gap = 2
        total_w = 5 * (self.p_width + self.p_gap) - self.p_gap
        total_h = 5 * (self.p_height + self.p_gap) - self.p_gap
        self.start_x = (160 - total_w) // 2
        self.start_y = (120 - total_h) // 2 + 6
        
        js.showTitle()
        pyxel.run(self.update, self.draw)

    def reset_game(self):
        self.board = [0] * 25
        self.turn = 1
        self.ai_delay = 0
        self.attack_chance_used = False
        self.flip_effects = []
        self.effect_timer = 0
        self.state = "PLAYING"

    def get_flippable_cells(self, idx, color):
        flippable = []
        row, col = idx // 5, idx % 5
        opp_color = 3 - color 
        dirs = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
        for dr, dc in dirs:
            r, c = row + dr, col + dc
            temp = []
            while 0 <= r < 5 and 0 <= c < 5 and self.board[r * 5 + c] == opp_color:
                temp.append(r * 5 + c)
                r += dr
                c += dc
            if 0 <= r < 5 and 0 <= c < 5 and self.board[r * 5 + c] == color:
                flippable.extend(temp)
        return flippable

    def get_valid_moves(self, color):
        sandwich_moves, adjacent_moves, empty_moves = [], [], []
        for i in range(25):
            if self.board[i] != 0: continue
            empty_moves.append(i)
            flips = self.get_flippable_cells(i, color)
            if flips: sandwich_moves.append(i)
            else:
                row, col = i // 5, i % 5
                is_adj = False
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if dr == 0 and dc == 0: continue
                        nr, nc = row + dr, col + dc
                        if 0 <= nr < 5 and 0 <= nc < 5 and self.board[nr * 5 + nc] == color:
                            is_adj = True
                if is_adj: adjacent_moves.append(i)
        if sandwich_moves: return sandwich_moves
        if adjacent_moves: return adjacent_moves
        return empty_moves

    def check_winner(self):
        if 0 not in self.board:
            p1, p2 = self.board.count(1), self.board.count(2)
            if p1 > p2: return 1
            elif p2 > p1: return 2
            else: return -1
        return 0

    def get_ai_move(self):
        valid_moves = self.get_valid_moves(2)
        if not valid_moves: return None
        if self.level == 1: return random.choice(valid_moves)
        best_move, max_flips = None, -1
        for idx in valid_moves:
            flips = self.get_flippable_cells(idx, 2)
            if len(flips) > max_flips:
                max_flips = len(flips)
                best_move = idx
        if self.level == 2 and random.random() < 0.3: return random.choice(valid_moves)
        return best_move if best_move is not None else random.choice(valid_moves)

    def get_ai_attack_chance_target(self):
        opp_panels = [i for i, v in enumerate(self.board) if v == 1]
        return random.choice(opp_panels) if opp_panels else None

    def make_move(self, idx, color):
        flips = self.get_flippable_cells(idx, color)
        self.board[idx] = color
        for f in flips: self.board[f] = color
        if flips:
            self.flip_effects = flips[:]
            self.effect_timer = 10 
        self.process_turn_end(color)

    def process_turn_end(self, current_player):
        if self.board.count(0) == 5 and not self.attack_chance_used:
            if (3 - current_player) in self.board:
                self.state = "ATTACK_CHANCE"
                self.attack_chance_used = True
                self.ai_delay = 0
                return
        result = self.check_winner()
        if result == 1: self.state = "WIN"; js.showWin()
        elif result == 2 or result == -1: self.state = "LOSE"; js.showLose()
        else: self.turn = 3 - current_player; self.ai_delay = 0

    def start_playing(self):
        self.board = [0] * 25
        self.turn = 1
        self.ai_delay = 0
        self.attack_chance_used = False
        self.state = "PLAYING"
        js.showGame()

    def update(self):
        mx, my = pyxel.mouse_x, pyxel.mouse_y
        if self.effect_timer > 0:
            self.effect_timer -= 1
            if self.effect_timer == 0: self.flip_effects = []
            return

        if self.state == "TITLE":
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                if 20 <= mx <= 50 and 85 <= my <= 100: self.level = 1; self.start_playing()
                elif 65 <= mx <= 95 and 85 <= my <= 100: self.level = 2; self.start_playing()
                elif 110 <= mx <= 140 and 85 <= my <= 100: self.level = 3; self.start_playing()
        elif self.state == "PLAYING":
            if self.turn == 1:
                if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                    c, r = (mx - self.start_x)//18, (my - self.start_y)//18
                    if 0 <= c < 5 and 0 <= r < 5:
                        idx = r * 5 + c
                        if idx in self.get_valid_moves(1): self.make_move(idx, 1)
            elif self.turn == 2:
                self.ai_delay += 1
                if self.ai_delay > 20:
                    idx = self.get_ai_move()
                    if idx is not None: self.make_move(idx, 2)
        elif self.state == "ATTACK_CHANCE":
            opp = 3 - self.turn
            if self.turn == 1:
                if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                    c, r = (mx - self.start_x)//18, (my - self.start_y)//18
                    if 0 <= c < 5 and 0 <= r < 5:
                        idx = r * 5 + c
                        if self.board[idx] == opp:
                            self.board[idx] = 1
                            self.effect_timer = 10
                            self.state = "PLAYING"
            elif self.turn == 2:
                self.ai_delay += 1
                if self.ai_delay > 30:
                    idx = self.get_ai_attack_chance_target()
                    if idx is not None: self.board[idx] = 2
                    self.state = "PLAYING"
        elif self.state in ["WIN", "LOSE"]:
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) or pyxel.btnp(pyxel.KEY_SPACE):
                self.state = "TITLE"
                js.showTitle()

    def draw(self):
        if self.state in ["TITLE", "WIN", "LOSE"]: return
        pyxel.cls(0)
        p1, p2 = self.board.count(1), self.board.count(2)
        pyxel.text(6, 6, f"LV {self.level} | P1:{p1} AI:{p2}", 7)
        if self.state == "ATTACK_CHANCE": pyxel.text(90, 6, "ATTACK CHANCE!", 10)
        for i in range(25):
            r, c = i // 5, i % 5
            x, y = self.start_x + c * 18, self.start_y + r * 18
            color = 13 if self.board[i]==0 else (11 if self.board[i]==1 else 8)
            pyxel.rect(x, y, 16, 16, color)
            pyxel.rectb(x, y, 16, 16, 7)
        if self.effect_timer > 0:
            for f in self.flip_effects:
                pyxel.rect(self.start_x + (f%5)*18, self.start_y + (f//5)*18, 16, 16, 7)

Attack25Game()
