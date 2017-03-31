## This file adds tilemap exploring function into adventure framework.
## This framework requres tilemap.rpy and adventure.rpy.
## adventure にタイルマップを探索する機能を追加するファイルです。
## tilemap.rpy と adventure.rpy が必要になります。

##############################################################################
## How to Use
##############################################################################


## まずタイルマップを作成します。
## 次にそれらを使ってレベルを Field(image, music, tilemap) で定義します。
## image はタイルマップで作成した画像タグです。
## tilemap は作成したタイルマップです。

define level.field = Field(image="map", tilemap=tilemap)


## 最後に冒険者を Explorer クラスで定義します。

default explorer = Explorer("field", pos=(1,1))


## フィールドのイベントを定義します。

define ev.enter = Event("field", pos=(1,1))
label enter:
    "enter point"
    return

## pos を文字列にするとその文字列のある map の座標でイベントが発生します。
define ev.ev2 = Event("field", pos="2")
label ev2:
    "2"
    return

define ev.none = Event("field", priority=-10)
label none:
    "There is nothing"
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
    $ explorer.after_interact = False

    # Play music
    if explorer.music:
        if renpy.music.get_playing() != explorer.music:
            play music explorer.music fadeout 1.0

    # Show background
    if explorer.image:
        scene black with Dissolve(.25)
        scene expression explorer.image
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

        $ explorer.after_interact = True
        $ block()
        
        # show eventmap
        if explorer.in_field():
            call screen field(explorer)
        else:
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
                
        # move
        else:
            $ explorer.pos = _return
            jump explore_loop

            
##############################################################################
## Field screen
## screen that shows orientation buttons in tilemap field
## This overwrites default eventmap screen

screen field(explorer):
    
    # show coordinate
    if explorer.tilemap.coordinate:
        $ coord = explorer.tilemap.coordinate    
        text "[coord]"
        key "button_select" action Return(coord)
        
        ## show cursor
        

    ## show events
    for i in explorer.get_events(click=True):
        button pos i.pos:
            action Return(i)
            if  i.image:
                add i.image


##############################################################################
## Field class.

init -2 python:

    class Field(Level):

        """
        Expanded Level class to holds tilemap class.
        """

        def __init__(self, image=None, music=None, tilemap = None, info=""):

            super(Field, self).__init__(image, music, info)
            self.tilemap = tilemap


##############################################################################
## Explore class

    class Explorer(Player):

        """
        Expanded Player Class that stores various methods and data for exploring.
        """
            
        @property
        def tilemap(self):
            return self.get_level(self.level).tilemap


        def in_field(self):
            # returns true if explorer is in field

            return isinstance(self.get_level(self.level), Field)


        def _check_pos(self, ev, click, pos):
            # It overrides a same method to support coordinate

            if ev.pos == None or ev.pos == pos:
                return True
            if not self.in_field() and click:
                return True
            elif pos:
                if len(ev.pos) == 2:
                    if ev.pos[0] == pos[0] and ev.pos[1] == pos[1]:
                        return True
                else:
                    if ev.pos == self.tilemap.map[pos[1]][pos[0]]:
                        return True

