import pyxel, random, js

class Attack25Game:
    def __init__(self):
        pyxel.init(160, 120, title="PANEL ATTACK 3MOKU")
        pyxel.mouse(True)
        self.reset_game()
        pyxel.run(self.update, self.draw)

    def reset_game(self):
        # 演出用タイマーと状態管理
        self.state = "TITLE_IMG"
        self.timer = 0
        self.level = 1
        self.board = [0] * 25
        self.turn = 1
        self.ai_delay = 0
        self.start_x, self.start_y = 35, 25

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
                        if 0 <= r+dr < 5 and 0 <= c+dc < 5 and self.board[(r+dr)*5+(c+dc)] == color:
                            a.append(i); break
        return s if s else (a if a else e)

    def update(self):
        self.timer += 1
        
        # 5秒間の画像演出管理 (30fps * 5s = 150フレーム)
        if self.state == "TITLE_IMG" and self.timer >= 150:
            self.state = "TITLE"; js.showTitle()
        elif self.state in ["WIN_IMG", "LOSE_IMG"] and self.timer >= 150:
            self.state = "RESULT"; js.showResult("WIN!" if "WIN" in self.state else "LOSE!")

        # メニュー選択
        if self.state == "TITLE" and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            my = pyxel.mouse_y
            if 60 <= my <= 110:
                self.level = 1 if my < 75 else (2 if my < 90 else 3)
                self.board = [0] * 25
                self.state = "PLAYING"
                js.showGame()
        
        # ゲームプレイ
        elif self.state == "PLAYING":
            if self.turn == 1 and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                c, r = (pyxel.mouse_x - self.start_x) // 18, (pyxel.mouse_y - self.start_y) // 18
                if 0 <= c < 5 and 0 <= r < 5 and (idx := r * 5 + c) in self.get_valid_moves(1):
                    self.board[idx] = 1
                    for f in self.get_flippable(idx, 1): self.board[f] = 1
                    self.process_end(1)
            elif self.turn == 2:
                self.ai_delay += 1
                if self.ai_delay > 20:
                    moves = self.get_valid_moves(2)
                    if moves:
                        if self.level == 1: idx = random.choice(moves)
                        elif self.level == 2: idx = sorted([(len(self.get_flippable(m, 2)), m) for m in moves], reverse=True)[:3][0][1]
                        else: idx = max([(len(self.get_flippable(m, 2)), m) for m in moves])[1]
                        self.board[idx] = 2
                        for f in self.get_flippable(idx, 2): self.board[f] = 2
                        self.process_end(2)
        
        # 結果表示後にクリックでタイトルへ
        elif self.state == "RESULT" and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self.reset_game(); js.showTitle()

    def process_end(self, color):
        if 0 not in self.board:
            p1, p2 = self.board.count(1), self.board.count(2)
            self.state = "WIN_IMG" if p1 > p2 else "LOSE_IMG"
            self.timer = 0
            js.showWin() if self.state == "WIN_IMG" else js.showLose()
        else: self.turn = 3 - color; self.ai_delay = 0

    def draw(self):
        pyxel.cls(0)
        if self.state == "PLAYING":
            for i in range(25):
                x, y = self.start_x + (i % 5) * 18, self.start_y + (i // 5) * 18
                pyxel.rect(x, y, 16, 16, 13 if self.board[i]==0 else (11 if self.board[i]==1 else 8))
                pyxel.rectb(x, y, 16, 16, 7)

Attack25Game()
