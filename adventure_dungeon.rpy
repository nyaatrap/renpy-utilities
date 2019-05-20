## This file adds pseudo-3D dungeon crawling function into adventure framework.
## To play the sample game, download the dungeon folder then place it in the game directory.
## adventure に疑似３Dダンジョン探索機能を追加するファイルです。
## サンプルを実行するには dungeon フォルダーの画像をダウンロードする必要があります。

##############################################################################
## How to Use
##############################################################################

## まず最初に画像の種類を文字列のリストで定義します。
## 文字列は表示する画像ファイルの接頭辞になります
## リストの一番最初はどのレイヤーでも共通で表示する背景画像になります。

define dungeonset = ["dungeon/base", "dungeon/floor", "dungeon/wall", "dungeon/door"]

## 次にダンジョンに表示する壁などの画像の数や重なりを2次元配列で定義します。
## この例では、一番遠くに7つ、一番近くに3つの画像を表示できるようにしています。
## c0をプレイヤーがいる位置と思って、上が画面の奥になるようイメージしてください。
## 文字列は表示する画像ファイルの接尾辞になります

define dungeon_layers = [
   ["llll7", "lll6", "ll6", "l6", "c6", "r6", "rr6", "rrr6", "rrrr6"],
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
## 0 や空集合の場合は描画しません

define map2 =[
[2,2,2,2,2,2,2,2],
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

## ダンジョンの画像を LayeredMap(map, tileset, tile_mapping, layers, pov) で定義します。
## map, tileset, layers は上で定義したもので、pov は最後に定義するダンジョンプレイヤークラスを文字列で与えます。
## mirror を"left" か "right" にすると、指定した側の画像を反対側の画像を反転して表示します。

define map_image = LayeredMap(map2, dungeonset, layers=dungeon_layers, pov="dungeonplayer", mirror = "left")


## それらを使ってレベルを Dungeon(image, music, map, collision) で定義します。
## ここでもう一度 map を与えているのは衝突判定に利用するためです。
default level.dungeon = Dungeon(image=map_image, map=map2, collision=collision)


## 最後に冒険者を DungeonPlayer クラスで定義します。
## ダンジョンの pos は (x,y,dx,dy) の組で、dx が 1 ならみぎ、-1 ならひだりを向きます。
## adventure.rpy との定義の重複を避けるため別名にしていますが、
## ゲームスタート後は player に戻して使います。

default dungeonplayer = DungeonPlayer("dungeon", pos=(1,1,0,1), turn=0)


## ダンジョンのイベントを定義します。

## イベントにはパッシブ、アクティブ、コリジョンの三種類があります。
## デフォルトはパッシブで、その座標に移動した時に呼ばれます。
## アクティブはその座標にいる上で、さらにクリックすると呼ばれます。
## コリジョンは侵入不可能の座標に移動しようとした時に呼ばれます。

## 通所のパッシブイベントは、プレイヤーが pos の位置に移動した時に呼び出されます。
## dx,dy を与えるとその向きのみイベントが発生します。
define ev.entrance = Event("dungeon", pos=(1,1), precede=True, once=True)
label entrance:
    "Enter point"
    return


## pos が与えられていないイベントは、そのレベル内ならどこでも発生します。
## active を True にすると、その座標でクリックした時のみ呼び出されるアクティブイベントになります。
define ev.nothing = Event("dungeon", priority=100, active=True)
label nothing:
    "There is nothing"
    return


## pos を整数もしくは文字列にすると、その文字列がマップを定義した二元配列の値と一致する座標の場合に、イベントが発生します。
## 移動しようとした場所が衝突する座標の場合、その座標のコリジョンイベントが呼ばれます。

define ev.collision_wall = Event("dungeon", pos=2)
label collision_wall:
    with vpunch
    return


define ev.collision_pit = Event("dungeon", pos=0)
label collision_pit:
    "There is a pit"
    return


## player.next_pos には次に移動しようとする座標が格納されています。
## player.front_pos, back_pos, left_pos, right_pos で対応する座標を得られます。
## player.front2_pos, back2_pos は２歩前、２歩後ろの座標です。

define ev.collision_door = Event("dungeon", pos=3)
label collision_door:
    if player.front_pos == player.next_pos:
        return player.front2_pos
    else:
        with vpunch
        return

## image event

define ev.sprite = Event("dungeon", pos=(2,6), active=True, image = Image("dungeon/sprite.png"))
label sprite:
    "Hello"
    return


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

    jump adventure_dungeon_loop


label adventure_dungeon_loop:
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
                jump adventure_dungeon
            $ _loop += 1

        $ player.after_interact = True

        # sub loop to execute active/collision events without moving.
        while True:

            # show eventmap or dungeon navigator
            $ block()
            if player.in_dungeon():
                call screen dungeon_navigator(player)
            else:
                call screen eventmap_navigator(player)

            #  If return value is a place, move to there
            if isinstance(_return, Place):
                $ player.pos = _return.pos
                jump adventure_dungeon

            # If return value is an active event, execute it.
            elif isinstance(_return, Event):
                if not player.in_dungeon():
                    $ player.pos = _return.pos
                $ player.event = _return
                $ block()
                $ player.happened_events.add(player.event.name)
                call expression player.event.label or player.event.name
                $ player.done_events.add(player.event.name)
                if player.move_pos(_return):
                    jump adventure_dungeon
                jump adventure_dungeon_loop

            # if return value is coordinate and it's coordinate is in collision,
            # then execute collision events.
            elif isinstance(_return, Coordinate) and player.map[_return.y][_return.x] in player.collision:

                # check collision events
                $ block()
                $ player.next_pos = _return.unpack()
                $ _events = player.get_passive_events(pos = player.next_pos)

                # sub loop to execute all collision events
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

                jump adventure_dungeon_loop

            # else if return value is coordinate, move to the new coordinate
            elif isinstance(_return, Coordinate):

                $ player.next_pos = _return.unpack()

                # if movement is only rotation, don't trigger passive events
                if player.next_pos[0] == player.pos[0] and player.next_pos[1] == player.pos[1]:
                    $ player.move_pos(player.next_pos)
                    show expression player.image at topleft

                # otherwise, loop up to check passive events
                else:
                    $ player.move_pos(player.next_pos)
                    show expression player.image at topleft
                    jump adventure_dungeon_loop


##############################################################################
## Dungeon navigator screen
## screen that shows orientation buttons in dungeon

screen dungeon_navigator(player):

    $ coord = Coordinate(*player.pos)

    ## show active events
    for i in player.get_active_events():
        button:
            xysize (config.screen_width, config.screen_height)

            if i.active:
                action Return(i)


    # move buttons
    fixed style_prefix "move":
        textbutton "W" action Return(coord.front())  xcenter .5 ycenter .86
        textbutton "S" action Return(coord.back())  xcenter .5 ycenter .96
        textbutton "E" action Return(coord.turnright())  xcenter .58 ycenter .91
        textbutton "Q" action Return(coord.turnleft())   xcenter .42 ycenter .91
        textbutton "D" action Return(coord.right()) xcenter .65 ycenter .96
        textbutton "A" action Return(coord.left())  xcenter .35 ycenter .96


    # move keys
        for i in ["repeat_w", "w","repeat_W","W", "focus_up"]:
            key i action Return(coord.front())
        for i in ["repeat_s", "s","repeat_S","S", "focus_down"]:
            key i action Return(coord.back())
        for i in ["repeat_d","d", "repeat_D","D", "rollforward"]:
            key i action Return(coord.right())
        for i in ["repeat_a","a", "repeat_A","A", "rollback"]:
            key i action Return(coord.left())
        for i in ["repeat_q", "q","repeat_Q","Q", "focus_left"]:
            key i action Return(coord.turnleft())
        for i in ["repeat_e", "e","repeat_E","E", "focus_right"]:
            key i action Return(coord.turnright())

style move_button_text:
    size 50


##############################################################################
## Dungeon class.

init -2 python:

    class Dungeon(Level):

        """
        Expanded Level class that holds collision data.
        """

        def __init__(self, image=None, music=None, map = None, collision=None):

            super(Dungeon, self).__init__(image, music)
            self.map = map
            self.collision = collision


##############################################################################
## DungeonPlayer class

    class DungeonPlayer(Player):

        """
        Expanded Player Class that stores various methods and data for dungeon crawling.
        """


        def __init__(self, level=None, pos=None, **kwargs):

            super(DungeonPlayer, self).__init__(level, pos, **kwargs)

            self.next_pos = None


        @property
        def map(self):
            return self.get_level(self.level).map


        @property
        def collision(self):
            return self.get_level(self.level).collision


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


        def get_active_events(self, pos=None):
            # returns event and place list that is shown in the navigation screen.

            pos = pos or self.pos

            events = []
            for i in self.current_events+self.current_places:
                if not i.once or not self.happened(i):
                    if i.pos == None or i.pos == pos or i.pos == self.image.map[pos[1]][pos[0]] or self.compare(i.pos):
                        if eval(i.cond):
                            events.append(i)

            events.sort(key = lambda ev: -ev.priority)

            return events


        def get_passive_events(self, pos=None):
            # returns event list that happens in the given pos.
            # this overwrites the same method in player class.
            # if pos is give, it gets events on the given pos

            pos = pos or self.pos

            events = []
            for i in self.current_events:
                if not i.once or not self.happened(i):
                    if i.precede or self.after_interact:
                        if i.pos == None or i.pos == pos or i.pos == self.image.map[pos[1]][pos[0]] or self.compare(i.pos):
                            if not i.active and eval(i.cond):
                                events.append(i)

            return self.cut_events(events)


##############################################################################
## Coordinate class

init -3 python:

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
        layers - 2-dimensional list of strings to be shown in the perspective view.
            the first list is farthest layers, from left to right. the last list is the nearest layers. this string is used as suffix of displayable.
        pov - string that represents dungeonplayer class. it determines point of view
        """


        def __init__(self, map, tileset, tile_mapping = None, layers = None, pov = None, mirror=None, **properties):

            super(LayeredMap, self).__init__(**properties)
            self.map = map
            self.tileset = tileset
            self.tile_mapping = tile_mapping
            self.pov = pov
            self.layers = layers
            self.mirror = mirror
            self.tile_width = 0.9
            self.horizontal_line = 0.35


        def render(self, width, height, st, at):

            render = renpy.Render(width, height)

            # render background
            render.blit(renpy.render(Image(self.tileset[0]+".png"), width, height, st, at), (0,0))

            # get coordinate
            pov = getattr(store, self.pov)

            # depth loop
            depth = len(self.layers)

            for d in range(depth):
                coord = Coordinate(*pov.pos)
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
                        if self.tile_mapping:
                            if self.map[y][x] in self.tile_mapping.keys():
                                tile = self.tile_mapping[self.map[y][x]]
                            else:
                                tile = 0
                        else:
                            tile = self.map[y][x]

                    except IndexError:
                        tile = 0

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
                        image = Image(self.tileset[tile]+"_"+surfix+".png")
                        if flip:
                            image = Transform(image, xzoom=-1)
                        render.blit(renpy.render(image, width, height, st, at), (0,0))

                    # blit image over tile
                    for sprite in pov.current_events:
                        if sprite.image and sprite.pos and sprite.pos[0] == x and sprite.pos[1] == y:
                            zoom = 1.0/(depth-d)
                            if b<center:
                                xpos = 0.5 - self.tile_width*zoom*(center-b)
                            else:
                                xpos = 0.5 + self.tile_width*zoom*(b-center)
                            image = Fixed(
                                Transform(sprite.image, zoom=zoom, xanchor=0.5, xpos=xpos, yalign=self.horizontal_line),
                                )
                            render.blit(renpy.render(image, width, height, st, at), (0, 0))

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

