## This file adds pseudo-3D dungeon crawling function into adventurer framework.
## This framework requires adventure.rpy.
## To play the sample game, download the dungeon folder then place it in the game directory.
## To show sample dungeon correctly, set screen size 800x600.
## adventure に疑似３Dダンジョン探索機能を追加するファイルです。
## adventure.rpy が必要になります。
## サンプルを実行するには dungeon フォルダーの画像をダウンロードして game ディレクトリに配置する必要があります。
## サンプルを正しく表示するには、スクリーンサイズを 800x600 に設定する必要があります。

##############################################################################
## How to Use
##############################################################################

## まず最初に画像の種類を文字列のリストで定義します。
## 文字列は表示する画像ファイルの接頭辞になります
## リストの一番最初はどのレイヤーでも共通で表示する背景画像になります。

define dungeonset = ["dungeon/base", "dungeon/floor", "dungeon/wall", "dungeon/door"]

## 次にダンジョンに表示する壁などの画像の数や重なりを2次元配列で定義します。
## この例では、一番遠くに９つ、一番近くに３つの画像を表示できるようにしています。
## c0をプレイヤーがいる位置と思って、上が画面の奥になるようイメージしてください。
## 文字列は表示する画像ファイルの接尾辞になります

define dungeon_layers = [
   ["llll6", "lll6", "ll6", "l6", "c6", "r6", "rr6", "rrr6", "rrrr6"],
            ["lll5", "ll5", "l5", "c5", "r5", "rr5", "rrr5"],
            ["lll4", "ll4", "l4", "c4", "r4", "rr4", "rrr4"],
                    ["ll3", "l3", "c3", "r3", "rr3"],
                    ["ll2", "l2", "c2", "r2", "rr2"],
                            ["l1","c1","r1"],
                            ["l0","c0","r0"],
    ]

## 上で定義した接頭辞と接尾辞の組み合わせで作る画像を用意します。
## "dungeon/floor_lll6.png" など
## 背景画像のみ最初で定義したリストの一番目と同じ名前にします。
## "dungeon/base.png"


## 描画したいマップを整数の二次元配列で表現します。
## 配列の値は上で定義したリストのインデックスで
## dungeonset = ["dungeonbase", "floor", ...] の場合 1 は floor を表します。
## 0 や空集合の場合は描画せず、後ろの背景画像が見えるようになります。

define map2 =[
[2,3,2,2,2,2,2,2],
[2,1,2,1,1,1,1,2],
[2,1,3,1,1,1,1,2],
[2,1,2,1,1,2,1,2],
[2,1,0,0,1,1,1,2],
[2,1,1,1,1,1,1,2],
[2,0,1,1,1,1,1,2],
[2,1,1,1,1,1,1,2],
[2,1,1,1,1,1,1,2],
[2,1,0,1,1,1,1,2],
[2,1,0,1,2,2,3,2],
[2,1,0,1,1,1,1,2],
[2,1,0,0,1,1,1,2],
[2,1,1,1,1,2,1,2],
[2,0,1,2,2,2,1,2],
[2,2,2,2,2,2,2,2]
]

## 侵入できないタイルの種類のリストも作成しておきます。
define collision = (0, 2, 3)

## ダンジョンの画像を LayeredMap(map, tileset, layers, mirror) で定義します。
## map, tileset, layers は上で定義したもので、pov は最後に定義するダンジョンプレイヤークラスを文字列で与えます。
## mirror を "left" か "right" にすると、指定した側の画像を反対側の画像を反転して描画します。
define dungeon_image = LayeredMap(map2, dungeonset, layers=dungeon_layers, mirror = "left")

## さらに ミニマップとして使うタイルマップを用意します。
define mm_tileset = [Solid("#000", xysize=(16,16)), Solid("#633", xysize=(16,16)), Solid("#ea3", xysize=(16,16)), Solid("#f33", xysize=(16,16))]

define minimap = Tilemap(map2, mm_tileset, 16)

## それらを使ってレベルを Dungeon(image, music, tilemap, collision) で定義します。
define level.dungeon = Dungeon(image=dungeon_image, tilemap = minimap, collision=collision)


## 最後に冒険者を DungeonPlayer クラスで定義します。
## ダンジョンの pos は (x,y,dx,dy) の組で、dx が 1 ならみぎ、-1 ならひだりを向きます。
## adventure.rpy との定義の重複を避けるため別名にしていますが、
## ゲームスタート後は player に戻して使います。

default dungeonplayer = DungeonPlayer("dungeon", pos=(1,1,0,1), turn=0, icon = Text("P"))


## ダンジョンのイベントを定義します。

## イベントには trigger によって発生条件が別れます。
## デフォルトの trigger = "move" は、その座標の上に移動した時に呼ばれます。
## "movefrom" - その座標から離れた時
## "nextto" - その座標の隣に移動した時
## "moveto" - 侵入不可能タイルに移動しようとした時
## "faceto" - 移動、または向きを変えて正面一歩前にタイルを捉えた時
## "click" - そのタイルの上でクリックした時
## "clickto" - そのタイルの正面一歩前でクリックした時
## "stay" - 状態にかかわらずそのタイルにいる時。これは行動前にも判定されます。


## パッシブイベントは、プレイヤーが pos の上下左右に移動した時に呼び出されます。
define ev.entrance = Event("dungeon", pos=(1,1), trigger="stay", once=True)
label entrance:
    "Enter point"
    return


## pos が与えられていないイベントは、そのレベル内ならどこでも発生します。
define ev.nothing = Event("dungeon", trigger = "click", priority=100)
label nothing:
    "There is nothing"
    return


## pos をマップを定義した二元配列の値と一致する整数または文字列にすると、そのイベントが発生します。

define ev.collision_wall = Event("dungeon", pos=2, trigger="moveto")
label collision_wall:
    with vpunch
    return


define ev.collision_pit = Event("dungeon", pos=0, trigger="moveto")
label collision_pit:
    "There is a pit"
    return


## player.next_pos には次に移動しようとする座標が格納されています。
## player.front_pos, back_pos, left_pos, right_pos で対応する座標を得られます。
## player.front2_pos, back2_pos は２歩前、２歩後ろの座標です。
## 返り値に (x,y) 座標を与えるとその場所に移動します。

define ev.collision_door = Event("dungeon", pos=3, trigger="moveto")
label collision_door:
    if player.front_pos == player.next_pos:
        scene black with dissolve
        return player.front2_pos
    else:
        with vpunch
        return


## 返り値に文字列と移動先の座標を与えるとそのレベルの場所に移動します。
define ev.exit = Event("dungeon", pos=(1,0), trigger="moveto", priority = -1)
label exit:
    menu:
        "Do you exit?"
        "yes":
            scene black with dissolve
            "You exited"
            return "dungeon", (1, 1, 0, 1)
        "no":
            pass
    return


## イベントに image を与えると、ダンジョンのタイル上に表示できます。
image sp = Solid("#4a3", xysize=(16,16))
image sp2 = "dungeon/sprite.png"
define ev.sprite = Event("dungeon", pos=(1, 8), trigger = "click", icon = "sp", image="sp2")
label sprite:
    "Hello"
    return

## 画像の表示位置は LayeredMap に以下のプロパティーを与えることで調整します。
## horizon_height はアイレベルの高さで、1.0 は画面の下端になります。
## tile_length はプレイヤーが立ってる地点のタイルの横幅で、1.0 は画面の右端になります。
## first_distance は視点と同じタイルにいるオブジェクトとの距離で
## 値が大きいほど次以降のオブジェクトのサイズが縮小しにくくなります。
## Shading は遠くにある画像にかぶせる色で、通常黒 ("#000") を与えます。


## start ラベルから adventure_dungeon へジャンプすると探索を開始します。


##############################################################################
## Definitions
##############################################################################

##############################################################################
## Main label
## Jumping to this label starts dungeon adventure

label adventure_dungeon:

    # rename back
    $ player = dungeonplayer

    # Update event list in the current level
    $ player.update_events()
    $ player.action = "stay"
    $ player.update_dungeonmap()
    $ player.automove=False

    # Play music
    if player.music:
        if renpy.music.get_playing() != player.music:
            play music player.music fadeout 1.0

    # Show background
    if player.image:
        scene black with Dissolve(.25)
        scene expression player.image at topleft
        with Dissolve(.25)

    jump adventure_dungeon_loop


label adventure_dungeon_loop:
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
                jump adventure_dungeon
            $ _loop += 1

        $ block()

        # show eventmap or dungeon navigator
        if player.in_dungeon():
            call screen dungeon_navigator(player)
        else:
            call screen eventmap_navigator(player)

        if isinstance(_return, basestring):
            $ player.action = _return

        elif isinstance(_return, tuple):

            if player.get_tile(pos = _return, numeric=True) in player.collision:
                $ player.action = "collide"
                $ player.next_pos = _return
                $ player.automove = False

            elif player.compare(_return):
                $ player.action = "rotate"
                $ player.move_pos(_return)

            else:
                $ player.action = "move"
                $ player.move_pos(_return)

            # Show background
            if player.image:
                $ player.update_dungeonmap()
                scene expression player.image at topleft

        else:
            $ player.action = "move"
            $ player.move_pos(_return)


##############################################################################
## Dungeon navigator screen
## screen that shows orientation buttons in dungeon

screen dungeon_navigator(player):

    on "show" action Show("blocking_screen", player=player)

    # When outside of navigation is clicked
    button:
        xysize (config.screen_width, config.screen_height)
        action Return("click")


    # move buttons
    fixed fit_first True style_prefix "move" align 0.02, 0.97:
        grid 3 4:
            null
            textbutton "2" action [SetField(player, "automove", True), Return(player.front_pos)]
            null
            textbutton "Q" action Return(player.turnleft_pos)
            textbutton "W" action Return(player.front_pos)
            textbutton "E" action Return(player.turnright_pos)
            textbutton "A" action Return(player.left_pos)
            textbutton "S" action Return(player.back_pos)
            textbutton "D" action Return(player.right_pos)
            null
            textbutton "X" action Return(player.turnback_pos)
            null

    # move keys
        for i in ["repeat_2","2", "toggle_skip"]:
            key i action [SetField(player, "automove", True), Return(player.front_pos)]
        for i in ["repeat_w", "w","focus_up"]:
            key i action Return(player.front_pos)
        for i in ["repeat_s", "s","focus_down"]:
            key i action Return(player.back_pos)
        for i in ["repeat_d","d", "rollforward"]:
            key i action Return(player.right_pos)
        for i in ["repeat_a","a", "rollback"]:
            key i action Return(player.left_pos)
        for i in ["repeat_q", "q", "focus_left"]:
            key i action Return(player.turnleft_pos)
        for i in ["repeat_e", "e", "focus_right"]:
            key i action Return(player.turnright_pos)
        for i in ["repeat_x", "x",]:
            key i action Return(player.turnback_pos)

        # override rollforward/rollback
        key 'mousedown_4' action [SetField(player, "automove", True), Return(player.front_pos)]
        key 'mousedown_5' action Return(player.back_pos)


    # add minimap
    add player.minimap(area=(270,270)) align 0.98, 0.97


style move_button_text:
    size 60

style move_button:
    xysize (60, 60)

init python:
    config.keymap['self_voicing'].remove('v')
    # config.keymap['toggle_fullscreen'].remove('f')
    config.keymap['screenshot'].remove('s')
    # config.keymap['hide_windows'].remove('h')
    config.keymap['accessibility'].remove('K_a')
    config.keymap['director'].remove('d')


##############################################################################
## Blocking screen

screen blocking_screen(player):
    zorder 1000

    if player.automove:
        timer 0.02 action [Hide("blocking_screen"), Return(player.front_pos)]
    else:
        timer 0.025 action Hide("blocking_screen")

    for i in ["repeat_w", "w","repeat_W","W", "focus_up"]:
        key i action NullAction()
    for i in ["repeat_s", "s","repeat_S","S", "focus_down"]:
        key i action [SetField(player, "automove", False)]
    for i in ["repeat_d","d", "repeat_D","D", "rollforward"]:
        key i action [SetField(player, "automove", False)]
    for i in ["repeat_a","a", "repeat_A","A", "rollback"]:
        key i action [SetField(player, "automove", False)]
    for i in ["repeat_q", "q","repeat_Q","Q", "focus_left"]:
        key i action [SetField(player, "automove", False)]
    for i in ["repeat_e", "e","repeat_E","E", "focus_right"]:
        key i action [SetField(player, "automove", False)]
    for i in ["dismiss", "game_menu", "hide_windows", "skip", "toggle_skip","stop_skipping"]:
        key i action [SetField(player, "automove", False)]
    key 'mousedown_4' action NullAction()


##############################################################################
## Fullmap screen

screen fullmap(player=player):

    tag menu

    use game_menu("Map"):

        if player and player.in_dungeon():
            $ player.tilemap.area = None
            add player.tilemap


##############################################################################
## Dungeon class.

init -5 python:

    class Dungeon(TiledLevel):

        """
        Expanded Level class that holds collision.
        """

        def __init__(self, image=None, music=None, tilemap = None, collision=None):

            super(Dungeon, self).__init__(image, music, tilemap)
            self.collision = collision


##############################################################################
## DungeonPlayer class

    class DungeonPlayer(TilemapPlayer):

        """
        Expanded Player Class that stores various methods and data for dungeon crawling.
        """


        def __init__(self, level=None, pos=None, icon=None, mask_tilemap=False, **kwargs):

            super(DungeonPlayer, self).__init__(level, pos, icon, mask_tilemap, **kwargs)

            self.next_pos = self.pos
            self.automove = False

        @property
        def collision(self):
            return self.get_level(self.level).collision

        @property
        def turnback_pos(self):
            return Coordinate(*self.pos).turnback().unpack()

        @property
        def turnleft_pos(self):
            return Coordinate(*self.pos).turnleft().unpack()

        @property
        def turnright_pos(self):
            return Coordinate(*self.pos).turnright().unpack()

        @property
        def front_pos(self):
            return Coordinate(*self.pos).front().unpack()

        @property
        def front2_pos(self):
            return Coordinate(*self.pos).front2().unpack()

        @property
        def back_pos(self):
            return Coordinate(*self.pos).back().unpack()

        @property
        def back2_pos(self):
            return Coordinate(*self.pos).back2().unpack()

        @property
        def left_pos(self):
            return Coordinate(*self.pos).left().unpack()

        @property
        def right_pos(self):
            return Coordinate(*self.pos).right().unpack()

        def compare(self, target):
            # compares self coordinate to target.

            if isinstance(self.pos, tuple):
                return Coordinate(*self.pos).compare(target)
            return False


        def in_dungeon(self):
            # returns true if player is in dungeon

            return isinstance(self.get_level(self.level), Dungeon)


        def get_events(self, pos = None, action= None):
            # returns event list that happens in the given pos.

            pos = pos or self.pos

            actions = ["stay"]
            if action == "click":
                actions += ["click", "clickto"]
            if action == "move":
                actions += ["move", "movefrom", "nextto", "faceto"]
            if action == "rotate":
                actions += ["faceto"]
            if action == "collide":
                actions += ["moveto"]

            if self.in_dungeon() and action:
                loop = [player.pos, player.front_pos, player.back_pos, player.left_pos, player.right_pos]
            else:
                loop = [pos]

            events = []
            for i in self.current_events:
                for pos in loop:
                    if i.once and self.happened(i):
                        continue
                    if action and i.trigger not in actions:
                        continue
                    if action == None or i.pos == None or i.pos == pos:
                        if eval(i.cond):
                            events.append(i)
                    elif self.in_dungeon() and (i.pos == self.get_tile(pos=pos) or Coordinate(*pos).compare(i.pos)):
                        if i.trigger in ("clickto", "faceto") and not Coordinate(*player.front_pos).compare(pos):
                            continue
                        elif i.trigger == "movefrom" and not Coordinate(*player.previous_pos).compare(pos):
                            continue
                        elif i.trigger == "nextto" and Coordinate(*player.pos).compare(pos):
                            continue
                        elif i.trigger == "moveto" and not Coordinate(*player.next_pos).compare(pos):
                            continue
                        elif i.trigger in ("stay", "click", "move") and not Coordinate(*player.pos).compare(pos):
                            continue
                        elif eval(i.cond):
                            events.append(i)

            if action:
                return self.cut_events(events)
            else:
                return events


        def add_dungeon_objects(self):

            if not self.in_dungeon():
                return

            objects = []
            for i in self.get_events():
                if i.image and i.pos:
                    objects.append((i.pos, i.image))

            self.image.objects = objects


        def add_dungeon_replaced_tiles(self):

            if not self.in_dungeon():
                return

            if self.level in self.replaced_tiles.keys():
                self.image.replaced_tiles = self.replaced_tiles[self.level]


        def update_dungeonmap(self):

            self.image.pov=self.pos
            self.add_dungeon_objects()
            self.add_dungeon_replaced_tiles()
            self.update_tilemap()

        def minimap(self, area):

            w = self.tilemap.tile_width
            h = self.tilemap.tile_height

            xpos = (area[0]-w)/2
            ypos = (area[1]-h)/2

            self.tilemap.area=(self.pos[0]*w - xpos, player.pos[1]*h - ypos, area[0], area[1])


            return self.tilemap

##############################################################################
## Coordinate class

init -10 python:

    class Coordinate(object):

        """
        A class that calculates coordinates.
        """

        def __init__(self, x=0, y=0, dx=0, dy=0):

            self.x=x
            self.y=y
            self.dx=dx
            self.dy=dy

        def turnback(self):
            return Coordinate(self.x, self.y, -self.dx, -self.dy)

        def turnleft(self):
            return Coordinate(self.x, self.y, self.dy, -self.dx)

        def turnright(self):
            return Coordinate(self.x, self.y, -self.dy, self.dx)

        def front(self):
            return Coordinate(self.x+self.dx, self.y+self.dy, self.dx, self.dy)

        def front2(self):
            return self.front().front()

        def back(self):
            return Coordinate(self.x-self.dx, self.y-self.dy, self.dx, self.dy)

        def back2(self):
            return self.back().back()

        def left(self):
            return Coordinate(self.x+self.dy, self.y-self.dx, self.dx, self.dy)

        def right(self):
            return Coordinate(self.x-self.dy, self.y+self.dx, self.dx, self.dy)

        def moveright(self):
            return Coordinate(self.x+1, self.y, 1, 0)

        def moveleft(self):
            return Coordinate(self.x-1, self.y, -1, 0)

        def movebottom(self):
            return Coordinate(self.x, self.y+1, 0, 1)

        def movetop(self):
            return Coordinate(self.x, self.y-1, 0, -1)

        def moveto(self, x, y):
            return Coordinate(self.x+x, self.y+y, self.dx, self.dy)

        def unpack(self):
            return (self.x, self.y, self.dx, self.dy)

        def compare(self, target):
            # Returns True if current coord and target coord shares x and y.

            if isinstance(target, tuple):
                if self.x==target[0] and self.y==target[1]:
                    return True

            if isinstance(target, Coordinate):
                if self.x==target.x and self.y==target.y:
                    return True

            return False


##############################################################################
## LayeredMap class

    class LayeredMap(renpy.Displayable):

        """
        This creates a displayable by layering other displayables. It has the following field values.

        map -  A 2-dimensional list of strings that represent index of a tileset.
        tileset -  A list of displayables that is used as a tile of tilemap.
        tile_mapping - a dictionary that maps string of map to index of tileset.
            If None, each coordinate of map should be integer.
        layers - 2-dimensional list of strings to be shown in the perspective view. The first list is farthest layers,
            from left to right. the last list is the nearest layers. this string is used as suffix of displayable.
        pov - string that represents dungeonplayer class. it determines point of view
        mirror - if "left" or "right", it uses flipped images from the other side.
        horizon_height - height of horizon relative to screen.
        tile_length - length of the nearest tile relative to screen.
        first_distance - distance to the first object. this determines focal length.
        shading - if color is given, it will blend the color over sprites.
        substitution - displayable that is used when proper image is not found.
        """


        def __init__(self, map, tileset, layers = None, mirror=None,
            horizon_height = 0.5, tile_length = 1.0, first_distance = 1.0, shading = None, object_offset = (0,0), substitution = Null(), filetype = "png",
            **properties):

            super(LayeredMap, self).__init__(**properties)
            self.map = map
            self.tileset = tileset
            self.layers = layers
            self.mirror = mirror
            self.horizon_height = horizon_height
            self.tile_length = tile_length
            self.first_distance = first_distance
            self.shading = shading
            self.substitution = substitution
            self.pov = (0,0,0,0)
            self.objects = []
            self.object_offset = object_offset
            self.replaced_tiles = {}
            self.filetype = filetype


        def render(self, width, height, st, at):

            import re
            pattern = "[0-9]+"

            render = renpy.Render(width, height)

            # render background
            render.blit(renpy.render(Image(self.tileset[0]+"."+self.filetype), width, height, st, at), (0,0))


            # depth loop
            depth = len(self.layers)

            for d in range(depth):
                coord = Coordinate(*self.pov)
                for i in xrange(depth-1-d):
                    coord = coord.front()

                # breadth loop
                breadth = len(self.layers[d])
                center = breadth//2
                wrange = range(breadth-center)
                for k in xrange(center):
                    wrange.insert(0, k+center+1)

                for b in wrange:
                    coord2 = coord
                    if b > center:
                        for j in xrange(b-center):
                            coord2 = coord2.right()
                    else:
                        for j in xrange(center-b):
                            coord2 = coord2.left()

                    # Get index of tileset
                    x,y = coord2.x, coord2.y

                    try:
                        tile = self.map[y][x]
                    except IndexError:
                        tile = 0

                    # if tile is replaced
                    if self.replaced_tiles:
                        if (x, y) in self.replaced_tiles.keys():
                            tile = self.replaced_tiles[(x,y)]

                    # change value to integer
                    if not tile:
                        tile = 0
                    elif isinstance(tile, basestring):
                        tile = int(re.findall(pattern, tile)[0])

                    # blit image if tile is not None
                    if tile:
                        if self.mirror == "left" and b<center:
                            surfix = self.layers[d][breadth-b-1]
                            flip=True
                        elif self.mirror == "right" and b>center:
                            surfix = self.layers[d][breadth-b-1]
                            flip=True
                        else:
                            surfix=self.layers[d][b]
                            flip=False
                        im_name = self.tileset[tile]+"_"+surfix+"."+self.filetype
                        image = Image(im_name) if renpy.loadable(im_name) else self.substitution
                        if flip:
                            image = Transform(image, xzoom=-1)
                        render.blit(renpy.render(image, width, height, st, at), (0,0))

                    # blit image over tile
                    if self.objects:
                        for pos, im in self.objects:
                            try:
                                if pos == self.map[y][x] or isinstance(pos, tuple) and (pos[0], pos[1]) == (x,y):
                                    zoom = (self.first_distance)/(depth-d+self.first_distance - 1.0)
                                    if b<center:
                                        xpos = 0.5 - self.tile_length*zoom*(center-b)
                                    else:
                                        xpos = 0.5 + self.tile_length*zoom*(b-center)
                                    im = renpy.displayable(im)
                                    im = Fixed(
                                        Transform(im, zoom=zoom, anchor=(0.5, 0.5), xpos=xpos, ypos=self.horizon_height),
                                        )
                                    if self.shading:
                                        im = shade_image(im, alpha=float(depth-1-d)/float(depth-1), color=self.shading)
                                    render.blit(renpy.render(im, width, height, st, at), self.object_offset)
                            except IndexError:
                                pass

            # Redraw regularly
            # renpy.redraw(self, 1.0/30)

            return render


        def per_interact(self):

            # Redraw per interact.
            renpy.redraw(self, 0)

        ## TODO
        #def visit(self):

           # If the displayable has child displayables, this method should be overridden to return a list of those displayables.
           #return


# transform that shades displayable
    def shade_image(d, alpha = 0.5, color="#000"):
        return AlphaBlend(Transform(d, alpha = alpha), d, Solid(color, xysize=(config.screen_width, config.screen_height)), True)
