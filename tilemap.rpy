## This file defines Tilemap class that create single map from small tile images.
## 小さな画像を並べて一枚の画像にする Tilemap クラスを追加するファイルです。


##############################################################################
## How to Use
##############################################################################

init python:

    ## まず最初に、 各タイルを displayable（表示可能オブジェクト）のリストとして定義します。
    tileset =[Solid("#77f", xysize=(32,32)), Solid("#ff9", xysize=(32,32)), Solid("#3f6", xysize=(32,32))]

    ## タイルを並べた一枚の画像を分割したい時は、次の関数も使えます。
    # tileset = read_spritesheet(filename, sprite_width, sprite_height, columns=1, rows=1)


    ## 次に整数の二次元配列を定義します。値は tileset のインデックスで 0 は tileset[0] を表します。

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
    tilemap = Tilemap(map1, tileset, 32, 32)

# 画像タグに関連付けても使えます。
image map = tilemap


## ゲームがスタートしたら jump sample_tilemap でここに飛んでください。

label sample_tilemap:

    ## イメージで定義した画像を表示します。
    show map at truecenter

    ## tilemap.area を None 以外にすると、その範囲のみ描画します。
    $ tilemap.area = (64,64,256,256)
    pause

    ## tilemap.area を None にすると、画像全てを描画します。
    $ tilemap.area = None

    ## tilemap.coordinate でマウスがホバーしているタイルの座標を取得する事ができます。
    call screen tilemap_coordinate(tilemap)
    "[_return]"

    return


##############################################################################
## Screen that shows coordinate of tilemap

screen tilemap_coordinate(tilemap):    

    text "Cick a tile to return its coodinate" align .5, .9

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
        tile_mapping - a dictionaly that maps string of map to index of tileset.
           If None, each corrdinate of map should be integer.
        tile_offset - blank pixel of (left, top) side of each tile
        isometric - if true, isometric tile is used. 
        area - (x,y,w,h) tuple to render. If it's None, default, it renders all tiles.
        mask - 2-dimentional list of 0 or 1. If it's 0, tile will no be rendered.
        interact - If true, it restarts interaction when mouse position is changed onto another tile.
        coordinate - (x, y) coordinate of a tile  where mouse is hovering.
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


