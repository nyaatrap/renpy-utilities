## This file provides exploration game framework that uses event maps.
## ２Dマップにイベントを配置する探索型ゲームのフレームワークを追加するファイルです。
## ラベルをオブジェクトとのペアで管理することで、マップ上にイベントとして配置して呼び出すことができます。
## RPGからSLGまで様々に使えるように汎用性を高くしてありますが、その分コードは少し複雑になっています。

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


## それから現在位置や達成イベントなどを保持する探検者を Explorer(place, image) で default で定義します
## 任意のパラメーターを追加すると、各イベントを呼び出す条件に使えます。
default explorer = Explorer("home", turn=0)


## 各イベントは define と label のペアで定義します。
## defne ラベル名 = Event(place, cond, priority, once, multi, precede, click, image) で定義します。
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
    
## click を True にすると場所と同じように image を表示して
## クリックから即座にリンクしたラベルを呼び出します。
## click が False の場合は移動後にイベントをチェックします。
## explorer.seen(ev) でそのイベントを見たかどうか評価できます。
define ev.direct = Event(cond="explorer.seen(ev.shop)", level="west", pos=(.1,.1), click=True, image=Text("click here"))
label direct:
    "this is a direct click event"
    return ev.direct.pos
    
## このラベルは毎ターン最後に呼ばれ、ターンの経過を記録しています。
define ev.turn = Event(priority = -100, precede =True, multi=True)
label turn:
    #"turn+1"
    $ explorer.turn += 1
    return

    
## start ラベルから explore へジャンプすると探索を開始します。

    
##############################################################################
## Definitions
##############################################################################

##############################################################################
## Main label
## Jumping to this label starts exploration

label explore:

    # Update event list in current level
    $ explorer.update_events()
    $ explorer.ignore_precede = True

    # Play music
    if explorer.lv.music:
        if renpy.music.get_playing() != explorer.lv.music:
            play music explorer.lv.music fadeout 1.0

    # Show background
    if explorer.lv.image:
        scene black with Dissolve(.25)        
        scene expression explorer.lv.image
        with Dissolve(.25)
        
    jump explore_loop
    

label explore_loop:
    while True:

        # check passive events
        $ block()
        $ _events = explorer.get_events()

        # sub loop to excecute all passive events
        $ _loop = 0
        while _loop < len(_events):
            
            $ explorer.event = _events[_loop]
            $ block()
            call expression explorer.event.label or explorer.event.name
            if explorer.move_pos(_return):
                jump explore
            $ _loop += 1

        $ explorer.ignore_precede = False
        
        # show eventmap
        $ block()
        call screen eventmap(explorer)

        # move by place
        if isinstance(_return, Place):
            $ explorer.pos = _return.pos
            
        # excecute click event
        elif isinstance(_return, Event):
            $ explorer.event = _return
            $ block()
            call expression explorer.event.label or explorer.event.name
            if explorer.move_pos(_return):
                jump explore

            
label after_load():

    # Update event list in current level
    $ explorer.update_events()
    return
                
    
init python:    

    def block():
        # blocks rollback then allows saving data in the current interaction
        
        renpy.block_rollback()
        renpy.retain_after_load()


##############################################################################
## Eventmap screen
## screen that shows events and places over the current level

screen eventmap(explorer):
    
    ## show places
    for i in explorer.get_places():
        button pos i.pos:
            action Return(i)
            if i.image:
                add i.image
                
    ## show events
    for i in explorer.get_events(click=True):
        button pos i.pos:
            action Return(i)
            if  i.image:
                add i.image
        

##############################################################################
## Level class

init -3 python:

    class Level(object):

        """
        Class that represents level that place events on it. It has following fields:
        
        image - image that is shown behind events
        music - music that is played while explorer in this level
        """

        def __init__(self, image=None, music=None):

            self.image = image
            self.music = music


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
        Class that represents events that is places on level or place. It has the following fileds:
        
        level - String of level where this events placed onto.
        pos - (x, y) coordinate on the screen.
        cond - Conditions to evaluate this event happnes or not. This should be quotated.
        priority - An event with higher value happens firster. default is 0.
        once - Set this true prevents calling this event second time.
        multi - Set this true don't prevent other events in the same interaction.
        precede - Set this true serches this event before showing event map screen.
        click - Set this true makes click events. Like an event place object, that allows clicking this event on map.
                Otherwise, this is passive event.
        image - Imagebutton to be shown on eventmap if click is True.
        label - If it's given this label is called instead of object name.
        info - Information text to be shown on event map screen.
        """

        def __init__(self, place = None, cond="True", priority=0, once=False, multi=False, precede=False, click=False, image=None, level=None, pos=None, label=None, info=""):            

            self.level = Explorer.get_place(place).level if place else level
            self.pos = Explorer.get_place(place).pos if place else pos
            self.cond = cond
            self.priority = int(priority)
            self.once = once
            self.multi = multi
            self.precede = precede
            self.click = click
            self.image = image
            self.label = label
            self.info = info
            self.name = ""
            

##############################################################################
## Explorer class

    class Explorer(object):

        """
        Class that stores various methods and data for explroring.
        """
        
        def __init__(self, place=None, level=None, pos=None, **kwargs):
            
            self.level = Explorer.get_place(place).level if place else level
            self.pos = Explorer.get_place(place).pos if place else pos
            
            self.ignore_precede = True
            self.event = None
            self.current_events = []
            self.current_places = []
            self.seen_events = set()

            for i in kwargs.keys():
                setattr(self, i, kwargs[i])
            
                
        @property
        def lv(self):
            # shortcut to access the current level
            
            return self.get_level(self.level)
            
            
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
                        

        def get_events(self, click = False, pos=None):
            # returns event list that happens in the given pos.
            
            pos = pos or self.pos
            
            events = []
            for i in self.current_events:
                if i.click == click:
                    if not i.once or not self.seen(i):
                        if click or i.precede or not self.ignore_precede:
                            if self._check_pos(i, click, pos) and eval(i.cond):
                                events.append(i)
            
            return self.cut_events(events)
            
            
        def _check_pos(self, ev, click, pos):
            # internal function for get_events.
            
            if click or ev.pos == None or ev.pos == pos:
                return True                
            
                                
        def cut_events(self, events):
            # if not multi is False, remove second or later  
            
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
            # returns item object from name

            if isinstance(name, Level): return name
            elif name in dir(store.level): return getattr(store.level, name)
            elif name in dir(store): return getattr(store, name)
            

        @classmethod            
        def get_place(self, name):
            # make place object from name

            if isinstance(name, Place): return name
            elif name in dir(store.place): return getattr(store.place, name)
            elif name in dir(store): return getattr(store, name)
            

        @classmethod
        def get_event(self, name):
            # make event object from name

            if isinstance(name, Event): return name
            elif name in dir(store.event): return getattr(store.event, name)
            elif name in dir(store.ev): return getattr(store.ev, name)
            elif name in dir(store): return getattr(store, name)
            

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


