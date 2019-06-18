## This file adds tilemap exploring function into adventure framework.
## This framework requires tilemap.rpy and adventure.rpy.
## adventure にタイルマップを探索する機能を追加するファイルです。
## tilemap.rpy と adventure.rpy が必要になります。

##############################################################################
## How to Use
##############################################################################


## まずタイルマップを作成します。
# tilemap1 = Tilemap(map1, tileset, 32, 32)

## 次にそれを使ってレベルを TiledLevel(image, music, tilemap) で定義します。
## image はタイルマップから定義した画像、 tilemap は元のタイルマップオブジェクトです。
## ここでは、tilemap.rpy で定義した tilemap を使うため、init offset を設定しています。
init offset = 1
define level.field = TiledLevel("tilemap1", tilemap=tilemap1)


## それから冒険者を TilemapPlayer(level, pos) を使って default で定義します。
## level はゲームをスタートするレベル、pos はそのタイルの座標です。
## 通常の adventure と異なり整数のペア(x,y)で与えます。
## adventure.rpy との定義の重複を避けるため別名にしていますが、
## ゲームスタート後は player に戻して使います。

default tilemapplayer = TilemapPlayer("field", pos=(0,0), turn=0, icon = Text("P"))


## タイルマップ上のイベントを定義します。
## define ラベル名 = Event(level, pos, cond, priority, once, multi) で定義します。

## クリックで発生するイベントです。 icon を与えると tilemap の上にその画像が表示されます。
## タイルマップはすべての座標がクリック可能となるので place や active を設定する必要はありません。

define ev.iconA = Event("field", pos=(5,0), icon=Text("A"))
label iconA:
    "icon A is clicked"
    return


define ev.iconB = Event("field", pos=(8,7), icon=Text("B"))
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
    $ player.update_tilemap()

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
            $ player.update_tilemap()


##############################################################################
## Tilemap navigator screen

screen tilemap_navigator(player):

    # show coordinate
    python:
        tilemap = player.tilemap
        width = tilemap.tile_width
        height = tilemap.tile_height

    on "show" action SetField(tilemap, "show_cursor", True)
    on "hide" action SetField(tilemap, "show_cursor", False)

    # When outside of map is clicked.
    button:
        xysize (config.screen_width, config.screen_height)
        action Return("click")


    if tilemap.coordinate:

        ## show coordinate
        $ x, y = tilemap.coordinate
        text "([x], [y])"

        ## returns coordinate of tiles
        key "button_select" action Return((x, y))



##############################################################################
## TiledLevel class.

init -9 python:

    class TiledLevel(Level):

        """
        Expanded Level class.
        """

        def __init__(self, image=None, music=None, tilemap=None):

            super(TiledLevel, self).__init__(image, music)
            self.tilemap = tilemap


##############################################################################
## TilemapPlayer class


    class TilemapPlayer(Player):

        """
        Expanded Player Class that stores various methods and data for tilemap exploring.
        """

        def __init__(self, level=None, pos=None, icon=None, **kwargs):

            super(TilemapPlayer, self).__init__(level, pos, **kwargs)

            self.replaced_tiles = {}
            self.seen_tiles = {}
            self.icon = icon
            self.mask_tilemap = True


        @property
        def tilemap(self):
            return self.get_level(self.level).tilemap


        def in_tilemap(self):
            # returns true if player is in tilemap

            return isinstance(self.tilemap, Tilemap)


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
                elif self.in_tilemap() and pos and i.pos == self.get_tile(pos=pos):
                    if eval(i.cond):
                        events.append(i)
            if action:
                return self.cut_events(events)
            else:
                return events


        def get_tile(self, level=None, pos=None, numeric=False):
            # returns tile from current or given pos

            import re
            pattern = "[0-9]+"

            if not self.in_tilemap():
                return

            level = level or self.level
            pos = pos or self.pos

            if (pos[0], pos[1]) in self.replaced_tiles.get(level, ()):
                tile = level.replaced_tiles[level][(pos[0], pos[1])]
            else:
                tile = self.get_level(level).tilemap.map[pos[1]][pos[0]]

            if tile and numeric and isinstance(tile, basestring):
                tile = int(re.findall(pattern, tile)[0])

            return tile


        def set_tile(self, tile, level=None, pos=None):

            if not self.in_tilemap():
                return

            level = level or self.level
            pos = pos or self.pos

            self.replaced_tiles.setdefault("level", {})
            self.replaced_tiles[level].setdefault((pos[0], pos[1]), tile)


        def set_seen_tile(self, level=None, pos=None, around=1):

            if not self.in_tilemap():
                return

            level = level or self.level
            pos = pos or self.pos

            if not level in self.seen_tiles.keys():
                self.seen_tiles[level] = [[0 for j in xrange(len(self.tilemap.map[0]))] for i in xrange(len(self.tilemap.map))]
            for x in xrange(-around, 1+around):
                for y in xrange(-around, 1+around):
                    if pos[1]+y >= 0 and pos[0]+x >=0:
                        try:
                            self.seen_tiles[level][pos[1]+y][pos[0]+x]=1
                        except IndexError:
                            pass


        def add_mask(self):

            if not self.in_tilemap():
                return

            if self.level in self.seen_tiles.keys():
                self.tilemap.mask = self.seen_tiles[self.level]


        def add_objects(self):

            if not self.in_tilemap():
                return

            objects = []
            for i in self.get_events():
                if i.icon and i.pos:
                    objects.append((i.pos, i.icon))

            if self.icon and self.pos:
                objects.append(((self.pos[0], self.pos[1]), self.icon))

            self.tilemap.objects = objects


        def add_replaced_tiles(self):

            if not self.in_tilemap():
                return

            if self.level in self.replaced_tiles.keys():
                self.tilemap.replaced_tiles = self.replaced_tiles[self.level]


        def update_tilemap(self):

            self.add_objects()
            self.add_replaced_tiles()

            if self.mask_tilemap:
                self.set_seen_tile()
                self.add_mask()




