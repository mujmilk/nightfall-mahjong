import sys
import pygame
from pygame.locals import *
import copy

import random

# "sysimg/open_tiles/"+TILES[n]+"_"+str(i)+".gif"
TILES = ["p_no_", "p_ms1_", "p_ms2_", "p_ms3_", "p_ms4_", "p_ms5_", "p_ms6_", "p_ms7_", "p_ms8_", "p_ms9_",
         "p_ji_h_", "p_ps1_", "p_ps2_", "p_ps3_", "p_ps4_", "p_ps5_", "p_ps6_", "p_ps7_", "p_ps8_", "p_ps9_",
         "p_ji_c_", "p_ss1_", "p_ss2_", "p_ss3_", "p_ss4_", "p_ss5_", "p_ss6_", "p_ss7_", "p_ss8_", "p_ss9_",
         "p_ji_e_", "p_ji_s_", "p_ji_w_", "p_ji_n_"]

# テスト用色分け
POS_COLORS = [(222, 50, 50), (50, 222, 50), (50, 50, 222), (222, 50, 222)]

IMG_SIZE = {
    0: {'size_x': 33, 'size_y': 60, 'x':20, 'y':520, 'dx':33, 'dy':0}, # 自家通常
    1: {'size_x': 26, 'size_y': 25, 'x':754, 'y':200, 'dx':0, 'dy':25},# 下家通常
    2: {'size_x': 33, 'size_y': 59, 'x':300, 'y':20, 'dx':33, 'dy':0},# 対面通常
    3: {'size_x': 26, 'size_y': 25, 'x':20, 'y':40, 'dx':0, 'dy':-25}, # 上家通常

    4: {
        'size_x': 33, 'size_y': 59,
        'x':250, 'y':350, 'dx':33, 'dy':0,
        'new_dx':0, 'new_dy':50,
        'rev_flag':0
        }, # 自家河
    5: {
        'size_x': 44, 'size_y': 49, 
        'x':690, 'y':170, 'dx':0, 'dy':40, 
        'new_dx':-44, 'new_dy':0,
        'rev_flag':1
        }, # 下家河 逆
    6: {
        'size_x': 33, 'size_y': 59, 
        'x':250, 'y':110, 'dx':33, 'dy':0, 
        'new_dx':0, 'new_dy':50,
        'rev_flag':1
        }, # 対面河 逆
    7: {
        'size_x': 44, 'size_y': 49, 
        'x':180, 'y':170, 'dx':0, 'dy':35, 
        'new_dx':-44, 'new_dy':0,
        'rev_flag':0
        }, # 上家河
}

# TODO: 画像ナンバリングし直し
IMG_NUM = {
    4: 1,
    5: 3,
    6: 2,
    7: 4
}

# 副露牌を管理するクラス
class Furo:
    def __init__(self, from_pos, tiles):
        self.from_pos = from_pos
        self.tiles = tiles

# =======================
# 衝突判定
# =======================
# 四角形1つ1つのクラス
class TileSprite(pygame.sprite.Sprite):
    def __init__(self, width, height, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(x, y, width, height)

    def check(self, pos):
        return self.rect.collidepoint(pos)

# == テスト用 =============================
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
# == テスト用関数 ここまで ======================


# tilesからまとめてスプライトを生成するクラス: player用
class TileSprites:
    def __init__(self, tiles_num, width, height, x, y, dx=33, dy=0):
        
        self.tiles = []

        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy

        xx = x
        yy = y

        for t in range(tiles_num):
            self.tiles.append(TileSprite(width, height, xx, yy))
            
            xx += dx # imgtype: 0の画像の横の長さ
            yy += dy

            if t >= 12:
                xx += dx # imgtype: 0の画像の横の長さ
                yy += dy
        
        self.xx = xx
        self.yy = yy

    def checkall(self, pos):
        for i in range(len(self.tiles)):
            if self.tiles[i].check(pos):
                return i
        return -1
    
    def adjust(self, tiles_num):
        # (時間あれば)todo:1個ずつ削除する方式に変更する
        for i in range(len(self.tiles)-1, -1, -1):
            self.tiles[i].kill()
        self.tiles.clear()

        self.xx = self.x
        self.yy = self.y

        for t in range(tiles_num):
            self.tiles.append(TileSprite(self.width, self.height, self.xx, self.yy))
            
            self.xx += self.dx # imgtype: 0の画像の横の長さ
            self.yy += self.dy

            if t == tiles_num - 2:
                self.xx += self.dx # imgtype: 0の画像の横の長さ
                self.yy += self.dy

    def remove_one(self):
        self.xx -= self.dx
        self.yy -= self.dy
        if len(self.tiles) >= 13:
            self.xx -= self.dx
            self.yy -= self.dy
        del self.tiles[-1]
    
    def add_one(self):
        self.tiles.append(TileSprite(self.width, self.height, self.xx, self.yy))
        
        self.xx += self.dx
        self.yy += self.dy

        if len(self.tiles) >= 13:
            self.xx += self.dx
            self.yy += self.dy
    

# =======================
# 手牌管理
# =======================
class Hands:
    # tiles: 持ち牌
    # pos: 
    # wind: 
    def __init__(self, tiles, wind):
        self.tiles = tiles
        self.wind = wind
        self.pong_tiles = []
        self.chow_tiles = []
        self.kong_tiles = []

        self.discarded_tiles = []
        self.discarded_tiles_not_shown = []
    
    def sort_hands(self):
        pass
    
    def discard(self, tile):
        if tile not in self.tiles:
            print('error: tile not in players hand')
            return
        
        self.discarded_tiles.append(tile)
        self.tiles.remove(tile)
    
    def discard_to_not_shown(self, tile):
        if self.discarded_tiles[-1] != tile:
            print('err discarded_tiles[-1] is not', tile)
            return
        del self.discarded_tiles[-1]
        self.discarded_tiles_not_shown.append(tile)

    def discard_idx(self, tile_idx):
        if tile_idx < 0 or len(self.tiles) <= tile_idx:
            print('error: too big or too small idx players hand')
            return
        
        self.discarded_tiles.append(self.tiles[tile_idx])
        del self.tiles[tile_idx]
    
    def add(self, tile):
        self.tiles.append(tile)
    
    def check_menzen(self, player_pos):
        flag = (len(self.pong_tiles) == 0 and len(self.chow_tiles) == 0)
        for kong in self.kong:
            if kong.from_pos != player_pos:
                flag = False
        return flag
    
    def pong(self, tile, from_pos):
        self.pong_tiles.append(Furo(from_pos, [tile for i in range(3)]))
        self.tiles.remove(tile)
        self.tiles.remove(tile)
    
    def chow(self, tiles, from_pos):
        self.chow_tiles.append(Furo(from_pos, tiles))

        remove_count = 0
        for tile in tiles:
            if tile in self.tiles:
                self.tiles.remove(tile)
                remove_count += 1

        if remove_count != 2:
            print('chow err')
    
    def kong(self, tile, from_pos, self_flag=False, add=False):
        print('kong: (self_flag, add):', self_flag, add)
        

        if self_flag:
            if add: # 槍槓
                idx = -1
                for i in range(len(self.pong_tiles)):
                    if tile in self.pong_tiles[i].tiles:
                        idx = i
                if idx == -1:
                    print('err cannot chankan: not found tile[', tile, ']')
                from_pos = self.pong_tiles[idx].from_pos
                self.pong_tiles.pop(idx)
                self.tiles.remove(tile)
            else: # 暗槓
                for i in range(4):
                    self.tiles.remove(tile)
        else: # ミンカン
            for i in range(3):
                self.tiles.remove(tile)

        self.kong_tiles.append(Furo(from_pos, [tile for i in range(4)]))



class Player:
    # riichi: 0のとき,ダブリー 1のとき,ノーマル立直
    def __init__(self, tiles, pos, wind, oya=False, riichi=-1, tenpai=False):
        self.pos = pos
        self.oya = oya
        self.hands = Hands(tiles, wind)
        self.sprites = None
        self.riichi = riichi

        self.tenpai = tenpai
        self.tenpai_hai = []

        self.menzen = True

        if pos == 0:
            size_x = IMG_SIZE[pos]['size_x']
            size_y = IMG_SIZE[pos]['size_y']
            x = IMG_SIZE[pos]['x']
            y = IMG_SIZE[pos]['y']
        
            self.sprites = TileSprites(13, size_x, size_y, x, y, dx=size_x, dy=0)
 
    def pong(self, tile, from_pos):
        self.hands.pong(tile, from_pos)
        self.menzen = False
        if self.pos == 0:
            self.sprites.adjust(len(self.hands.tiles))
    
    def chow(self, tiles, from_pos):
        self.hands.chow(tiles, from_pos)
        self.menzen = False
        if self.pos == 0:
            self.sprites.adjust(len(self.hands.tiles))
    
    def kong(self, tile, from_pos, add=False):
        if from_pos != self.pos: #ポンのときにmenzen=Falseされているため、槍槓時の判定不要
            self.menzen = False
        
        self.hands.kong(tile, from_pos, self_flag=(self.pos==from_pos), add=add)
        if self.pos == 0:
            self.sprites.adjust(len(self.hands.tiles))

    def discard(self, tile):
        self.hands.discard(tile)
        if self.pos == 0:
            self.sprites.remove_one()
        self.hands.sort_hands()

    def discard_to_not_shown(self, tile):
        self.hands.discard_to_not_shown(tile)

    def discard_idx(self, tile_idx):
        self.hands.discard_idx(tile_idx)
        if self.pos == 0:
            self.sprites.remove_one()
        self.hands.sort_hands()
    
    def add(self, tile):
        self.hands.add(tile)
        if self.pos == 0:
            self.sprites.add_one()
        self.hands.sort_hands()
    
    def check_discard(self, pos):
        if self.sprites is not None:
            clicked_idx = self.sprites.checkall(pos)
            if clicked_idx >= len(self.hands.tiles): #2重
                return -1
            else:
                return clicked_idx
        else:
            print('error: not player')
    
    # 面前かどうか
    # True: 面前 False: 面前でない
    def check_menzen(self):
        return self.menzen

    
    # 牌表示
    # 0: player     1: 上家     2: 対面     3: 下家
    def show_tiles(self, screen):

        # テスト用
        print('=== show_tiles player['+str(self.pos)+'] ===')
        print('\t', nanno_koma_list(self.hands.tiles))
        print('\tfuro:')
        if len(self.hands.pong_tiles) != 0:
            print('\t\tpong:')
            for pong_tiles in self.hands.pong_tiles:
                print('\t\t\tfrom_pos:', pong_tiles.from_pos)
                print('\t\t\t[', pong_tiles.tiles, ']')
        if len(self.hands.chow_tiles) != 0:
            print('\t\tchow:')
            for pong_tiles in self.hands.chow_tiles:
                print('\t\t\tfrom_pos:', pong_tiles.from_pos)
                print('\t\t\t[', pong_tiles.tiles, ']')
        if len(self.hands.kong_tiles) != 0:
            print('\t\tkong:')
            for pong_tiles in self.hands.kong_tiles:
                print('\t\t\tfrom_pos:', pong_tiles.from_pos)
                print('\t\t\t[', pong_tiles.tiles, ']')
        print()
        # テスト用ここまで

        pos = self.pos
        tiles = self.hands.tiles
        
        bg_top = min(IMG_SIZE[pos]['y'], IMG_SIZE[pos]['y']+IMG_SIZE[pos]['dy']*13+IMG_SIZE[pos]['dy'])
        bg_left = min(IMG_SIZE[pos]['x'], IMG_SIZE[pos]['x']+IMG_SIZE[pos]['dx']*13+IMG_SIZE[pos]['dx'])
        bg_height = abs(IMG_SIZE[pos]['y']+IMG_SIZE[pos]['dy']*13+IMG_SIZE[pos]['dy'])
        bg_width = abs(IMG_SIZE[pos]['x']+IMG_SIZE[pos]['dx']*13+IMG_SIZE[pos]['dx'])

        screen.fill(POS_COLORS[pos], (bg_left, bg_top, bg_width, bg_height))
        
        size_x = IMG_SIZE[pos]['size_x']
        size_y = IMG_SIZE[pos]['size_y']
        x = IMG_SIZE[pos]['x']
        y = IMG_SIZE[pos]['y']
        dx = IMG_SIZE[pos]['dx']
        dy = IMG_SIZE[pos]['dy']

        if pos == 0: # player
            for i in range(len(self.hands.tiles)):
                timgpath = "sysimg/open_tiles/"+TILES[self.hands.tiles[i]]+"1.gif"
                timg = pygame.image.load(timgpath)
                screen.blit(timg, (x, y))
                x += size_x
                if i == len(self.hands.tiles) - 2:
                    x += size_x
                
        else:
            if pos == 1: # 上家伏せ牌表示
                timgpath = "sysimg/ms/p_bk_8.png"
            elif pos == 2: # 対面伏せ牌表示
                timgpath = "sysimg/ms/p_bk_5.gif"
            elif pos == 3: # 下家伏せ牌表示
                timgpath = "sysimg/ms/p_bk_9.png"
            else:
                print("error show_tiles n", file=sys.stderr)
            
            timg = pygame.image.load(timgpath)
            for i in range(len(self.hands.tiles)):
                screen.blit(timg, (x, y))
                x += dx
                y += dy
    
    # 河表示
    # 0: player     1: 下家     2: 対面     3: 下家
    def show_rivers(self, screen):

        # テスト用
        print('--- show_rivers player['+str(self.pos)+']')
        print(nanno_koma_list(self.hands.discarded_tiles))
        print()
        # テスト用ここまで

        pos = self.pos
        pos += 4

        x = IMG_SIZE[pos]['x']
        y = IMG_SIZE[pos]['y']
        dx = IMG_SIZE[pos]['dx']
        dy = IMG_SIZE[pos]['dy']
        new_dx = IMG_SIZE[pos]['new_dx']
        new_dy = IMG_SIZE[pos]['new_dy']
        xx = x
        yy = y
        rev_flag = IMG_SIZE[pos]['rev_flag']

        # posの描画領域を白で塗りつぶす
        #"""
        bg_top = min(IMG_SIZE[pos]['y'], IMG_SIZE[pos]['y']+IMG_SIZE[pos]['dy']*13+IMG_SIZE[pos]['dy'])
        bg_left = min(IMG_SIZE[pos]['x'], IMG_SIZE[pos]['x']+IMG_SIZE[pos]['dx']*13+IMG_SIZE[pos]['dx'])
        bg_height = abs(IMG_SIZE[pos]['y']+IMG_SIZE[pos]['dy']*13+IMG_SIZE[pos]['dy'])
        bg_width = abs(IMG_SIZE[pos]['x']+IMG_SIZE[pos]['dx']*13+IMG_SIZE[pos]['dx'])

        screen.fill(POS_COLORS[self.pos], (bg_left, bg_top, bg_width, bg_height))
        #"""
        
        if rev_flag:
            xx -= dx * (6 - len(self.hands.discarded_tiles) % 6)
            yy -= dy * (4 - len(self.hands.discarded_tiles) // 4)
            y = yy
            cnt = len(self.hands.discarded_tiles) % 6
            for t in reversed(self.hands.discarded_tiles):
                print(t)
                timgpath = "sysimg/open_tiles/" + TILES[t] + str(IMG_NUM[pos]) + ".gif"
                timg = pygame.image.load(timgpath)
                screen.blit(timg, (xx, yy))
                cnt += 1
                if cnt % 6 == 0:
                    xx = x + new_dx * (cnt // 6)
                    yy = y + new_dy * (cnt // 6)
                else:
                    xx += dx
                    yy += dy
        else:
            cnt = 0
            for t in self.hands.discarded_tiles:
                timgpath = "sysimg/open_tiles/" + TILES[t] + str(IMG_NUM[pos]) + ".gif"
                timg = pygame.image.load(timgpath)
                screen.blit(timg, (xx, yy))
                cnt += 1
                if cnt % 6 == 0:
                    xx = x + new_dx * (cnt // 6)
                    yy = y + new_dy * (cnt // 6)
                else:
                    xx += dx
                    yy += dy


# シャンテン数を返却
def check_hands(hands, menzen):
    # Dots      : 1~9 : 筒子
    # Bamboo    : 11~19 : 索子
    # Characters: 21~29 : 萬子
    # Dragons   : 0, 10, 20 : 白，ハツ，中
    # Winds     : 30, 31, 32, 33 : 東，南，西，北

    # 0ならアガリ
    # 1ならテンパイ
    # 2以上ならn-1シャンテン
    
    shanten_num = 8

    sorted_tiles = sorted(hands.tiles)
    set_tiles = sorted(list(set(hands.tiles)))
    
    # ダミー追加
    if len(sorted_tiles) == 14:
        pass
    elif len(sorted_tiles) == 13:
        sorted_tiles.append(100)
        set_tiles.append(100)
    
    count_tiles = [sorted_tiles.count(tile) for tile in set_tiles]

    #menzen = player.check_menzen()

    # 国士無双の判定
    kokushi = 10^6
    if menzen:
        kokushi_tiles = [0, 1, 9, 10, 11, 19, 20, 21, 29, 30, 31, 32, 33]
        
        kokushi_idx = 0
        tmp_tiles = sorted_tiles.copy()
        for t in kokushi_tiles:
            if t in tmp_tiles:
                tmp_tiles.remove(t)
        for t in kokushi_tiles:
            if t in tmp_tiles:
                tmp_tiles.remove(t)
                break
        kokushi = len(tmp_tiles)

    # 七対子の判定
    chitoitsu = 10^6
    if menzen:
        toitsu_cnt = 0
        for c in count_tiles:
            if c >= 2:
                toitsu_cnt += 1
        
        if len(set_tiles)==7 and toitsu_cnt==7:
            chitoitsu = -1
        elif len(set_tiles)>=7 and toitsu_cnt==6:
            chitoitsu = 0
        elif len(set_tiles)==6 and toitsu_cnt==6:
            chitoitsu = 1
        else:
            chitoitsu = 6 - toitsu_cnt
    
    # 通常の役の判定
    """
    1. 手牌のなかで、3枚で完成した面子（順子か刻子）があれば2点とする
    2. あと1枚で順子になるターツ、あるいは対子があれば、1点とする
    3. すべての点数を足して、8点から引く
    4. 引き算の答えがシャンテン数
    """
    normal = 8

    return min(kokushi, min(chitoitsu, normal))

# どのidxの牌を切ったときテンパイとなるか
# どれを切ってもテンパイとならない場合、[]を返却
def tenpai_hai_check(player):
    menzen = player.menzen
    tmp_tiles = player.hands.tiles.copy()
    hai_list = []
    for tile in tmp_tiles:
        player.hands.tiles.remove(tile)
        shanten = check_hands(player.hands, menzen)
        if shanten == 1:
            hai_list.append(tile)
        player.hands.add(tile)

    return hai_list

# 役を確認
# 戻り値: [0, 1, 1, 0, 0]
# 役番号の配列　その役が有効なら1 なしなら0
# ドラは1以上の値が入る場合もあり
# 点数計算、集計の場面で使用される

"""
役一覧
====================

1ハン
0: 立直
1: 役牌
2: たんやおちゅー
3: 平和【面前】
4: 面前自摸
5: 一発 #なし
6: 一盃口【面前】
7: ほうていろん
8: ほうていつも
9: 嶺上開花
10: ダブル立直
11: 槍槓

2ハン
12: 対々和
13: 三色同順
14: 七対子【面前】
15: 一気通貫【鳴き-1】
16: 混全帯么九【鳴き-1】
17: 三暗刻
18: 小三元
19: 混老頭
20: 三色同刻
21: 三槓子
22: 三色同順【鳴き-1】

3ハン
23: ホンイツ【鳴き-1】
24: 純全帯么九【鳴き-1】
25: 二盃口【面前】

6ハン
26: 清一色【鳴き-1】

役満(13ハン)
27: 四暗刻【面前】
28: 国士無双【面前】
29: 国士無双十三面待ち【面前】
30: 大三元
31: 四喜和
32: 字一色
33: 清老頭
34: 地和【面前】
35: 緑一色
36: 九蓮宝燈【面前】
37: 四槓子
38: 天和【面前】

39: 流局[テンパイ]
40: ドラ
"""
# 評価関数
# あがったかとはんすう
# シャンテン数と期待できる役?


# ツモまたはロンしたときに役を判定
# シャンテン数0(?)のとき限定
# ba_windが東かつ約牌が東の場合や、親の場合は約牌を複数追加する
# ドラが複数なことに注意
def check_yaku(player, last_tile, ba_wind, bonus_tiles, tumo=True):

    sorted_tiles = sorted(player.hands.tiles)
    set_tiles = sorted(list(set(player.hands.tiles)))
    count_tiles = [sorted_tiles.count(tile) for tile in set_tiles]

    menzen = player.check_menzen()

    yaku = []

    # テンパイ状態でないなら[]を返却
    if check_hands(player.hands, player.menzen) != 0:
        return []
    
    if player.riichi == 0:
        yaku.append(10)
    elif player.riichi == 1:
        yaku.append(0)

    # 役満判定
    if menzen:
        # 四暗刻
        if count_tiles.count(3) == 4 and count_tiles.count(2) == 1:
            yaku.append(27)

        # 国士無双
        kokushi_tiles = [0, 1, 9, 10, 11, 19, 20, 21, 29, 30, 31, 32, 33]
        tmp_tiles = sorted_tiles.copy()
        for t in kokushi_tiles:
            if t in tmp_tiles:
                tmp_tiles.remove(t)
        if len(tmp_tiles)==0 and last_tile in kokushi_tiles:
            yaku.append(29) # 国士無双十三面待ち
        elif len(tmp_tiles)==1 and tmp_tiles[0] in kokushi_tiles and last_tile in kokushi_tiles and last_tile != tmp_tiles[0]:
            yaku.append(28) # 国士無双
    
    # 大三元
    if daisangen in set_tiles:
    #player.hands.tiles = tiles
    #self.wind = wind
    #self.pung[i].tiles
    #self.pung[i].from
    #self.chow[i].tiles
    #self.kong[i].tiles
        pass

    
#31: 四喜和
#32: 字一色
#33: 清老頭
#34: 地和【面前】
#35: 緑一色
#36: 九蓮宝燈【面前】
#37: 四槓子
#38: 天和【面前】
    
    # 役満の場合は判定終了
    if len(yaku) != 0:
        return yaku

    # 一般の役
    return yaku



# 点数を返却
# ツモアガリの場合[アガった人が親の場合に全員から徴収する点数, 子の場合に徴収する点数]
# ロンアガリの場合、[ロンされた人が親の場合に徴収する点数, 子の場合に徴収する点数]
# ↑自分が親かどうかによって変動する
def calc_points(yaku, oya=False, tumo=False):
    return 19

# 役名を返却
def yaku_name(yaku_num):
    if yaku_num == 0:
        yaku_name = "立直"
    elif yaku_num == 1:
        yaku_name = "役牌"
    elif yaku_num == 2:
        yaku_name = "断么九"
    elif yaku_num == 3:
        yaku_name = "平和"
    elif yaku_num == 4:
        yaku_name = "面前自摸"
    elif yaku_num == 5:
        yaku_name = "一発"
    elif yaku_num == 6:
        yaku_name = "一盃口"
    elif yaku_num == 7:
        yaku_name = "河底撈魚"
    elif yaku_num == 8:
        yaku_name = "海底摸月"
    elif yaku_num == 9:
        yaku_name = "嶺上開花"
    elif yaku_num == 10:
        yaku_name = "ダブル立直"
    elif yaku_num == 11:
        yaku_name = "槍槓"
    elif yaku_num == 12:
        yaku_name = "対々和"
    elif yaku_num == 13:
        yaku_name = "三色同順"
    elif yaku_num == 14:
        yaku_name = "七対子"
    elif yaku_num == 15:
        yaku_name = "一気通貫"
    elif yaku_num == 16:
        yaku_name = "混全帯么九"
    elif yaku_num == 17:
        yaku_name = "三暗刻"
    elif yaku_num == 18:
        yaku_name = "小三元"
    elif yaku_num == 19:
        yaku_name = "混老頭"
    elif yaku_num == 20:
        yaku_name = "三色同刻"
    elif yaku_num == 21:
        yaku_name = "三槓子"
    elif yaku_num == 22:
        yaku_name = "三色同順"
    elif yaku_num == 23:
        yaku_name = "ホンイツ"
    elif yaku_num == 24:
        yaku_name = "純全帯么九"
    elif yaku_num == 25:
        yaku_name = "二盃口"
    elif yaku_num == 26:
        yaku_name = "清一色"
    elif yaku_num == 27:
        yaku_name = "四暗刻"
    elif yaku_num == 28:
        yaku_name = "国士無双"
    elif yaku_num == 29:
        yaku_name = "国士無双十三面待ち"
    elif yaku_num == 30:
        yaku_name = "大三元"
    elif yaku_num == 31:
        yaku_name = "四喜和"
    elif yaku_num == 32:
        yaku_name = "字一色"
    elif yaku_num == 33:
        yaku_name = "清老頭"
    elif yaku_num == 34:
        yaku_name = "地和"
    elif yaku_num == 35:
        yaku_name = "緑一色"
    elif yaku_num == 36:
        yaku_name = "九蓮宝燈"
    elif yaku_num == 37:
        yaku_name = "四槓子"
    elif yaku_num == 38:
        yaku_name = "天和"
    return yaku_name

# ゲームの変数をここで保存するかどうか考え中
# main.pyで直接管理してもいいかも 
"""
class Game:
    def __init__(self):
"""

class Scrap:
    def __init__(self):
        pass
    
    # どの牌を捨てるか,idx
    # -1の場合、アガリ
    def think(self, hands):
        idx = random.randint(0, len(hands.tiles)-1)
        # 役満てんぱいの場合上がるように
        # あとはシャンテン数*はんすうに応じて判定させる?

        # てんぱいなら立直も候補に
        return hands.tiles[idx]
    
    def think_furo(self, hands, discard_tile):
        flag = random.randint(0, 1)
        return flag