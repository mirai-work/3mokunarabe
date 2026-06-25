<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<title>ATTACK 5MOKU</title>

<script src="https://cdn.jsdelivr.net/gh/kitao/pyxel/wasm/pyxel.js"></script>

<style>

html,body{
    margin:0;
    width:100%;
    height:100%;
    overflow:hidden;
    background:black;
}

#bg{
    position:fixed;
    left:0;
    top:0;
    width:100%;
    height:100%;
    background-size:cover;
    background-position:center center;
    background-repeat:no-repeat;
    z-index:0;
}

canvas{
    position:absolute;
    left:50%;
    top:50%;
    transform:translate(-50%,-50%);
    z-index:1;
}

</style>

<script>

function showTitleBG(){
    document.getElementById("bg").style.backgroundImage =
    "url('title.jpg')";
}

function showWinBG(){
    document.getElementById("bg").style.backgroundImage =
    "url('win.jpg')";
}

function showLoseBG(){
    document.getElementById("bg").style.backgroundImage =
    "url('lose.jpg')";
}

function clearBG(){
    document.getElementById("bg").style.backgroundImage = "none";
}

window.onload = function(){
    showTitleBG();
}

</script>

</head>

<body>

<div id="bg"></div>

<pyxel-play
root="."
name="3MOKUGAMEATTALETUKI.py">
</pyxel-play>

</body>
</html>
