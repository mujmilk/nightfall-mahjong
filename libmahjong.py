import sys
import pygame
from pygame.locals import *
import copy

import random

# "sysimg/open_tiles/"+TILES[n]+"_"+str(i)+".gif"
SCREEN_SIZE = (800, 600)

# テスト用色分け
POS_COLORS = [(222, 50, 50), (50, 222, 50), (50, 50, 222), (222, 50, 222)]

TILE_IMG_FOLDER = './sysimg/tiles/'
SCALE = 0.4
OTHER_SCALE = 0.7

IMG_SIZE = {'size_x': int(90*SCALE), 'size_y': int(128*SCALE)}
TILE_POS_HANDS = [{'x':80, 'y':SCREEN_SIZE[1]-IMG_SIZE['size_y']-10},
                    {'x':SCREEN_SIZE[0]-IMG_SIZE['size_y'], 'y':SCREEN_SIZE[1]-80}, #1: 下家(右)
                    {'x':SCREEN_SIZE[0]-80, 'y':0}, #2: 対面
                    {'x':0, 'y':80}] #3: 上家(左)
TILE_POS_RIVER = [{'x':250+30, 'y':350},
                    {'x':SCREEN_SIZE[0]-180-IMG_SIZE['size_x'], 'y':SCREEN_SIZE[1]-170-IMG_SIZE['size_y']}, #1: 下家(右)
                    {'x':SCREEN_SIZE[0]-250-IMG_SIZE['size_x'], 'y':SCREEN_SIZE[1]-350-IMG_SIZE['size_y']}, #2: 対面
                    {'x':180, 'y':170+30}] #3: 上家(左)
POPUP_MSG_POS = [0, 0, 100, 30]


# 副露牌を管理するクラス
class Furo:
    def __init__(self, idx, from_pos, tiles):
        self.idx = idx
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

            if t == tiles_num - 2:
                xx += dx // 2 # imgtype: 0の画像の横の長さ
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

        #print('::: adjust', tiles_num)

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
        self.tiles = sorted(self.tiles)
    
    def discard(self, tile):
        if tile not in self.tiles:
            print('error: tile not in players hand')
            return
        
        self.discarded_tiles.append(tile)
        self.tiles.remove(tile)
        self.sort_hands()
    
    def discard_to_not_shown(self, tile):
        if self.discarded_tiles[-1] != tile:
            print('err discarded_tiles[-1] is not', tile)
            return
        del self.discarded_tiles[-1]
        self.discarded_tiles_not_shown.append(tile)

    def discard_idx(self, tile_idx):
        if tile_idx < 0 or len(self.tiles) <= tile_idx:
            print('error: too big or too small idx players hand:', tile_idx)
            return
        
        self.discarded_tiles.append(self.tiles[tile_idx])
        del self.tiles[tile_idx]
        self.sort_hands()
    
    def add(self, tile):
        self.tiles.append(tile)
        self.sort_hands()
    
    def check_menzen(self, player_pos):
        flag = (len(self.pong_tiles) == 0 and len(self.chow_tiles) == 0)
        for kong in self.kong:
            if kong.from_pos != player_pos:
                flag = False
        return flag
    
    def pong(self, idx, tile, from_pos):
        print('pong:')
        print(' -:', self.tiles)
        self.pong_tiles.append(Furo(idx, from_pos, [tile for i in range(3)]))
        self.tiles.remove(tile)
        self.tiles.remove(tile)
        print(' -:', self.tiles)
        self.sort_hands()
    
    def chow(self, idx, tiles, from_pos):
        print('chow:')
        print(' -:', self.tiles)
        self.chow_tiles.append(Furo(idx, from_pos, tiles))

        remove_count = 0
        for tile in tiles:
            if tile in self.tiles:
                self.tiles.remove(tile)
                remove_count += 1

        if remove_count != 2:
            print('chow err')
        print(' -:', self.tiles)
        self.sort_hands()
    
    def kong(self, idx, tile, from_pos, self_flag=False, add=False):
        print('kong: (self_flag, add):', self_flag, add)
        print(' -:', self.tiles)
        
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

        print(' -:', self.tiles)
        self.kong_tiles.append(Furo(idx, from_pos, [tile for i in range(4)]))
        self.sort_hands()



class Player:
    # riichi: 0のとき,ダブリー 1のとき,ノーマル立直
    def __init__(self, tiles, pos, wind, oya=False, riichi=-1, tenpai=False):
        self.pos = pos
        self.oya = oya
        self.hands = Hands(tiles, wind)
        self.sprites = None
        self.riichi = riichi

        self.furo_num = 0

        self.tenpai = tenpai
        self.tenpai_hai = []

        self.menzen = True

        if pos == 0:
            size_x = IMG_SIZE['size_x']
            size_y = IMG_SIZE['size_y']
            x = TILE_POS_HANDS[0]['x']
            y = TILE_POS_HANDS[0]['y']
        
            self.sprites = TileSprites(13, size_x, size_y, x, y, dx=size_x, dy=0)
 
    def pong(self, tile, from_pos):
        self.hands.pong(self.furo_num, tile, from_pos)
        self.menzen = False
        if self.pos == 0:
            self.sprites.adjust(len(self.hands.tiles))
        
        # テスト表示用
        if self.pos == 0:
            print('test show: pong', tile)
        print('[pong', self.furo_num)
        self.furo_num += 1
    
    def chow(self, tiles, from_pos):
        self.hands.chow(self.furo_num, tiles, from_pos)
        self.menzen = False
        if self.pos == 0:
            self.sprites.adjust(len(self.hands.tiles))
        
        # テスト表示用
        if self.pos == 0:
            print('test show: chow', tile)
        print('[chow', self.furo_num)
        self.furo_num += 1
    
    def kong(self, tile, from_pos, add=False):
        if from_pos != self.pos: #ポンのときにmenzen=Falseされているため、槍槓時の判定不要
            self.menzen = False

        # テスト表示用
        if self.pos == 0:
            print('test show: kong', tile)
            
        self.hands.kong(self.furo_num, tile, from_pos, self_flag=(self.pos==from_pos), add=add)
        if self.pos == 0:
            self.sprites.adjust(len(self.hands.tiles))
        
        if add:
            pongs = self.hands.pong_tiles
            remove_idx = -1
            for pong_idx in range(len(pongs)):
                if tile in pongs[pong_idx].tiles:
                    remove_idx = pong_idx
                    break
            if remove_idx == -1:
                print('err: cannot found add pong')
            del self.hands.pong_tiles[remove_idx]

        print('[kong', self.furo_num)
        self.furo_num += 1

    def discard(self, tile):
        # テスト表示用
        if self.pos == 0:
            print('test show: discard', tile)

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
        # テスト表示用
        if self.pos == 0:
            print('test show: add', tile)
        self.hands.add(tile)
        if self.pos == 0:
            self.sprites.add_one()
        self.hands.sort_hands()
        
        if self.pos == 0:
            self.sprites.adjust(len(self.hands.tiles))
    
    def check_discard(self, pos):
        if self.sprites is not None:
            clicked_idx = self.sprites.checkall(pos)
            print('clicked idx:', clicked_idx)
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
        
# =======================
# 表示
# =======================
# open_pos: 手牌を公開するpos
def show_all_tiles(screen, players, open_pos=[], test=False):

    if test:
        # テスト用テキスト表示
        print('==== show tiles ====')
        for i in range(len(players)):
            print(' - player['+str(i)+']')
            print('\t', nanno_koma_list(players[i].hands.tiles))
            print('\tfuro:')
            if len(players[i].hands.pong_tiles) != 0:
                print('\t\tpong:')
                for pong_tiles in players[i].hands.pong_tiles:
                    print('\t\t\tfrom_pos:', pong_tiles.from_pos)
                    print('\t\t\t[', pong_tiles.tiles, ']')
            if len(players[i].hands.chow_tiles) != 0:
                print('\t\tchow:')
                for pong_tiles in players[i].hands.chow_tiles:
                    print('\t\t\tfrom_pos:', pong_tiles.from_pos)
                    print('\t\t\t[', pong_tiles.tiles, ']')
            if len(players[i].hands.kong_tiles) != 0:
                print('\t\tkong:')
                for pong_tiles in players[i].hands.kong_tiles:
                    print('\t\t\tfrom_pos:', pong_tiles.from_pos)
                    print('\t\t\t[', pong_tiles.tiles, ']')
            print()

        print('==== show river ====')
        for i in range(len(players)):
            print(' - player['+str(i)+']')
            print(nanno_koma_list(players[i].hands.discarded_tiles))
            print()
        # テスト用テキスト表示 ここまで
        return


    # 描画領域を塗りつぶす(呼ぶたびにリセットされるように)
    for i in range(4):
        if i == 0:
            bg_hand_left = TILE_POS_HANDS[i]['x']
            bg_hand_top = TILE_POS_HANDS[i]['y']
            bg_hand_width = round(IMG_SIZE['size_x'] * 14.5)
            bg_hand_height = IMG_SIZE['size_y']

            bg_river_left = TILE_POS_RIVER[i]['x']
            bg_river_top = TILE_POS_RIVER[i]['y']
            bg_river_width = IMG_SIZE['size_x'] * 6
            bg_river_height = IMG_SIZE['size_y'] * 4
        elif i == 1:
            bg_hand_left = TILE_POS_HANDS[i]['x']
            bg_hand_top = TILE_POS_HANDS[i]['y']
            bg_hand_width = IMG_SIZE['size_y']
            bg_hand_height = IMG_SIZE['size_x'] * 14

            bg_river_left = TILE_POS_RIVER[i]['x']
            bg_river_top = TILE_POS_RIVER[i]['y'] - 5 * IMG_SIZE['size_x']
            bg_river_width = IMG_SIZE['size_y'] * 4
            bg_river_height = IMG_SIZE['size_x'] * 6
        elif i == 2:
            bg_hand_left = TILE_POS_HANDS[i]['x']
            bg_hand_top = TILE_POS_HANDS[i]['y']
            bg_hand_width = IMG_SIZE['size_x'] * 14
            bg_hand_height = IMG_SIZE['size_y']

            bg_river_left = TILE_POS_RIVER[i]['x'] - 5 * IMG_SIZE['size_x']
            bg_river_top = TILE_POS_RIVER[i]['y'] - 3 * IMG_SIZE['size_y']
            bg_river_width = IMG_SIZE['size_x'] * 6
            bg_river_height = IMG_SIZE['size_y'] * 4
        elif i == 3:
            bg_hand_left = TILE_POS_HANDS[i]['x']
            bg_hand_top = TILE_POS_HANDS[i]['y']
            bg_hand_width = IMG_SIZE['size_y']
            bg_hand_height = IMG_SIZE['size_x'] * 14

            bg_river_left = TILE_POS_RIVER[i]['x'] - 3 * IMG_SIZE['size_y']
            bg_river_top = TILE_POS_RIVER[i]['y']
            bg_river_width = IMG_SIZE['size_y'] * 4
            bg_river_height = IMG_SIZE['size_x'] * 6
        
        pos_color = (200,200,200)#POS_COLORS[i]
        screen.fill(pos_color, (bg_hand_left, bg_hand_top, bg_hand_width, bg_hand_height))
        screen.fill(pos_color, (bg_river_left, bg_river_top, bg_river_width, bg_river_height))

    # posによる回転角度
    angles = [0, 90, 180, -90]

    # 手牌の表示
    for i in range(len(players)):
        pos = players[i].pos
        open_flag = (pos in open_pos) or (pos == 0)
        angle = angles[pos]
        tile_pos = [TILE_POS_HANDS[pos]['x'], TILE_POS_HANDS[pos]['y']]
        scale = 1.0
        if pos != 0:
            scale *= OTHER_SCALE

        for tile_idx in range(len(players[i].hands.tiles)):
            if open_flag:
                timgpath = TILE_IMG_FOLDER+str(players[i].hands.tiles[tile_idx])+'.png'
            else:
                timgpath = TILE_IMG_FOLDER+'34.png'
            
            timg = pygame.image.load(timgpath)
            scaled_timg = pygame.transform.rotozoom(timg, angle, SCALE*scale)
            screen.blit(scaled_timg, tuple(tile_pos))

            if pos == 0:
                tile_pos[0] += round(IMG_SIZE['size_x'] * scale)
            elif pos == 1:
                tile_pos[1] -= round(IMG_SIZE['size_x'] * scale)
            elif pos == 2:
                tile_pos[0] -= round(IMG_SIZE['size_x'] * scale)
            elif pos == 3:
                tile_pos[1] += round(IMG_SIZE['size_x'] * scale)

            if pos == 0 and tile_idx == len(players[i].hands.tiles)-2:
                tile_pos[0] += IMG_SIZE['size_x'] // 2
    
    # 河の表示
    for i in range(len(players)):
        pos = players[i].pos
        angle = angles[pos]
        tile_pos = [TILE_POS_RIVER[pos]['x'], TILE_POS_RIVER[pos]['y']]
        scale = OTHER_SCALE

        cnt = 0
        for tile_idx in range(len(players[i].hands.discarded_tiles)):
            timgpath = TILE_IMG_FOLDER+str(players[i].hands.discarded_tiles[tile_idx])+'.png'
            timg = pygame.image.load(timgpath)
            scaled_timg = pygame.transform.rotozoom(timg, angle, SCALE*scale)
            screen.blit(scaled_timg, tuple(tile_pos))
            cnt += 1

            if cnt == 6:
                if pos == 0:
                    tile_pos[0] = TILE_POS_RIVER[pos]['x']
                    tile_pos[1] += round(IMG_SIZE['size_y'] * scale)
                elif pos == 1:
                    tile_pos[0] += round(IMG_SIZE['size_y'] * scale)
                    tile_pos[1] = TILE_POS_RIVER[pos]['y']
                elif pos == 2:
                    tile_pos[0] = TILE_POS_RIVER[pos]['x']
                    tile_pos[1] -= round(IMG_SIZE['size_y'] * scale)
                elif pos == 3:
                    tile_pos[0] -= round(IMG_SIZE['size_y'] * scale)
                    tile_pos[1] = TILE_POS_RIVER[pos]['y']
                cnt = 0
            else:
                if pos == 0:
                    tile_pos[0] += round(IMG_SIZE['size_x'] * scale)
                elif pos == 1:
                    tile_pos[1] -= round(IMG_SIZE['size_x'] * scale)
                elif pos == 2:
                    tile_pos[0] -= round(IMG_SIZE['size_x'] * scale)
                elif pos == 3:
                    tile_pos[1] += round(IMG_SIZE['size_x'] * scale)
    
    # 副露牌の表示
    from_poses = [[3,2,1,0],[2,3,0,1],[1,0,3,2],[0,1,2,3]]#4番目の数字はダミー,被らないように
    for i in range(len(players)):
        pos = players[i].pos
        angle = angles[pos]
        scale = 1.0
        if pos != 0:
            scale *= OTHER_SCALE

        tile_pos = [TILE_POS_HANDS[pos]['x'], TILE_POS_HANDS[pos]['y']]

        if pos == 0:
            tile_pos[0] = SCREEN_SIZE[0] - tile_pos[0]
        elif pos == 1:
            tile_pos[1] = SCREEN_SIZE[1] - tile_pos[1]
        elif pos == 2:
            tile_pos[0] = SCREEN_SIZE[0] - tile_pos[0]
        elif pos == 3:
            tile_pos[1] = SCREEN_SIZE[1] - tile_pos[1]

        cnt = 0
        for furo_idx in range(players[i].furo_num):

            tiles = []
            from_pos = -1

            for pong in players[i].hands.pong_tiles:
                if pong.idx == furo_idx:
                    tiles = pong.tiles.copy()
                    from_pos = pong.from_pos

            for pong in players[i].hands.chow_tiles:
                if pong.idx == furo_idx:
                    tiles = pong.tiles.copy()
                    from_pos = pong.from_pos
            
            for pong in players[i].hands.kong_tiles:
                if pong.idx == furo_idx:
                    tiles = pong.tiles.copy()
                    from_pos = pong.from_pos
                    if from_pos == pos:
                        tiles[0] = 34
                        tiles[3] = 34
            
            for tile_idx in range(len(tiles)):
                timgpath = TILE_IMG_FOLDER+str(tiles[tile_idx])+'.png'
                timg = pygame.image.load(timgpath)
                
                if from_pos != pos and from_pos == from_poses[pos][tile_idx]:
                    
                    tmp_angle = angle
                    if pos == 0 or pos == 2:
                        tmp_angle = 90
                    else:
                        tmp_angle = 0
                    scaled_timg = pygame.transform.rotozoom(timg, tmp_angle, SCALE*scale)
                    
                    if pos == 0:
                        tile_pos[0] -= round(IMG_SIZE['size_y'] * scale)
                    elif pos == 1:
                        tile_pos[1] += round(IMG_SIZE['size_y'] * scale)
                    elif pos == 2:
                        tile_pos[0] += round(IMG_SIZE['size_y'] * scale)
                    elif pos == 3:
                        tile_pos[1] -= round(IMG_SIZE['size_y'] * scale)
                else:
                    scaled_timg = pygame.transform.rotozoom(timg, angle, SCALE*scale)
                    screen.blit(scaled_timg, tuple(tile_pos))
                    
                    if pos == 0:
                        tile_pos[0] -= round(IMG_SIZE['size_x'] * scale)
                    elif pos == 1:
                        tile_pos[1] += round(IMG_SIZE['size_x'] * scale)
                    elif pos == 2:
                        tile_pos[0] += round(IMG_SIZE['size_x'] * scale)
                    elif pos == 3:
                        tile_pos[1] -= round(IMG_SIZE['size_x'] * scale)

# 最もあまりが少なくなるように分解する

def bunkai(tiles):
    print('bunkaied -------------------', len(tiles), tiles)
    sorted_tiles = sorted(tiles) # ダミー入り
    set_tiles = sorted(list(set(sorted_tiles)))

    if len(tiles) == 1:
        return (0, tiles)
    elif len(tiles) == 2:
        if tiles[0] == tiles[1]:
            return (1, tiles)
        else:
            return (0, tiles)

    tehai = tiles.copy()
    bunkai_idx = 0
    bunkai_tiles = []
    tensu = 0
    
    max_tensu = 0
    max_bunkai = []

    # 字牌
    for jihai in [0, 10, 20, 30, 31, 32, 33]:
        if jihai not in tehai:
            continue
        
        bunkai_t = jihai

        cnt = tehai.count(bunkai_t)
        if cnt != 0:
            if cnt >= 3:
                tensu += 2
                cnt = 2
            elif cnt >= 2:
                tensu += 1
                cnt = 1
            
            bunkai_tiles.append([bunkai_t for i in range(cnt)])

            for i in range(cnt):
                tehai.remove(bunkai_t)
            continue
    
    bunkai_idx = 0
    # 数牌
    while len(tehai) != 0 and bunkai_idx < len(set_tiles):
        bunkai_t = set_tiles[bunkai_idx]
        bunkai_idx += 1

        if bunkai_t not in tehai:
            continue
        
        # 面子を取る準備
        mentsu_kouho = []
        print('suhai ==============', bunkai_t%10)
        if 2 <= (bunkai_t%10) <= 8:
            mentsu_kouho.append([bunkai_t-1, bunkai_t, bunkai_t+1])
        if 1 <= (bunkai_t%10) <= 7:
            mentsu_kouho.append([bunkai_t, bunkai_t+1, bunkai_t+2])
        if 3 <= (bunkai_t%10) <= 9:
            mentsu_kouho.append([bunkai_t-2, bunkai_t-1, bunkai_t])
        mentsu_kouho.append([bunkai_t for i in range(3)])
        
        # 面子を取る
        max_tmp_tensu = 0
        max_tmp_mentsu = []
        max_tmp_bunkai = []

        for mentsu in mentsu_kouho:
            # [1, 2, 3], [1, 1, 1]

            cnt = 0

            if mentsu[0] == mentsu[1]:
                cnt = tehai.count(mentsu[0])
            else:
                for m in mentsu:
                    if m in tehai:
                        cnt += 1
            removed_tiles = []
            if cnt >= 3:
                print(mentsu)
                print(tehai)
                
                for m in mentsu:
                    tehai.remove(m)
                    removed_tiles.append(m)
                
                tmp_tensu, tmp_bunkai = bunkai(tehai)
                tmp_tensu += 2

                if tmp_tensu > max_tmp_tensu:
                    max_tmp_tensu = tmp_tensu
                    max_tmp_mentsu = mentsu
                    max_tmp_bunkai = tmp_bunkai
                
            elif cnt >= 2:
                print(mentsu)
                print(tehai)

                for m in mentsu:
                    if m in tehai:
                        tehai.remove(m)
                        removed_tiles.append(m)
                
                tmp_tensu, tmp_bunkai = bunkai(tehai)
                tmp_tensu += 1
                
                if tmp_tensu > max_tmp_tensu:
                    max_tmp_tensu = tmp_tensu
                    max_tmp_mentsu = mentsu
                    max_tmp_bunkai = tmp_bunkai

            for m in removed_tiles:
                tehai.append(m)
            removed_tiles = []
        
        if len(max_tmp_bunkai) != 0:
            for m in max_tmp_mentsu:
                if m in tehai:
                    tehai.remove(m)
            max_tensu += max_tmp_tensu
            bunkai_tiles.append(max_tmp_bunkai)
        else:
            tehai.remove(bunkai_t)
            bunkai_tiles.append([bunkai_t])

    return (tensu+max_tensu, bunkai_tiles)

# シャンテン数を返却
def check_hands(hands, menzen):
    # Dots      : 1~9 : 筒子
    # Bamboo    : 11~19 : 索子
    # Characters: 21~29 : 萬子
    # Dragons   : 0, 10, 20 : 白，ハツ，中
    # Winds     : 30, 31, 32, 33 : 東，南，西，北

    # 0ならテンパイ(1から変更)
    
    shanten_num = 8

    sorted_tiles = sorted(hands.tiles)
    set_tiles = sorted(list(set(hands.tiles)))
    count_tiles = [sorted_tiles.count(tile) for tile in set_tiles]
    
    # ダミー追加
    if len(sorted_tiles) == 14:
        pass
    elif len(sorted_tiles) <= 13:
        while len(sorted_tiles) < 14:
            sorted_tiles.append(100)
    
    
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

    print('======= bunkai =======', hands.tiles)
    tensu, bunkaied_tiles = bunkai(hands.tiles)
    print(tensu, bunkaied_tiles)
    for furo in hands.pong_tiles:
        bunkaied_tiles.append(furo.tiles)
    for furo in hands.chow_tiles:
        bunkaied_tiles.append(furo.tiles)

    tensu = 0
    # TODO: 点数が高くなるように
    for bunkai_tile in bunkaied_tiles:
        if len(bunkai_tile) == 3:
            tensu += 2
        elif len(bunkai_tile) == 2:
            tensu += 1
    normal = 8 - tensu

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
# last_tileはplayer.hands.tilesの中に含まれることに注意
def check_yaku(player, last_tile, ba_wind, bonus_tiles, tumo=True, rinshan=False):

    sorted_tiles = sorted(player.hands.tiles)
    set_tiles = sorted(list(set(player.hands.tiles)))
    count_tiles = [sorted_tiles.count(tile) for tile in set_tiles]

    menzen = player.check_menzen()

    yaku = []

    # テンパイ状態でないなら[]を返却
    if check_hands(player.hands, player.menzen) != 0:
        return []
    # フリテンなら[]を返却
    if tumo == False and (last_tile in player.hands.discarded_tiles or last_tile in player.hands.discarded_tiles_not_shown):
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
        
        # 九蓮宝燈 36
    
    # 大三元
    daisangen = True
    for tile in [0, 10, 20]:
        if tile in set_tiles and (count_tiles[set_tiles.index(tile)] >= 3 or (count_tiles[set_tiles.index(tile)] >= 2 and tile == last_tile)):
            pass
        else:
            sangenhai_flag = False
            for tile_check in player.hands.pong_tiles:
                if tile in tile_check.tiles:
                    sangenhai_flag = True
                    break
            for tile_check in player.hands.kong_tiles:
                if tile in tile_check.tiles:
                    sangenhai_flag = True
                    break
            if sangenhai_flag == False:
                daisangen = False
                break
    if daisangen:
        yaku.append(30)

    #31: 四喜和
    #32: 字一色
    #33: 清老頭
    #35: 緑一色
    #37: 四槓子
    
    # 役満の場合は判定終了
    if len(yaku) != 0:
        return yaku

    
    # 一般の役

    # 刻子に分解する
    kotsus = []
    for furo in player.hands.pong_tiles:
        kotsus.append(furo.tiles)
    for furo in player.hands.chow_tiles:
        kotsus.append(furo.tiles)
    for furo in player.hands.kong_tiles:
        kotsus.append(furo.tiles)
    print('kotsus:', kotsus)

    max_hansuu = 0
    # パターンの数だけ繰り返し

    # 1ハン
    # 0: 立直
    if player.riichi == 1:
        yaku.append(0)

    # 1: 役牌
    # 2: たんやおちゅー

    # 3: 平和【面前】
    if menzen:
        pass
    
    # 4: 面前自摸
    if menzen and tumo:
        yaku.append(4)
    
    # 5: 一発 #なし

    # 6: 一盃口【面前】
    if menzen:
        pass

    # 7: ほうていろん #main
    # 8: ほうていつも #main

    # 9: 嶺上開花
    if rinshan:
        yaku.append(9)

    # 10: ダブル立直
    if player.riichi == 0:
        yaku.append(10)
    
    # 11: 槍槓

    # 2ハン
    # 12: 対々和
    # 13: 三色同順
    # 14: 七対子【面前】
    # 15: 一気通貫【鳴き-1】
    # 16: 混全帯么九【鳴き-1】
    # 17: 三暗刻
    # 18: 小三元
    # 19: 混老頭
    # 20: 三色同刻
    # 21: 三槓子
    # 22: 三色同順【鳴き-1】

    # 3ハン
    # 23: ホンイツ【鳴き-1】
    # 24: 純全帯么九【鳴き-1】
    # 25: 二盃口【面前】

    # 6ハン
    # 26: 清一色【鳴き-1】

    # 40: ドラ
    return yaku



# 点数を返却
# ツモアガリの場合[アガった人が親の場合に全員から徴収する点数, 子の場合に徴収する点数]
# ロンアガリの場合、[ロンされた人が親の場合に徴収する点数, 子の場合に徴収する点数]
# ↑自分が親かどうかによって変動する
def calc_points(yaku, oya=False, tumo=False):
    return [19,19]

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
    elif yaku_num == 39:
        yaku_name = "流局"
    elif yaku_num == 40:
        yaku_name = "ドラ"
    return yaku_name

def yaku_names(yaku_list):
    yakunames = ''
    for yaku in yaku_list:
        if yaku_list[0] != yaku:
            yakunames += ', '
        yakuname = yaku_name(yaku)
        yakunames += yakuname
    return yakunames

def popup(screen, msg, font):

    print(msg)
    #POPUP_MSG_POS

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
    def think(self, player, tile, ba_wind, bonus_tiles):
        idx = random.randint(0, len(player.hands.tiles)-1)
        
        # 役満てんぱいの場合上がるように
        yaku = check_yaku(player, tile, ba_wind, bonus_tiles)
        for y in yaku:
            if 12 <= y <= 38:
                return -1

        # あとはシャンテン数*はんすうに応じて判定させる?

        # てんぱいなら立直も候補に
        return player.hands.tiles[idx]
    
    def think_furo(self, hands, discard_tile, tumo=True):
        # tumo == Trueの場合, discard_tileがhands.tilesに含まれている
        flag = random.randint(0, 1)
        return flag