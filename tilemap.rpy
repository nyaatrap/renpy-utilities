﻿## This file defines Tilemap class that create single map from small tile images.
## 小さな画像を並べて一枚の画像にする Tilemap クラスを追加するファイルです。

##############################################################################
## How to Use
##############################################################################

init python:

    ## まず最初に、 各タイルを displayable（表示可能オブジェクト）のリストとして定義します。
    tileset =[Solid("#77f", xysize=(32,32)), Solid("#ff9", xysize=(32,32)), Solid("#3f6", xysize=(32,32))]

    ## タイルを並べた一枚の画像を分割したい時は、次の関数も使えます。
    # tileset = read_spritesheet(filename, sprite_width, sprite_height, columns=1, rows=1)


    ## 次に整数の二次元配列を定義します。。値は tileset のインデックスで 0 は tileset[0] を表します。

    map1 = [
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0],
        [0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0],
        [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0],
        [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,2,2,1,1,1,1,1,1],
        [1,1,1,1,1,2,2,2,2,2,2,2,1,1,1,1,1],
        [1,1,1,1,1,2,2,2,2,2,2,2,1,1,1,1,1],
        [1,1,1,1,1,2,2,2,2,2,2,2,1,1,1,1,1],
        [1,1,1,1,1,2,2,2,2,2,2,2,1,1,1,1,1],
        [1,1,1,1,1,1,1,2,2,2,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        ]

    ## 文字列で map を作る場合は次のように tile_mapping も定義して、どの文字がどのインデックスに
    ## 対応するか定めます。
    # tile_mapping = {"0":0, "1":1, "2":2}

    ## 最後にタイルマップの displayable を Tilemap(map, tileset, tile_width, tile_height, tile_mapping, click)
    ## の形で定義します。
    tilemap = Tilemap(map1, tileset, 32, 32)

# 画像タグに関連付けても使えます。
image map = tilemap


## ゲームがスタートしたら jump sample_tilemap でここに飛んでください。

label sample_tilemap:

    ## イメージで定義した画像を表示します。
    ## tilemap.area を None にすると、画像全てを描画します。
    $ tilemap.area = None
    show map at truecenter
    pause

    ## tilemap.area を None 以外にすると、その範囲のみ描画します。
    $ tilemap.area = (64,64,256,256)
    pause
    
    ## スクリーン上に表示ことも出来ます。
    ## click を True にすると、クリックした時に座標を返すようになります。
    $ tilemap.area = None
    $ tilemap.click = True
    call screen tilemapscreen
    "[_return]"

    return
    
    
screen tilemapscreen():
    text "Cick a tile to get its coodinate" align .5, .9
    add tilemap at truecenter


##############################################################################
## Definitions
##############################################################################

init -3 python:

    class Tilemap(renpy.Displayable):

        """
        This creates a displayable by tiling other displayables. It has the following field values.

        map -  A 2-dimensional list of strings that represent index of a tileset.
        tileset -  A list of displayables that is used as a tile of tilemap.
        tile_width - width of each tile.
        tile_height - height of each tile.
        tile_mapping - a dictionaly that maps string of map to index of tileset.
           If None, each corrdinate of map should be integer.
        click - If true, it returns coodinate when you clicked this displayable on screens. 
        area - (x,y,w,h) tuple to render. If it's None, default, it renders all tiles.
        mask - 2-dimentional list of 0 or 1. If it's 0, tile will no be rendered.
        """

        def __init__(self, map, tileset, tile_width, tile_height = None, tile_mapping = None, click = False, area = None, mask = None, **properties):

            super(Tilemap, self).__init__(**properties)
            self.map = map
            self.tileset = tileset
            self.tile_width = tile_width
            self.tile_height = tile_height or tile_width
            self.tile_mapping = tile_mapping
            self.click = click
            self.area = area
            self.mask = mask


        def render(self, width, height, st, at):

            render = renpy.Render(width, height)

            # Blit all tiles into the render.
            if self.area == None:

                # Get tile position
                for y in xrange(len(self.map)):
                    for x in xrange(len(self.map[y])):
                        if not self.mask or self.mask[y][x] == 1:

                            # Get index of tileset
                            if self.tile_mapping:
                                if self.map[y][x] in self.tile_mapping.keys():
                                    tile = self.tile_mapping[self.map[y][x]]
                                else:
                                    tile = 0
                            else:
                                tile = self.map[y][x]

                            # Blit
                            render.blit(
                                renpy.render(self.tileset[tile], self.tile_width, self.tile_height, st, at),
                                (x*self.tile_width, y*self.tile_height)
                                )

                # Adjust the render size.
                render = render.subsurface((0, 0, len(self.map[0])*self.tile_width, len(self.map)*self.tile_height))

            # Blit only tiles around the area into the render
            else:

                # Calculate where the area is positioned on the entire map.
                self.xoffset = divmod(self.area[0], self.tile_width)
                self.yoffset = divmod(self.area[1], self.tile_height)

                # Get tile position
                for y in xrange(self.yoffset[0], min(len(self.map), self.area[3]//self.tile_height+self.yoffset[0]+1)):
                    for x in xrange(self.xoffset[0], min(len(self.map[y]), self.area[2]//self.tile_width+self.xoffset[0]+1)):
                        if 0 <=  y < len(self.map) and 0 <= x < len(self.map[0]):
                            if not self.mask or self.mask[y][x] == 1:

                                # Get index of tileset
                                if self.tile_mapping:
                                    if self.map[y][x] in self.tile_mapping.keys():
                                            tile = self.tile_mapping[self.map[y][x]]
                                    else:
                                            tile = 0
                                else:
                                    tile = self.map[y][x]

                                # Blit
                                render.blit(
                                    renpy.render(self.tileset[tile], self.tile_width, self.tile_height, st, at),
                                    (x*self.tile_width, y*self.tile_height)
                                    )

                # Crop the render.
                render = render.subsurface(self.area)

            # Redraw regularly
            # renpy.redraw(self, 1.0/30)

            return render
            
            
        def event(self, ev, x, y, st):
            
            # Returns coodinate of displayable when it's clicked  
            # If you want to pass coordinate into a screen, change store variables instead of return.
            if self.click:
                if renpy.map_event(ev, "button_select") and 0<x< len(self.map[0])*self.tile_width and 0<y< len(self.map)*self.tile_height:
                    return int(x/self.tile_width), int(y/self.tile_height)


        def per_interact(self):

            # Redraw per interact.
            renpy.redraw(self, 0)


        def visit(self):

           # If the displayable has child displayables, this method should be overridden to return a list of those displayables.
           return self.tileset


    def read_spritesheet(file, sprite_width, sprite_height=None, columns=1, rows=1, spacing=0, margin=0, livecrop=False):

        """ Function that returns a list of displayables from a spritesheet. """

        sprite_height = sprite_height or sprite_width
        sprites=[]
        for r in xrange(rows):
            for c in xrange(columns):
                rect = ((sprite_width+spacing)*c+margin, (sprite_height+spacing)*r+margin, sprite_width, sprite_height)
                if livecrop:
                    sprites.append(LiveCrop(rect, file))
                else:
                    sprites.append(im.Crop(file, rect))

        return sprites


