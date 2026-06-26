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

#bgvideo{
    position:fixed;
    left:0;
    top:0;
    width:100%;
    height:100%;
    object-fit:cover;
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

let bgvideo = null;

function playBG(filename, loop=true){
    if(!bgvideo){
        bgvideo = document.getElementById("bgvideo");
    }

    bgvideo.pause();
    bgvideo.src = filename;
    bgvideo.loop = loop;
    bgvideo.load();

    bgvideo.play().catch(()=>{});
}

function showTitleBG(){
    playBG("title.mp4", true);
}

function showWinBG(){
    playBG("win.mp4", false);
}

function showLoseBG(){
    playBG("lose.mp4", false);
}

function clearBG(){
    if(!bgvideo){
        bgvideo = document.getElementById("bgvideo");
    }

    bgvideo.pause();
    bgvideo.removeAttribute("src");
    bgvideo.load();
}

window.onload = function(){
    showTitleBG();
};

</script>

</head>

<body>

<video
id="bgvideo"
autoplay
muted
playsinline
preload="auto">
</video>

<pyxel-play
root="."
name="3MOKUGAMEATTALETUKI.py">
</pyxel-play>

</body>
</html>
