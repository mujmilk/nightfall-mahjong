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
# ファイル名で指定
# 0: select.ogg  ボタンのマウスオーバー時
# 1: cancel.ogg  何もないところをクリックした時
# 2: enter.ogg  決定音

# システム


def exitgame():
    # config.iniを書き換える
    # se, bgmの音量
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.fadeout(100)
    sys.exit()


# ==================================
# 音関連
# ==================================

bgm_filenames = []
playsound = [] # flag
se_sounds = {}

def playbgm(n):
    if playsound[0]:
        bgm_idx = random.randrange(0, len(bgm_filenames[n]))
        bgm_file = bgm_filenames[n][bgm_idx]
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.fadeout(100)
            time.sleep(0.1)
        pygame.mixer.music.load(bgm_file)
        pygame.mixer.music.play(-1)

def playse(name):
    se_sounds[name].play()
    

def change_bgm_mode():
    if playsound[0]:
        playsound[0] = False
        #if pygame.mixer.music.get_busy():
        pygame.mixer.music.pause()
    else:
        playsound[0] = True
        pygame.mixer.music.unpause()

def change_se_mode():
    if playsound[1]:
        for i in range(8):
            pygame.mixer.Channel(i).set_volume(0)
    else:
        for i in range(8):
            pygame.mixer.Channel(i).set_volume(1.0)
    playsound[1] = not playsound[1]

def get_bgm_stats():
    return playsound[0]

def get_se_stats():
    return playsound[1]

# ゲーム起動時に1回だけ必ず実行される
def init(bgm_volume=100, se_volume=100):

    # SE用チャンネルの初期化．うまくいっていない？
    # 音がかなり遅れて聞こえる
    pygame.mixer.set_num_channels(8)
    for i in range(8):
        pygame.mixer.Channel(i).set_volume(se_volume / 100.0)

    # musicフォルダからBGMファイル一覧の取得
    for i in range(2):
        path = "music/" + str(i) + "/*"
        bgm_filenames.append(glob.glob(path))
    
    
    # soundフォルダからSEファイルの事前読み込み
    sepath = "sound/*"
    sepathlist = glob.glob(sepath)
    for path in sepathlist:
        print(path)
        se_sounds[path[6:-4]] = pygame.mixer.Sound(path)
        print(path[6:-4])
    
    playsound.append(bool(bgm_volume))
    playsound.append(bool(se_volume))
