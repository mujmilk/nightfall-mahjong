import pygame
from pygame.locals import *
#import sys
import random

import libmahjong

# 定数の宣言 
SCREEN_SIZE = (800, 600)  # 画面サイズ
TITLE = "Nightfall Mahjong"

# "sysimg/"+str(0)+"/"+TILES[n]+".gif"
TILES = ["p_no_", "p_ms1_", "p_ms2_", "p_ms3_", "p_ms4_", "p_ms5_", "p_ms6_", "p_ms7_", "p_ms8_", "p_ms9_",
         "p_ji_h_", "p_ps1_", "p_ps2_", "p_ps3_", "p_ps4_", "p_ps5_", "p_ps6_", "p_ps7_", "p_ps8_", "p_ps9_",
         "p_ji_c_", "p_ss1_", "p_ss2_", "p_ss3_", "p_ss4_", "p_ss5_", "p_ss6_", "p_ss7_", "p_ss8_", "p_ss9_",
         "p_ji_e_", "p_ji_s_", "p_ji_w_", "p_ji_n_"]


def nanno_koma(n): # testok
    s = ""
    if n >= 30:
        namelist = ["東", "南", "西", "北"]
        s += namelist[n - 30]
    elif n % 10 == 0:
        namelist = ["白", "發", "中"]
        s += namelist[int(n / 10)]
    elif n >= 20:
        namelist = ["一", "二", "三", "四", "五", "六", "七", "八" ,"九"]
        s += namelist[n % 10 - 1] + "萬"
    else:
        if n >= 10:
            s += "索子(ソーズ)の"
        else:
            s += "筒子(ピンズ)の"
        s += str(n%10)
    return s

# 初期化
pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption(TITLE)
font = pygame.font.Font(None, 55)

def title(refreshbgm=True):
    # BGM開始
    if refreshbgm:
        libmahjong.playbgm(0)

    # ボタン
    start_button   = pygame.Rect(153, 330, 196, 211)
    config_button = pygame.Rect(455, 330, 196, 211)
    startimg = pygame.image.load("sysimg/button/start.png")
    configimg = pygame.image.load("sysimg/button/config.png")

    # 背景画像
    bgimg = pygame.image.load("bgimg/title.png")
    screen.blit(bgimg, (0, 0))
    screen.blit(startimg, (153, 337))
    screen.blit(configimg, (455, 337))

    pygame.display.update()

    while True:
        # イベント処理
        for event in pygame.event.get():
            if event.type == QUIT:  # 終了イベント
                libmahjong.exitgame()
            
            if event.type == MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    return 2
                elif config_button.collidepoint(event.pos):
                    return 1

def option():
    # フルスクリーンに切り替えるかどうか
    # 音量の設定
    # 背景画像
    bgimg = pygame.image.load("bgimg/config.png")
    
    backtotitle1 = pygame.Rect(0, 0, 100, 600)
    backtotitle2 = pygame.Rect(700, 0, 100, 600)

    # ボタン
    bgm_toggle   = pygame.Rect(380, 240, 271, 76)
    se_toggle = pygame.Rect(380, 340, 271, 76)

    toggleonimg = pygame.image.load("sysimg/button/on.png")
    toggleoffimg = pygame.image.load("sysimg/button/off.png")

    bgmstats = True
    sestats = True

    def update():
        # 描画
        screen.blit(bgimg, (0, 0))
        bgmstats = libmahjong.get_bgm_stats()
        if bgmstats:
            screen.blit(toggleonimg, (380, 240))
        else:
            screen.blit(toggleoffimg, (380, 240))
        
        sestats = libmahjong.get_se_stats()
        if sestats:
            screen.blit(toggleonimg, (380, 340))
        else:
            screen.blit(toggleoffimg, (380, 340))
        pygame.display.update()
    
    update()

    while True:
        # イベント処理
        for event in pygame.event.get():
            if event.type == QUIT:  # 終了イベント
                libmahjong.exitgame()
            
            if event.type == MOUSEBUTTONDOWN:
                if bgm_toggle.collidepoint(event.pos):
                    libmahjong.change_bgm_mode()
                    update()
                elif se_toggle.collidepoint(event.pos):
                    libmahjong.change_se_mode()
                    update()
                elif backtotitle1.collidepoint(event.pos) or backtotitle2.collidepoint(event.pos):
                    return 10

def menu():
    # 四人，三人の選択
    # スタンダード，はんしばり，超接待，カスタムの選択

    # 文字
    yon_text = font.render(" 4 ", True, (222, 222, 222))
    san_text = font.render(" 3 ", True, (222, 222, 222))

    # ボタン
    yon_button   = pygame.Rect(250, 360, 300, 60)
    san_button   = pygame.Rect(250, 500, 300, 60)

    while True:
        screen.fill((20,20,20))

        pygame.draw.rect(screen, (0, 80, 0), yon_button)
        pygame.draw.rect(screen, (0, 80, 0), san_button)

        screen.blit(yon_text, [275, 375])
        screen.blit(san_text, [275, 550])

        pygame.display.update()
        # イベント処理
        for event in pygame.event.get():
            if event.type == QUIT:  # 終了イベント
                libmahjong.exitgame()
            
            if event.type == MOUSEBUTTONDOWN:
                if yon_button.collidepoint(event.pos):
                    game()
                    return 0
                elif san_button.collidepoint(event.pos):
                    game(playernum=3)
                    return 0

def game(playernum=4, sibari=0):

    # Dots      : 1~9 : 筒子
    # Bamboo    : 11~19 : 索子
    # Characters: 21~29 : 萬子
    # Dragons   : 0, 10, 20 : 白，ハツ，中
    # Winds     : 30, 31, 32, 33 : 東，南，西，北

    img_playertiles = []

    # 毎回ソートして，表示用の配列を別に作る

    # 初期化
    players = [{"tiles":[], "wind":0}, # 0, 自分
               {"tiles":[], "wind":0}, # 1, 右どなり(下家)
               {"tiles":[], "wind":0}, # 2, 対面
               {"tiles":[], "wind":0}] # 3, 左どなり(上家)
    wall = [i for i in range(34) for j in range(4)]
    #for i in range(34):
    #    for j in range(4):
    #        wall.append(i)
    prevailing_wind = 30 # 東


    # 親決め testok
    def choose_dealer(): # sitting_a_seat
        # →4人の中から一人がサイコロを振る
        kariton = random.randrange(0, playernum)
        #print("仮東は", kariton)
        
        # ↑の位置にサイコロを表示
        # サイコロを二個振る
        dice1 = random.randint(1, 6)
        dice2 = random.randint(1, 6)
        #print("サイコロの出目は ", dice1, dice2)
        karioya = (kariton + dice1 + dice2) % playernum
        #print("仮親は ", karioya)

        # サイコロを二個振る
        dice1 = random.randint(1, 6)
        dice2 = random.randint(1, 6)
        #print("サイコロの出目は ", dice1, dice2)
        oya = (karioya + dice1 + dice2) % playernum
        #print("親は ", oya)

        for i in range(playernum):
            players[(oya + i) % playernum]["wind"] = 30 + i
            #print((oya+i)%playernum, 30+i)
    
    choose_dealer()
        
    
    # シャッフル，配牌
    random.shuffle(wall)
    # いつかちゃんとした配り方も実装したい，今はとりあえず完全ランダム
    for i in range(4):
        for j in range(13):
            players[i]["tiles"].append(wall.pop())

    # ドラ決め testok
    bonus_tile = wall.pop()
    #print("ドラ表示牌は", bonus_tile)
    if bonus_tile >= 30:
        bonus_tile = 30 + (bonus_tile % 30 + 1) % 4
    elif bonus_tile % 10 == 0:
        bonus_tile = (bonus_tile + 10) % 30
    elif bonus_tile % 10 == 9:
        bonus_tile -= 8
    else:
        bonus_tile += 1
    print("ドラは", nanno_koma(bonus_tile))

    scale = 1.4
    size_x = int(33 * scale)
    size_y = int(60 * scale)

    x = 20
    y = 600 - size_y

    #開始時アニメーション
    screen.fill((20,20,20))

    players[0]["tiles"] = sorted(players[0]["tiles"])

    for t in players[0]["tiles"]:
        timgpath = "sysimg/"+str(0)+"/resize/"+TILES[t]+str(0)+".jpg"
        timg = pygame.image.load(timgpath)
        #timg = pygame.transform.rotozoom(timg, 0, scale) # 拡大，プレビュー用
        screen.blit(timg, (x, y))
        x += size_x

    text = font.render("GAME", True, (222, 222, 222))
    screen.blit(text, [100, 100])

    pygame.display.update()
    
    while True:

        # 

        # 内部状態に基づいて描画

        # イベント処理
        for event in pygame.event.get():
            if event.type == QUIT:  # 終了イベント
                libmahjong.exitgame()
            
            if event.type == MOUSEBUTTONDOWN:
                return


# main
stats = 0 # 0:title, 1:option, 2:menu, 3:custommenu, 4:game, 5:result
settings_game = []
settings_option = []
libmahjong.init()

while True:
    print(stats)
    if stats == 0:
        stats = title()
    elif stats == 10:
        stats = title(refreshbgm=False)
    elif stats == 1:
        stats = option()
    elif stats == 2:
        stats = menu()
    #elif stats == 3:
        #stats = custommenu()
    #elif stats == 4:
        #stats = game()