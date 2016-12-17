## This file defines Actor and Arena class to compete
## このファイルはターン制の競争を行うためのアクタークラスとアリーナクラスを提供します。
## 基本的には戦闘に利用しますが、勝負条件を変えればコンテストなどにも使えます。

##############################################################################
## How to Use
##############################################################################

## まずアクターが使用するスキルを Skill(name, type, value、target) で定義します。
## type は使用した時の効果です。"attack", "heal" 以外は Skill クラスに書き加えて。
## value は効果のスキルを使用した時の効果の強さです。
## skill の名前空間も使えます。

define skill.attack = Skill("Attack", type="attack", value=5, target="foe")
define skill.heal = Skill("Heal", type="heal", value=5, target="friend")

## 次にアクターを Actor(name, skills, hp) で定義します。
## skills は上で定義したオブジェクトそのままを使います
## hp 以外の特性値は Actor クラスを書き換えることで追加します。

default knight = Actor("Knight", [skill.attack], hp=20)
default bishop = Actor("Bishop", [skill.attack, skill.heal], hp=15)
default pawn = Actor("Pawn", [skill.attack], hp=10)
default pawn2 = pawn.copy()
default pawn3 = pawn.copy()

## 最後に競走中のデータを保存するアリーナを定義します。
default arena = Arena()

## 以上で準備完了です。


## ゲームがスタートしたら jump sample_compete でここに飛んでください。

label sample_compete:    
    
    ## 競争仲間と競争相手のアクターをリストとしてアリーナに追加します。    
    
    $ arena.friends = [knight, bishop]
    $ arena.foes = [pawn, pawn2, pawn3]
    
    ## ここから競争開始。
    call compete(arena)
    
    ## 競争が終わると結果を arena.state で知ることができます。
    if arena.state == "win":
         "You win"
     
    elif arena.state == "lose":
        "You lose"
        
    else:
        "Draw"
        
    return
    
    
##############################################################################
## Definition
##############################################################################

##############################################################################
## Compete label

label compete(arena):
    
    $ _rollback = False
    
    # initialize
    $ arena.init()        
    show screen compete_ui(arena)
    
    while arena.state not in ["win", "lose", "draw"]: 
        
        python:            
            
            # get current actor to perform
            _actor = arena.get_turn()
            
            # get skill and target
            if _actor in arena.friends:
                _skill = renpy.call_screen("choose_skill", _actor)
                _target_list = arena.friends if _skill.target=="friend" else arena.foes
                _target = renpy.call_screen("choose_target", _target_list)
            else:
                _skill = _actor.choose_skill()
                _target_list = arena.foes if _skill.target=="friend" else arena.friends
                _target = _actor.choose_target(_target_list)
                            
            # perform skill
            _actor.use_skill(_skill, _target)
            
            # update arena's state
            arena.update_state()
    
    # crean up
    hide screen battle_ui        
    $ arena.reset()
    
    $ _rollback = False
    $ renpy.block_rollback()
    
    return

    
##############################################################################
## Compete screens

screen compete_ui(arena):
    
    zorder -1
    
    # show friends status
    vbox:
        for i in arena.friends:
            hbox:
                text "[i.name]: HP [i.hp]"
    
    # show foes status
    vbox xalign 1.0:
        for i in arena.foes:
            hbox:
                text "[i.name]: HP [i.hp]"
    

screen choose_skill(actor):
    
    tag menu
    modal True
    
    # caption
    label "[actor.name]'s turn" align .5, .2
    
    # commands
    vbox align .5, .5:
        for i in actor.skills:
            textbutton i.name action Return(i)
            
            
screen choose_target(actors):
    
    tag menu
    modal True
    
    # caption
    label "Choose target" align .5, .2
    
    # commands
    vbox align .5, .5:
        for i in actors:
            textbutton i.name action Return(i)


##############################################################################
## Skill class.

init -3 python:

    class Skill(object):

        """
        Class that represents skill that is stored by actor object. It has follwing fields:
        
        name - skill name that is shown on the screen
        type - skill category
        value - quality of skill
        target - target of skill. if not "friend", "foe" is default
        info - description that is shown when an skill is focused
        """
        
        types = ["attack", "heal"]


        def __init__(self, name="", type=None, value=0, target="foe", info=""):

            self.name = name
            self.type = type
            self.value = int(value)
            self.target = target
            self.info = info
            
            
        def use(self, target):
            # use skill on target.
            
            if self.type == "attack":
                target.hp -= self.value
                narrator ("{} loses {} HP".format(target.name, self.value))
                
            elif self.type == "heal":
                target.hp += self.value
                narrator ("{} gains {} HP".format(target.name, self.value))

            # write your own code
            
            return
            

##############################################################################
## Actor class.

    class Actor(object):

        """
        Class that performs skills. It has follwing fields:
        
        name - name of this actor
        skills - list of skills
        attr - there are many values defined by self.attr = value form
                attr can be defined the blow
        default_attr - default value of attr. if it's positive number, attr's value is limited to this value.
        """
        
        # This will create self.hp and self.default_hp
        attributes = ["hp"] 

        def __init__(self, name, skills=None, **kwargs):

            self.name = name            
            self.skills = skills or []
                    
            # creates attributes as field value
            for i in self.attributes:
                if i in kwargs.keys():
                    setattr(self, "default_"+i, kwargs[i])
                    setattr(self, i, kwargs[i])
                else:
                    setattr(self, "default_"+i, None)
                    setattr(self, i, None)
                    
                    
        def copy(self, name=None):
            # Returns copy of actor, changing its name.
            
            from copy import copy
            
            actor = copy(self)
            if name:
                actor.name = name
            
            return copy(self)
            
            
        def update_state(self):
            # call this each turn to amend invalid attributes
            
            for i in self.attributes:
                attr = getattr(self, i)
                max = getattr(self, "default_"+i)
                if max > 0 and attr > max:
                    setattr(self, i, max)
                if attr < 0:
                    setattr(self, i, 0)
                    
                    
        def reset(self):
            # reset attributes
            
            for i in self.attributes:
                setattr(self, i, getattr(self, "default_"+i))
                
                    
        def use_skill(self, skill, target):
            # use skill on target
            
            skill.use(target)
            self.update_state()
            target.update_state()
            
            
        def choose_skill(self):
            # returns skill randomly
            
            return renpy.random.choice(self.skills)
            
            
        def choose_target(self, actors):
            # returns target randomly
            
            return renpy.random.choice([x for x in actors if x.hp>0])
            
                    
                    
##############################################################################
## Arena class.

    class Arena(object):
        
        '''
        This class represents acting field for actors. It has the follwing fields:
        
        friends - list of playable actors
        foes - list of unplayable actors
        state - curernt state of arena. "win", "lose", "draw" ends compete, otherwise keep performing.
        '''
        
        def __init__(self, friends=None, foes=None):
            
            self.friends = friends or []
            self.foes = foes or []
            
            self.order = []
            self.state = None
            
            
        def init(self):
            # call this to set order
            
            self.state = None
            self.order = self.friends+self.foes
            renpy.random.shuffle(self.order)
            
            
        def reset(self):
            # reset actors
            
            for i in self.friends + self.foes:
                i.reset()
            
        
        def get_turn(self):
            # returns the next performer
            
            while True:
                actor = self.order.pop(0)
                self.order.append(actor)
                if actor.hp > 0:
                    return actor
        
                    
        def update_state(self):
            # call this each turn to update arena's state
            
            for i in self.friends:
                if i.hp > 0:
                    break
            else:
                self.state = "lose"
                    
            for i in self.foes:
                if i.hp > 0:
                    break
            else:
                self.state = "win"
            

##############################################################################
## Create namespace

init -999 python in skill:
    pass


        