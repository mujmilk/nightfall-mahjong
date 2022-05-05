import pygame
from pygame.locals import *
import sys
import random
import configparser

import libmahjong
import liboption

# 定数の宣言 
SCREEN_SIZE = (800, 600)  # 画面サイズ
TITLE = "Nightfall Mahjong"

#ファイル名
# "sysimg/"+str(0)+"/"+libmahjong.TILES[n]+".gif"

def init():
    # 初期化
    pygame.init()

    # config.iniが存在しないとき，設定がないとき，値がおかしいときの
    # エラー対応別途必要
    config_ini = configparser.ConfigParser()
    config_ini.read('config.ini', encoding='utf-8')
    
    c_bgm = config_ini['SOUND']['BGM_Volume']
    c_se = config_ini['SOUND']['SE_Volume']
    c_fs = config_ini['DISPLAY']['FullScreen']

    c_bgm_f = float(c_bgm) / 100.0
    c_se_f = float(c_se) / 100.0

    liboption.init(bgm_volume=c_bgm_f, se_volume=c_se_f)

    return (c_fs == "True")

pygame.display.set_icon(pygame.image.load('sysimg/icon.png'))
fullscreen = init()
if fullscreen:
    screen = pygame.display.set_mode(SCREEN_SIZE, pygame.FULLSCREEN)
else:
    screen = pygame.display.set_mode(SCREEN_SIZE)


pygame.display.set_caption(TITLE)
font = pygame.font.Font(None, 55)
clock = pygame.time.Clock()

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



def title(refreshbgm=True):
    # BGM開始
    if refreshbgm:
        liboption.playbgm(0)

    # ボタン
    start_button   = pygame.Rect(153, 330, 196, 211)
    config_button = pygame.Rect(455, 330, 196, 211)
    startimg = pygame.image.load("sysimg/button/start.png")
    configimg = pygame.image.load("sysimg/button/config.png")

    # 背景画像
    #bgimg = pygame.image.load("bgimg/title.png")
    collide_start_button = False

    frame = 0
    bairitsu = 1
    bgimg = pygame.image.load("anime/title/nm_"+str(int(frame/bairitsu)).zfill(4)+".bmp")

    while True:
        clock.tick(30) #フレームレートの宣言，大事！ これがないとかなり重くなる
        screen.blit(bgimg, (0, 0))
        screen.blit(startimg, (153, 337))
        screen.blit(configimg, (455, 337))

        pygame.display.update()
        
        frame = (frame + 1) % (288 * bairitsu)
        if frame % bairitsu == 0:
            bgimg = pygame.image.load("anime/title/nm_"+str(int(frame/bairitsu)).zfill(4)+".bmp")
        
        # イベント処理
        for event in pygame.event.get():
            if event.type == QUIT:  # 終了イベント
                liboption.exitgame()
            
            if event.type == MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    liboption.playse("enter")
                    return 2
                elif config_button.collidepoint(event.pos):
                    liboption.playse("enter")
                    return 1
                else:
                    liboption.playse("cancel")
            
            elif event.type == MOUSEMOTION:
                if start_button.collidepoint(event.pos):
                    if not collide_start_button:
                        liboption.playse("select")
                        collide_start_button = True
                else:
                    if collide_start_button:
                        liboption.playse("select")
                        collide_start_button = False


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
        bgmstats = liboption.get_bgm_stats()
        if bgmstats:
            screen.blit(toggleonimg, (380, 240))
        else:
            screen.blit(toggleoffimg, (380, 240))
        
        sestats = liboption.get_se_stats()
        if sestats:
            screen.blit(toggleonimg, (380, 340))
        else:
            screen.blit(toggleoffimg, (380, 340))
        pygame.display.update()
    
    update()

    while True:
        clock.tick(30)
        # イベント処理
        for event in pygame.event.get():
            if event.type == QUIT:  # 終了イベント
                liboption.exitgame()
            
            if event.type == MOUSEBUTTONDOWN:
                if bgm_toggle.collidepoint(event.pos):
                    liboption.change_bgm_mode()
                    liboption.playse("enter")
                    update()
                elif se_toggle.collidepoint(event.pos):
                    liboption.change_se_mode()
                    liboption.playse("enter")
                    update()
                elif backtotitle1.collidepoint(event.pos) or backtotitle2.collidepoint(event.pos):
                    liboption.playse("cancel")
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
        clock.tick(30)
        screen.fill((20,20,20))

        pygame.draw.rect(screen, (0, 80, 0), yon_button)
        pygame.draw.rect(screen, (0, 80, 0), san_button)

        screen.blit(yon_text, [275, 375])
        screen.blit(san_text, [275, 550])

        pygame.display.update()
        # イベント処理
        for event in pygame.event.get():
            if event.type == QUIT:  # 終了イベント
                liboption.exitgame()
            
            if event.type == MOUSEBUTTONDOWN:
                if yon_button.collidepoint(event.pos):
                    game()
                    return 0
                elif san_button.collidepoint(event.pos):
                    game(playernum=3)
                    return 0


def game(playernum=4, sibari=0):

    liboption.playbgm(1)

    # Dots      : 1~9 : 筒子
    # Bamboo    : 11~19 : 索子
    # Characters: 21~29 : 萬子
    # Dragons   : 0, 10, 20 : 白，ハツ，中
    # Winds     : 30, 31, 32, 33 : 東，南，西，北

    img_playertiles = []

    # 毎回ソートして，表示用の配列を別に作る

    # 初期化
    # 各プレイヤーの手牌. プレイヤー0は自分
    players = [{"tiles":[], "wind":0, "pung":0, "chow":0, "kong":0} for i in range(playernum)]
    discarded_tiles = [[] for i in range(playernum)]

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
    
    choose_dealer()
    
    # シャッフル，配牌
    random.shuffle(wall)
    # 完全ランダム
    for i in range(playernum):
        for j in range(13):
            players[i]["tiles"].append(wall.pop())
        players[i]["tiles"] = sorted(players[i]["tiles"])

    # ドラ決め testok
    bonus_tile = wall.pop()
    #print("ドラ表示牌は", bonus_tile)
    #bonus_tileimg = TILES[bonus_tile] #表示用
    if bonus_tile >= 30:
        bonus_tile = 30 + (bonus_tile % 30 + 1) % 4
    elif bonus_tile % 10 == 0:
        bonus_tile = (bonus_tile + 10) % 30
    elif bonus_tile % 10 == 9:
        bonus_tile -= 8
    else:
        bonus_tile += 1
    print("ドラは", nanno_koma(bonus_tile))

    scale = 1.0

    #開始時アニメーション
    screen.fill((20,20,20))

    # playerのインデックス番号を格納，誰がどこに座っているか
    seat = [-1 for i in range(4)] # player, 対面, 下家, 上家
    for i in range(playernum):
        seat[((players[0]["wind"]-players[i]["wind"])%4)] = i


    # 手牌表示
    # 1: playeropen 2: 上家open 3: 対面open 4: 下家open
    # 5: player     6: 上家     7: 対面     8: 下家
    def show_tiles(tiles, n):
        if n == 7: #対面伏せ牌表示
            n = 6
            size_x = int(33 * scale)
            size_y = int(59 * scale)

            x = 300
            y = 20
            timgpath = "sysimg/ms/p_bk_5.gif"
            timg = pygame.image.load(timgpath)
            timg = pygame.transform.rotozoom(timg, 0, scale) # 拡大，プレビュー用
        
            for i in range(len(tiles)): # 定数でいいと思う
                screen.blit(timg, (x, y))
                x += size_x
        elif n == 8: # 下家伏せ牌表示
            n = 7
            size_x = int(26 * scale)
            dy = int(25 * scale)

            x = 800 - size_x - 20 # margin:20
            y = 200
            timgpath = "sysimg/ms/p_bk_9.png"
            timg = pygame.image.load(timgpath)
            timg = pygame.transform.rotozoom(timg, 0, scale) # 拡大，プレビュー用
        
            for i in range(len(tiles)): # 定数でいいと思う
                screen.blit(timg, (x, y))
                y += dy
        elif n == 6: # 上家伏せ牌表示
            n = 8
            size_x = int(26 * scale)
            dy = int(25 * scale)

            x = 20 # margin:20
            y = 40
            timgpath = "sysimg/ms/p_bk_8.png"
            timg = pygame.image.load(timgpath)
            timg = pygame.transform.rotozoom(timg, 0, scale) # 拡大，プレビュー用
        
            for i in range(len(tiles)): # 定数でいいと思う
                screen.blit(timg, (x, y))
                y += dy
        elif n == 5: # player
            n = 0
            size_x = 33 # 画像サイズ
            size_y = 60

            x = 20
            y = 600 - size_y - 20
        
            for t in tiles:
                timgpath = "sysimg/"+str(n)+"/"+libmahjong.TILES[t]+str(n)+".gif"
                timg = pygame.image.load(timgpath)
                #timg = pygame.transform.rotozoom(timg, 0, scale) # 拡大，プレビュー用
                screen.blit(timg, (x, y))
                x += size_x
        else:
            print("error show_tiles n", file=sys.stderr)

    xy = [(350, 350), (282, 200), (348, 149), (500,200)]
    
    # 手牌の表示
    for i in range(len(seat)):
        if i == 0:
            continue
        if seat[i] == -1:
            continue
        show_tiles(players[seat[i]]["tiles"], i+5)

        # 風の表示
        timgpath = "sysimg/ms/c_"+str(players[seat[i]]["wind"])+"_"+str(i)+".gif"
        timg = pygame.image.load(timgpath)
        screen.blit(timg, xy[i])
    
    pl0 = libmahjong.TileSprites(players[0]["tiles"], 0, 20, 520)
    pl0.drawall(screen)
    ds0 = libmahjong.TileSprites([], 1, 350, 350)
    

    # プレイヤーの駒の当たり判定追加

    text = font.render("GAME", True, (222, 222, 222))
    screen.blit(text, [100, 100])

    pygame.display.update()

    hand = wall.pop()
    new1 = libmahjong.TileSprite(hand, 0, 600, 500)
    new1.draw(screen)
    pygame.display.update()
    
    while True:
        clock.tick(30)


        # 1枚捨てる

        # イベント処理
        for event in pygame.event.get():
            if event.type == QUIT:  # 終了イベント
                liboption.exitgame()
            
            if event.type == MOUSEBUTTONDOWN:
                if new1.check(event.pos):
                    discarded_tiles.append(hand)
                    ds0.addtile(hand)
                    ds0.drawall(screen)
                    pygame.display.update()
                    hand = wall.pop()
                    new1 = libmahjong.TileSprite(hand, 0, 600, 500)
                    new1.draw(screen)
                    pygame.display.update()
                    print(new1.get_tileid())
                    break
                    
                b = pl0.checkall(event.pos)
                if b != -1:
                    discarded_tiles.append(players[0]["tiles"][b])
                    ds0.addtile(players[0]["tiles"][b])
                    ds0.drawall(screen)
                    pygame.display.update()
                    del players[0]["tiles"][b]
                    players[0]["tiles"].append(hand)
                    players[0]["tiles"] = sorted(players[0]["tiles"])
                    
                    pl0.discardtile(b)
                    pl0.addtile(hand)
                    pl0.sort()
                    pl0.drawall(screen)
                    
                    pygame.display.update()
                    hand = wall.pop()
                    new1 = libmahjong.TileSprite(hand, 0, 600, 500)
                    new1.draw(screen)
                    pygame.display.update()

                else:
                    return


# main
stats = 0 # 0:title, 1:option, 2:menu, 3:custommenu, 4:game, 5:result
settings_game = []
settings_option = []

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