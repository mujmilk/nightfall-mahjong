import pygame
from pygame.locals import *
import sys

import libmahjong

# 定数,変数の宣言 
SCREEN_SIZE = (800, 600)  # 画面サイズ
TITLE = "Nightfall Mahjong"

# 初期化
pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption(TITLE)
font = pygame.font.Font(None, 55)

def title():
    # BGM開始
    libmahjong.playbgm(0)

    # 文字
    title_text = font.render("NIGHTFALL MAHJONG", True, (222, 222, 222))
    menu_text = font.render("GAME START", True, (222, 222, 222))

    # ボタン
    menu_button   = pygame.Rect(250, 360, 300, 60)
    option_button = pygame.Rect(250, 450, 300, 60)

    #while True:
    screen.fill((20,20,20))

    pygame.draw.rect(screen, (0, 80, 0), menu_button)
    pygame.draw.rect(screen, (0, 80, 0), option_button)

    screen.blit(title_text, [100, 100])
    screen.blit(menu_text, [275, 375])


    pygame.display.update()

    while True:
        # イベント処理
        for event in pygame.event.get():
            if event.type == QUIT:  # 終了イベント
                libmahjong.exitgame()
            
            if event.type == MOUSEBUTTONDOWN:
                if menu_button.collidepoint(event.pos):
                    return 2
                elif option_button.collidepoint(event.pos):
                    return 1

def option():
    # フルスクリーンに切り替えるかどうか
    # 音量の設定

    while True:
        screen.fill((20,20,20))

        pygame.draw.rect(screen, (0, 80, 0), Rect(10, 10, 80, 50))
        text = font.render("OPTION", True, (222, 222, 222))
        screen.blit(text, [100, 100])

        pygame.display.update()
        # イベント処理
        for event in pygame.event.get():
            if event.type == QUIT:  # 終了イベント
                libmahjong.exitgame()
            
            if event.type == MOUSEBUTTONDOWN:
                return 0

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
        screen.blit(san_text, [275, 400])

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
                    game(players=3)
                    return 0

def game(players=4, sibari=0):

    # Dots      : 1~9 : 筒子
    # Bamboo    : 11~19 : 索子
    # Characters: 21~29 : 萬子
    # Dragons   : 0, 10, 20 : 白，ハツ，中
    # Winds     : 30, 31, 32, 33 : 東，南，西，北

    # 毎回ソートして，表示用の配列を別に作る

    # 初期化
    player1 = {"tiles":[], "wind":0}
    player2 = {"tiles":[], "wind":0}
    player3 = {"tiles":[], "wind":0}
    player4 = {"tiles":[], "wind":0}
    wall = [i for i in range(34)]

    # 親決め
    # シャッフル，配牌
    # ドラ決め?

    #

    #開始時アニメーション
    screen.fill((20,20,20))

    text = font.render("GAME", True, (222, 222, 222))
    screen.blit(text, [100, 100])

    pygame.display.update()
    
    while True:

        screen.fill((20,20,20))

        # 

        # 内部状態に基づいて描画

        # イベント処理
        for event in pygame.event.get():
            if event.type == QUIT:  # 終了イベント
                libmahjong.exitgame()
            
            if event.type == MOUSEBUTTONDOWN:
                return


stats = 0 # 0:title, 1:option, 2:menu, 3:custommenu, 4:game, 5:result
settings_game = []
settings_option = []
libmahjong.init()

while True:
    print(stats)
    if stats == 0:
        stats = title()
    elif stats == 1:
        stats = option()
    elif stats == 2:
        stats = menu()
    #elif stats == 3:
        #stats = custommenu()
    #elif stats == 4:
        #stats = game()