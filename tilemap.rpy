## This file defines Tilemap class that create single map from small tile images.
## 小さな画像を並べて一枚の画像にする Tilemap クラスを追加するファイルです。

##############################################################################
## How to Use
##############################################################################

init python:

    ## まず最初に、 各タイルを displayable（表示可能オブジェクト）のリストとして定義します。
    tileset =[Solid("#77f", xysize=(32,32)), Solid("#ff9", xysize=(32,32)), Solid("#3f6", xysize=(32,32))]

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

    ## 最後にタイルマップの displayable を Tilemap(map, tileset, tile_width, tile_height, tile_mapping)
    ## の形で定義します。
    tilemap = Tilemap(map1, tileset, 32,32)

# 画像タグに関連付けても使えます。
image map = tilemap


## ゲームがスタートしたら、 イメージで定義した画像を表示します。
# show map at truecenter
# "マップ全てを表示"

## tilemap.area を None 以外にすると、その範囲のみ描画します。
# $ tilemap.area = (64,64,256,256)
# "マップの一部を表示"


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
        area - (x,y,w,h) tuple to render. If it's None, default, it renders all tiles.
        """

        def __init__(self, map, tileset, tile_width, tile_height, tile_mapping = None, area = None, **properties):

            super(Tilemap, self).__init__(**properties)
            self.map = map
            self.tileset = tileset
            self.tile_width = tile_width
            self.tile_height = tile_height
            self.tile_mapping = tile_mapping
            self.area = area


        def render(self, width, height, st, at):

            render = renpy.Render(width, height)

            if self.area == None:
                # Blit all tiles into the render.
                for y in xrange(len(self.map)):
                    for x in xrange(len(self.map[y])):
                        tile = self.tile_mapping[self.map[y][x]]  if self.tile_mapping else self.map[y][x]
                        render.blit(renpy.render(self.tileset[tile], self.tile_width, self.tile_height, st, at), (x*self.tile_width, y*self.tile_height))

                    # Adjust the render size.
                    render = render.subsurface((0, 0, len(self.map[0])*self.tile_width, len(self.map)*self.tile_height))

            else:

                # Calculate where the area is positioned on the entire map.
                self.xoffset = divmod(self.area[0], self.tile_width)
                self.yoffset = divmod(self.area[1], self.tile_height)

                # Blit only tiles around the area into the render
                for y in xrange(self.yoffset[0], min(len(self.map), self.area[3]//self.tile_height+self.yoffset[0]+1)):
                    for x in xrange(self.xoffset[0], min(len(self.map[y]), self.area[2]//self.tile_width+self.xoffset[0]+1)):
                        if 0 <=  y < len(self.map) and 0 <= x < len(self.map[0]):
                            tile = self.tile_mapping[self.map[y][x]]  if self.tile_mapping else self.map[y][x]
                            render.blit(renpy.render(self.tileset[tile], self.tile_width, self.tile_height, st, at), (x*self.tile_width, y*self.tile_height))

                # Crop the render.
                render = render.subsurface(self.area)

            return render


        def per_interact(self):

            # Redraw per interact.
            renpy.redraw(self, 0)


        def visit(self):

           # If the displayable has child displayables, this method should be overridden to return a list of those displayables.
           return self.tileset


    ## 次の関数は一枚の画像を分割して displayable のリストにして返します。

    def read_spritesheet(file, sprite_width, sprite_height, columns, rows, spacing=0, margin=0, livecrop=False):

        ''' Function that returns a list of displayables from a spritesheet. '''

        sprites=[]
        for r in xrange(rows):
            for c in xrange(columns):
                rect = ((sprite_width+spacing)*c+margin, (sprite_height+spacing)*r+margin, sprite_width, sprite_height)
                if livecrop:
                    sprites.append(LiveCrop(rect, file))
                else:
                    sprites.append(im.Crop(file, rect))

        return sprites
        
    
    

