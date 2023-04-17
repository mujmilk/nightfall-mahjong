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
GAME_BUTTON = [10, 10, 100, 60] # [左上x座標, 左上y座標, 横幅, 縦幅]
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
oya = 0
# 局
kyoku = 1
# 起家
first_oya = 0
# 本場
honba = 0
# 点数
points = [35000 for i in range(4)]
# AIs
scraps = [0]
# game button
game_buttons = []

for i in range(4): #playerの最大数が4
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
font = pygame.font.Font('sysimg/fonts/PixelMplus12-Regular.ttf', 30)
ui_font = pygame.font.Font('sysimg/fonts/x8y12pxTheStrongGamer.ttf', 40)

clock = pygame.time.Clock()

def show_game_button(buttons, screen):

    xy = GAME_BUTTON

    xys = []
    texts = []
    button_rects = []

    for button in buttons:
        # 文字
        text = font.render(GAME_BUTTON_LABELS[button], True, GAME_BUTTON_COLOR)
        screen.blit(text, xy[0:2])

        xys.append(xy[0:2])
        texts.append(text)
        button_rects.append(pygame.Rect(*xy))
        xy[1] *= button
    pygame.display.update()

    # クリック待ち
    # ボタン以外の部分がクリックされたらスキップ
    while True:
        clock.tick(30)
        for i in range(len(buttons)):
            # 文字
            pygame.draw.rect(screen, (80, 0, 80), button_rects[i])
            screen.blit(texts[i], xys[i])
        pygame.display.update()

        # イベント処理
        for event in pygame.event.get():
            if event.type == QUIT:  # 終了イベント
                liboption.exitgame()
            
            if event.type == MOUSEBUTTONDOWN:

                for i in range(len(button_rects)):
                    if button_rects[i].collidepoint(event.pos):
                        return buttons[i]
                return -1

def nanno_koma(n): # testok
    s = ""
    if n >= 30:
        namelist = ["東", "南", "西", "北"]
        s += namelist[n - 30]
    elif n % 10 == 0:
        namelist = ["白", "發", "中"]
        s += namelist[int(n / 10)]
    elif n < 10:
        namelist = ["一", "二", "三", "四", "五", "六", "七", "八" ,"九"]
        s += namelist[n % 10 - 1] + "萬"
    else:
        if n >= 20:
            s += "索子(ソーズ)の"
        else:
            s += "筒子(ピンズ)の"
        s += str(n%10)
    return s

def nanno_koma_list(tiles):
    l = []
    for t in tiles:
        l.append(nanno_koma(t))
    return l

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

    # Characters: 1~9   : 萬子(マンズ)
    # Dots      : 11~19 : 筒子(ピンズ)
    # Bamboo    : 21~29 : 索子(ソーズ)
    # Dragons   : 0, 10, 20 : 白，ハツ，中
    # Winds     : 30, 31, 32, 33 : 東，南，西，北

    # === ゲーム初期設定 =========

    # 回をまたいで持ち越さない情報のみを持つクラス
    players = [] # player, 下家, 対面, 上家

    # 洗牌
    wall = [i for i in range(34) for j in range(4)]

    
    open_pos = []

    test = False#True
    if not test:
        random.shuffle(wall)

    # 初回のみ
    if init:
        # 場風
        prevailing_wind = 30
        # 親決定
        oya = random.randint(0, 3)
        # 起家
        first_oya = oya
        # 局数
        kyoku = 1
    
    # TODO: 表示
    print('親:', oya, libmahjong.nanno_koma(prevailing_wind), oya,first_oya, '局', honba, '本場')
    
    # 配牌
    if test:
        for i in range(playernum):
            wind = ((4-oya)%4+i)%4+30 # 三麻に未対応
            players.append(libmahjong.Player(tiles=wall[0:13], pos=i, wind=wind))
            del wall[0:13]
    else:
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

    # 背景描画
    screen.fill((20,20,20))

    # TODO: ドラ表示(GUI)
    print("【ドラ", nanno_koma(bonus_tile), "】")
    bonus_tiles = [bonus_tile]

    text = font.render(libmahjong.nanno_koma(prevailing_wind)+str(kyoku)+'局'+str(honba)+'本場', True, (222, 222, 222))
    screen.blit(text, [SCREEN_SIZE[0]//2-100, SCREEN_SIZE[1]//2-20])
    libmahjong.show_all_tiles(screen, players, open_pos=open_pos, test=False)
    pygame.display.update()

    # TODO: ポン・チー・カンの判定
    skip_flag = -1

    if oya != 0:
        for i in range(oya, playernum):
            hand = wall.pop()
            players[i].add(hand)
            yaku = libmahjong.check_yaku(players[i], hand, prevailing_wind, bonus_tiles)

            if len(yaku) != 0:
                if i == oya:
                    tmp_yaku = [38] # 天和
                else:
                    tmp_yaku = [34] # 地和
                
                result_num = result([tmp_yaku], [i])
                return result_num

            players[i].add(hand)

            discard_tile = scraps[i].think(players[i], hand, prevailing_wind, bonus_tiles)
            players[i].discard(discard_tile)
            
            print('player:', i, ',code 1')
            libmahjong.show_all_tiles(screen, players, open_pos=open_pos, test=True)

            # TODO: ロン・ポン・チーの判定

            libmahjong.show_all_tiles(screen, players)
            pygame.display.update()

    
    hand = wall.pop()
    players[0].add(hand)

    # 手牌の表示
    libmahjong.show_all_tiles(screen, players)
    yaku = libmahjong.check_yaku(players[0], hand, prevailing_wind, bonus_tiles)
    pygame.display.update()

    if len(yaku) != 0:
        if oya == 0:
            tmp_yaku = [38] # 天和
        else:
            tmp_yaku = [34] # 地和
        
        game_buttons.append(0)
        return_button = show_game_button(game_buttons, screen)
        game_buttons.clear()
        
        if return_button == 0:
            return_button = -1
            result_num = result([tmp_yaku], [i])
            return result_num
    
    # カン判定
    tiles_uniqs = list(set(players[0].hands.tiles))
    tiles_count = [players[0].hands.tiles.count(tiles_uniqs[i]) for i in range(len(tiles_uniqs))]
    yon_tiles = []
    for idx_tiles_count in range(len(tiles_count)):
        if tiles_count[idx_tiles_count] == 4:
            yon_tiles.append(tiles_uniqs[idx_tiles_count])
    if len(yon_tiles) != 0:
        game_buttons = [4]
        return_button = show_game_button(game_buttons, screen)
        if return_button == 4:
            selecting_flag = (len(yon_tiles) != 1)
            
            if selecting_flag:
                while selecting_flag:
                    clock.tick(30)
                    for event in pygame.event.get():
                        if event.type == QUIT:  # 終了イベント
                            liboption.exitgame()
                        
                        if event.type == MOUSEBUTTONDOWN:
                            yon_discarded_idx = players[0].check_discard(event.pos)
                            if players[0].hands.tiles[yon_discarded_idx] in yon_tiles:
                                players[0].kong(players[0].hands.tiles[yon_discarded_idx], 0)
                                selecting_flag = False
            else:
                players[0].kong(yon_tiles[0], 0)
            
            hand = wall.pop()
            players[0].add(hand)

            yaku = libmahjong.check_yaku(players[0], hand, prevailing_wind, bonus_tiles, rinshan=True)
            
            libmahjong.show_all_tiles(screen, players)
            pygame.display.update()

            # 嶺上開花 未テスト
            if len(yaku) != 0:
                game_buttons = [0]
                return_button = show_game_button(game_buttons, screen)
                game_buttons.clear()
                
                if return_button == 0:
                    return_button = -1
                    result_num = result([yaku], [0])
                    return result_num

            libmahjong.show_all_tiles(screen, players)
            pygame.display.update()

        return_button = -1
        game_buttons.clear()
    
    rinshan_flag = False

    while True:
        clock.tick(30)

        screen.fill((20,20,20))
        text = font.render(libmahjong.nanno_koma(prevailing_wind)+str(kyoku)+'局'+str(honba)+'本場', True, (222, 222, 222))
        screen.blit(text, [SCREEN_SIZE[0]//2-100, SCREEN_SIZE[1]//2-20])
        libmahjong.show_all_tiles(screen, players, open_pos=open_pos, test=False)
        pygame.display.update()

        # 1枚捨てる
        # イベント処理
        for event in pygame.event.get():

            if event.type == KEYDOWN:
                if event.key == K_LEFT or event.key == K_3:
                    if 3 in open_pos:
                        open_pos.remove(3)
                    else:
                        open_pos.append(3)
                    liboption.playse('select')
                
                if event.key == K_RIGHT or event.key == K_1:
                    if 1 in open_pos:
                        open_pos.remove(1)
                    else:
                        open_pos.append(1)
                    liboption.playse('select')

                if event.key == K_UP or event.key == K_2:
                    if 2 in open_pos:
                        open_pos.remove(2)
                    else:
                        open_pos.append(2)
                    liboption.playse('select')

            if event.type == QUIT:  # 終了イベント
                liboption.exitgame()
            
            if event.type == MOUSEBUTTONDOWN or skip_flag != -1:
                
                if skip_flag == -1 or skip_flag == 0:
                    
                    skip_flag = -1

                    # 山から1枚とり、手牌を捨てる
                    discarded_idx = players[0].check_discard(event.pos)
                    game_buttons = []

                    if discarded_idx == -1:
                        continue

                if (players[0].riichi == -1 and discarded_idx != -1) or (players[0].riichi != -1 and discarded_idx == 13):

                    if skip_flag == -1 or skip_flag == 0:
                        players[0].discard_idx(discarded_idx)
                    
                        print('player:', 0, 'code 0')
                        libmahjong.show_all_tiles(screen, players, open_pos=open_pos, test=True)
                        # TODO: ここで牌をソートする
                        pygame.display.update()
                    
                    #順番にツモる
                    for i in range(1, playernum):

                        if skip_flag == 0:
                            break
                        
                        if skip_flag != -1:
                            if skip_flag != i:
                                continue

                        # 流局判定
                        if len(wall) == 0:
                            # テンパイしているかどうか調査
                            tenpai_players = []
                            to_players = [i for i in range(playernum)]
                            for j in range(playernum):
                                shanten = libmahjong.check_hands(players[j].hands, players[j].menzen)
                                if shanten <= 1:
                                    tenpai_players.append(j)
                                    to_players.remove(j)
                            
                            result_num = result([[39]], tenpai_players, to_player_num=to_players, tumo=False)
                            return result_num

                        hand = wall.pop()
                        players[i].add(hand)

                        yaku = libmahjong.check_yaku(players[i], hand, prevailing_wind, bonus_tiles, rinshan=rinshan_flag)
                        rinshan_flag = False

                        # === 槍槓 ===
                        add_kong_flag = False
                        for k in range(len(players[i].hands.pong_tiles)):
                            if hand in players[i].hands.pong_tiles[k].tiles:
                                add_kong_flag = True
                                break
                        
                        skip_flag = -1
                        if add_kong_flag:
                            kong_flag = scraps[i].think_furo(players[i].hands, hand)
                            if kong_flag:
                                players[i].kong(hand, i, add=True)
                                skip_flag = i
                                
                                tmp_bonus_tile = wall.pop() # 最後だった場合おかしくなる
                                if tmp_bonus_tile >= 30:
                                    tmp_bonus_tile = 30 + (bonus_tile % 30 + 1) % 4
                                elif tmp_bonus_tile % 10 == 0:
                                    tmp_bonus_tile = (bonus_tile + 10) % 30
                                elif tmp_bonus_tile % 10 == 9:
                                    tmp_bonus_tile -= 8
                                else:
                                    tmp_bonus_tile += 1
                                bonus_tiles.append(tmp_bonus_tile)
                                print("0 ドラ追加:", nanno_koma(tmp_bonus_tile))

                                rinshan_flag = True
                                add_kong_flag = False
                                continue
                        else:
                            # カンするかどうか(ツモ時)
                            kong_flag = False
                            for tile in list(set(players[i].hands.tiles)):
                                if players[i].hands.tiles.count(tile) >= 4:
                                    kong_flag = scraps[i].think_furo(players[i].hands, tile)
                                    if kong_flag:
                                        players[i].kong(tile, i)
                                        skip_flag = i
                                        
                                        tmp_bonus_tile = wall.pop() # 最後だった場合おかしくなる
                                        if tmp_bonus_tile >= 30:
                                            tmp_bonus_tile = 30 + (bonus_tile % 30 + 1) % 4
                                        elif tmp_bonus_tile % 10 == 0:
                                            tmp_bonus_tile = (bonus_tile + 10) % 30
                                        elif tmp_bonus_tile % 10 == 9:
                                            tmp_bonus_tile -= 8
                                        else:
                                            tmp_bonus_tile += 1
                                        bonus_tiles.append(tmp_bonus_tile)
                                        print("1 ドラ追加:", nanno_koma(tmp_bonus_tile))

                                        rinshan_flag = True
                                        kong_flag = True
                                        break
                            if kong_flag:
                                kong_flag = False
                                continue
                        
                        discard_tile = scraps[i].think(players[i], hand, prevailing_wind, bonus_tiles)

                        # ツモアガりの判定
                        if discard_tile == -1:
                            # はいていつも
                            if len(wall) == 0:
                                yaku.append(8)
                            
                            result_num = result([yaku], [i])
                            return result_num
                        
                        players[i].discard(discard_tile)
                        print('player:', i, 'code 2')
                        libmahjong.show_all_tiles(screen, players, open_pos=open_pos, test=True)
                        
                        # ロンアガりの判定 =======
                        ron = []
                        yakus = []
                        for j in range(playernum):
                            if j == i:
                                continue
                            
                            if discard_tile in players[j].hands.discarded_tiles or discard_tile in players[j].hands.discarded_tiles_not_shown:
                                continue
                            
                            yaku = libmahjong.check_yaku(players[j], discard_tile, prevailing_wind, bonus_tiles, tumo=False)
                            if len(yaku) != 0:
                                if j == 0:
                                    ron.append(0)
                                    yakus.append(yaku)
                                    game_buttons.append(1)
                                else:
                                    ron.append(j)
                                    yakus.append(yaku)
                        
                        if len(ron) != 0:
                            if len(ron) == 1 and ron[0] == 0:
                                pass # ロンするかどうか、ポンとかの判定と一緒に判定する
                            else:
                                # 他家がロンした場合、自家もロンする
                                result_num = result(yakus, ron, to_player_num=[i], tumo=False, playernum=playernum)
                                return result_num
                        # ロンあがりの判定 ここまで ========


                        # ポン,カンの判定 タイミング:捨て========
                        pongs = -1
                        kongs = -1

                        for j in range(playernum):
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
                                    #furo = players[j].think_furo(players[j].hands, discard_tile)

                                    pongs = j
                                    if tiles_count >= 3: # TODO:カンするなら
                                        kongs = j
                                        pongs = -1
                                    break
                        
                        libmahjong.show_all_tiles(screen, players, open_pos=open_pos, test=False)
                        pygame.display.update()

                                
                        # 判定待ち
                        if len(ron) == 1 and ron[0] == 0 and ((pongs != 0 and pongs != -1) or (kongs != -1 and kongs != 0)):
                            # 他家がポンまたはカンしようとしている場合かつ自家がロンできる場合、ロンするかどうかボタン表示
                            return_button = show_game_button(game_buttons, screen)
                            game_buttons.clear()
                            if return_button != -1:
                                return_button = -1
                                result_num = result(yakus, ron, to_player_num=[i], tumo=False)
                                return result_num
                        
                        # ポンする
                        if pongs != -1 and pongs != 0:
                            pong_flag = scraps[pongs].think_furo(players[pongs].hands, discard_tile, tumo=False)
                            if pong_flag:
                                players[pongs].pong(discard_tile, i)
                                players[i].discard_to_not_shown(discard_tile)
                                skip_flag = pongs
                                
                                libmahjong.show_all_tiles(screen, players, open_pos=open_pos, test=False)
                                pygame.display.update()

                                continue
                        
                        # カンする
                        if kongs != -1 and kongs != 0:
                            kong_flag = scraps[kongs].think_furo(players[kongs].hands, discard_tile, tumo=False)
                            if kong_flag:
                                players[kongs].kong(discard_tile, i)
                                players[i].discard_to_not_shown(discard_tile)
                                skip_flag = kongs
                                
                                tmp_bonus_tile = wall.pop()
                                #print("ドラ表示牌は", bonus_tile)
                                #bonus_tileimg = TILES[bonus_tile] #表示用
                                if tmp_bonus_tile >= 30:
                                    tmp_bonus_tile = 30 + (bonus_tile % 30 + 1) % 4
                                elif tmp_bonus_tile % 10 == 0:
                                    tmp_bonus_tile = (bonus_tile + 10) % 30
                                elif tmp_bonus_tile % 10 == 9:
                                    tmp_bonus_tile -= 8
                                else:
                                    tmp_bonus_tile += 1
                                bonus_tiles.append(tmp_bonus_tile)
                                print("2 ドラ追加:", nanno_koma(tmp_bonus_tile))

                                libmahjong.show_all_tiles(screen, players, open_pos=open_pos, test=False)
                                pygame.display.update()

                                rinshan_flag = True
                                continue
                        # ポン,カンの判定 ここまで ========
                        #else: #何このelse?
                            #pass

                        # チーの判定 ================
                        chow_tiles = []
                        # チーの判定 ここまで ========

                        # ロン・ポン・チー・カン(他家から)をまとめて表示
                        
                        libmahjong.show_all_tiles(screen, players, open_pos=open_pos, test=False)
                        pygame.display.update()

                        if len(game_buttons) != 0:
                            return_button = show_game_button(game_buttons, screen)
                            game_buttons.clear()
                            if return_button != -1:
                                if return_button == 1:
                                    result_num = result(yakus, ron, to_player_num=[i], tumo=False)
                                    return result_num
                                elif return_button == 2:
                                    players[0].pong(discard_tile, i)
                                    players[i].discard_to_not_shown(discard_tile)
                                elif return_button == 3:
                                    players[0].chow(chow_tiles, i)
                                    players[i].discard_to_not_shown(discard_tile)
                                elif return_button == 4:
                                    players[0].kong(discard_tile, i)
                                    players[i].discard_to_not_shown(discard_tile)
                                
                                return_button = -1
                    
                        # 流局判定
                        if len(wall) == 0:
                            # テンパイしているかどうか調査
                            tenpai_players = []
                            to_players = [i for i in range(playernum)]
                            for j in range(playernum):
                                shanten = libmahjong.check_hands(players[j].hands, players[j].menzen)
                                if shanten <= 1:
                                    tenpai_players.append(j)
                                    to_players.remove(j)
                            
                            result_num = result([[39]], tenpai_players, to_player_num=to_players, tumo=False)
                            return result_num

                    if skip_flag == -1 or skip_flag == 0:
                        skip_flag = -1

                        hand = wall.pop()
                        players[0].add(hand)

                        # カン判定
                        tiles_uniqs = list(set(players[0].hands.tiles))
                        tiles_count = [players[0].hands.tiles.count(tiles_uniqs[i]) for i in range(len(tiles_uniqs))]
                        yon_tiles = []
                        for idx_tiles_count in range(len(tiles_count)):
                            if tiles_count[idx_tiles_count] == 4:
                                yon_tiles.append(tiles_uniqs[idx_tiles_count])
                        if len(yon_tiles) != 0:
                            game_buttons = [4]
                            return_button = show_game_button(game_buttons, screen)
                            game_buttons.clear()
                            if return_button == 4:
                                selecting_flag = (len(yon_tiles) != 1)
                                
                                if selecting_flag:
                                    while selecting_flag:
                                        clock.tick(30)
                                        for event in pygame.event.get():
                                            if event.type == QUIT:  # 終了イベント
                                                liboption.exitgame()
                                            
                                            if event.type == MOUSEBUTTONDOWN:
                                                yon_discarded_idx = players[0].check_discard(event.pos)
                                                if players[0].hands.tiles[yon_discarded_idx] in yon_tiles:
                                                    players[0].kong(players[0].hands.tiles[yon_discarded_idx], 0)
                                                    selecting_flag = False
                                else:
                                    players[0].kong(yon_tiles[0], 0)

                                # 嶺上開花 未テスト
                                rinshan_flag = True
                            return_button = -1
                            game_buttons.clear()

                        # ツモあがりの判定
                        yaku = libmahjong.check_yaku(players[0], hand, prevailing_wind, bonus_tiles, rinshan=rinshan_flag)
                        rinshan_flag = False

                        if len(yaku) != 0:
                            game_buttons = [0]
                            return_button = show_game_button(game_buttons, screen)
                            game_buttons.clear()
                
                            if return_button == 0:
                                result_num = result([yaku], [0], playernum=playernum)
                                return result_num
                            
                            return_button = -1
                        
                        tenpai_hai = libmahjong.tenpai_hai_check(players[0])


# 結果画面                  
# 龍局の場合、テンパイ人を  
def result(yakus, player_num, to_player_num=[], tumo=True, playernum=4):
    global oya
    global honba
    global kyoku

    # 戻り値: 画面番号(ゲーム続行なら4, 終了なら0(タイトル画面))
    # 点数計算
    
    if [39] in yakus:
        if len(player_num) == playernum:
            pass
        elif len(player_num) == 1:
            for i in to_player_num:
                points[i] -= 1000
            for i in player_num:
                points[i] += 3000
        elif len(player_num) == 2:
            for i in to_player_num:
                points[i] -= 1500
            for i in player_num:
                points[i] += 1500
        elif len(player_num) == 3:
            for i in to_player_num:
                points[i] -= 3000
            for i in player_num:
                points[i] += 1000
        
    elif tumo:
        if len(yakus) != 1 or len(player_num) != 1:
            print('err result func')
        
        sorted_yaku = sorted(yakus[0])
        get_points_oya_ko = libmahjong.calc_points(sorted_yaku, tumo=True)
        get_points = get_points_oya_ko[0]
        if oya != player_num[0]:
            get_points = get_points_oya_ko[1]

        # 点数差し引き
        get_total_points = get_points * (playernum - 1)
        for i in range(playernum):
            if player_num[0] == i:
                continue
            points[i] -= get_points
        points[player_num[0]] += get_total_points
    else:
        if len(to_player_num) == 0:
            print('err to_player_num is []')
        
        sorted_yakus = []
        get_points = []

        for player_idx in range(len(player_num)):
            sorted_yaku = sorted(yakus[player_idx])
            sorted_yakus.append(sorted_yaku)
            get_points_oya_ko = libmahjong.calc_points(sorted_yaku, oya=(oya==player_num[player_idx]))
            
            if oya == to_player_num[0]:
                points[to_player_num[0]] -= get_points_oya_ko[0]
                points[player_num[player_idx]] += get_points_oya_ko[0]
            else:
                points[to_player_num[0]] -= get_points_oya_ko[1]
                points[player_num[player_idx]] += get_points_oya_ko[1]
    
    # 点数表示
    # 文字
    text = font.render("結果", True, (222, 222, 222))
    screen.fill((20,20,20))
    screen.blit(text, [100, 100])
    xy = [150, 150]

    # 対象
    for i in to_player_num:
        text = font.render(': プレイヤー'+str(i), True, (222, 222, 222))
        screen.blit(text, xy)
        xy[1] += 30

    # あがった人
    for i in range(len(player_num)):
        text = font.render('プレイヤー'+str(player_num[i]), True, (222, 222, 222))
        screen.blit(text, xy)
        xy[0] += 100
        xy[1] += 30

        yakunames = libmahjong.yaku_names(yakus[i])
        text = font.render(yakunames, True, (222, 222, 222))
        screen.blit(text, xy)
        xy[0] -= 100
        xy[1] += 50
        

    pygame.display.update()

    while True:
        clock.tick(30)

        # イベント処理
        break_flag = False
        for event in pygame.event.get():
            if event.type == QUIT:  # 終了イベント
                liboption.exitgame()
            
            if event.type == MOUSEBUTTONDOWN:
                break_flag = True
                break
        if break_flag:
            break
    
    # 続行判定
    return_num = 0

    for i in range(playernum): #飛び判定
        if points[i] <= 0:
            return_num = 5
            return return_num

    if [39] in yakus:
        if oya in player_num:
            honba += 1
        else:
            oya = (oya + 1) % playernum
            honba += 1
            kyoku += 1
            if oya == first_oya:
                if prevailing_wind == 30:
                    prevailing_wind = 31
                    kyoku = 1
                    return_num = 4 #game(init=False)
                elif prevailing_wind == 31:
                    return_num = 5 #result_all()
                else:
                    print('err result next')
    else:
        if oya in player_num:
            honba += 1
        else:
            oya = (oya + 1) % playernum
            honba = 0
            kyoku += 1
            if oya == first_oya:
                if prevailing_wind == 30:
                    prevailing_wind = 31
                    kyoku = 1
                    return_num = 4 #game(init=False)
                elif prevailing_wind == 31:
                    return_num = 5 #result_all()
                else:
                    print('err result next')

    return return_num

# 結果表示
def result_all():
    # 点数表示
    # タイトル画面へ、終了 の2つのボタンの表示

    # 文字
    yon_text = font.render("タイトル画面へ", True, (222, 222, 222))
    san_text = font.render("終了", True, (222, 222, 222))

    # ボタン
    yon_button   = pygame.Rect(250, 360, 300, 60)
    san_button   = pygame.Rect(250, 500, 300, 60)

    while True:
        clock.tick(30)
        screen.fill((20,20,20))

        pygame.draw.rect(screen, (80, 80, 80), yon_button)
        pygame.draw.rect(screen, (80, 80, 80), san_button)

        screen.blit(yon_text, [275, 375])
        screen.blit(san_text, [275, 510])

        pygame.display.update()
        # イベント処理
        for event in pygame.event.get():
            if event.type == QUIT:  # 終了イベント
                liboption.exitgame()
            
            if event.type == MOUSEBUTTONDOWN:
                if yon_button.collidepoint(event.pos):
                    liboption.exitgame()
                elif san_button.collidepoint(event.pos):
                    return 0

# main
stats = 0 # 0:title, 1:option, 2:menu, 3:custommenu, 4:game, 5:result
settings_game = []
settings_option = []

while True:
    print('stats:', stats)
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
    elif stats == 5:
        stats = result_all()