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
        pyxel.init(SCREEN_SIZE, SCREEN_SIZE, title="ATTACK3MOKU")
        try:
            pyxel.load("KAIYOU.pyxres")
        except:
            pass
        self.init_sound()
        pyxel.mouse(True)
        self.reset_game()
        pyxel.run(self.update, self.draw)

    def init_sound(self):
        # --- 効果音 (SE) ---
        pyxel.sound(0).set("e2e2", "n", "7", "f", 5) # ピースを置く音
        pyxel.sound(1).set("g3g3 c4", "p", "7", "v", 10) # アタック音
        # エラー回避のため c5 を c4 に修正
        pyxel.sound(2).set("c4e4g4 c4 r c4", "p", "7", "v", 10) # アタックチャンス発動音

        # --- BGM 0: タイトル画面 ---
        pyxel.sound(10).set("c3 e3 g3 c4  e3 g3 c4 e4", "t", "4", "n", 25)
        pyxel.sound(11).set("c2 g2 c2 g2  c2 g2 c2 g2", "s", "4", "n", 25)
        pyxel.music(0).set([10], [11], [], [])

        # --- BGM 1: ゲームプレイ画面 (LV1用) ---
        pyxel.sound(12).set("a2 c3 e3 a3  g2 b2 d3 g3", "t", "5", "n", 25)
        pyxel.sound(13).set("a1 e2 a1 e2  g1 d2 g1 d2", "p", "5", "n", 25)
        pyxel.music(1).set([12], [13], [], [])

        # --- BGM 4: ゲームプレイ画面 (LV2用) --- 追加
        pyxel.sound(16).set("c3 e3 g3 c4 g3 e3 c3 e3", "t", "5", "n", 20)
        pyxel.sound(17).set("c2 g2 c2 g2 c2 g2 c2 g2", "p", "5", "n", 20)
        pyxel.music(4).set([16], [17], [], [])

        # --- BGM 5: ゲームプレイ画面 (LV3用) --- 追加
        pyxel.sound(18).set("e3 e3 g3 e3 a3 g3 e3 d3", "t", "6", "n", 15)
        pyxel.sound(19).set("e2 e2 e2 e2 e2 e2 e2 e2", "n", "5", "f", 15)
        pyxel.music(5).set([18], [19], [], [])

        # --- BGM 2: YOU WIN (勝利) ---
        # エラー回避のため c5 を c4 に修正
        pyxel.sound(14).set("c3 e3 g3 c4 e4 c4 e4 g4 c4 r r r", "p", "6", "n", 25)
        pyxel.music(2).set([14], [], [], [])

        # --- BGM 3: YOU LOSE / DRAW (敗北・引き分け) ---
        pyxel.sound(15).set("c3 g2 d#2 c2 g1 d#1 c1 r r r", "s", "6", "f", 25)
        pyxel.music(3).set([15], [], [], [])

    def reset_game(self):
        self.grids = [[0] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.grids[1][1] = 2; self.grids[2][2] = 2
        self.grids[1][2] = 1; self.grids[2][1] = 1
        self.turn = 1; self.status = 0; self.wait_timer = 0
        self.pass_timer = 0; self.attack_chance_available = True
        self.difficulty = 2
        self.scene = "TITLE_START"
        self.transition_timer = 90
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
        pyxel.play(3, 0) # CPUが駒を置いたときの音
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
            pyxel.play(3, 2)
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
        self.transition_timer = 90
        
        # HTML（JS）側への通知
        if js:
            try:
                if self.status == 1: js.showWinBG()
                elif self.status == 2: js.showLoseBG()
            except: pass
        
        # BGMを切り替え（1=WIN: music(2), 2=LOSE/3=DRAW: music(3)）
        pyxel.stop()
        pyxel.playm(2 if self.status == 1 else 3, loop=False)

    def update(self):
        if self.pass_timer > 0: self.pass_timer -= 1
        
        if self.scene == "TITLE_START" or self.scene == "RESULT_START":
            self.transition_timer -= 1
            if self.transition_timer <= 0:
                if self.scene == "TITLE_START":
                    self.scene = "TITLE"
                    # タイトルBGM再生
                    pyxel.playm(0, loop=True)
                else:
                    self.reset_game()
                if js:
                    try: js.clearBG()
                    except: pass
            return
            
        if self.scene == "TITLE":
            if pyxel.btnp(pyxel.KEY_1) or pyxel.btnp(pyxel.KEY_2) or pyxel.btnp(pyxel.KEY_3):
                self.difficulty = 1 if pyxel.btnp(pyxel.KEY_1) else (2 if pyxel.btnp(pyxel.KEY_2) else 3)
                self.scene = "GAME"
                
                # 難易度に合わせてBGMを出し分け
                bgm = 1 if self.difficulty == 1 else (4 if self.difficulty == 2 else 5)
                pyxel.playm(bgm, loop=True)
                
            elif pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.difficulty = 2
                self.scene = "GAME"
                # マウスクリック時はデフォルトLV2のBGM
                pyxel.playm(4, loop=True)
                
        elif self.scene == "GAME":
            if self.turn == 1 and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                mx, my = pyxel.mouse_x // CELL_SIZE, pyxel.mouse_y // CELL_SIZE
                if 0 <= mx < BOARD_SIZE and 0 <= my < BOARD_SIZE:
                    flips = self.get_flips(mx, my, 1)
                    if flips:
                        self.grids[my][mx] = 1
                        for fx, fy in flips: self.grids[fy][fx] = 1
                        pyxel.play(3, 0) # プレイヤーが駒を置いたときの音
                        self.check_attack_chance_trigger()
            elif self.turn == 2:
                if self.wait_timer > 0: self.wait_timer -= 1
                else: self.cpu_move()
                
        elif self.scene == "ATTACK_CHANCE":
            if self.turn == 1 and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
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
        if self.scene == "TITLE_START": return
        
        # 以前のコードの通り、Pyxelでタイトルを描画
        if self.scene == "TITLE":
            pyxel.text(2, 5, "ATTACK3MOKU", pyxel.frame_count % 16)
            pyxel.text(5, 18, "LV1", 11); pyxel.text(5, 26, "LV2", 10); pyxel.text(5, 34, "LV3", 8)
        else:
            for i in range(BOARD_SIZE + 1):
                pyxel.line(i * CELL_SIZE, 0, i * CELL_SIZE, BOARD_SIZE * CELL_SIZE, 1)
                pyxel.line(0, i * CELL_SIZE, BOARD_SIZE * CELL_SIZE, i * CELL_SIZE, 1)
            for y in range(BOARD_SIZE):
                for x in range(BOARD_SIZE):
                    if self.grids[y][x]:
                        u, v = CHARACTER_LIST[self.grids[y][x] - 1]
                        pyxel.blt(x * CELL_SIZE + 1, y * CELL_SIZE + 1, 0, u, v, 8, 8, 0)
                        
            if self.scene != "RESULT_START":
                pyxel.text(2, SCREEN_SIZE - 8, "YOU BLUE" if self.turn == 1 else "CPU RED", 7)
                if self.pass_timer > 0:
                    pyxel.rect(5, 15, 35, 10, 0); pyxel.rectb(5, 15, 35, 10, 7); pyxel.text(12, 18, "PASS", 7)
                if self.scene == "ATTACK_CHANCE":
                    c = 10 if pyxel.frame_count % 10 < 5 else 7
                    pyxel.rectb(0, 0, SCREEN_SIZE, SCREEN_SIZE, c)
                    pyxel.text(2, 20, "ATTACK!", 10)
            elif self.status == 3:
                # 困った顔の描写（プログラムコードで直接描画）
                pyxel.circ(23, 23, 8, 7)
                pyxel.line(19, 20, 21, 22, 0)
                pyxel.line(25, 20, 27, 22, 0)
                pyxel.line(20, 27, 26, 27, 0)
                # 光るDRAW!の文字
                c = 7 if pyxel.frame_count % 10 < 5 else 0
                pyxel.text(10, 35, "DRAW!", c)

Othello25()
