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
        
        # 25マスの盤面 (横5×縦5)
        # 0: 空白, 1: プレイヤー(緑), 2: AI(赤)
        self.board = [0] * 25
        self.turn = 1          
        self.ai_delay = 0      
        
        # アタックチャンス管理
        self.attack_chance_used = False
        
        # エフェクト管理用
        self.flip_effects = []
        self.effect_timer = 0
        
        # パネル配置計算 (5x5)
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
        """指定マスに置いた時にひっくり返せるマスのリストを取得"""
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
        """【アタック25ルール】優先順位に基づいた配置可能マスの取得"""
        sandwich_moves = []
        adjacent_moves = []
        empty_moves = []
        
        for i in range(25):
            if self.board[i] != 0:
                continue
                
            empty_moves.append(i)
            
            # ① はさめる場所
            flips = self.get_flippable_cells(i, color)
            if flips:
                sandwich_moves.append(i)
            else:
                # ② 自分のパネルに隣接する場所
                row, col = i // 5, i % 5
                is_adj = False
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if dr == 0 and dc == 0: continue
                        nr, nc = row + dr, col + dc
                        if 0 <= nr < 5 and 0 <= nc < 5:
                            if self.board[nr * 5 + nc] == color:
                                is_adj = True
                if is_adj:
                    adjacent_moves.append(i)
                    
        # 優先順位に従って返す
        if sandwich_moves:
            return sandwich_moves
        if adjacent_moves:
            return adjacent_moves
        return empty_moves

    def check_winner(self):
        """盤面が埋まったら、枚数で勝敗を判定"""
        if 0 not in self.board:
            p1_count = self.board.count(1)
            p2_count = self.board.count(2)
            if p1_count > p2_count: return 1
            elif p2_count > p1_count: return 2
            else: return -1 # 引き分け
        return 0 # ゲーム継続

    def get_ai_move(self):
        valid_moves = self.get_valid_moves(2)
        if not valid_moves: return None

        if self.level == 1:
            return random.choice(valid_moves)

        # レベル2 & 3: 獲得枚数を最大化する手を優先
        best_move = None
        max_flips = -1

        for idx in valid_moves:
            flips = self.get_flippable_cells(idx, 2)
            if len(flips) > max_flips:
                max_flips = len(flips)
                best_move = idx

        # レベル2はたまにランダムにミスをする
        if self.level == 2 and random.random() < 0.3:
            return random.choice(valid_moves)

        return best_move if best_move is not None else random.choice(valid_moves)

    def get_ai_attack_chance_target(self):
        """アタックチャンス時のAIの標的選択"""
        opp_panels = [i for i, v in enumerate(self.board) if v == 1]
        return random.choice(opp_panels) if opp_panels else None

    def make_move(self, idx, color):
        """パネルを配置し、ひっくり返す"""
        flips = self.get_flippable_cells(idx, color)
        self.board[idx] = color
        for f in flips:
            self.board[f] = color
            
        if flips:
            self.flip_effects = flips[:]
            self.effect_timer = 10 
            
        self.process_turn_end(color)

    def process_turn_end(self, current_player):
        # アタックチャンス発動判定（残り5マスになった瞬間）
        if self.board.count(0) == 5 and not self.attack_chance_used:
            # 相手のパネルが1枚でもあれば発動
            opp_color = 3 - current_player
            if opp_color in self.board:
                self.state = "ATTACK_CHANCE"
                self.attack_chance_used = True
                self.ai_delay = 0
                return # ターンは変えずにアタックチャンス状態へ移行

        result = self.check_winner()
        if result == 1:
            self.state = "WIN"; js.showWin()
        elif result == 2 or result == -1:
            self.state = "LOSE"; js.showLose()
        else:
            self.turn = 3 - current_player
            self.ai_delay = 0

    def start_playing(self):
        self.reset_game()
        js.showGame()

    def update(self):
        mx, my = pyxel.mouse_x, pyxel.mouse_y

        if self.effect_timer > 0:
            self.effect_timer -= 1
            if self.effect_timer == 0:
                self.flip_effects = []
            return

        if self.state == "TITLE":
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                if 20 <= mx <= 50 and 85 <= my <= 100: self.level = 1; self.start_playing()
                elif 65 <= mx <= 95 and 85 <= my <= 100: self.level = 2; self.start_playing()
                elif 110 <= mx <= 140 and 85 <= my <= 100: self.level = 3; self.start_playing()

        elif self.state == "PLAYING":
            if self.turn == 1:
                if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                    col = (mx - self.start_x) // (self.p_width + self.p_gap)
                    row = (my - self.start_y) // (self.p_height + self.p_gap)
                    if 0 <= col < 5 and 0 <= row < 5:
                        idx = row * 5 + col
                        if idx in self.get_valid_moves(1):
                            self.make_move(idx, 1)

            elif self.turn == 2:
                self.ai_delay += 1
                if self.ai_delay > 20:
                    idx = self.get_ai_move()
                    if idx is not None:
                        self.make_move(idx, 2)

        elif self.state == "ATTACK_CHANCE":
            # アタックチャンス処理（相手のパネルを自分の色に塗り替える）
            opp_color = 3 - self.turn
            
            if self.turn == 1: # プレイヤーの選択
                if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                    col = (mx - self.start_x) // (self.p_width + self.p_gap)
                    row = (my - self.start_y) // (self.p_height + self.p_gap)
                    if 0 <= col < 5 and 0 <= row < 5:
                        idx = row * 5 + col
                        if self.board[idx] == opp_color:
                            self.board[idx] = 1 # 自分の色に！
                            self.flip_effects = [idx]
                            self.effect_timer = 10
                            self.state = "PLAYING" # 引き続き自分のターン

            elif self.turn == 2: # AIの選択
                self.ai_delay += 1
                if self.ai_delay > 30:
                    idx = self.get_ai_attack_chance_target()
                    if idx is not None:
                        self.board[idx] = 2
                        self.flip_effects = [idx]
                        self.effect_timer = 10
                    self.state = "PLAYING"

        elif self.state in ["WIN", "LOSE"]:
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) or pyxel.btnp(pyxel.KEY_SPACE):
                self.state = "TITLE"
                js.showTitle()

    def draw(self):
        pyxel.cls(0)

        if self.state == "TITLE":
            pyxel.text(48, 70, "SELECT DIFFICULTY", 7)
            pyxel.rect(20, 85, 30, 15, 5); pyxel.text(28, 90, "LV 1", 7)
            pyxel.rect(65, 85, 30, 15, 6); pyxel.text(73, 90, "LV 2", 7)
            pyxel.rect(110, 85, 30, 15, 8); pyxel.text(118, 90, "LV 3", 7)

        elif self.state in ["PLAYING", "ATTACK_CHANCE"]:
            pyxel.text(6, 6, f"LV {self.level}", 7)
            
            # スコア（枚数）表示
            p1_c = self.board.count(1)
            p2_c = self.board.count(2)
            pyxel.text(6, 16, f"P1: {p1_c}", 11)
            pyxel.text(6, 26, f"AI: {p2_c}", 8)

            if self.state == "ATTACK_CHANCE":
                if self.effect_timer % 4 < 2: # 点滅
                    pyxel.text(90, 6, "ATTACK CHANCE!", 10)
                msg = "STEAL AI PANEL!" if self.turn == 1 else "AI STEALING..."
                pyxel.text(90, 16, msg, 7)
            else:
                if self.turn == 1: pyxel.text(114, 6, "YOUR TURN", 11)
                else: pyxel.text(114, 6, "AI THINKING", 8)

            valid_moves = self.get_valid_moves(1) if self.turn == 1 else []

            # 25マスのパネル描画
            for i in range(25):
                row = i // 5
                col = i % 5
                px = self.start_x + col * (self.p_width + self.p_gap)
                py = self.start_y + row * (self.p_height + self.p_gap)
                
                # アタックチャンス中は相手のパネルをハイライト
                is_ac_target = (self.state == "ATTACK_CHANCE" and self.turn == 1 and self.board[i] == 2)
                selectable = (i in valid_moves and self.state == "PLAYING") or is_ac_target
                
                if self.board[i] == 0:
                    pyxel.rect(px, py, self.p_width, self.p_height, 13)
                    border_color = 7 if selectable else 5
                    pyxel.rectb(px, py, self.p_width, self.p_height, border_color)
                elif self.board[i] == 1:
                    pyxel.rect(px, py, self.p_width, self.p_height, 11)
                    pyxel.rectb(px, py, self.p_width, self.p_height, 7)
                elif self.board[i] == 2:
                    pyxel.rect(px, py, self.p_width, self.p_height, 8)
                    border_color = 10 if is_ac_target else 7
                    pyxel.rectb(px, py, self.p_width, self.p_height, border_color)

            if self.effect_timer > 0 and self.effect_timer % 2 == 0:
                for f in self.flip_effects:
                    frow = f // 5
                    fcol = f % 5
                    fpx = self.start_x + fcol * (self.p_width + self.p_gap)
                    fpy = self.start_y + frow * (self.p_height + self.p_gap)
                    pyxel.rect(fpx, fpy, self.p_width, self.p_height, 7)

        elif self.state in ["WIN", "LOSE"]:
            result_text = "YOU WIN!" if self.state == "WIN" else ("DRAW!" if self.board.count(1) == self.board.count(2) else "YOU LOSE...")
            color = 11 if self.state == "WIN" else (7 if result_text == "DRAW!" else 8)
            pyxel.text(60, 50, result_text, color)
            pyxel.text(42, 105, "CLICK TO RETURN TITLE", 7)

# ゲーム起動
Attack25Game()
