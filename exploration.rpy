## This file provides exploration game framework that uses event maps.
## このファイルはマップ探索型ゲームのフレームワークを追加します。
## ラベルをオブジェクトとのペアで管理することで、マップ上にイベントとして配置して呼び出すことができます。

##############################################################################
## How to Use
##############################################################################


## まず最初にイベントを配置するレベル（マップ／ステージ）を Level(image, music) で定義します。
## level、lv の名前空間でも定義できます。

define lv.east = Level(image="black")
define lv.west = Level(image="black")


## 次にイベント発生の場所を place(level, coord, cond, image) で定義します。
## レベルは上で定義した level を文字列で与えます。coord は表示する座標です。
## cond が満たされると image がマップに表示されクリックするとその場所に移動します。
## place、pl の名前空間でも定義できます。

define pl.home = Place(level="east", coord=(.8,.5), image=Text("home"))
define pl.e_station = Place(level="east", coord=(.6,.7), image=Text("east-station"))
define pl.w_station = Place(level="west", coord=(.4,.4), image=Text("west-station"))
define pl.shop = Place(level="west", coord=(.2,.5), image=Text("shop"))


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
## event.seen でそのイベントを見たかどうか評価できます。
## cond 内では ev. や event. は省略できません。
define ev.direct = Event(cond="ev.shop.seen", level="west", coord=(.1,.1), click=True, image=Text("click here"))
label direct:
    "this is a direct click event"
    return ev.direct.coord
    
## このラベルは毎ターン最後に呼ばれ、ターンの経過を記録しています。
define ev.turn = Event(priority = -100, first =True, multi=True)
label turn:
    #"turn+1"
    $explorer.turn += 1
    return

    
## start ラベルから exploration へジャンプすると探索を開始します。

    
##############################################################################
## Definitions
##############################################################################

##############################################################################
## main label
## jumping to this label starts exploration

label exploration:

    # Update event list in current level
    $ explorer.update_events()

    # Play music
    if explorer.level.music:
        if renpy.music.get_playing() != explorer.level.music:
            play music explorer.level.music fadeout 1.0

    # Show background
    if explorer.level.image:
        scene expression explorer.level.image
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
                jump exploration
            $ _loop += 1

        # show eventmap
        $ block()
        call screen eventmap(explorer)

        # move by place
        if isinstance(_return, Place):
            $explorer.coord = _return.coord
            
        # excecute click event
        elif isinstance(_return, Event):
            $ explorer.event = _return
            $ block()
            call expression explorer.event.label or explorer.event.name
    
            # check next coodinate. if this returns not None, terminate this loop to change level
            if explorer.check_jump(_return):
                jump exploration
                
        $explorer.first = False

            
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
## eventmap screen

screen eventmap(explorer):
    
    ## show places
    for i in explorer.get_places():
        button pos i.coord:
            action Return(i)
            if i.image:
                add i.image
                
    ## show events
    for i in explorer.get_events(click=True):
        button pos i.coord:
            action Return(i)
            if  i.image:
                add i.image

    ## show explorer
    if explorer.image:
        add explorer.image pos explorer.coord
        

##############################################################################
## level class

init -3 python:

    class Level(object):

        def __init__(self, image=None, music=None):

            self.image = image
            self.music = music


        @staticmethod
        def get(name):
            # make string into level object

            if isinstance(name, Level):
                return name
            try:
                return getattr(store.level, name)
            except: pass
            try:
                return getattr(store.lv, name)
            except: pass
            try:
                return getattr(store, name)
            except: pass
            return None


##############################################################################
## place class

    class Place(object):

        def __init__(self, level=None, coord=None, cond="True", image=None, info=""):

            self._level = level
            self.coord = coord
            self.cond = cond
            self.image = image
            self.info = info
            

        @staticmethod
        def get(name):
            # make string into place object

            if isinstance(name, Place):
                return name
            try:
                return getattr(store.place, name)
            except: pass
            try:
                return getattr(store.pl, name)
            except: pass
            try:
                return getattr(store, name)
            except: pass
            return None


        @property
        def level(self):
            return Level.get(self._level)


##############################################################################
## event class

    class Event(object):

        def __init__(self, place = None, cond="True", priority=0, once=False, multi=False, first=False, click=False, image=None, level=None, coord=None, label=None, info=""):

            self._level = Place.get(place)._level if place else level
            self.coord = Place.get(place).coord if place else coord
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
            

        @staticmethod
        def get(name):
            # make string into event object

            if isinstance(name, Event):
                return name
            try:
                return getattr(store.event, name)
            except: pass
            try:
                return getattr(store.ev, name)
            except: pass
            try:                    
                 return getattr(store, name)
            except: pass
            return None

                
        @property
        def level(self):
            return Level.get(self._level)


        @property
        def seen(self, explorer="explorer"):
            #returns True if this event is seen by explorer.

            return self.name in getattr(store, explorer).seen_events


##############################################################################
## explorer class

    class Explorer(object):
        
        def __init__(self, place=None, image=None, level=None, coord=None, **kwargs):

            self._level = Place.get(place)._level if place else level
            self.coord = Place.get(place).coord if place else coord
            self.image = image
            self.first = True
            self.event = None
            self.current_events = []
            self.current_places = []
            self.seen_events = set()

            for i in kwargs.keys():
                setattr(self, i, kwargs[i])
                
                
        @property
        def level(self):
            return Level.get(self._level)
            

        def update_events(self, check=True):
            # get current_events and current_places in the current level
            
            # get current events
            self.current_events = []
            for i in dir(store.event) + dir(store.ev) + dir(store):
                if not i.startswith("_"):
                    ev = Event.get(i)
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
                    pl = Place.get(i)
                    if isinstance(pl, Place) and (pl.level == None or pl.level == self.level):
                        self.current_places.append(pl)
                        

        def get_events(self, click = False):
            # returns event list that happens in current interaction.

            events = []
            for i in self.current_events:
                if i.click == click:
                    if click or i.coord in [None, self.coord]:
                        if not i.once or not i.seen(self):
                            if click or i.first or not self.first:
                                if eval(i.cond):
                                    events.append(i)
                                
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
            # Changes own level and coord
            # if nothing changed, return None

            # before checking jump, add current event into the seen list.
            explorer.seen_events.add(self.event.name)

            # no transition
            if not _return:
                return None                
                              
            self.first = True

            # try place
            rv = Place.get(_return)
            if rv and isinstance(rv, Place):
                self._level = rv._level
                self.coord = rv.coord
                return True
                
            # try level
            rv = Level.get(_return)
            if rv and isinstance(rv, Level):
                self._level = _return
                self.coord = None
                return True

            # try coord
            if isinstance(_return, tuple):

                # try level and coord
                rv = Level.get(_return[0])
                if rv and isinstance(rv, Level):
                    self._level = _return[0]
                    self.coord = _return[1]
                    return True
                    
                # only coord
                self.coord = _return
                return True

            # jump to do transition
            return True


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

