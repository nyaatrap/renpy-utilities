## This file adds tilemap exploring function into adventure framework.
## This framework requres tilemap.rpy and adventure.rpy.
## adventure にタイルマップを探索する機能を追加するファイルです。
## tilemap.rpy と adventure.rpy が必要になります。

##############################################################################
## How to Use
##############################################################################


## まずタイルマップを作成します。

init python:
    
    tileset2 =[Image("ground/1.png"), Image("ground/2.png")]

    map2 = [
        ["1","1","1","1","1","1"],
        ["1","0","1","0","0","0"],
        ["1","0","1","0","1","1"],
        ["1","0","0","0","0","1"],
        ["1","0","1","1","0","0"],
        ["1","0","0","0","0","1"],
        ]
        
    tile_mapping = {"0":0, "1":1}
        
    tilemap2 = Tilemap(map2, tileset2, 192, 96, tile_mapping, tile_offset = (0, 44), isometric=True)        
        
## 次にそれらを使ってレベルを Level(image, music) で定義します。
## image は画像ではなく、タイルマップオブジェクトです。
## default で定義します。

default level.field = Level(tilemap2)


## 最後に冒険者を Explorer クラスで定義します。

default explorer = Explorer("field", pos=(1,1), cursor = Image("ground/0.png"))


## フィールドのイベントを定義します。

define ev.enter = Event("field", pos=(1,1))
label enter:
    "enter point"
    return

define ev.none = Event("field", priority=-10)
label none:
    "There is nothing"
    return

## pos を文字列にするとその文字列のある map の座標でイベントが発生します。
define ev.passive1 = Event("field", pos="1", priority=-1)
label passive1:
    "passive event on tile 1"
    return True
        

define place.wood = Place("field", pos=(3,0), image="top/1.png")
define ev.wood = Event("wood")
label wood:
    "icon is clicked"
    return
    
define place.wood2 = Place("field", pos=(0, 5), image="top/2.png")
define ev.wood2 = Event("wood2")
label wood2:
    "icon is clicked"
    return
    
define place.wood3 = Place("field", pos = (3,3), image="top/3.png")
define ev.wood3 = Event("wood3")
label wood3:
    "icon is clicked"
    return


## start ラベルから explore へジャンプすると探索を開始します。


##############################################################################
## Definitions
##############################################################################

##############################################################################
## Main label
## Jumping to this label starts exploration

label explore:

    # Update event list in current level
    $ explorer.update_events()
    $ explorer.after_interact = False

    # Play music
    if explorer.music:
        if renpy.music.get_playing() != explorer.music:
            play music explorer.music fadeout 1.0

    # Show background
    if explorer.image:
        scene black with Dissolve(.25)
        show expression explorer.image at topleft
        with Dissolve(.25)

    jump explore_loop


label explore_loop:
    while True:

        # check passive events
        $ block()
        $ _events = explorer.get_events()

        # sub loop to excecute all passive events
        $ _loop = 0
        while _loop < len(_events):

            $ explorer.event = _events[_loop]
            $ block()
            call expression explorer.event.label or explorer.event.name
            if explorer.move_pos(_return):
                jump explore
            $ _loop += 1

        $ explorer.after_interact = True
        $ block()
        
        # show eventmap
        if explorer.in_tilemap():
            call screen tilemap_navigator(explorer)
        else:
            call screen eventmap_navigator(explorer)

        # move by place
        if isinstance(_return, Place):
            $ explorer.pos = _return.pos

        # excecute click event
        elif isinstance(_return, Event):
            $ explorer.event = _return
            $ block()
            call expression explorer.event.label or explorer.event.name
            if explorer.move_pos(_return):
                jump explore
                
        # move
        else:
            $ explorer.pos = _return
            jump explore_loop

            
##############################################################################
## Tilemap navigator screen
## This overwrites eventmap screen

screen tilemap_navigator(explorer):       
    
    # show coordinate
    python:
        tilemap = explorer.image
        width = tilemap.tile_width
        height = tilemap.tile_height
    
    if tilemap.coordinate:
        $ x, y = tilemap.coordinate
    
        text "([x], [y])"
    
        ## show cursor
        if explorer.cursor:
            add explorer.cursor:
                if tilemap.isometric:
                    xoffset (x-y)*width/2
                    yoffset (x+y)*height/2
                    xpos (len(tilemap.map) -1)*width/2
                else:
                    xoffset x*width
                    yoffset y*height
                    
        key "button_select" action Return((x, y))                

    ## show places and events
    for i in explorer.get_places() + explorer.get_events(click=True):
        button xysize (width, height):
            action Return(i)
            if  i.image:
                add i.image
            if tilemap.isometric:
                xoffset (i.pos[0]-i.pos[1])*width/2 - tilemap.tile_offset[0]
                yoffset (i.pos[0]+i.pos[1])*height/2 - tilemap.tile_offset[1]
                xpos (len(tilemap.map) -1)*width/2
            else:
                xoffset i.pos[0]*width - tilemap.tile_offset[0]
                yoffset i.pos[1]*height- tilemap.tile_offset[1]

            

##############################################################################
## Explore class

init -2 python:

    class Explorer(Player):

        """
        Expanded Player Class that stores various methods and data for tilemap exploring.
        """

        def in_tilemap(self):
            # returns true if explorer is in tilemap

            return isinstance(self.image, Tilemap)


        def _check_pos(self, ev, click, pos):
            # It overrides a same method to support coordinate

            if click or ev.pos == None or ev.pos == pos:
                return True
                
            elif ev.pos == self.image.map[pos[1]][pos[0]]:
                return True


