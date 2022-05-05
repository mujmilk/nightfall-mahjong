import sys
import pygame
from pygame.locals import *

# "sysimg/"+str(0)+"/"+TILES[n]+".gif"
TILES = ["p_no_", "p_ms1_", "p_ms2_", "p_ms3_", "p_ms4_", "p_ms5_", "p_ms6_", "p_ms7_", "p_ms8_", "p_ms9_",
         "p_ji_h_", "p_ps1_", "p_ps2_", "p_ps3_", "p_ps4_", "p_ps5_", "p_ps6_", "p_ps7_", "p_ps8_", "p_ps9_",
         "p_ji_c_", "p_ss1_", "p_ss2_", "p_ss3_", "p_ss4_", "p_ss5_", "p_ss6_", "p_ss7_", "p_ss8_", "p_ss9_",
         "p_ji_e_", "p_ji_s_", "p_ji_w_", "p_ji_n_"]

# 1つ1つの麻雀牌のクラス
# id: 牌の種類, imgtype: 牌の向き(画像の種類), x,y:生成する位置
class TileSprite(pygame.sprite.Sprite):
    def __init__(self, tileid, imgtype, x, y):
        pygame.sprite.Sprite.__init__(self)

        self.img = pygame.image.load("sysimg/"+str(imgtype)+"/"+TILES[tileid]+str(imgtype)+".gif")
        self.width = self.img.get_width()
        self.height = self.img.get_height()
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.tileid = tileid
    
    def move(self, xx, yy):
        self.x = xx
        self.y = yy
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def check(self, pos):
        return self.rect.collidepoint(pos)
    
    def draw(self, screen):
        screen.blit(self.img, self.rect)
    
    def get_tileid(self):
        return self.tileid


# tilesからまとめてスプライトを生成するクラス
# postype: 表示位置 0ならプレイヤーの手牌
class TileSprites:
    def __init__(self, tiles, postype, x, y):
        self.tiles = []
        xx = x
        yy = y
        n = 0
        for t in tiles:
            self.tiles.append(TileSprite(t, postype, xx, yy))
            n += 1
            if postype == 0:
                xx += 33 # imgtype: 0の画像の横の長さ
            elif postype == 1:
                xx = x + 33 * (n % 6)
                yy = y + 60 * int(n / 6)
            else:
                print("error: TileSprites: unknown postype", file=sys.stderr)
                sys.exit()
        self.x = xx
        self.y = yy
        self.postype = postype
    
    def addtile(self, tile):
        self.tiles.append(TileSprite(tile, self.postype, self.x, self.y)) 
        if self.postype == 0:
            self.x += 33 # imgtype: 0の画像の横の長さ
        elif self.postype == 1:
            if len(self.tiles) % 6 == 0:
                self.x -= 33 * 5
                self.y += 40
            else:
                #self.x += 33
                pass
    
    def sort(self):
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

    
    def discardtile(self, idx):
        del self.tiles[idx]

    
    def checkall(self, pos):
        for i in range(len(self.tiles)):
            if self.tiles[i].check(pos):
                return i
        return -1
    
    def drawall(self, screen):
        for t in self.tiles:
            t.draw(screen)


# イーシャンテンなら2，聴牌なら1，アガリなら0を返す．それ以外は-1
def check_hands(tiles, riichi, dora):
    # Dots      : 1~9 : 筒子
    # Bamboo    : 11~19 : 索子
    # Characters: 21~29 : 萬子
    # Dragons   : 0, 10, 20 : 白，ハツ，中
    # Winds     : 30, 31, 32, 33 : 東，南，西，北
    return 
