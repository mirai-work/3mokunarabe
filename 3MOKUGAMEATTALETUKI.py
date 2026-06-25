<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="utf-8">
    <title>ATTACK 5MOKU</title>
    <script src="https://cdn.jsdelivr.net/gh/kitao/pyxel/wasm/pyxel.js"></script>
    <style>
        html, body { margin: 0; width: 100%; height: 100%; overflow: hidden; background: black; }

        /* 背景動画エリア */
        #bg {
            position: fixed;
            left: 0; top: 0;
            width: 100%; height: 100%;
            object-fit: cover;
            z-index: 0;
        }

        /* ゲーム画面（Pyxel） */
        pyxel-run {
            position: absolute;
            left: 50%; top: 50%;
            transform: translate(-50%, -50%);
            z-index: 1;
        }
    </style>
</head>
<body>

    <video id="bg" autoplay loop muted playsinline></video>

    <pyxel-run name="3MOKUGAMEATTALETUKI.py"></pyxel-run>

    <script>
        // 動画切り替え用関数
        function playVideo(src) {
            let bg = document.getElementById("bg");
            bg.src = src;
            bg.play();
        }

        // シーンに合わせて呼び出す関数
        function showTitleBG() { playVideo("title.mp4"); }
        function showWinBG()   { playVideo("win.mp4"); }
        function showLoseBG()  { playVideo("lose.mp4"); }

        // 初回ロード時
        window.onload = showTitleBG;
    </script>
</body>
</html>
