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


## 最後に冒険者を TilemapPlayer クラスで定義します。
## pos はゲームをスタートするタイルの座標です。
## cursor はマウスの乗っているタイルを色変えする画像です。
## adventure.rpy との定義の重複を避けるため別名にしていますが、
## ゲームスタート後は player に戻して使います。

default tilemapplayer = TilemapPlayer("field", pos=(1,1), cursor = Transform(Solid("#f66", xysize=(32,32)), alpha=0.5), turn=0)


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
define ev.ev0 = Event("field", priority=1)
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


## start ラベルから adventure_tilemap へジャンプすると探索を開始します。


##############################################################################
## Definitions
##############################################################################

##############################################################################
## Main label
## Jumping to this label starts exploration

label adventure_tilemap:

    # rename back
    $ player = tilemapplayer
    
    # Update event list in current level
    $ player.update_events()
    $ player.after_interact = False

    # Play music
    if player.music:
        if renpy.music.get_playing() != player.music:
            play music player.music fadeout 1.0

    # Show background
    if player.image:
        scene black with Dissolve(.25)
        show expression player.image at topleft
        with Dissolve(.25)

    jump adventure_tilemap_loop


label adventure_tilemap_loop:
    while True:

        # check passive events
        $ block()
        $ _events = player.get_events()

        # sub loop to excecute all passive events
        $ _loop = 0
        while _loop < len(_events):

            $ player.event = _events[_loop]
            $ block()
            $ player.happened_events.add(player.event.name)
            call expression player.event.label or player.event.name
            $ player.done_events.add(player.event.name)
            if player.move_pos(_return):
                jump adventure_tilemap
            $ _loop += 1

        $ player.after_interact = True
        $ block()
        
        # show eventmap or tilemap navigator
        if player.in_tilemap():
            call screen tilemap_navigator(player)
        else:
            call screen eventmap_navigator(player)
        
        #  If return value is a place
        if isinstance(_return, Place):
            $ player.pos = _return.pos
        
        # If return value is an event
        elif isinstance(_return, Event):
            $ player.pos = _return.pos
            $ player.event = _return
            $ block()
            $ player.happened_events.add(player.event.name)
            call expression player.event.label or player.event.name
            $ player.done_events.add(player.event.name)
            if player.move_pos(_return):
                jump adventure_tilemap
            
        # If return value is coordinate
        elif isinstance(_return, tuple):
            $ player.pos = _return

            
##############################################################################
## Tilemap navigator screen

screen tilemap_navigator(player):       
    
    # show coordinate
    python:
        tilemap = player.image
        width = tilemap.tile_width
        height = tilemap.tile_height
    
    if tilemap.coordinate:
        
        ## show coodinate
        $ x, y = tilemap.coordinate    
        text "([x], [y])"
    
        ## show cursor
        if player.cursor:
            add player.cursor:
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
    for i in player.get_places() + player.get_shown_events():
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

    class TilemapPlayer(Player):

        """
        Expanded Player Class that stores various methods and data for tilemap exploring.
        """

        def in_tilemap(self):
            # returns true if player is in tilemap

            return isinstance(self.image, Tilemap)
            

        def get_events(self):
            # returns event list that happens in the given pos.
            # this overwrites the same method in player class.

            events = []
            for i in self.current_events:
                if not i.once or not self.happened(i):
                    if i.precede or self.after_interact:
                        if i.pos == None or i.pos == self.pos or i.pos == self.image.map[self.pos[1]][self.pos[0]]:
                            if not i.active and eval(i.cond):
                                events.append(i)

            return self.cut_events(events)


