##This file provides adventure game framework that uses event maps.
##イベントを配置した２Dマップを探索するアドベンチャーゲームのフレームワークを追加するファイルです。
##ラベルをオブジェクトとのペアで管理することで、マップ上にイベントとして配置して呼び出すことができます。
##RPGからSLGまで様々に使えるように汎用性を高くしてありますが、その分コードは少し複雑になっています。

##############################################################################
## How to Use
##############################################################################


## まず最初にイベントを配置するレベル（マップ／ステージ）を Level(image, music) で定義します。
## level の名前空間でも定義できます。

define level.east = Level(image=Solid("#6a6"))
define level.west = Level(image=Solid("#339"))


## 次にイベント発生の場所を place(level, pos, cond, image) で定義します。
## レベルは上で定義した level を文字列で与えます。pos は表示する座標です。
## cond が満たされると image がマップに表示されクリックするとその場所に移動します。
## place の名前空間でも定義できます。

define place.home = Place(level="east", pos=(.8,.5), image=Text("home"))
define place.e_station = Place(level="east", pos=(.6,.7), image=Text("east-station"))
define place.w_station = Place(level="west", pos=(.4,.4), image=Text("west-station"))
define place.shop = Place(level="west", pos=(.2,.5), image=Text("shop"))


## それから現在位置や達成イベントなどを保持する探検者を Player(level, pos, image) で default で定義します
## level のかわりに place を使うこともできます。
## 任意のパラメーターを追加すると、各イベントを呼び出す条件に使えます。
default player = Player("home", turn=0)


## 各イベントは define と label のペアで定義します。
## defne ラベル名 = Event(level, pos, cond, priority, once, multi, precede) で定義します。
## 探索者が place の場所にいて cond が満たされると、リンクしたラベルが呼ばれます。
## priorty は発生の優先度で、一番数字が大きいものが優先して実行されます。
## once を True にすると一度しか実行されません。
## multi を True にすると他のイベントも同時に発生します。
## precede を True にするとマップ表示前にイベントを確認します。
## event、ev の名前空間でも定義できます。

define ev.myhome = Event("home")
label myhome:
    "this is my home"
    return

define ev.e_station = Event("e_station")
label e_station:
    ## return のあとに次に移動するレベルや場所を指定できます。
    return "w_station"

define ev.w_station = Event("w_station")
label w_station:
    return "e_station"

define ev.shop = Event("shop")
label shop:
    "this is a shop"
    return

## image を与えると、イベントマップ上にその画像が表示されます。
## さらに active を True にすると place のようにクリックでイベントを呼び出せます。
## player.seen(ev) でそのイベントを見たかどうか評価できます。
define ev.shop2 = Event("west", pos=(.1,.1), cond="player.seen(ev.shop)", active = True, image=Text("hidden shop"))
label shop2:
    "this is a hidden shop."
    return

## このラベルは毎ターン最後に呼ばれ、ターンの経過を記録しています。
define ev.turn = Event(priority = -100, precede =True, multi=True)
label turn:
    #"turn+1"
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

    jump adventure_loop


label adventure_loop:
    while True:

        # check passive events
        $ block()
        $ _events = player.get_events()

        # sub loop to excecute all passive events
        $ _loop = 0
        while _loop < len(_events):

            $ player.event = _events[_loop]
            $ block()
            call expression player.event.label or player.event.name
            if player.move_pos(_return):
                jump adventure
            $ _loop += 1

        $ player.after_interact = True
        $ block()
        
        # show eventmap navigator
        call screen eventmap_navigator(player)
        
        #  If return value is a place
        if isinstance(_return, Place):
            $ player.pos = _return.pos
        
        # If return value is an event
        elif isinstance(_return, Event):
            $ player.pos = _return.pos
            $ player.event = _return
            $ block()
            call expression player.event.label or player.event.name
            if player.move_pos(_return):
                jump adventure


label after_load():

    # Update event list in current level
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

    ## show places and events                                 
    for i in player.get_places() + player.get_shown_events():
        button:
            pos i.pos
            if isinstance(i, Place) or i.active:
                action Return(i)
            if i.image:
                add i.image
                

##############################################################################
## Level class

init -3 python:

    class Level(object):

        """
        Class that represents level that place events on it. It has following fields:

        image - image that is shown behind events
        music - music that is played while player in this level
        info - Information text to be shown on event map screen.
        """

        def __init__(self, image=None, music=None, info=""):

            self.image = image
            self.music = music
            self.info = info


##############################################################################
## Place class

    class Place(object):

        """
        Class that places event on level.
        This class's fileds are same to event class
        """

        def __init__(self, level=None, pos=None, cond="True", image=None, info=""):

            self.level = level
            self.pos = pos
            self.cond = cond
            self.image = image
            self.info = info


##############################################################################
## Event class

    class Event(object):

        """
        Class that represents events that is places on level or place. It has the following fields:

        level - String of level where this events placed onto.
        pos - (x, y) coordinate on the screen.
        cond - Conditions to evaluate this event happnes or not. This should be quotated.
        priority - An event with higher value happens firster. default is 0.
        once - Set this true prevents calling this event second time.
        multi - Set this true don't prevent other events in the same interaction.
        precede - Set this true searches this event before showing event map screen.
        active - Set this true makes this event as 'active event'. 
                An active event is exceuted when you clicked its image on an eventmap.
        image - Image that is shown on an eventmap.
        label - If it's given this label is called instead of object name.
        info - Information text to be shown on event map screen.
        """

        def __init__(self, level=None, pos=None, cond="True", priority=0, once=False, multi=False, precede=False, 
            active=False, image=None, label=None, info=""):

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
            self.info = info
            self.name = ""
            
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
        Class that stores various methods and data for explroring. It has the following fields:
        
        level - current level.
        pos - current coordinate
        image - image that is shown behind events
        music - music that is played while player in this level
        event - current event
        """

        def __init__(self, level=None, pos=None, **kwargs):

            place = Player.get_place(level)
            self.level = place.level if place else level
            self.pos = place.pos if place else pos

            self.after_interact = False
            self.event = None
            self.current_events = []
            self.current_places = []
            self.seen_events = set()

            for i in kwargs.keys():
                setattr(self, i, kwargs[i])


        @property
        def music(self):
            return self.get_level(self.level).music
            
            
        @property
        def image(self):
            return self.get_level(self.level).image
            
            
        @property
        def info(self):
            return self.get_level(self.level).info


        def seen(self, ev):
            # returns True if this event is seen.

            return ev.name in self.seen_events


        def update_events(self, check=True):
            # get current_events and current_places in the current level

            # get current events
            self.current_events = []
            for i in dir(store.event) + dir(store.ev) + dir(store):
                if not i.startswith("_"):
                    ev = self.get_event(i)
                    if isinstance(ev, Event) and (ev.level == None or ev.level == self.level):
                        ev.name = i.split(".")[1] if i.count(".") else i
                        self.current_events.append(ev)

                        if check:
                            try:
                                eval(ev.cond)
                            except:
                                raise Exception("Invalid syntax '{}' in '{}'".format(ev.cond, ev.name))

            self.current_events.sort(key = lambda ev: ev.priority, reverse =True)

            # get current places
            self.current_places = []
            for i in dir(store.place) + dir(store.place) + dir(store):
                if not i.startswith("_"):
                    pl = self.get_place(i)
                    if isinstance(pl, Place) and (pl.level == None or pl.level == self.level):
                        self.current_places.append(pl)
            

        def get_shown_events(self):
            # returns event list that is shown in the navigation screen

            events = []
            for i in self.current_events:
                if not i.once or not self.seen(i):
                    if isinstance(i.pos, tuple):
                        if eval(i.cond):
                            events.append(i)

            return events


        def get_events(self):
            # returns event list that happens in the given pos.

            events = []
            for i in self.current_events:
                if not i.once or not self.seen(i):
                    if i.precede or self.after_interact:
                        if i.pos == None or i.pos == self.pos:
                            if not i.active and eval(i.cond):
                                events.append(i)

            return self.cut_events(events)


        def cut_events(self, events):
            # If not multi is False, remove second or later
            # This is only used in passive events 

            found = False
            for i in events[:]:
                if not i.multi:
                    if found:
                        events.remove(i)
                    else:
                        found=True

            return events
            

        def get_places(self):
            # returns place list that shown in current interaction.

            places = []
            for i in self.current_places:
                if eval(i.cond):
                    places.append(i)

            return places


        def move_pos(self, _return):
            # Changes own level and pos
            # if nothing changed, return None

            # before checking jump, add current event into the seen list.
            self.seen_events.add(self.event.name)

            # don't move
            if not _return:
                return None

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
        def get_level(self, name):
            # returns level object from name

            if isinstance(name, Level):
                return name
                
            elif isinstance(name, basestring):
                obj = getattr(store.level, name, None) or getattr(store, name, None)
                if obj: 
                    return obj


        @classmethod
        def get_place(self, name):
            # make place object from name

            if isinstance(name, Place): 
                return name
                
            elif isinstance(name, basestring):
                obj = getattr(store.place, name, None) or getattr(store, name, None)
                if obj: 
                    return obj


        @classmethod
        def get_event(self, name):
            # make event object from name

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

