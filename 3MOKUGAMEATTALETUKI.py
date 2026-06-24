import pyxel
import random

try:
    import js
except:
    js = None

CELL_SIZE = 9
BOARD_SIZE = 5
# 表示領域を縦に少し拡張しました
SCREEN_SIZE = CELL_SIZE * BOARD_SIZE + 1
VIEW_HEIGHT = SCREEN_SIZE + 10 
DIRECTIONS = [(-1,-1), (0,-1), (1,-1), (-1,0), (1,0), (-1,1), (0,1), (1,1)]
CHARACTER_LIST = [(0, 128), (0, 136)]

class Othello25:
    def __init__(self):
        # 拡張した縦サイズを反映
        pyxel.init(SCREEN_SIZE, VIEW_HEIGHT, title="ATTACK3MOKU")
        try:
            pyxel.load("KAIYOU.pyxres")
        except:
            pass
        self.init_sound()
        pyxel.mouse(True)
        self.reset_game()
        pyxel.run(self.update, self.draw)

    def is_decision_pressed(self):
        # MOUSE, GAMEPAD, KEYBOARD の入力をタプルで同時判定
        match (pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT), pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A), pyxel.btnp(pyxel.KEY_SPACE)):
            case (True, _, _) | (_, True, _) | (_, _, True):
                return True
            case _:
                return False

    def init_sound(self):
        pyxel.sound(0).set("e2e2", "n", "7", "f", 5)
        pyxel.sound(1).set("g3g3 c4", "p", "7", "v", 10)
        pyxel.sound(2).set("c4e4g4 c4 r c4", "p", "7", "v", 10)
        pyxel.sound(10).set("c3 e3 g3 c4  e3 g3 c4 e4", "t", "4", "n", 25)
        pyxel.sound(11).set("c2 g2 c2 g2  c2 g2 c2 g2", "s", "4", "n", 25)
        pyxel.music(0).set([10], [11], [], [])
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
        self.scene = "TITLE_START"
        self.transition_timer = 90
        self.cursor_x = 2; self.cursor_y = 2
        pyxel.stop()
        match bool(js):
            case True:
                try: js.showTitleBG()
                except: pass

    def get_flips(self, x, y, player_turn):
        match self.grids[y][x]:
            case 0:
                flips = []
                opponent = 3 - player_turn
                for dx, dy in DIRECTIONS:
                    nx, ny = x + dx, y + dy
                    temp = []
                    while 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and self.grids[ny][nx] == opponent:
                        temp.append((nx, ny)); nx += dx; ny += dy
                    
                    match (0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and self.grids[ny][nx] == player_turn):
                        case True:
                            flips.extend(temp)
                return flips
            case _:
                return []

    def cpu_move(self):
        valid_moves = []
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                flips = self.get_flips(x, y, 2)
                match bool(flips):
                    case True:
                        score = self.evaluate_move(x, y, len(flips))
                        valid_moves.append((x, y, flips, score))
        
        match valid_moves:
            case []: 
                self.change_turn()
            case _:
                match self.difficulty:
                    case 1:
                        move = random.choice(valid_moves)
                    case 2:
                        valid_moves.sort(key=lambda x: x[3], reverse=True)
                        move = random.choice(valid_moves[:2])
                    case _:
                        valid_moves.sort(key=lambda x: x[3], reverse=True)
                        move = valid_moves[0]
                
                bx, by, bflips, _ = move
                self.grids[by][bx] = 2
                for fx, fy in bflips: self.grids[fy][fx] = 2
                pyxel.play(3, 0)
                self.check_attack_chance_trigger()

    def evaluate_move(self, x, y, flips_count):
        score = flips_count
        match (x, y):
            # 四隅の判定
            case (0, 0) | (0, 4) | (4, 0) | (4, 4):
                score += 100
            # 外周の判定（ガード節を利用）
            case _ if x == 0 or x == 4 or y == 0 or y == 4:
                score += 10
            case _:
                score -= 5
        return score

    def check_attack_chance_trigger(self):
        empty_count = sum(row.count(0) for row in self.grids)
        match (self.attack_chance_available and empty_count <= 8):
            case True:
                self.scene = "ATTACK_CHANCE"
                self.attack_chance_available = False
                pyxel.play(3, 2)
                # アタックチャンス突入時も手番に応じたウェイトを設定
                self.wait_timer = 20
            case False:
                self.change_turn()

    def cpu_attack(self):
        targets = [(x, y) for y in range(BOARD_SIZE) for x in range(BOARD_SIZE) if self.grids[y][x] == 1]
        match bool(targets):
            case True:
                tx, ty = random.choice(targets)
                self.grids[ty][tx] = 0
                pyxel.play(3, 1)
        self.scene = "GAME"
        self.change_turn()

    def change_turn(self):
        next_turn = 3 - self.turn
        can_next = any(len(self.get_flips(x,y,next_turn))>0 for y in range(BOARD_SIZE) for x in range(BOARD_SIZE))
        match can_next:
            case True:
                self.turn = next_turn
                # ★修正箇所：プレイヤー・CPU問わず、手番移行時に一律でウェイト（15フレーム）をかける
                self.wait_timer = 15
            case False:
                can_me = any(len(self.get_flips(x,y,self.turn))>0 for y in range(BOARD_SIZE) for x in range(BOARD_SIZE))
                match can_me:
                    case False: 
                        self.check_game_over()
                    case True: 
                        self.pass_timer = 30

    def check_game_over(self):
        p1 = sum(row.count(1) for row in self.grids)
        cpu = sum(row.count(2) for row in self.grids)
        
        # 勝敗ステータスの判定
        match (p1 > cpu, cpu > p1):
            case (True, False): self.status = 1
            case (False, True): self.status = 2
            case _: self.status = 3
            
        self.scene = "RESULT_START"
        self.transition_timer = 90
        
        match bool(js):
            case True:
                try:
                    match self.status:
                        case 1: js.showWinBG()
                        case 2: js.showLoseBG()
                except: pass
                
        pyxel.stop()
        match self.status:
            case 1: pyxel.playm(2, loop=False)
            case _: pyxel.playm(3, loop=False)

    def update(self):
        # パス表示中はタイマーを減らして処理を中断（早期リターン）する
        match (self.pass_timer > 0):
            case True: 
                self.pass_timer -= 1
                return

        # 十字キーの入力をそれぞれmatch文へ
        match pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_UP):
            case True: self.cursor_y = max(0, self.cursor_y - 1)
        match pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN):
            case True: self.cursor_y = min(BOARD_SIZE - 1, self.cursor_y + 1)
        match pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT):
            case True: self.cursor_x = max(0, self.cursor_x - 1)
        match pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT):
            case True: self.cursor_x = min(BOARD_SIZE - 1, self.cursor_x + 1)

        # メインのシーンコントロール分岐
        match self.scene:
            case "TITLE_START" | "RESULT_START":
                self.transition_timer -= 1
                match (self.transition_timer <= 0):
                    case True:
                        match self.scene:
                            case "TITLE_START":
                                self.scene = "TITLE"
                                pyxel.playm(0, loop=True)
                            case _:
                                self.reset_game()
                        match bool(js):
                            case True:
                                try: js.clearBG()
                                except: pass
                return
                
            case "TITLE":
                # 1, 2, 3 のキー判定をタプルでマルチマッチング
                match (pyxel.btnp(pyxel.KEY_1), pyxel.btnp(pyxel.KEY_2), pyxel.btnp(pyxel.KEY_3)):
                    case (True, _, _):
                        self.difficulty = 1
                        self.scene = "GAME"
                        pyxel.playm(1, loop=True)
                    case (_, True, _):
                        self.difficulty = 2
                        self.scene = "GAME"
                        pyxel.playm(4, loop=True)
                    case (_, _, True):
                        self.difficulty = 3
                        self.scene = "GAME"
                        pyxel.playm(5, loop=True)
                    case _:
                        match self.is_decision_pressed():
                            case True:
                                self.difficulty = 2
                                self.scene = "GAME"
                                pyxel.playm(4, loop=True)
                                
            case "GAME":
                match self.turn:
                    case 1:
                        # ★修正箇所：プレイヤーのターンでもウェイトタイマーがある場合は入力を受け付けない
                        match (self.wait_timer > 0):
                            case True:
                                self.wait_timer -= 1
                            case False:
                                match (pyxel.mouse_x >= 0):
                                    case True: mx, my = pyxel.mouse_x // CELL_SIZE, pyxel.mouse_y // CELL_SIZE
                                    case False: mx, my = self.cursor_x, self.cursor_y
                                    
                                match self.is_decision_pressed():
                                    case True:
                                        match (0 <= mx < BOARD_SIZE and 0 <= my < BOARD_SIZE):
                                            case True:
                                                flips = self.get_flips(mx, my, 1)
                                                match bool(flips):
                                                    case True:
                                                        self.grids[my][mx] = 1
                                                        for fx, fy in flips: self.grids[fy][fx] = 1
                                                        pyxel.play(3, 0)
                                                        self.check_attack_chance_trigger()
                    case 2:
                        match (self.wait_timer > 0):
                            case True: self.wait_timer -= 1
                            case False: self.cpu_move()
                            
            case "ATTACK_CHANCE":
                match self.turn:
                    case 1:
                        match (self.wait_timer > 0):
                            case True:
                                self.wait_timer -= 1
                            case False:
                                match self.is_decision_pressed():
                                    case True:
                                        match (pyxel.mouse_x >= 0):
                                            case True: mx, my = pyxel.mouse_x // CELL_SIZE, pyxel.mouse_y // CELL_SIZE
                                            case False: mx, my = self.cursor_x, self.cursor_y
                                            
                                        match (0 <= mx < BOARD_SIZE and 0 <= my < BOARD_SIZE and self.grids[my][mx] == 2):
                                            case True:
                                                self.grids[my][mx] = 0
                                                pyxel.play(3, 1)
                                                self.scene = "GAME"
                                                self.change_turn()
                    case 2:
                        match (self.wait_timer > 0):
                            case True: self.wait_timer -= 1
                            case False: self.cpu_attack()

    def draw(self):
        pyxel.cls(0)
        match self.scene:
            case "TITLE_START":
                return
                
            case "TITLE":
                pyxel.text(2, 5, "ATTACK3MOKU", pyxel.frame_count % 16)
                pyxel.text(5, 18, "LV1", 11)
                pyxel.text(5, 26, "LV2", 10)
                pyxel.text(5, 34, "LV3", 8)
                
            case _:
                # 盤面グリッドの描画
                for i in range(BOARD_SIZE + 1):
                    pyxel.line(i * CELL_SIZE, 0, i * CELL_SIZE, BOARD_SIZE * CELL_SIZE, 1)
                    pyxel.line(0, i * CELL_SIZE, BOARD_SIZE * CELL_SIZE, i * CELL_SIZE, 1)
                    
                # コマの描画
                for y in range(BOARD_SIZE):
                    for x in range(BOARD_SIZE):
                        match self.grids[y][x]:
                            case 0: pass
                            case g:
                                u, v = CHARACTER_LIST[g - 1]
                                pyxel.blt(x * CELL_SIZE + 1, y * CELL_SIZE + 1, 0, u, v, 8, 8, 0)
                                
                match self.turn:
                    case 1:
                        pyxel.rectb(self.cursor_x * CELL_SIZE, self.cursor_y * CELL_SIZE, CELL_SIZE + 1, CELL_SIZE + 1, 11)
                        
                match self.scene:
                    case "RESULT_START":
                        match self.status:
                            case 3: # DRAW
                                pyxel.circ(23, 23, 8, 7)
                                pyxel.line(19, 20, 21, 22, 0)
                                pyxel.line(25, 20, 27, 22, 0)
                                pyxel.line(20, 27, 26, 27, 0)
                                match (pyxel.frame_count % 10 < 5):
                                    case True: c = 7
                                    case False: c = 0
                                pyxel.text(10, 35, "DRAW!", c)
                    case _:
                        p1 = sum(row.count(1) for row in self.grids)
                        cpu = sum(row.count(2) for row in self.grids)
                        y_pos = SCREEN_SIZE + 2
                        pyxel.text(2, y_pos, f"YOU:{p1}", 7)
                        pyxel.text(2, y_pos, f"YOU:{p1}", 12)
                        pyxel.text(25, y_pos, f"CPU:{cpu}", 7)
                        pyxel.text(25, y_pos, f"CPU:{cpu}", 8)
                        
                        match (self.pass_timer > 0):
                            case True:
                                pyxel.rect(5, 15, 35, 10, 0)
                                pyxel.rectb(5, 15, 35, 10, 7)
                                pyxel.text(12, 18, "PASS", 7)
                                
                        match self.scene:
                            case "ATTACK_CHANCE":
                                match (pyxel.frame_count % 10 < 5):
                                    case True: c = 10
                                    case False: c = 7
                                pyxel.rectb(0, 0, SCREEN_SIZE, SCREEN_SIZE, c)
                                pyxel.text(2, 20, "ATTACK!", 10)

Othello25()
