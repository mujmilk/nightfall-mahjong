import pygame
from pygame.locals import *
import sys
import random
import configparser

import libmahjong
import liboption

# == 定数の宣言 ====
# 画面サイズ
SCREEN_SIZE = (800, 600) # TODO: 1920x1080に入れ替える
# ウィンドウタイトル
TITLE = "Nightfall Mahjong"

# タイトル画面系 ------
# スタートボタン
SIZE_START_BUTTON = [153, 330, 196, 211] # [左上x座標, 左上y座標, 横幅, 縦幅]
# コンフィグボタン
SIZE_CONFIG_BUTTON = [455, 330, 196, 211] # [左上x座標, 左上y座標, 横幅, 縦幅]

# スタートボタン
PATH_IMG_START_BUTTON = "sysimg/button/start.png"
# コンフィグボタン
PATH_IMG_CONFIG_BUTTON = "sysimg/button/config.png"

# ゲーム画面系 ------
GAME_BUTTON_LABELS = ["ツモ", "ロン", "ポン", "チー", "カン"] #MAX4つ表示されるはず
GAME_BUTTON = [300, 300, 100, 60] # [左上x座標, 左上y座標, 横幅, 縦幅]
GAME_BUTTON_COLOR = (222, 222, 222)
GAME_BUTTON_BG_COLOR = (0, 0, 0)

#ファイル名
# "sysimg/"+str(0)+"/"+libmahjong.TILES[n]+".gif"

# == 変数の宣言 ====
# ゲーム毎に引き継ぐ変数のみ
# ゲーム設定変数 ------
# 場風
prevailing_wind = 30 # 東
# 親
oya = 21012
# 本場
honba = 0
# 点数
points [35000 for i in range(4)]
# AIs
scraps = [0]
# game button
game_buttons = []

for i in range(playernum-1):
    scraps.append(libmahjong.Scrap())

def init():
    # 初期化
    pygame.init()

    # config.iniから、サウンドの音量、フルスクリーンかどうかの設定値を取得する
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

# ゲームウィンドウのアイコンを設定
pygame.display.set_icon(pygame.image.load('sysimg/icon.png'))
# 初期化(config.iniの取得)、戻り値:config.iniのフルスクリーン設定値(True:フルスクリーン)
fullscreen = init()
# 画面サイズの設定
if fullscreen:
    screen = pygame.display.set_mode(SCREEN_SIZE, pygame.FULLSCREEN)
else:
    screen = pygame.display.set_mode(SCREEN_SIZE)

# ウィンドウタイトルの設定
pygame.display.set_caption(TITLE)
# フォントサイズの設定
font = pygame.font.Font(None, 55)

clock = pygame.time.Clock()

def show_game_button(buttons):
    for button in buttons:
        # 文字
        text = font.render(GAME_BUTTON_LABELS[button], True, GAME_BUTTON_COLOR)

        # ボタン
        # TODO: 文字色変更
        xy = GAME_BUTTON
        xy[1] *= button
        button   = pygame.Rect(*xy)

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

# タイトル画面
def title(refreshbgm=True):
    # BGM開始
    if refreshbgm:
        liboption.playbgm(0)

    # ボタン
    start_button = pygame.Rect(*SIZE_START_BUTTON)
    config_button = pygame.Rect(*SIZE_CONFIG_BUTTON)
    startimg = pygame.image.load(PATH_IMG_START_BUTTON)
    configimg = pygame.image.load(PATH_IMG_CONFIG_BUTTON)

    # 背景画像
    #bgimg = pygame.image.load("bgimg/title.png")
    collide_start_button = False

    frame = 0
    bairitsu = 1
    bgimg = pygame.image.load("anime/title/nm_"+str(int(frame/bairitsu)).zfill(4)+".bmp")

    while True:
        clock.tick(30) #フレームレートの宣言，重要！ これがないとかなり重くなる
        screen.blit(bgimg, (0, 0)) # 左上座標
        screen.blit(startimg, (SIZE_START_BUTTON[0], SIZE_START_BUTTON[1]+5))
        screen.blit(configimg, (SIZE_CONFIG_BUTTON[0], SIZE_CONFIG_BUTTON[1]+5))

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
                    return 3#2 #2:さんまか四麻の選択画面, 3:ゲーム開始(4麻固定)
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

# 未使用
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
        screen.blit(san_text, [275, 510])

        pygame.display.update()
        # イベント処理
        for event in pygame.event.get():
            if event.type == QUIT:  # 終了イベント
                liboption.exitgame()
            
            if event.type == MOUSEBUTTONDOWN:
                if yon_button.collidepoint(event.pos):
                    game(init=True)
                    return 0
                elif san_button.collidepoint(event.pos):
                    game(init=True, playernum=3)
                    return 0


def game(init=False, playernum=4, sibari=0):

    liboption.playbgm(1)

    # Dots      : 1~9 : 筒子
    # Bamboo    : 11~19 : 索子
    # Characters: 21~29 : 萬子
    # Dragons   : 0, 10, 20 : 白，ハツ，中
    # Winds     : 30, 31, 32, 33 : 東，南，西，北


    # === ゲーム初期設定 =========

    # 回をまたいで持ち越さない情報のみを持つクラス
    players = [] # player, 下家, 対面, 上家

    # 洗牌
    wall = [i for i in range(34) for j in range(4)]
    random.shuffle(wall)

    # 初回のみ
    if init:
        # 場風
        prevailing_wind = 30
        # 親決定
        oya = random.randint(0, 3)
    
    # 配牌
    for i in range(playernum):
        wind = ((4-oya)%4+i)%4+30 # 三麻に未対応
        players.append(libmahjong.Player(tiles=wall[0:13], pos=i, wind=wind))
        del wall[0:13]

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

    # TODO: ドラ表示(GUI)
    print("ドラは", nanno_koma(bonus_tile))


    #開始時アニメーション
    screen.fill((20,20,20))
    # 左上にGAMEと表示する TODO:背景画像表示に変更
    text = font.render("GAME", True, (222, 222, 222))
    screen.blit(text, [100, 100])

    pygame.display.update()

    # TODO: 親からはじめる
    if oya != 0:
        for i in range(oya, player_num):
            hand = wall.pop()
            yaku = check_yaku(players[i], hand)

            if len(yaku) != 0:
                if i == oya:
                    tmp_yaku = [38] # 天和
                else:
                    tmp_yaku = [34] # 地和
                
                result_num = result(tmp_yaku, players[i].hands, hand, [i])
                return result_num

            players[i].add(hand)

            discard_tile = scraps[i].think(players[i].hands)
            players[i].discard(discard_tile)

            players[i].show_tiles(screen)
            players[i].show_rivers(screen)

            pygame.display.update()

    
    hand = wall.pop()
    players[0].add(hand)

    # 手牌の表示
    for i in range(playernum):
        players[i].show_tiles(screen)
    
    pygame.display.update()

    # TODO: 天和・ちほーの判定
    
    while True:
        clock.tick(30)

        # 1枚捨てる
        # イベント処理
        for event in pygame.event.get():
            if event.type == QUIT:  # 終了イベント
                liboption.exitgame()
            
            if event.type == MOUSEBUTTONDOWN:

                # 山から1枚とり、手牌を捨てる
                discarded_idx = players[0].check_discard(event.pos)

                if discarded_idx != -1:
                    players[0].discard_idx(discarded_idx)
                    players[0].show_tiles(screen)
                    players[0].show_rivers(screen)

                    pygame.display.update()
                    
                    #順番にツモる
                    for i in range(1, playernum):
                        hand = wall.pop()
                        players[i].add(hand)
                        discard_tile = scraps[i].think(players[i].hands)

                        # ツモアガりの判定
                        if discard_tile == -1:
                            result_num = result(yaku, players[i].hands, hand, [i])
                            return result_num
                        
                        players[i].discard(discard_tile)
                        
                        # ロンアガりの判定 =======
                        ron = []
                        yakus = []
                        for j in range(player_num):
                            if j == i:
                                continue
                            
                            # 未テスト
                            yaku = check_yaku(players[j], discarded_tile, tumo=False)
                            if len(yaku) != 0:
                                if j == 0:
                                    game_buttons.append(1)
                                else:
                                    # TODO: ロンするかどうか
                                    ron.append(j)
                                    yakus.append(yaku)
                        
                        if len(ron) != 0:
                            if len(ron) == 1 and ron[0] == 0:
                                pass # ロンするかどうか、ポンとかの判定と一緒に判定する
                            else:
                                # 他家がロンした場合、自家もロンする
                                result_num = result(yaku, players[i].hands, hand, ron, i, tumo=False)
                                return result_num
                        # ロンあがりの判定 ここまで ========


                        # ポン,カンの判定 ========
                        pongs = -1
                        kongs = -1
                        # TODO: ポンとカンのボタンを並べて表示
                        for j in range(player_num):
                            if i == j:
                                continue
                            
                            tiles_count = players[j].hands.tiles.count(discard_tile)
                            if tiles_count >= 2:
                                
                                # ポンのボタン表示
                                if j == 0:
                                    pongs = 0
                                    if tiles_count >= 3:
                                        kongs = 0
                                        game_buttons.append(4)
                                    game_buttons.append(2)
                                    break
                                else:
                                    # (自家がロンせずに、ポンできるとして)ポンするかどうか判定
                                    pongs = j
                                    if tiles_count >= 3:
                                        kongs = j
                                    break
                                
                        # 判定待ち
                        if len(ron) == 1 and ron[0] == 0 and pongs != 0 and pongs != -1:
                            # 他家がポンしようとしている場合かつ自家がロンできる場合、ロンするかどうかボタン表示
                            show_game_button(game_buttons)
                            pygame.display.update()

                            # TODO: クリック待ちの実装
                            if event.type == MOUSEBUTTONDOWN:
                                pass
                        
                        # ポンする
                        if pongs != -1 and pongs != 0:
                            pass
                        # ポンの判定 ここまで ========
                        else:
                            # チーの判定 ========
                            # チーの判定 ここまで ========

                        players[i].show_tiles(screen)
                        players[i].show_rivers(screen)
                        print(i, players[i].hands.discarded_tiles)
                    pygame.display.update()
                    
                    hand = wall.pop()
                    players[0].add(hand)

                    # シャンテン数の判定
                    # つもった牌を除く、どれか1つの牌を捨てた場合にテンパイとなる場合、playerにテンパイフラグを付与？
                    # 立直ボタンを設置、クリックしたら該当する牌しか捨てられないようにする

# 結果画面                    
def result(yaku, hands, last_tile, player_num, to_player_num=-1, tumo=True):

    # 戻り値: 画面番号(ゲーム続行なら4, 終了なら0(タイトル画面))
    # 点数計算

    # 点数差し引き

    # 続行判定

    # 場風と親の更新

    pass


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
    elif stats == 3:
        stats = game(init=True)
    elif stats == 4:
        stats = game()