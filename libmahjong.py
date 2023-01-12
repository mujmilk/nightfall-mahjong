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
        'x':240, 'y':170, 'dx':0, 'dy':40, 
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
        self.pung = []
        self.chow = []
        self.kong = []

        self.discarded_tiles = []
        self.discarded_tiles_not_shown = []
    
    def sort_hands(self):
        for i in range(len(self.tiles)-1):
            min = i
            for j in range(i, len(self.tiles)):
                if self.tiles[min].get_tileid() > self.tiles[j].get_tileid():
                    min = j
            tmpx = self.tiles[min].x
            tmpy = self.tiles[min].y
            self.tiles[j].x = self.tiles[min].x
            self.tiles[j].y = self.tiles[min].y
            self.tiles[min].x = tmpx
            self.tiles[min].y = tmpy
            self.tiles[min].move(self.tiles[min].x, self.tiles[min].y)
            self.tiles[j].move(self.tiles[j].x, self.tiles[j].y)

            tmp = self.tiles[min]
            self.tiles[min] = self.tiles[i]
            self.tiles[i] = tmp
    
    def discard(self, tile):
        if tile not in self.tiles:
            print('error: tile not in players hand')
            return
        
        self.discarded_tiles.append(tile)
        self.tiles.remove(tile)

    def discard_idx(self, tile_idx):
        if tile_idx < 0 or len(self.tiles) <= tile_idx:
            print('error: too big or too small idx players hand')
            return
        
        self.discarded_tiles.append(self.tiles[tile_idx])
        del self.tiles[tile_idx]
    
    def add(self, tile):
        self.tiles.append(tile)
    
    def check_menzen(self, player_pos):
        flag = (self.pung == 0 and self.chow == 0)
        for kong in self.kong:
            if kong.from_pos != player_pos:
                flag = False
        return flag



class Player:
    def __init__(self, tiles, pos, wind, riichi=False, tenpai=False):
        self.pos = pos
        self.hands = Hands(tiles, wind)
        self.sprites = None
        self.riichi = riichi
        self.tenpai = tenpai
        self.tenpai_hai = []

        if pos == 0:
            size_x = IMG_SIZE[pos]['size_x']
            size_y = IMG_SIZE[pos]['size_y']
            x = IMG_SIZE[pos]['x']
            y = IMG_SIZE[pos]['y']
        
            self.sprites = TileSprites(13, size_x, size_y, x, y, dx=size_x, dy=0)

    def discard(self, tile):
        self.hands.discard(tile)
        if self.pos == 0:
            self.sprites.remove_one()
        self.hands.sort_hands()

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
            return self.sprites.checkall(pos)
        else:
            print('error: not player')
    
    # 面前かどうか
    # True: 面前 False: 面前でない
    def check_menzen(self):
        self.hands.check_furo(self.pos)
    
    # 牌表示
    # 0: player     1: 上家     2: 対面     3: 下家
    def show_tiles(self, screen):

        pos = self.pos
        tiles = self.hands.tiles
        
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
                if i >= 12:
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
                if i >= 12:        
                    x += dx
                    y += dy
        
        # TODO: 副露牌の表示
    
    # 河表示
    # 0: player     1: 下家     2: 対面     3: 下家
    def show_rivers(self, screen):

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
def check_hands(player):
    # Dots      : 1~9 : 筒子
    # Bamboo    : 11~19 : 索子
    # Characters: 21~29 : 萬子
    # Dragons   : 0, 10, 20 : 白，ハツ，中
    # Winds     : 30, 31, 32, 33 : 東，南，西，北

    # 0ならアガリ
    # 1ならテンパイ
    # 2以上ならn-1シャンテン
    
    shanten_num = 8

    sorted_tiles = sorted(player.hands.tiles)
    set_tiles = sorted(list(set(player.hands.tiles)))
    count_tiles = [sorted_tiles.count(tile) for tile in set_tiles]

    menzen = player.check_menzen()

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

    return 

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
5: 一発
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
"""
# 評価関数
# あがったかとはんすう
# シャンテン数と期待できる役?


# ツモまたはロンしたときに役を判定
# シャンテン数0のとき限定
def check_yaku(player, last_tile, tumo=True):

    sorted_tiles = sorted(player.hands.tiles)
    set_tiles = sorted(list(set(player.hands.tiles)))
    count_tiles = [sorted_tiles.count(tile) for tile in set_tiles]

    menzen = player.check_menzen()

    yaku = []

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

    
31: 四喜和
32: 字一色
33: 清老頭
34: 地和【面前】
35: 緑一色
36: 九蓮宝燈【面前】
37: 四槓子
38: 天和【面前】
    
    # 役満の場合は判定終了
    if len(yaku) != 0:
        return yaku

    # 一般の役



# 点数を返却
def calc_points(hands, riichi, dora, ba_wind):


class Scrap:
    def __init__(self):
        pass
    
    def think(self, hands):
        idx = random.randint(0, len(hands.tiles)-1)
        return hands.tiles[idx]