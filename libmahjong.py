import pygame
from pygame.locals import *
import sys
import os
import time
import glob
import random

# =======================
# BGM
# =======================
# musicフォルダ配下数字(シーン別)フォルダに放り込んだファイルがランダムに再生される
# 以下シーン一覧
# 0: タイトル画面

# =======================
# SE
# =======================
# 数字で指定
# 0: mouseover.ogg  ボタンのマウスオーバー時
# 1: click.ogg  何もないところをクリックした時
# 2: enter.ogg  決定音


# システム
bgm_files = []
playsound = []

def exitgame():
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.fadeout(100)
    sys.exit()

def playbgm(n):
    if playsound[0]:
        bgm_idx = random.randrange(0, len(bgm_files[n]))
        bgm_file = bgm_files[n][bgm_idx]
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.fadeout(100)
            time.sleep(0.1)
        pygame.mixer.music.load(bgm_file)
        pygame.mixer.music.play(-1)

def playse(name):
    if playsound[1]:
        pass

def change_bgm_mode():
    if playsound[0]:
        playsound[0] = False
        #if pygame.mixer.music.get_busy():
        pygame.mixer.music.pause()
    else:
        playsound[0] = True
        pygame.mixer.music.unpause()

    # config.iniを書き換える

def change_se_mode():
    playsound[1] = not playsound[1]
    # config.iniを書き換える

def get_bgm_stats():
    return playsound[0]

def get_se_stats():
    return playsound[1]

# ゲーム起動時に1回だけ必ず実行される
def init():
    for i in range(1):
        path = "./music/" + str(i) + "/*"
        bgm_files.append(glob.glob(path))
    
    # config.iniから読み込むように変更する
    playsound.append(True)
    playsound.append(True)


# 麻雀


# イーシャンテンなら2，聴牌なら1，アガリなら0を返す．それ以外は-1
def check_hands(tiles, riichi, dora):
    # Dots      : 1~9 : 筒子
    # Bamboo    : 11~19 : 索子
    # Characters: 21~29 : 萬子
    # Dragons   : 0, 10, 20 : 白，ハツ，中
    # Winds     : 30, 31, 32, 33 : 東，南，西，北
    return 
