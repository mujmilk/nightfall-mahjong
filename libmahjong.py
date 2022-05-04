import pygame
from pygame.locals import *
import sys
import os
import time
import glob
import random

# システム
bgm_files = []

# ゲーム起動時に1回だけ必ず実行される
def init():
    for i in range(1):
        path = "./music/" + str(i) + "/*"
        bgm_files.append(glob.glob(path))

def exitgame():
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.fadeout(100)
    sys.exit()
    
def playbgm(n):
    bgm_idx = random.randrange(0, len(bgm_files[n]))
    bgm_file = bgm_files[n][bgm_idx]
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.fadeout(100)
        time.sleep(0.1)
    pygame.mixer.music.load(bgm_file)
    pygame.mixer.music.play(-1)

# 麻雀

# イーシャンテンなら2，聴牌なら1，アガリなら0を返す．それ以外は-1
def check_hands(tiles, naki, riichi, dora):
    # Dots      : 1~9 : 筒子
    # Bamboo    : 11~19 : 索子
    # Characters: 21~29 : 萬子
    # Dragons   : 0, 10, 20 : 白，ハツ，中
    # Winds     : 30, 31, 32, 33 : 東，南，西，北
    return 
