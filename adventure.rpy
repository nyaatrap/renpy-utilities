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
## define ラベル名 = Event(place, cond, priority, once, multi, precede) または、
## define ラベル名 = Event(level, pos, cond, priority, once, multi, precede) で定義します。
## 探索者が place の場所に移動すると、そのイベントと同じ名前のラベルを呼び出します。
## cond が与えられると、その条件式を満たした場合にのみイベントを実行します。
## priority は発生の優先度で、数字が小さい順に実行されます。デフォルトは０です。
## once を True にすると一度しか実行されません。デフォルトでは何度も実行されます。
## multi を True にすると他のイベントも同時に発生します。ただし active＝True のイベントは発生しません。
## precede を True にすると、プレイヤーが操作する前にイベントを確認します。
## デフォルトでは、プレイヤーが１度操作した後からイベントを確認します。
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


## イベントに image を与えると、イベントマップ上にその画像が表示されます。
## さらに active を True にすると place を使わずに画像を直接クリックしてイベントを呼び出せるようになります。
## player.happened(ev) でそのイベントが過去に呼び出されたかどうか評価できます。
## player.done(ev) でそのイベントが過去に最後まで実行されたかどうか評価できます。
define ev.shop2 = Event("west", pos=(.1,.1), cond="player.happened(ev.shop)", active = True, image=Text("hidden shop"))
label shop2:
    "this is a hidden shop."
    return


## active = True にして image を与えない場合、画面のどこをクリックしてもイベントが発生します。
## また label を定義すると、イベント名の代わりにそのラベル名を呼び出します。
define ev.west_nothing = Event("west", active=True, priority=99)
define ev.east_nothing = Event("east", active=True, priority=99, label="west_nothing")
label west_nothing:
    "There is nothing there"
    return

## このラベルは毎ターン操作の直前に呼ばれ、ターンの経過を記録しています。
define ev.turn = Event(priority = 999, precede =True, multi=True)
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

    jump adventure_loop


label adventure_loop:
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
                jump adventure
            $ _loop += 1

        $ player.after_interact = True
        $ block()

        # show eventmap navigator
        call screen eventmap_navigator(player)

        # If return value is a place, move to there
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
                jump adventure


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

    ## show places and active events
    for i in player.get_active_events():
        button:
            if i.pos:
                pos i.pos
            else:
                xysize (config.screen_width, config.screen_height)

            if i.active:
                action Return(i)

            # show image on screen. you can also show them on the background.
            if i.image:
                add i.image


##############################################################################
## Level class

init -3 python:

    class Level(object):

        """
        Class that represents level that places events on it. It has following fields:

        image - image that is shown behind events.
        music - music that is played while player is in this level.
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
            self.precede = False
            self.active = True


##############################################################################
## Event class

    class Event(object):

        """
        Class that represents events that is places on level or place. It has the following fields:

        level - String of level where this events placed onto.
        pos - (x, y) coordinate on the screen.
        cond - Condition that evaluates this event happen or not. This should be quoted expression.
        priority - An event with higher value happens earlier. default is 0.
        once - Set this true prevents calling this event second time.
        multi - Set this true don't prevent other events in the same interaction.
        precede - Set this true searches this event before showing event map screen.
        active - Set this true makes this event as 'active event'.
                An active event is executed when you clicked its image on an eventmap.
        image - Image that is shown on an eventmap.
        label - If it's given this label is called instead of object name.
        """

        def __init__(self, level=None, pos=None, cond="True", priority=0, once=False, multi=False, precede=False,
            active=False, image=None, label=None):

            self.place = level if Player.get_place(level) else None
            self._level = None if self.place else level
            self._pos = None if self.place else pos
            self.cond = cond
            self.priority = int(priority)
            self.once = once
            self.multi = multi
            self.precede = precede
            self.active = active
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

        level - current level.
        pos - current coordinate.
        event - current event.
        image - shortcut to level.image.
        music - shortcut to level.music.

        happening(event) - returns True if an event is happened.
        done(event) - returns True if an event is happened and done.
        """

        def __init__(self, level=None, pos=None, **kwargs):

            place = Player.get_place(level)
            self.level = place.level if place else level
            self.pos = place.pos if place else pos
            self.previous_pos = self.pos

            self.after_interact = False
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


        def get_active_events(self):
            # returns event and place list that is shown in the navigation screen.

            events = []
            for i in self.current_events+self.current_places:
                if not i.once or not self.happened(i):
                    if eval(i.cond):
                        events.append(i)

            events.sort(key = lambda ev: -ev.priority)

            return events


        def get_passive_events(self):
            # returns event list that happens in the given pos.

            events = []
            for i in self.current_events:
                if not i.once or not self.happened(i):
                    if i.precede or self.after_interact:
                        if i.pos == None or i.pos == self.pos:
                            if not i.active and eval(i.cond):
                                events.append(i)

            return self.cut_events(events)


        def cut_events(self, events):
            # If multi is True, remove second or later
            # This is only used in passive events

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

