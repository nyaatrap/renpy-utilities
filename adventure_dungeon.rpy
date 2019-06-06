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

## ダンジョンの画像を LayeredMap(map, tileset, tile_mapping, layers, pov) で定義します。
## map, tileset, layers は上で定義したもので、pov は最後に定義するダンジョンプレイヤークラスを文字列で与えます。
## mirror を "left" か "right" にすると、指定した側の画像を反対側の画像を反転して描画します。
define map_image = LayeredMap(map2, dungeonset, layers=dungeon_layers, pov="dungeonplayer", mirror = "left")


## それらを使ってレベルを Dungeon(image, music, collision) で定義します。
default level.dungeon = Dungeon(image=map_image, collision=collision)


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

## パッシブイベントは、プレイヤーが pos の位置に移動した時に呼び出されます。
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
## 返り値に (x,y) 座標を与えるとその場所に移動します。

define ev.collision_door = Event("dungeon", pos=3)
label collision_door:
    if player.front_pos == player.next_pos:
        scene black with dissolve
        return player.front2_pos
    else:
        with vpunch
        return


## 返り値に文字列と移動先の座標を与えるとそのレベルの場所に移動します。
define ev.exit = Event("dungeon", pos=(1,0), priority = -1)
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
image sp = "dungeon/sprite.png"
define ev.sprite = Event("dungeon", pos=(1, 8), active=True, image = "sp")
label sprite:
    "Hello"
    return

## 画像の表示位置は LayeredMap に以下のプロパティーを与えることで調整します、
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
    $ player.after_interact = False

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
            elif isinstance(_return, tuple) and player.get_tile(pos = _return) in player.collision:

                # check collision events
                $ block()
                $ player.next_pos = _return
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

            # if return value is coordinate, move to the new coordinate
            elif isinstance(_return, tuple):

                $ player.next_pos = _return
                $ player.move_pos(player.next_pos)

                # Show background
                if player.image:
                    scene expression player.image at topleft

                # if movement is not rotation, jump up to the outer loop
                if not player.compare(player.previous_pos):
                    jump adventure_dungeon_loop


##############################################################################
## Dungeon navigator screen
## screen that shows orientation buttons in dungeon

screen dungeon_navigator(player):

    ## show active events
    for i in player.get_active_events():
        button:
            xysize (config.screen_width, config.screen_height)

            if i.active:
                action Return(i)


    # move buttons
    fixed style_prefix "move":
        textbutton "W" action Return(player.front_pos)  xcenter .5 ycenter .85
        textbutton "S" action Return(player.back_pos)  xcenter .5 ycenter .95
        textbutton "E" action Return(player.turnright_pos)  xcenter .58 ycenter .90
        textbutton "Q" action Return(player.turnleft_pos)   xcenter .42 ycenter .90
        textbutton "D" action Return(player.right_pos) xcenter .65 ycenter .95
        textbutton "A" action Return(player.left_pos)  xcenter .35 ycenter .95


    # move keys
        for i in ["repeat_w", "w","repeat_W","W", "focus_up"]:
            key i action Return(player.front_pos)
        for i in ["repeat_s", "s","repeat_S","S", "focus_down"]:
            key i action Return(player.back_pos)
        for i in ["repeat_d","d", "repeat_D","D", "rollforward"]:
            key i action Return(player.right_pos)
        for i in ["repeat_a","a", "repeat_A","A", "rollback"]:
            key i action Return(player.left_pos)
        for i in ["repeat_q", "q","repeat_Q","Q", "focus_left"]:
            key i action Return(player.turnleft_pos)
        for i in ["repeat_e", "e","repeat_E","E", "focus_right"]:
            key i action Return(player.turnright_pos)

        # override rollforward/rollback
        key  'mousedown_4' action Return(player.front_pos)
        key  'mousedown_5' action Return(player.back_pos)


style move_button_text:
    size 50


##############################################################################
## Dungeon class.

init -5 python:

    class Dungeon(Level):

        """
        Expanded Level class that holds collision and map change data.
        """

        def __init__(self, image=None, music=None, collision=None):

            super(Dungeon, self).__init__(image, music)
            self.collision = collision
            self.changed_tiles = {}


##############################################################################
## DungeonPlayer class

    class DungeonPlayer(Player):

        """
        Expanded Player Class that stores various methods and data for dungeon crawling.
        """


        def __init__(self, level=None, pos=None, **kwargs):

            super(DungeonPlayer, self).__init__(level, pos, **kwargs)

            self.next_pos = self.pos


        @property
        def collision(self):
            return self.get_level(self.level).collision

        @property
        def changed_tiles(self):
            return self.get_level(self.level).changed_tiles

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


        def get_tile(self, level=None, pos=None):
            # returns tile from current or given pos

            if player.in_dungeon():
                level = level or self.level
                pos = pos or self.pos
                level = self.get_level(level)

                if (pos[0], pos[1]) in level.changed_tiles:
                    return level.changed_tiles[(pos[0], pos[1])]
                else:
                    return level.image.map[pos[1]][pos[0]]


        def set_tile(self, tile, level=None, pos=None):

            if player.in_dungeon():
                level = level or self.level
                pos = pos or self.pos
                level = self.get_level(level)

                level.changed_tiles[(pos[0], pos[1])] = tile


        def get_active_events(self, pos=None):
            # returns event and place list that is shown in the navigation screen.
            # this overwrites the same method in player class.
            # if pos is give, it gets events on the given pos

            pos = pos or self.pos

            events = []
            for i in self.current_events+self.current_places:
                if not i.once or not self.happened(i):
                    if not self.in_dungeon():
                        if eval(i.cond):
                            events.append(i)
                    elif i.pos == None or i.pos == self.get_tile(pos=pos) or Coordinate(*pos).compare(i.pos):
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
                        if i.pos == None or i.pos == pos:
                            if not i.active and eval(i.cond):
                                events.append(i)
                        elif self.in_dungeon() and (i.pos == self.get_tile(pos=pos) or Coordinate(*pos).compare(i.pos)):
                            if not i.active and eval(i.cond):
                                events.append(i)

            return self.cut_events(events)



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


        def __init__(self, map, tileset, tile_mapping = None, layers = None, pov = None, mirror=None,
            horizon_height = 0.5, tile_length = 1.0, first_distance = 1.0, shading = None, substitution = Null(),
            **properties):

            super(LayeredMap, self).__init__(**properties)
            self.map = map
            self.tileset = tileset
            self.tile_mapping = tile_mapping
            self.pov = pov
            self.layers = layers
            self.mirror = mirror
            self.horizon_height = horizon_height
            self.tile_length = tile_length
            self.first_distance = first_distance
            self.shading = shading
            self.substitution = substitution


        def render(self, width, height, st, at):

            import re
            pattern = "[0-9]+?"

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
                        tile = pov.get_tile(pos = (x,y))
                    except IndexError:
                        tile = 0

                    if self.tile_mapping:
                        if not tile:
                            tile = 0
                        else:
                            tile = re.findall(pattern, tile)[0]
                            for k in self.tile_mapping.keys():
                                if tile in k.replace(" ", "").split(","):
                                    tile = self.tile_mapping[k]
                                    break
                    else:
                        tile = int(tile)

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
                        im_name = self.tileset[tile]+"_"+surfix+".png"
                        image = Image(im_name) if renpy.loadable(im_name) else self.substitution
                        if flip:
                            image = Transform(image, xzoom=-1)
                        render.blit(renpy.render(image, width, height, st, at), (0,0))

                    # blit image over tile
                    for sprite in pov.current_events:
                        if sprite.image and sprite.pos and sprite.pos[0] == x and sprite.pos[1] == y:
                            zoom = (self.first_distance)/(depth-d+self.first_distance - 1.0)
                            if b<center:
                                xpos = 0.5 - self.tile_length*zoom*(center-b)
                            else:
                                xpos = 0.5 + self.tile_length*zoom*(b-center)
                            image = Fixed(
                                Transform(sprite.image, zoom=zoom, xanchor=0.5, xpos=xpos, yalign=self.horizon_height),
                                )
                            if self.shading:
                                image = shade_image(image, alpha=float(depth-1-d)/float(depth-1), color=self.shading)
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


# transform that shades displayable
    def shade_image(d, alpha = 0.5, color="#000"):
        return AlphaBlend(Transform(d, alpha = alpha), d, Solid(color, xysize=(config.screen_width, config.screen_height)), True)
