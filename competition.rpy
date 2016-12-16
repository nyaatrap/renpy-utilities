## This file defines Actor and Arena class for competition

define skill.attack = Skill("Attack", type="attack", value=5)
define skill.heal = Skill("Heal", type="heal", value=5)

default knight = Actor("Knight", [skill.attack], hp=20)
default bishop = Actor("Bishop", [skill.attack, skill.heal], hp=15)
default pawn = Actor("Pawn", [skill.attack], hp=10)
default pawn2 = pawn.copy()
default pawn3 = pawn.copy()

default arena = Arena()


label sample_competition:
    
    $ arena.friends = [knight, bishop]
    $ arena.foes = [pawn, pawn2, pawn3]
    
    call competition(arena)
    
    if arena.state == "win":
         "You win"
     
    elif arena.state == "lose":
        "You lose"
        
    else:
        "Draw"
        
    return
    

##############################################################################
## Competition label

label competition(arena):
    
    $ _rollback = False
    
    # initialize
    $ arena.init()        
    show screen competition_ui(arena)
    
    while arena.state not in ["win", "lose", "draw"]: 
        
        python:            
            
            # get current actor to perform
            _actor = arena.get_turn()
            
            # get skill and target
            if _actor in arena.friends:
                _skill = renpy.call_screen("choose_skill", _actor)
                _target_list = arena.friends if _skill.type=="heal" else arena.foes
                _target = renpy.call_screen("choose_target", _target_list)
            else:
                _skill = _actor.choose_skill()
                _target_list = arena.foes if _skill.type=="heal" else arena.friends
                _target = _actor.choose_target(_target_list)
                            
            # perform skill
            _actor.use_skill(_skill, _target)
            
            # update arena's state
            arena.set_state()
    
    # crean up
    hide screen battle_ui        
    $ arena.reset()
    
    $ _rollback = False
    $ renpy.block_rollback()
    
    return

    
##############################################################################
## Combat screens

screen competition_ui(arena):
    
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
        target - type of target. "friend" or "foe"
        value - quality of skill
        score - default score when it's added into actor
        info - description that is shown when an skill is focused
        """
        
        types = ["attack", "heal"]


        def __init__(self, name="", type=None, value=0, info=""):

            self.name = name
            self.type = type
            self.value = int(value)
            self.info = info
            
            
        def use(self, target):
            
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
        
        # This will create self.hp and self.max_hp
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
            
            from copy import copy
            
            actor = copy(self)
            if name:
                actor.name = name
            
            return copy(self)
            
            
        def check_state(self):
            
            for i in self.attributes:
                attr = getattr(self, i)
                max = getattr(self, "default_"+i)
                if max > 0 and attr > max:
                    setattr(self, i, max)
                if attr < 0:
                    setattr(self, i, 0)
                    
                    
        def reset(self):
            
            for i in self.attributes:
                setattr(self, i, getattr(self, "default_"+i))
                
                    
        def use_skill(self, skill, target):
            # use skill on target
            
            skill.use(target)
            self.check_state()
            target.check_state()
            
            
        def choose_skill(self):
            
            return renpy.random.choice(self.skills)
            
            
        def choose_target(self, actors):
            
            return renpy.random.choice([x for x in actors if x.hp>0])
            
                    
                    
##############################################################################
## Arena class.

    class Arena(object):
        
        '''
        This class represents acting field for actors. It has the follwing fields:
        
        friends - list of playable actors
        foes - list of unplayable actors
        '''
        
        def __init__(self, friends=None, foes=None):
            
            self.friends = friends or []
            self.foes = foes or []
            
            self.order = []
            self.state = None
            
            
        def init(self):
            
            self.turn = 0
            self.state = None
            self.order = self.friends+self.foes
            renpy.random.shuffle(self.order)
            
            
        def reset(self):
            
            for i in self.friends + self.foes:
                i.reset()
            
        
        def get_turn(self):
            
            while True:
                actor = self.order.pop(0)
                self.order.append(actor)
                if actor.hp > 0:
                    return actor
        
                    
        def set_state(self):
            
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


        
