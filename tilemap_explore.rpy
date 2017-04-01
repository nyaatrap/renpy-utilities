## This file adds tilemap exploring function into adventure framework.
## This framework requres tilemap.rpy and adventure.rpy.
## adventure にタイルマップを探索する機能を追加するファイルです。
## tilemap.rpy と adventure.rpy が必要になります。

##############################################################################
## How to Use
##############################################################################


## まずタイルマップを作成します。
## ここでは tilemap.rpy で定義したものを直接使います。
        
## 次にそれらを使ってレベルを Level(image, music) で定義します。
## image は画像ではなく、タイルマップオブジェクトです。
## default で定義します。

default level.field = Level(tilemap)


## 最後に冒険者を Explorer クラスで定義します。
## pos はゲームをスタートするタイルの座標です。
## cursor はマウスの乗っているタイルを色変えする画像です。

default explorer = Explorer("field", pos=(1,1), cursor = Transform(Solid("#f66", xysize=(32,32)), alpha=0.5))


## タイルマップ上のイベントを定義します。

## イベントは、プレイヤーがposの位置に移動した時に呼び出されます。
define ev.enter = Event("field", pos=(1,1), precede=True)
label enter:
    "enter point"
    return
    
## pos を文字列にすると、その文字列のある map の座標でイベントが発生します。
## タイルマップを文字列で定義したときのみ有効です。
define ev.ev1 = Event("field", pos="1")
label ev1:
    "tile 1"
    return

## pos が与えられていないイベントは、そのレベル内なら毎ターン発生します。
define ev.ev0 = Event("field", priority=-1)
label ev0:
    "tile 0"
    return

        
## image を与えると tilemap navigator 上に表示されます。

define ev.iconA = Event("field", pos=(5,0), image=Text("A"))
label iconA:
    "icon A is clicked"
    return
    
define ev.iconB = Event("field", pos=(8,7), image=Text("B"))
label iconB:
    "icon B is clicked"
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
        
        # show eventmap or tilemap navigator
        if explorer.in_tilemap():
            call screen tilemap_navigator(explorer)
        else:
            call screen eventmap_navigator(explorer)
        
        #  If return value is a place
        if isinstance(_return, Place):
            $ explorer.pos = _return.pos
        
        # If return value is an event
        elif isinstance(_return, Event):
            $ explorer.pos = _return.pos
            $ explorer.event = _return
            $ block()
            call expression explorer.event.label or explorer.event.name
            if explorer.move_pos(_return):
                jump explore
            
        # If return value is coordinate
        elif isinstance(_return, tuple):
            $ explorer.pos = _return

            
##############################################################################
## Tilemap navigator screen

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
                    
        ## returns coordinate of tiles 
        key "button_select" action Return((x, y))

    ## show places and events
    for i in explorer.get_places() + explorer.get_shown_events():
        button xysize (width, height):
            if tilemap.isometric:
                xoffset (i.pos[0]-i.pos[1])*width/2 - tilemap.tile_offset[0]
                yoffset (i.pos[0]+i.pos[1])*height/2 - tilemap.tile_offset[1]
                xpos (len(tilemap.map) -1)*width/2
            else:
                xoffset i.pos[0]*width - tilemap.tile_offset[0]
                yoffset i.pos[1]*height- tilemap.tile_offset[1]
            if isinstance(i, Place) or i.active:
                action Return(i)
            if i.image:
                add i.image

            

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
            

        def get_events(self):
            # returns event list that happens in the given pos.
            # this overwrites the same method in player class.

            events = []
            for i in self.current_events:
                if not i.once or not self.seen(i):
                    if i.precede or self.after_interact:
                        if i.pos == None or i.pos == self.pos or i.pos == self.image.map[self.pos[1]][self.pos[0]]:
                            if not i.active and eval(i.cond):
                                events.append(i)

            return self.cut_events(events)


