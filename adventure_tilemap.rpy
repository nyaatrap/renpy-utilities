## This file adds tilemap exploring function into adventure framework.
## This framework requires tilemap.rpy and adventure.rpy.
## adventure にタイルマップを探索する機能を追加するファイルです。
## tilemap.rpy と adventure.rpy が必要になります。

##############################################################################
## How to Use
##############################################################################


## まずタイルマップを作成します。
# tilemap = Tilemap(map1, tileset, 32, 32)

## 次にそれを使ってレベルを Level(image, music) で定義します。
## image は画像ではなく、タイルマップオブジェクトです。
## ここでは、tilemap.rpy で定義した tilemap を使うため、init offset を設定しています。
init offset = 1
define level.field = Level(tilemap)


## それから冒険者を TilemapPlayer(level, pos, cursor) を使って default で定義します。
## level はゲームをスタートするレベル、pos はそのタイルの座標です。
## 通常の adventure と異なり整数のペア(x,y)で与えます。
## cursor はマウスの乗っているタイルを色変えする画像です。
## adventure.rpy との定義の重複を避けるため別名にしていますが、
## ゲームスタート後は player に戻して使います。

default tilemapplayer = TilemapPlayer("field", pos=(0,0),
    cursor = Transform(Solid("#f66", xysize=(32,32)), alpha=0.5), turn=0)


## タイルマップ上のイベントを定義します。
## define ラベル名 = Event(level, pos, cond, priority, once, multi) で定義します。

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


## 次のイベントは、プレイヤーの操作前に呼び出されるイベントです。
define ev.enter = Event("field", once=True, trigger="stay")
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

define ev.outside_map = Event("field", trigger = "click", priority=99)
label outside_map:
    "You clicked outside of the map"
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
    $ player.action = "stay"

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
        $ _events = player.get_events(player.pos, player.action)

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

        $ block()

        # show eventmap or tilemap navigator
        if player.in_tilemap():
            call screen tilemap_navigator(player)
        else:
            call screen eventmap_navigator(player)

        if isinstance(_return, basestring):
            $ player.action = _return

        else:
            $ player.action = "move"
            $ player.move_pos(_return)


##############################################################################
## Tilemap navigator screen

screen tilemap_navigator(player):

    # When outside of map is clicked.
    button:
        xysize (config.screen_width, config.screen_height)
        action Return("click")

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


    ## show events
    for i in player.get_events():
        button:
            if i.image and isinstance(i.pos, tuple):
                xysize (width, height)
                if tilemap.isometric:
                    xoffset (i.pos[0]-i.pos[1])*width/2 - tilemap.tile_offset[0]
                    yoffset (i.pos[0]+i.pos[1])*height/2 - tilemap.tile_offset[1]
                    xpos (len(tilemap.map) -1)*width/2
                else:
                    xoffset i.pos[0]*width - tilemap.tile_offset[0]
                    yoffset i.pos[1]*height- tilemap.tile_offset[1]

                add i.image



##############################################################################
## TilemapPlayer class

init -5 python:

    class TilemapPlayer(Player):

        """
        Expanded Player Class that stores various methods and data for tilemap exploring.
        """

        def in_tilemap(self):
            # returns true if player is in tilemap

            return isinstance(self.image, Tilemap)


        def get_events(self, pos=None, action=None):
            # returns event list that happens in the given pos.
            # this overwrites the same method in player class.

            actions = ["stay"]
            if action == "move":
                actions += ["move"]
            if action == "click":
                actions += ["click"]

            events = []
            for i in self.current_events:
                if i.once and self.happened(i):
                    continue
                if action and i.trigger not in actions:
                    continue
                if action == None or i.pos == None or i.pos == pos:
                    if eval(i.cond):
                        events.append(i)
                elif self.in_tilemap() and pos and i.pos == self.image.map[pos[1]][pos[0]]:
                    if eval(i.cond):
                        events.append(i)

            if action:
                return self.cut_events(events)
            else:
                return events


