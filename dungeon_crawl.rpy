## This file adds pseudo-3D dungeon crawling function into adventure framework.
## To play the sample game, download the cave folder then place it in the images directory.
## adventure に疑似３Dダンジョン探索機能を追加するファイルです。
## サンプルを実行するには images/cave フォルダーの画像をダウンロードする必要があります。

##############################################################################
## How to Use
##############################################################################


## まず背景画像を定義します。
## ファイル名の最初はダンジョンの種類名、つぎは壁や扉などのタイル名、最後は座標です。
## 座標は下の図で player を上を向いたプレイヤーの位置とした相対座標です。

## left2, front2, right2
## left1, front1, right1
## left0, player, right0

# image cave floor = "images/cave floor.png"
# image cave wall left0 = "images/cave wall left0.png"
# image cave wall front1 ="images/cave wall front1.png"
# image cave wall left1 = "images/cave wall left1.png"
# image cave wall front2 = "images/cave wall front2.png"
# image cave wall left2 = "images/cave wall left2.png"


## 次に２次元配列 [[]] でマップを定義します。
## "0" または空白は画像なし、"1" は "wall"、"2" は"door" で定義した画像が
## 割り当てられます。この割り当てや衝突判定は Crawler クラスで変更できます。

define sample_map =[
["1","1","1","1","1","1","1","1"],
["1","0","1","0","0","0","0","1"],
["1","0","1","0","1","1","0","1"],
["1","0","0","0","0","1","0","1"],
["1","0","1","1","0","0","0","1"],
["1","0","0","0","0","1","0","1"],
["1","e","0","1","1","1","0","1"],
["1","1","1","1","1","1","1","1"]
]

## それらを使ってレベルを Dungeon(image, music, map) で定義します。
## image は先に定義したダンジョンの種類です。
## map は ２次元配列の map [[]] か、タブ区切りのスプレッドシートファイル名です。

default level.cave = Dungeon(image="cave", map=sample_map)


## 最後に冒険者を Crawler クラスで定義します。
## ダンジョンの pos は (x,y,dx,dy) の組で、dx が 1 ならみぎ、-1 ならひだりを向きます。

default crawler = Crawler("cave", pos=(1,1,0,1))


## ダンジョンのイベントを定義します。

## イベントは、プレイヤーがpos の位置に移動した時に呼び出されます。
define ev.entrance = Event("cave", pos=(1,1), precede=True, once=True)
label entrance:
    "Here starts crawling"
    return

## dx,dy を与えるとその向きのみイベントが発生します。
define ev.chest = Event("cave", pos=(6,6,0,1), active=True)
label chest:
    "You found a chest"
    return

## pos を文字列にするとその文字列のある map の座標でイベントが発生します。
define ev.enemy = Event("cave", pos="e", precede=True)
label enemy:
    "There is an enemy"
    return

## pos が与えられていないイベントは、そのレベル内なら毎ターン発生します。
## active を True にすると、クリックした時のみ呼び出されるアクティブイベントになります。
define ev.nothing = Event("cave", priority=-10, active=True)
label nothing:
    "There is nothing"
    return


## 衝突の場合は衝突先のイベントがアクティブイベントとして呼ばれます。
define ev.collision = Event("cave", pos="1", active=True)
label collision:
    with vpunch
    return

## start ラベルから crawl へジャンプすると探索を開始します。


##############################################################################
## Definitions
##############################################################################

##############################################################################
## Main label
## Jumping to this label starts dungeon crawling

label crawl:
    # Update event list in current level
    $ crawler.update_events()
    $ crawler.after_interact = False

    # Play music
    if crawler.music:
        if renpy.music.get_playing() != crawler.music:
            play music crawler.music fadeout 1.0

    # Show background
    if crawler.image:
        scene black with Dissolve(.25)
        if crawler.in_dungeon():
            $ crawler.draw_dungeon()
        else:
            show expression crawler.image at topleft
        with Dissolve(.25)

    jump crawl_loop


label crawl_loop:
    while True:

        # check passive events
        $ block()
        $ _events = crawler.get_events()

        # sub loop to excecute all passive events
        $ _loop = 0
        while _loop < len(_events):

            $ crawler.event = _events[_loop]
            $ block()
            $ crawler.happened_events.add(crawler.event.name)
            call expression crawler.event.label or crawler.event.name
            $ crawler.done_events.add(crawler.event.name)
            if crawler.move_pos(_return):
                jump crawl
            $ _loop += 1

        $ crawler.after_interact = True

        # sub loop to ignore passive events
        while True:

            # show eventmap or dungeon navigator
            $ block()
            if crawler.in_dungeon():
                call screen dungeon_navigator(crawler)
            else:
                call screen eventmap_navigator(crawler)

            #  If return value is a place
            if isinstance(_return, Place):
                $ crawler.pos = _return.pos
                jump crawl_loop

            # If return value is an event
            elif isinstance(_return, Event):
                if not crawler.in_dungeon():
                    $ crawler.pos = _return.pos
                $ crawler.event = _return
                $ block()
                $ crawler.happened_events.add(crawler.event.name)
                call expression crawler.event.label or crawler.event.name
                $ crawler.done_events.add(crawler.event.name)
                if crawler.move_pos(_return):
                    jump crawl
                jump crawl_loop

            # collision
            elif isinstance(_return, Coordinate) and crawler.map[_return.y][_return.x] in crawler.collision:

                # check active events
                $ block()
                $ _events = crawler.get_events(pos = _return.unpack(), active=True)

                # sub loop to excecute all active events
                $ _loop = 0
                while _loop < len(_events):

                    $ crawler.event = _events[_loop]
                    $ block()
                    $ crawler.happened_events.add(crawler.event.name)
                    call expression crawler.event.label or crawler.event.name
                    $ crawler.done_events.add(crawler.event.name)
                    if crawler.move_pos(_return):
                        jump crawl
                    $ _loop += 1

                jump crawl_loop

            # move
            elif isinstance(_return, Coordinate):
                if _return.x == crawler.pos[0] and _return.y == crawler.pos[1]:
                    $ crawler.move_pos(_return.unpack())
                    $ crawler.draw_dungeon()
                else:
                    $ crawler.move_pos(_return.unpack())
                    $ crawler.draw_dungeon()
                    jump crawl_loop


##############################################################################
## Dungeon navigator screen
## screen that shows orientation buttons in dungeon

screen dungeon_navigator(crawler):

    $ coord = Coordinate(*crawler.pos)

    ## show events
    for i in crawler.get_events(active=True):
        button xysize (config.screen_width, config.screen_height):
            if i.active:
                action Return(i)
            if  i.image:
                add i.image


    #move buttons
    fixed style_prefix "move":
        textbutton "W" action Return(coord.front())  xcenter .5 ycenter .86
        textbutton "S" action Return(coord.back())  xcenter .5 ycenter .96
        textbutton "E" action Return(coord.turnright())  xcenter .58 ycenter .91
        textbutton "Q" action Return(coord.turnleft())   xcenter .42 ycenter .91
        textbutton "D" action Return(coord.right()) xcenter .65 ycenter .96
        textbutton "A" action Return(coord.left())  xcenter .35 ycenter .96

    #keys
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
        Expanded Level class to hold 2-dimentional map.
        map should be list or filename of spreadsheet.
        """

        # Make a dict that maps characters in dungeon map to image names
        _mapping = {"1":"wall", "2":"door", "3":"up", "4":"down"}

        # tuple of collision on dungeon map.
        _collision = ("1", "2", "3", "4")

        def __init__(self, image=None, music=None, map = None, mapping=None, collision=None, info=""):

            super(Dungeon, self).__init__(image, music, info)
            self.map = self.read_map(map) if map and isinstance(map, basestring) else map
            self.mapping = mapping or self._mapping
            self.collision = collision or self._collision


        def read_map(self, file, separator="\t"):
            # read tsv file to make them into 2-dimentional map

            map=[]
            f = renpy.file(file)
            for l in f:
                l = l.decode("utf-8")
                a = l.rstrip().split(separator)
                map.append([x for x in a])
            f.close()

            return map


##############################################################################
## Coordinate class

init -2 python:

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


##############################################################################
## Crawler class

    class Crawler(Player):

        """
        Expanded Player Class that stores various methods and data for crawling.
        """
            
        @property
        def map(self):
            return self.get_level(self.level).map
            
        @property
        def mapping(self):
            return self.get_level(self.level).mapping
            
        @property
        def collision(self):
            return self.get_level(self.level).collision


        def in_dungeon(self):
            # returns true if crawler is in dungeon

            return isinstance(self.get_level(self.level), Dungeon)
            

        def get_events(self, active = False, pos=None):
            # returns event list that happens in the given pos.
            # this overwrites the same method in player class.
            
            pos = pos or self.pos

            events = []
            for i in self.current_events:
                if not i.once or not self.happened(i):
                    if i.precede or self.after_interact:
                        if i.pos == None or (isinstance(i.pos, basestring) and i.pos == self.map[pos[1]][pos[0]]) or\
                        i.pos == pos or (len(i.pos)==2 and i.pos[0] == pos[0] and i.pos[1] == pos[1]):
                            if active == i.active and eval(i.cond):
                                events.append(i)

            return self.cut_events(events)


        def draw_dungeon(self):
            # Draw front view image on the coord on the master layer.

            coord = Coordinate(*self.pos)
            tag = self.image
            map = self.map
            mapping = self.mapping

            # Calculate relative coordinates
            floor = coord
            turnleft = coord.turnleft()
            turnright = coord.turnright()
            turnback = coord.turnback()
            stepback = coord.back()
            left0 = coord.left()
            right0 = coord.right()
            front1 =  coord.front()
            left1 = front1.left()
            right1 = front1.right()
            front2 =  front1.front()
            left2 = front2.left()
            right2 = front2.right()

            # Composite background images.
            renpy.scene()

            # floor base
            renpy.show("{} floor".format(tag))

            for n, i in enumerate(["left2", "right2", "front2", "left1", "right1", "front1", "left0", "right0", "floor"]):

                # Try-except clauses are used to prevent IndexError
                try:
                    # get coordinate object defined above
                    tile=locals()[i]

                    if map[tile.y][tile.x] in mapping.keys():

                        # left side
                        if i in ["left2", "left1", "left0"]:
                            image = "{} {} {}".format(tag, mapping[map[tile.y][tile.x]], i)
                            if renpy.has_image(image):
                                renpy.show(i, what = Transform(image, yalign=.5))

                        # righit side use mirror image of left side
                        elif i in ["right2", "right1", "right0"]:
                            image = "{} {} {}".format(tag, mapping[map[tile.y][tile.x]], i.replace("right", "left"))
                            if renpy.has_image(image):
                                renpy.show(i, what = Transform(image, xzoom = -1, xalign = 1.0, yalign=.5))

                        # front
                        elif i in ["front2", "front1"]:
                            image = "{} {} {}".format(tag, mapping[map[tile.y][tile.x]], i)
                            if renpy.has_image(image):
                                renpy.show(i, what = Transform(image, align=(.5,.5)))

                except IndexError:
                    pass

