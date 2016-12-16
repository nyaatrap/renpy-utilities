## This file provides exploration game framework that uses event maps.
## このファイルはマップ探索型ゲームのフレームワークを追加します。
## ラベルをオブジェクトとのペアで管理することで、マップ上にイベントとして配置して呼び出すことができます。

##############################################################################
## How to Use
##############################################################################


## まず最初にイベントを配置するレベル（マップ／ステージ）を Level(image, music) で定義します。
## level、lv の名前空間でも定義できます。

define lv.east = Level(image=Solid("#6a6"))
define lv.west = Level(image=Solid("#339"))


## 次にイベント発生の場所を place(level, pos, cond, image) で定義します。
## レベルは上で定義した level を文字列で与えます。pos は表示する座標です。
## cond が満たされると image がマップに表示されクリックするとその場所に移動します。
## place、pl の名前空間でも定義できます。

define pl.home = Place(level="east", pos=(.8,.5), image=Text("home"))
define pl.e_station = Place(level="east", pos=(.6,.7), image=Text("east-station"))
define pl.w_station = Place(level="west", pos=(.4,.4), image=Text("west-station"))
define pl.shop = Place(level="west", pos=(.2,.5), image=Text("shop"))


## それから現在位置や達成イベントなどを保持する探検者を Explorer(place, image) で default で定義します
## 任意のパラメーターを追加すると、各イベントを呼び出す条件に使えます。
default explorer = Explorer("home", turn=0)


## 各イベントは define と label のペアで定義します。
## defne ラベル名 = Event(place, cond, priority, once, multi, first, click, image) で定義します。
## 探索者が place の場所にいて cond が満たされると、リンクしたラベルが呼ばれます。
## priorty は発生の優先度で、一番数字が大きいものが優先して実行されます。
## once を True にすると一度しか実行されません。
## multi を True にすると他のイベントも同時に発生します。
## first を True にするとマップ表示前にイベントを確認します。
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
## explorer.seen('ev') でそのイベントを見たかどうか評価できます。
define ev.direct = Event(cond="explorer.seen('shop')", level="west", pos=(.1,.1), click=True, image=Text("click here"))
label direct:
    "this is a direct click event"
    return ev.direct.pos
    
## このラベルは毎ターン最後に呼ばれ、ターンの経過を記録しています。
define ev.turn = Event(priority = -100, first =True, multi=True)
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

    # Play music
    if explorer.music:
        if renpy.music.get_playing() != explorer.music:
            play music explorer.music fadeout 1.0

    # Show background
    if explorer.image:
        scene black with Dissolve(.25)        
        scene expression explorer.image
        with Dissolve(.25)

    while True:

        # check normal events
        $ block()
        $ _events = explorer.get_events()

        # sub loop to excecute all normal events
        $ _loop = 0
        while _loop < len(_events):
            
            $ explorer.event = _events[_loop]
            $ block()
            call expression explorer.event.label or explorer.event.name
            # check next coodinate. if this returns not None, terminate this loop to change level
            if explorer.check_jump(_return):
                jump explore
            $ _loop += 1

        # show eventmap
        $ block()
        call screen eventmap(explorer)

        # move by place
        if isinstance(_return, Place):
            $explorer.pos = _return.pos
            
        # excecute click event
        elif isinstance(_return, Event):
            $ explorer.event = _return
            $ block()
            call expression explorer.event.label or explorer.event.name
    
            # check next coodinate. if this returns not None, terminate this loop to change level
            if explorer.check_jump(_return):
                jump explore
                
        $ explorer.first = False

            
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

        def __init__(self, image=None, music=None):

            self.image = image
            self.music = music


##############################################################################
## Place class

    class Place(object):

        def __init__(self, level=None, pos=None, cond="True", image=None, info=""):

            self.level = level
            self.pos = pos
            self.cond = cond
            self.image = image
            self.info = info


##############################################################################
## Event class

    class Event(object):

        def __init__(self, place = None, cond="True", priority=0, once=False, multi=False, first=False, click=False, image=None, level=None, pos=None, label=None, info=""):

            self.level = Explorer.get_place(place).level if place else level
            self.pos = Explorer.get_place(place).pos if place else pos
            self.cond = cond
            self.priority = int(priority)
            self.once = once
            self.multi = multi
            self.first = first
            self.click = click
            self.image = image
            self.label = label
            self.info = info
            self.name = ""
            

##############################################################################
## Explorer class

    class Explorer(object):
        
        def __init__(self, place=None, level=None, pos=None, **kwargs):

            self.level = Explorer.get_place(place).level if place else level
            self.pos = Explorer.get_place(place).pos if place else pos
            self.first = True
            self.event = None
            self.current_events = []
            self.current_places = []
            self.seen_events = set()

            for i in kwargs.keys():
                setattr(self, i, kwargs[i])
            
                
        @property
        def image(self):
            return self.get_level(self.level).image
            
            
        @property
        def music(self):
            return self.get_level(self.level).music
            
            
        def seen(self, ev):
            #returns True if this event is seen.

            return ev in self.seen_events
            

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
            for i in dir(store.place) + dir(store.pl) + dir(store):
                if not i.startswith("_"):
                    pl = self.get_place(i)
                    if isinstance(pl, Place) and (pl.level == None or pl.level == self.level):
                        self.current_places.append(pl)
                        

        def get_events(self, click = False):
            # returns event list that happens in current interaction.

            events = []
            for i in self.current_events:
                if i.click == click:
                    if not i.once or not i.seen(self):
                        if click or i.first or not self.first:
                            if self.check_pos(i, click) and eval(i.cond):
                                events.append(i)
            
            return self.cut_events(events)
            
            
        def check_pos(self, ev, click):
           if click or ev.pos == None or ev.pos == self.pos:
               return True                
            
                                
        def cut_events(self, events):
            # if not multi is False, remove scond or later  
            
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
            

        def check_jump(self, _return):
            # Changes own level and pos
            # if nothing changed, return None

            # before checking jump, add current event into the seen list.
            explorer.seen_events.add(self.event.name)

            # no transition
            if not _return:
                return None                
                              
            self.first = True

            # try place
            rv = self.get_place(_return)
            if rv and isinstance(rv, Place):
                self.level = rv.level
                self.pos = rv.pos
                return True
                
            # try level
            rv = self.get_level(_return)
            if rv and isinstance(rv, Level):
                self.level = _return
                self.pos = None
                return True

            # try tuple
            if isinstance(_return, tuple):

                # try level and pos
                rv = self.get_level(_return[0])
                if rv and isinstance(rv, Level):
                    self.level = _return[0]
                    self.pos = _return[1]
                    return True
                    
                # only pos
                self.pos = _return
                return True

            # jump to do transition
            return True
                

        @classmethod
        def get_level(self, name):
            # returns item object from name

            if isinstance(name, Level): return name
            elif name in dir(store.level): return getattr(store.level, name)
            elif name in dir(store.lv): return getattr(store.lv, name)
            elif name in dir(store): return getattr(store, name)
            

        @classmethod            
        def get_place(self, name):
            # make place object from name

            if isinstance(name, Place): return name
            elif name in dir(store.place): return getattr(store.place, name)
            elif name in dir(store.pl): return getattr(store.pl, name)
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
init -999 python in lv:
    pass
init -999 python in place:
    pass
init -999 python in pl:
    pass
init -999 python in event:
    pass
init -999 python in ev:
    pass

