import sys
import pygame
from pygame.locals import *

# "sysimg/"+str(0)+"/"+TILES[n]+".gif"
TILES = ["p_no_", "p_ms1_", "p_ms2_", "p_ms3_", "p_ms4_", "p_ms5_", "p_ms6_", "p_ms7_", "p_ms8_", "p_ms9_",
         "p_ji_h_", "p_ps1_", "p_ps2_", "p_ps3_", "p_ps4_", "p_ps5_", "p_ps6_", "p_ps7_", "p_ps8_", "p_ps9_",
         "p_ji_c_", "p_ss1_", "p_ss2_", "p_ss3_", "p_ss4_", "p_ss5_", "p_ss6_", "p_ss7_", "p_ss8_", "p_ss9_",
         "p_ji_e_", "p_ji_s_", "p_ji_w_", "p_ji_n_"]

IMG_SIZE = {
    0: {'size_x': 33, 'size_y': 60, 'x':20, 'y':520},
    1: {'size_x': 26, 'size_y': 25, 'x':754, 'y':200},
    2: {'size_x': 33, 'size_y': 59, 'x':300, 'y':200},
    3: {'size_x': 26, 'size_y': 25, 'x':20, 'y':40}
}

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

        xx = x
        yy = y

        for t in range(tiles_num):
            self.tiles.append(TileSprite(width, height, xx, yy))
            
            xx += dx # imgtype: 0の画像の横の長さ
            yy += dy

    def checkall(self, pos):
        for i in range(len(self.tiles)):
            if self.tiles[i].check(pos):
                return i
        return -1

# =======================
# 手牌管理
# =======================
class Hands:
    # tiles: 持ち牌
    # pos: 
    # wind: 
    def __init__(self, tiles, pos, wind):
        self.pos = pos
        self.tiles = tiles
        self.wind = wind
        self.pung = 0
        self.chow = 0
        self.kong = 0

        self.discarded_tiles = []
        self.discarded_tiles_not_shown = []
    
    def discard(self, tile_idx):
        if tile_idx < 0 or len(self.tiles) <= tile_idx:
            print('error: too big or too small idx players hand')
            return
        
        self.discarded_tiles.append(self.tiles[tile_idx])
        del self.tiles[tile_idx]
    
    def add(self, tile):
        self.tiles.append(tile)
    
    def discard_new(self, tile):
        self.discarded_tiles.append(tile)
    
    def get_tiles(self):
        return self.tiles

# =======================
# 牌表示
# =======================
# 0: player     1: 下家     2: 対面     3: 下家
def show_tiles(pos, tiles, screen):
    
    size_x = IMG_SIZE[pos]['size_x']
    size_y = IMG_SIZE[pos]['size_y']
    x = IMG_SIZE[pos]['x']
    y = IMG_SIZE[pos]['y']

    if pos == 0: # player
        for t in tiles:
            timgpath = "sysimg/1/"+TILES[t]+"1.gif"
            timg = pygame.image.load(timgpath)
            screen.blit(timg, (x, y))
            x += size_x
        
    else:
        if pos == 1: # 下家伏せ牌表示
            timgpath = "sysimg/ms/p_bk_9.png"
        elif pos == 2: # 対面伏せ牌表示
            timgpath = "sysimg/ms/p_bk_5.gif"
        elif pos == 3: # 上家伏せ牌表示
            timgpath = "sysimg/ms/p_bk_8.png"
        else:
            print("error show_tiles n", file=sys.stderr)
        
        timg = pygame.image.load(timgpath)
        for i in range(len(self.tiles)):
            screen.blit(timg, (x, y))
            y += size_y

class Player:
    def __init__(pos)

# イーシャンテンなら2，聴牌なら1，アガリなら0を返す．それ以外は-1
# シャンテン数を返却でもいいかも
def check_hands(tiles, riichi, dora):
    # Dots      : 1~9 : 筒子
    # Bamboo    : 11~19 : 索子
    # Characters: 21~29 : 萬子
    # Dragons   : 0, 10, 20 : 白，ハツ，中
    # Winds     : 30, 31, 32, 33 : 東，南，西，北
    return 
