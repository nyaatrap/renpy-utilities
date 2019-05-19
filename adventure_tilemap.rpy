## This file adds tilemap exploring function into adventure framework.
## This framework requires tilemap.rpy and adventure.rpy.
## adventure にタイルマップを探索する機能を追加するファイルです。
## tilemap.rpy と adventure.rpy が必要になります。

##############################################################################
## How to Use
##############################################################################


## まずタイルマップを作成します。
# tilemap = Tilemap(map1, tileset, 32, 32)

## 次にそれを使ってレベルを Level(image, music) を default で定義します。
## image は画像ではなく、タイルマップオブジェクトです。
## ここでは、tilemap.rpy で定義した tilemap を使います。

default level.field = Level(tilemap)


## それから冒険者を TilemapPlayer(level, pos, cursor) を使って default で定義します。
## level はゲームをスタートするレベル、pos はそのタイルの座標です。
## 通常の adventure と異なり整数のペア(x,y)で与えます。
## cursor はマウスの乗っているタイルを色変えする画像です。
## adventure.rpy との定義の重複を避けるため別名にしていますが、
## ゲームスタート後は player に戻して使います。

default tilemapplayer = TilemapPlayer("field", pos=(0,0),
    cursor = Transform(Solid("#f66", xysize=(32,32)), alpha=0.5), turn=0)


## タイルマップ上のイベントを定義します。
## define ラベル名 = Event(level, pos, cond, priority, once, multi, precede, label) で定義します。

## クリックで発生するイベントです。 image を与えると tilemap の上にその画像が表示されます。
## タイルマップはすべての座標がクリック可能となるので place や active を設定する必要はありません。

define ev.iconA = Event("field", pos=(5,0), image=Text("A"))
label iconA:
    "icon A is clicked"
    return


define ev.iconB = Event("field", pos=(8,7), image=Text("B"))
label iconB:
    "icon B is clicked"
    return


## pos が与えられていないイベントは、そのレベル内ならどこでも発生します。
define ev.ev0 = Event("field", priority=99)
label ev0:
    "there is nothing there"
    return


## 次のイベントは、プレイヤーがその座標にいる時に、プレイヤーの操作前に呼び出されるイベントです。
define ev.enter = Event("field", pos=(0,0), precede=True, priority=999)
label enter:
    "enter point"
    return


## pos を整数もしくは文字列にすると、その文字列がマップを定義した二元配列の値と一致する座標の場合に、イベントが発生します。
## タイルマップの定義に文字列を利用した場合に特に有効です。
define ev.ev1 = Event("field", pos=1, priority=1)
label ev1:
    "mapchip'1' is clicked"
    return

define ev.ev2 = Event("field", pos=2, priority=1)
label ev2:
    "mapchip'2' is clicked"
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

    # Update event list in the current level
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
        $ _events = player.get_passive_events()

        # sub loop to execute all passive events
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

        #  If return value is a place, move to there
        if isinstance(_return, Place):
            $ player.pos = _return.pos

        # If return value is an active event, execute it.
        elif isinstance(_return, Event):
            $ player.pos = _return.pos
            $ player.event = _return
            $ block()
            $ player.happened_events.add(player.event.name)
            call expression player.event.label or player.event.name
            $ player.done_events.add(player.event.name)
            if player.move_pos(_return):
                jump adventure_tilemap

        # If return value is coordinate, move to there
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

        ## show coordinate
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

    ## show places and active events
    for i in player.get_active_events():
        button:
            if isinstance(i.pos, tuple):
                xysize (width, height)
                if tilemap.isometric:
                    xoffset (i.pos[0]-i.pos[1])*width/2 - tilemap.tile_offset[0]
                    yoffset (i.pos[0]+i.pos[1])*height/2 - tilemap.tile_offset[1]
                    xpos (len(tilemap.map) -1)*width/2
                else:
                    xoffset i.pos[0]*width - tilemap.tile_offset[0]
                    yoffset i.pos[1]*height- tilemap.tile_offset[1]
            else:
                xysize (config.screen_width, config.screen_height)

            if i.active:
                action Return(i)

            # show image on screen. you can also show them on the background.
            if i.image:
                add i.image



##############################################################################
## TilemapPlayer class

init -2 python:

    class TilemapPlayer(Player):

        """
        Expanded Player Class that stores various methods and data for tilemap exploring.
        """

        def in_tilemap(self):
            # returns true if player is in tilemap

            return isinstance(self.image, Tilemap)


        def get_passive_events(self):
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


