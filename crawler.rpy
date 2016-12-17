## This file expand add dungeon crawl function into explorer framework.
## このファイルは explore.rpy に疑似３Dダンジョン機能を追加します。

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
["1","0","0","1","1","1","0","1"],
["1","1","1","1","1","1","1","1"]
]

## それらを使ってレベルを Dungeon(image, music, map) で定義します。
## image は先に定義したダンジョンの種類です。
## map は ２次元配列の map [[]] か、コンマ区切りかタブ区切りのスプレッドシートファイル名です。

define level.cave = Dungeon(image="cave", map=sample_map)


## 最後に冒険者を Crawler クラスで定義します。
## ダンジョンの pos は (x,y,dx,dy) の組で、dx が 1 ならみぎ、-1 ならひだりを向きます。

default crawler = Crawler(level="cave", pos=(1,1,0,1))


## ダンジョンのイベントを定義します。
## dx,dy を与えるとその向きのみイベントが発生します。

define ev.entrance = Event(level="cave", pos=(1,1), precede=True, once=True)
label entrance:
    "Here starts crawling"
    return

define ev.chest = Event(level="cave", pos=(6,6,0,1), click=True)
label chest:
    "You found a chest"
    return

define ev.nothing = Event(level="cave", priority=-10, click=True)
label nothing:
    "There is nothing"
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
    $ explorer.ignore_precede = True

    # Play music
    if crawler.lv.music:
        if renpy.music.get_playing() != crawler.lv.music:
            play music crawler.lv.music fadeout 1.0

    # Show background
    if crawler.lv.image:
        scene black with Dissolve(.25)
        if crawler.in_dungeon():
            $ crawler.draw_dungeon()
        else:
            scene expression crawler.lv.image            
        with Dissolve(.25)

    jump crawler_loop
    
    
label crawler_loop:        
    while True:

        # check passive events
        $ block()
        $ _events = crawler.get_events()

        # sub loop to excecute all passive events
        $ _loop = 0
        while _loop < len(_events):
            
            $ crawler.event = _events[_loop]
            $ block()
            call expression crawler.event.label or crawler.event.name
            if crawler.move_pos(_return):
                jump explore
            $ _loop += 1

        $ explorer.ignore_precede = False
            
        # sub loop to ignore passive events
        while True:
                
            # show eventmap or dungeon navigator
            $ block()
            if crawler.in_dungeon():
                call screen dungeon(crawler)
            else:
                call screen eventmap(crawler)
    
            # move by place
            if isinstance(_return, Place):
                $ crawler.pos = _return.pos
                jump crawler_loop
                
            # excecute click event
            elif isinstance(_return, Event):
                $ crawler.event = _return
                $ block()
                call expression crawler.event.label or crawler.event.name
                if crawler.move_pos(_return):
                    jump crawler
                jump crawler_loop
                    
            # collision 
            elif isinstance(_return, Coordinate) and crawler.lv.map[_return.y][_return.x] in crawler.collision:
                with vpunch
                                
            # move
            elif isinstance(_return, Coordinate):
                if _return.x == crawler.pos[0] and _return.y == crawler.pos[1]:
                    $ crawler.move_pos(_return.unpack())
                    $ crawler.draw_dungeon()   
                else:
                    $ crawler.move_pos(_return.unpack())
                    $ crawler.draw_dungeon()   
                    jump crawler_loop


##############################################################################
## Dungeon screen
## screen that shows orientation buttons in dungeon

screen dungeon(crawler):
    
    $ coord = Coordinate(*crawler.pos)
                
    ## show events
    for i in crawler.get_events(click=True):
        button xysize (config.screen_width, config.screen_height):
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
        
        def __init__(self, image=None, music=None, map = None):
            
            super(Dungeon, self).__init__(image, music)
            self.map = self.read_map(map) if map and isinstance(map, basestring) else map
                        
                
        def read_map(self, file):
            # read tsv or csv file to make them into 2-dimentional map
            
            map=[]
            f = renpy.file(file)
            for l in f:
                if l.find("\t"):
                    a = l.rstrip().split("\t")
                elif l.find(","):
                    a = l.rstrip().split(",")
                else:
                    raise Exception("Separater is not found in '{}'".format(file))
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

        def unpack(self):
            return (self.x, self.y, self.dx, self.dy)
            
            
##############################################################################
## Crawler class 

    class Crawler(Explorer):
        
        """
        Expanded Explorer Class that stores various methods and data for crawling. 
        """
                
        # Make a dict that maps characters in dungeon map to image names
        mapping = {"1":"wall", "2":"door", "3":"up", "4":"down"}
        
        # tuple of collision on dungeon map.
        collision = ("1", "2", "3", "4")
            
            
        def in_dungeon(self):
            # returns true if crawler is in dungeon
            
            return isinstance(self.get_level(self.level), Dungeon)
                            
            
        def _check_pos(self, ev, click, pos):
            # It overrides a same method to support coordinate
            
            if ev.pos == None:
                return True
            if pos:
                if len(pos) == 2:
                    if click or ev.pos == None or ev.pos[0] == pos:
                        return True
                elif len(ev.pos) == 4:
                    if ev.pos == pos:
                        return True                
                else:
                    if (ev.pos[0] == pos[0] and ev.pos[1] == pos[1]):
                        return True  
            
                                
        def draw_dungeon(self):            
            # Draw front view image on the coord on the master layer. 
            
            coord = Coordinate(*self.pos)
            image = self.lv.image
            map = self.lv.map
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
            renpy.show("{} floor".format(image))        
                
            for n, i in enumerate(["left2", "right2", "front2", "left1", "right1", "front1", "left0", "right0", "floor"]):
            
                # Try-except clauses are used to prevent IndexError 
                try:
                    # get coordinate object defined above
                    tile=locals()[i] 
                    
                    if map[tile.y][tile.x] in mapping.keys():
                        
                        # left side
                        if i in ["left2", "left1", "left0"]: 
                            if renpy.has_image("{} {} {}".format(image, mapping[map[tile.y][tile.x]], i)):
                                renpy.show(i, what = Transform("{} {} {}".format(image, mapping[map[tile.y][tile.x]], i), yalign=.5))
                                
                        # righit side use mirror image of left side
                        elif i in ["right2", "right1", "right0"]: 
                            if renpy.has_image("{} {} {}".format(image, mapping[map[tile.y][tile.x]], i.replace("right", "left"))):
                                renpy.show(i, what = Transform("{} {} {}".format(image, mapping[map[tile.y][tile.x]], i.replace("right", "left")),  xzoom = -1, xalign = 1.0, yalign=.5))
                                    
                        # front
                        elif i in ["front2", "front1"]: 
                            if renpy.has_image("{} {} {}".format(image, mapping[map[tile.y][tile.x]], i)):
                                renpy.show(i, what = Transform("{} {} {}".format(image, mapping[map[tile.y][tile.x]], i), align=(.5,.5)))  
                                
                except IndexError: 
                    pass
            
                
