## This file provides adventure game framework that uses event maps.
## イベントを配置した２Dマップを探索するアドベンチャーゲームのフレームワークを追加するファイルです。
## ラベルをオブジェクトとのペアで管理することで、マップ上にイベントとして配置して呼び出すことができます。

##############################################################################
## How to Use
##############################################################################


## まず最初にイベントを配置するレベル（マップ／ステージ）を Level(image, music) で定義します。
## image はそのレベルにいる時に表示される背景、music は流れる音楽です。
## level の名前空間でも定義できます。

define level.east = Level(image=Solid("#6a6"))
define level.west = Level(image=Solid("#339"))


## 次にイベントが発生する場所を place(level, pos, cond, image) で定義します。
## level はその場所が置かれるレベルで、上で定義した level を文字列で与えます。
## pos はその場所のモニターに対する相対座標になります。 (0.5, 0.5) が画面中央です。
## cond が満たされると image がレベルの背景上に表示され、クリックするとその場所に移動します。
## place の名前空間でも定義できます。

define place.home = Place(level="east", pos=(.8,.5), image=Text("home"))
define place.e_station = Place(level="east", pos=(.6,.7), image=Text("east-station"))
define place.w_station = Place(level="west", pos=(.4,.4), image=Text("west-station"))
define place.shop = Place(level="west", pos=(.2,.5), image=Text("shop"))


## それから現在位置や達成イベントなどを保持する探検者を Player(place)
## または Player(level, pos) で default で定義します
## place はスタート地点の場所です。level, pos を使うこともできます。
## 任意のパラメーターを追加すると、各イベントを呼び出す条件等に使えます。
default player = Player("home", turn=0)


## 各イベントは define と label のペアで定義します。
## define ラベル名 = Event(place, cond, priority, once, multi) または、
## define ラベル名 = Event(level, pos, cond, priority, once, multi) で定義します。
## 探索者が place の場所に移動すると、そのイベントと同じ名前のラベルを呼び出します。
## cond が与えられると、その条件式を満たした場合にのみイベントを実行します。
## priority は発生の優先度で、数字が小さい順に実行されます。デフォルトは０です。
## once を True にすると一度しか実行されません。デフォルトでは何度も実行されます。
## multi を True にすると他のイベントも同時に発生します。
## event、ev の名前空間でも定義できます。

define ev.myhome = Event("home")
label myhome:
    "this is my home"
    ## return で探索画面に戻ります
    return


define ev.e_station = Event("e_station")
label e_station:
    ## return のあとに次に移動するレベルや場所を文字列で指定できます。
    return "w_station"


define ev.w_station = Event("w_station")
label w_station:
    return "e_station"


define ev.shop = Event("shop")
label shop:
    "this is a shop"
    return


## player.happened(ev) でそのイベントが過去に呼び出されたかどうか評価できます。
## player.done(ev) でそのイベントが過去に最後まで実行されたかどうか評価できます。
define place.shop2 = Place(level="west", pos=(.1,.1), cond="player.done(ev.shop)", image=Text("hidden shop"))

## image を与えると、イベントマップのその場所の上に追加で画像が表示されます。
define ev.shop2 = Event("shop2", cond="player.done(ev.shop)", image=Text("(Now on sale)", size=20, yoffset=30))
label shop2:
    "this is a hidden shop."
    return


## レベルのみを与えると、画面のどこをクリックしてもイベントが発生します。
## また label を定義すると、イベント名の代わりにそのラベル名を呼び出します。
define ev.west_nothing = Event("west", priority=99)
define ev.east_nothing = Event("east", priority=99, label="west_nothing")
label west_nothing:
    "There is nothing there"
    return


## trigger を "stay" にすると、移動画面が現れる度にイベントを確認します。
## このラベルは毎ターン操作の直前に呼ばれ、ターンの経過を記録しています。
define ev.turn = Event(priority = 999, trigger = "stay", multi=True)
label turn:
    $ player.turn += 1
    return


## start ラベルから adventure へジャンプすると探索を開始します。


##############################################################################
## Definitions
##############################################################################

##############################################################################
## Main label
## Jumping to this label starts exploration

label adventure:

    # Update event list in the current level
    $ player.update_events()
    $ player.action = "stay"
    $ player.next_pos = None

    # Play music
    if player.music:
        if renpy.music.get_playing() != player.music:
            play music player.music fadeout 1.0

    # Show background
    if player.image:
        scene black with Dissolve(.25)
        show expression player.image at topleft
        with Dissolve(.25)

    jump adventure_loop


label adventure_loop:
    while True:

        # returns event list events
        $ block()
        $ _events = player.get_events(player.next_pos, player.action)

        # sub loop to execute events
        $ _loop = 0
        while _loop < len(_events):

            $ player.event = _events[_loop]
            $ block()
            $ player.happened_events.add(player.event.name)
            if player.event.trigger == "move":
                $ player.pos = player.next_pos
            call expression player.event.label or player.event.name
            $ player.done_events.add(player.event.name)
            if player.move_pos(_return):
                jump adventure
            $ _loop += 1

        $ block()

        # show eventmap navigator
        call screen eventmap_navigator(player)

        $ player.action = "move"
        $ player.next_pos = _return.pos if _return else None


label after_load():

    # Update event list in the current level
    $ player.update_events()

    return


init python:

    def block():
        # blocks rollback then allows saving data in the current interaction

        config.skipping = None
        renpy.checkpoint()
        renpy.block_rollback()
        renpy.retain_after_load()


##############################################################################
## Eventmap navigator screen
## screen that shows events and places over the current level

screen eventmap_navigator(player):

    button:
        xysize (config.screen_width, config.screen_height)
        action Return(False)

    ## show places
    for i in player.get_places():
        button:
            pos i.pos
            action Return(i)

            if i.image:
                add i.image

    ## show event images
    for i in player.get_events():
        button:
            if i.image:
                pos i.pos
                add i.image


##############################################################################
## Level class

init -10 python:

    class Level(object):

        """
        Class that represents level that places events on it. It has following fields:

        image - Image that is shown behind events.
        music - Music that is played while player is in this level.
        """

        def __init__(self, image=None, music=None):

            self.image = image
            self.music = music


##############################################################################
## Place class

    class Place(object):

        """
        Class that places events on a level.
        This class's fields are same to event class
        """

        def __init__(self, level=None, pos=None, cond="True", priority=0, image=None):

            self.level = level
            self.pos = pos
            self.cond = cond
            self.priority = int(priority)
            self.image = image
            self.once = False
            self.multi = False


##############################################################################
## Event class

    class Event(object):

        """
        Class that represents events that is places on level or place. It has the following fields:

        level - String of level where this events placed onto.
        pos - (x, y) coordinate on the screen.
        cond - Condition that evaluates this event happen or not. This should be quoted expression.
            If self.call is None, this determines to show its image.
        priority - An event with higher value happens earlier. default is 0.
        once - Set this true prevents calling this event second time.
        multi - Set this true don't prevent other events in the same interaction.
        image - Image that is shown on an eventmap.
        trigger - Determine when to evaluate this event happen.
            "move", default, is evaluated after moved to this pos,
            "moveto" is evaluated when trying to move this pos, and returns to the previous pos.
            "stay" is evaluated every time before screen is event map screen is shown.
            None never call this linked event. It's used to show only image.
        label - If it's given this label is called instead of object name.
        """

        def __init__(self, level=None, pos=None, cond="True", priority=0, once=False, multi=False,
            trigger="move", image=None, label=None):

            self.place = level if Player.get_place(level) else None
            self._level = None if self.place else level
            self._pos = None if self.place else pos
            self.cond = cond
            self.priority = int(priority)
            self.once = once
            self.multi = multi
            self.trigger = trigger
            self.image = image
            self.label = label

        @property
        def level(self):
            return Player.get_place(self.place).level if self.place else self._level

        @level.setter
        def level(self, value):
            self._level = value

        @property
        def pos(self):
            return Player.get_place(self.place).pos if self.place else self._pos

        @pos.setter
        def pos(self, value):
            self._pos = value


##############################################################################
## Player class

    class Player(object):

        """
        Class that stores various methods and data for exploring. It has the following fields:

        level - Current level.
        pos - Current coordinate that event is happening.
        previous_pos - Previous coordinate. when moving failed, player returns to this pos.
        event - Current event.
        image - Shortcut to level.image.
        music - Shortcut to level.music.

        happening(event) - returns True if an event is happened.
        done(event) - returns True if an event is happened and done.
        """

        def __init__(self, level=None, pos=None, **kwargs):

            place = Player.get_place(level)
            self.level = place.level if place else level
            self.pos = place.pos if place else pos
            self.next_pos = None

            self.action = "stay"
            self.event = None
            self.current_events = []
            self.current_places = []
            self.done_events = set()
            self.happened_events = set()

            for i in kwargs.keys():
                setattr(self, i, kwargs[i])


        @property
        def music(self):
            return self.get_level(self.level).music


        @property
        def image(self):
            return self.get_level(self.level).image


        def happened(self, ev):
            # returns True if this event is happened.

            return ev.name in self.happened_events


        def done(self, ev):
            # returns True if this event is done.

            return ev.name in self.done_events


        def update_events(self, check=True):
            # get current_events and current_places in the current level

            # get current events
            self.current_events = []
            for i in dir(store.event) + dir(store.ev) + dir(store):
                if not i.startswith("_") and i != "i":
                    ev = self.get_event(i)
                    if isinstance(ev, Event) and (ev.level == None or ev.level == self.level):
                        ev.name = i.split(".")[1] if i.count(".") else i
                        self.current_events.append(ev)

                        if check:
                            try:
                                eval(ev.cond)
                            except:
                                raise Exception("Invalid syntax '{}' in '{}'".format(ev.cond, ev.name))

            self.current_events.sort(key = lambda ev: ev.priority)

            # get current places
            self.current_places = []
            for i in dir(store.place) + dir(store.place) + dir(store):
                if not i.startswith("_"):
                    pl = self.get_place(i)
                    if isinstance(pl, Place) and (pl.level == None or pl.level == self.level):
                        self.current_places.append(pl)

            self.current_places.sort(key = lambda pl: pl.priority)


        def get_places(self):
            # returns place list that is shown in the navigation screen.

            events = []
            for i in self.current_places:
                if i.once and self.happened(i):
                    continue
                if eval(i.cond):
                    events.append(i)

            events.sort(key = lambda ev: -ev.priority)

            return events


        def get_events(self, pos = None, action= None):
            # returns event list that happens in the given pos.

            actions = ["stay"] if action=="stay" else ["moveto", "move", "stay",]

            events = []
            for i in self.current_events:
                if i.once and self.happened(i):
                    continue
                if i.trigger not in actions:
                    continue
                if action == None or i.pos == None or i.pos == pos:
                    if eval(i.cond):
                        events.append(i)

            if action:
                return self.cut_events(events)
            else:
                return events


        def cut_events(self, events):
            # If non-multi is found, remove second or later non-multi events

            found = False
            for i in events[:]:
                if not i.multi:
                    if found:
                        events.remove(i)
                    else:
                        found=True

            return events


        def move_pos(self, _return):
            # Changes own level and pos
            # if nothing changed, return None

            # don't move
            if not _return:
                return None

            self.previous_pos = self.pos

            # try place
            rv = self.get_place(_return)
            if rv and isinstance(rv, Place):
                self.level = rv.level
                self.pos = rv.pos

            # try level
            rv = self.get_level(_return)
            if rv and isinstance(rv, Level):
                self.level = _return
                self.pos = None

            # try tuple
            if isinstance(_return, tuple):

                rv = self.get_level(_return[0])
                if rv and isinstance(rv, Level):
                    self.level = _return[0]
                    self.pos = _return[1]
                else:
                    self.pos = _return

            # move
            return True


        @classmethod
        def get_level(cls, name):
            # returns level object from name

            if isinstance(name, Level):
                return name

            elif isinstance(name, basestring):
                obj = getattr(store.level, name, None) or getattr(store, name, None)
                if obj:
                    return obj


        @classmethod
        def get_place(cls, name):
            # returns place object from name

            if isinstance(name, Place):
                return name

            elif isinstance(name, basestring):
                obj = getattr(store.place, name, None) or getattr(store, name, None)
                if obj:
                    return obj


        @classmethod
        def get_event(cls, name):
            # returns event object from name

            if isinstance(name, Event):
                return name

            elif isinstance(name, basestring):
                obj = getattr(store.event, name, None) or getattr(store.ev, name, None) or getattr(store, name, None)
                if obj:
                    return obj


##############################################################################
## Create namespace

init -999 python in level:
    pass

init -999 python in place:
    pass

init -999 python in event:
    pass

init -999 python in ev:
    pass

