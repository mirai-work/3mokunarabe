import pyxel
import random

# Web環境（Pyodide）のJavaScript環境を安全にインポート
try:
    import js
except ImportError:
    # ローカルのPython環境で実行したときにエラーにならないためのダミー
    class DummyJS:
        def showTitle(self): pass
        def showGame(self): pass
        def showWin(self): pass
        def showLose(self): pass
    js = DummyJS()

class Attack3Moku:
    def __init__(self):
        # 画面サイズ 160x120 で初期化
        pyxel.init(160, 120, title="ATTACK 3MOKU")
        
        # マウスカーソルを表示
        pyxel.mouse(True)
        
        # ゲーム状態の定義: "TITLE", "PLAYING", "WIN", "LOSE"
        self.state = "TITLE"
        
        # 盤面の初期化 (0: 空白, 1: プレイヤー 'O', 2: AI 'X')
        self.board = [0] * 9
        self.turn = 1          # 1: プレイヤーの番, 2: AIの番
        self.ai_delay = 0      # AIが考えている風の演出用タイマー
        
        # 盤面の描画位置計算（中央に配置）
        self.cell_size = 24
        self.start_x = (160 - (self.cell_size * 3)) // 2
        self.start_y = (120 - (self.cell_size * 3)) // 2 + 8
        
        # 最初にタイトル背景を呼ぶ
        js.showTitle()
        
        # Pyxelのメインループ開始
        pyxel.run(self.update, self.draw)

    def reset_game(self):
        """ゲーム変数の初期化"""
        self.board = [0] * 9
        self.turn = 1
        self.ai_delay = 0

    def check_winner(self):
        """勝利判定 (1: プレイヤー勝利, 2: AI勝利, -1: 引き分け, 0: 継続)"""
        win_patterns = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8], # 横
            [0, 3, 6], [1, 4, 7], [2, 5, 8], # 縦
            [0, 4, 8], [2, 4, 6]             # 斜め
        ]
        
        for p in win_patterns:
            if self.board[p[0]] == self.board[p[1]] == self.board[p[2]] != 0:
                return self.board[p[0]]
                
        if 0 not in self.board:
            return -1 # 引き分け
            
        return 0 # 継続

    def update(self):
        # --- タイトル画面の処理 ---
        if self.state == "TITLE":
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) or pyxel.btnp(pyxel.KEY_SPACE):
                self.reset_game()
                self.state = "PLAYING"
                js.showGame() # JS側：背景を消去

        # --- ゲームメインの処理 ---
        elif self.state == "PLAYING":
            # プレイヤーのターン
            if self.turn == 1:
                if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                    mx, my = pyxel.mouse_x, pyxel.mouse_y
                    # クリックされた座標が盤面内か判定
                    if (self.start_x <= mx < self.start_x + self.cell_size * 3 and
                        self.start_y <= my < self.start_y + self.cell_size * 3):
                        
                        col = (mx - self.start_x) // self.cell_size
                        row = (my - self.start_y) // self.cell_size
                        idx = row * 3 + col
                        
                        # 空いているマスなら配置
                        if self.board[idx] == 0:
                            self.board[idx] = 1
                            result = self.check_winner()
                            
                            if result == 1:
                                self.state = "WIN"
                                js.showWin() # JS側：勝利背景
                            elif result == -1:
                                self.state = "LOSE"
                                js.showLose() # JS側：敗北（引き分け）背景
                            else:
                                self.turn = 2 # AIのターンへ
                                self.ai_delay = 0

            # AIのターン (少し時間を置いてから自動で置く)
            elif self.turn == 2:
                self.ai_delay += 1
                if self.ai_delay > 15: # 約0.5秒のウェイト
                    empty_cells = [i for i, val in enumerate(self.board) if val == 0]
                    if empty_cells:
                        idx = random.choice(empty_cells)
                        self.board[idx] = 2
                        result = self.check_winner()
                        
                        if result == 2:
                            self.state = "LOSE"
                            js.showLose() # JS側：敗北背景
                        elif result == -1:
                            self.state = "LOSE"
                            js.showLose()
                        else:
                            self.turn = 1 # プレイヤーのターンへ

        # --- 結果画面の処理（勝敗画面） ---
        elif self.state in ["WIN", "LOSE"]:
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) or pyxel.btnp(pyxel.KEY_SPACE):
                self.state = "TITLE"
                js.showTitle() # JS側：タイトル背景に戻す

    def draw(self):
        # 画面を透明（背景画像を透過させるため、pyxel側はクリアカラーを0にしつつ
        # HTML/CSS側の背景が見えるように設定。ただしPyxel Wasmの標準仕様に合わせて黒ベースで消去）
        pyxel.cls(0)

        if self.state == "TITLE":
            # タイトル文字（中央揃えの簡易配置）
            pyxel.text(56, 40, "ATTACK 3MOKU", 10)
            pyxel.text(42, 70, "CLICK OR SPACE TO START", 7)

        elif self.state == "PLAYING":
            # 盤面の枠線を描画
            for i in range(4):
                # 横線
                pyxel.line(self.start_x, self.start_y + i * self.cell_size, 
                           self.start_x + self.cell_size * 3, self.start_y + i * self.cell_size, 13)
                # 縦線
                pyxel.line(self.start_x + i * self.cell_size, self.start_y, 
                           self.start_x + i * self.cell_size, self.start_y + self.cell_size * 3, 13)

            # 駒の描画
            for i in range(9):
                row = i // 3
                col = i % 3
                cx = self.start_x + col * self.cell_size + self.cell_size // 2
                cy = self.start_y + row * self.cell_size + self.cell_size // 2
                
                if self.board[i] == 1:
                    # プレイヤー：青い○
                    pyxel.circb(cx, cy, 8, 12)
                elif self.board[i] == 2:
                    # AI：赤い×
                    pyxel.line(cx - 6, cy - 6, cx + 6, cy + 6, 8)
                    pyxel.line(cx + 6, cy - 6, cx - 6, cy + 6, 8)

            # ターン表示
            if self.turn == 1:
                pyxel.text(60, 6, "YOUR TURN", 12)
            else:
                pyxel.text(62, 6, "AI THINKING", 8)

        elif self.state == "WIN":
            pyxel.text(68, 50, "YOU WIN!", 10)
            pyxel.text(46, 75, "CLICK TO RESTART", 7)

        elif self.state == "LOSE":
            pyxel.text(68, 50, "GAME OVER", 8)
            pyxel.text(46, 75, "CLICK TO RESTART", 7)

# 実行
Attack3Moku()
