## This file defines Tilemap class that create single map from small tile images.
## 小さな画像を並べて一枚の画像にする Tilemap クラスを追加するファイルです。


##############################################################################
## How to Use
##############################################################################

init python:

    ## まず最初に、マップに使う各タイルを displayable（表示可能オブジェクト）のリストとして定義します。
    ## 例： tileset = ["water.png", "forest.png", ...]
    ## ここでは Ren'py の機能を使って単色の四角形を描画しています。

    tileset = [Solid("#77f", xysize=(32,32)), Solid("#ff9", xysize=(32,32)), Solid("#3f6", xysize=(32,32))]

    ## タイルを並べた一枚の画像を分割したい時は、次の関数も使えます。
    # tileset = read_spritesheet(filename, sprite_width, sprite_height, columns=1, rows=1, spacing=0, margin=0)


    ## 次に描画したいマップを整数の二次元配列で表現します。
    ## 配列の値は上で定義したリストのインデックスで
    ## tileset = ["water.png", "forest.png", ...] の場合 0 は "water.png" を表します。

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

    ## テキストファイルで定義したマップを次の関数で読み込むことも出来ます。
    ## numeral を True にすると、文字列を整数に変換して読み込みます。
    # map1 = read_spreadsheet(file, separator="\t", numeral=False):


    ## 最後にタイルマップを Tilemap(map, tileset, tile_width, tile_height, tile_mapping) の形で定義します。
    ## map, tileset は上で定義したもので、tile_width, tile_height は各タイルのサイズです。

    tilemap = Tilemap(map1, tileset, 32, 32)

    ## tile_mapping は整数以外の文字を使ってマップを作る場合に必要になります。
    ## 次のように tile_mapping を定義して、どの文字がどのインデックスに対応するか定めます。
    # tile_mapping = {"w":0, "f":1, ...}

    ## isometric を True にすると斜め見下ろしの視点で描画します。
    # tilemap = Tilemap(map1, tileset, 32, 32, isometric=True)

# Tilemap は displayable です。show 文で使う場合は画像タグに関連付けてから使います。
image map = tilemap


## ゲームがスタートしたら jump sample_tilemap でここに飛んでください。

label sample_tilemap:

    ## イメージで定義したマップ画像を表示します。
    show map at truecenter

    ## tilemap.area を None 以外にすると、その範囲のみ描画します。
    $ tilemap.area = (64,64,256,256)
    pause

    ## tilemap.area を None にすると、画像全てを描画します。
    $ tilemap.area = None

    ## また tilemap.coordinate にはマウスがホバーしているタイルの座標が格納されています。
    call screen track_coordinate(tilemap)
    "[_return]"

    return


##############################################################################
## Screen that shows coordinate of tilemap

screen track_coordinate(tilemap):

    text "Click a tile to return its coodinate" align .5, .9

    # show coordinate
    if tilemap.coordinate:
        text "[tilemap.coordinate]"
        key "button_select" action Return(tilemap.coordinate)


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
        tile_mapping - a dictionary that maps string of map to index of tileset.
           If None, each coordinate of map should be integer.
        tile_offset - blank pixel of (left, top) side of each tile
        isometric - if true, isometric tile is used.
        area - (x,y,w,h) tuple to render. If it's None, default, it renders all tiles.
        mask - 2- dimensional list of 0 or 1. If it's 0, tile will not be rendered.
        interact - If True, it restarts interaction when mouse position is changed onto another tile. default is True.
        coordinate - (x, y) coordinate of a tile where mouse is hovering.
        """

        def __init__(self, map, tileset, tile_width, tile_height = None, tile_mapping = None, tile_offset = (0,0),
            isometric = False, area = None, mask = None, interact = True, **properties):

            super(Tilemap, self).__init__(**properties)
            self.map = map
            self.tileset = tileset
            self.tile_width = tile_width
            self.tile_height = tile_height or tile_width
            self.tile_mapping = tile_mapping
            self.tile_offset = tile_offset
            self.isometric = isometric
            self.area = area
            self.mask = mask
            self.interact = interact
            self.coordinate = None


        def render(self, width, height, st, at):

            render = renpy.Render(width, height)

            # Blit all tiles into the render.
            if self.area == None:

                # Get tile position
                for y in xrange(len(self.map)):
                    for x in xrange(len(self.map[y])):

                        # render
                        self._render(render, st, at, x, y)

                # Adjust the render size.
                if self.isometric:
                    area = (
                        -len(self.map)*self.tile_width/2,
                        0,
                        (len(self.map) + len(self.map[0]))*self.tile_width/2,
                        (max(len(self.map[0]), len(self.map)) + 1)*self.tile_height
                        )
                else:
                    area = (0, 0, len(self.map[0])*self.tile_width, len(self.map)*self.tile_height)

                render = render.subsurface(area)

            # Blit only tiles around the area into the render
            else:

                # Calculate where the area is positioned on the entire map.
                self.xoffset = divmod(self.area[0], self.tile_width)
                self.yoffset = divmod(self.area[1], self.tile_height)

                # Get tile position
                for y in xrange(self.yoffset[0], min(len(self.map), self.area[3]//self.tile_height+self.yoffset[0]+1)):
                    for x in xrange(self.xoffset[0], min(len(self.map[y]), self.area[2]//self.tile_width+self.xoffset[0]+1)):
                        if 0 <=  y < len(self.map) and 0 <= x < len(self.map[0]):

                            # render
                            self._render(render, st, at, x, y)

                # Crop the render.
                render = render.subsurface(self.area)

            # Redraw regularly
            # renpy.redraw(self, 1.0/30)

            return render


        def _render(self, render, st, at, x, y):

            # don't render if mask is given
            if self.mask and not self.mask[y][x]:
                return

            # Get index of tileset
            if self.tile_mapping:
                if self.map[y][x] in self.tile_mapping.keys():
                    tile = self.tile_mapping[self.map[y][x]]
                else:
                    tile = 0
            else:
                tile = self.map[y][x]

            # Get tile position
            if self.isometric:
                tile_pos = (x-y-1)*self.tile_width/2, (x+y)*self.tile_height/2
            else:
                tile_pos = x*self.tile_width, y*self.tile_height

            # Blit
            render.blit(renpy.render(self.tileset[tile], self.tile_width, self.tile_height, st, at), tile_pos)


        def event(self, ev, x, y, st):

            # Get index of tile where mouse is hovered.
            if self.isometric:
                tile_x = (x-self.tile_offset[0])/self.tile_width + (y-self.tile_offset[1])/self.tile_height - len(self.map)/2
                tile_y = -(x/self.tile_width-self.tile_offset[0]) + (y-self.tile_offset[1])/self.tile_height + len(self.map)/2
                if len(self.map) % 2 ==1:
                    tile_x -= 0.5
                    tile_y += 0.5
            else:
                tile_x = (x-self.tile_offset[0])/self.tile_width
                tile_y = (y-self.tile_offset[1])/self.tile_height

            # Make coordinate None if it's out of displayable
            if tile_x < 0 or tile_y < 0 or tile_x >= len(self.map[0]) or tile_y >= len(self.map):
                coordinate = None
            else:
                coordinate = int(tile_x), int(tile_y)

            # Restart interaction only if coordinate has changed
            if self.coordinate != coordinate:
                self.coordinate = coordinate

                if self.interact:
                    renpy.restart_interaction()

            # Call event regularly
            renpy.timeout(1.0/60)


        def per_interact(self):

            # Redraw per interact.
            renpy.redraw(self, 0)


        def visit(self):

           # If the displayable has child displayables, this method should be overridden to return a list of those displayables.
           return self.tileset


    def read_spritesheet(file, sprite_width, sprite_height=None, columns=1, rows=1, spacing=0, margin=0):

        # Function that returns a list of displayables from a spritesheet.

        sprite_height = sprite_height or sprite_width
        sprites=[]
        for r in xrange(rows):
            for c in xrange(columns):
                rect = ((sprite_width+spacing)*c+margin, (sprite_height+spacing)*r+margin, sprite_width, sprite_height)
                sprites.append(im.Crop(file, rect))

        return sprites


    def read_spreadsheet(file, separator="\t", numeral=False):

        # Function that returns a 2-dimensional list from a text file.
        # If numeral is True, string will convert to integer.

        rv = []
        f = renpy.file(file)
        for l in f:
            l = l.decode("utf-8")
            a = l.rstrip().split(separator)
            rv2 = []
            for n, x in enumerate(a):
                if x.isdecimal() and numeral:
                    x = int(x)
                elif numeral:
                    x = 0
                rv2.append(x)
            rv.append(rv2)
        f.close()

        return rv

