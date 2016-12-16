## This file defines Actor and Arena class for combat (WIP)

define skill.attack = Skill("Attack", type="attack", value=5)
define skill.heal = Skill("Heal", type="heal", value=5)

default knight = Actor("Knight", ["attack"], health=20)
default bishop = Actor("Bishop", ["attack", "heal"], health=15)
default pawn = Actor("Pawn", ["attack"], health=10)
default pawn2 = copy(pawn)
default pawn3 = copy(pawn)

default arena = Arena()


label sample_combat:
    
    $ arena.friends = [knight, bishop]
    $ arena.foes = [pawn, pawn2, pawn3]
    
    call combat(arena)
    
    if battle.state == "win":
         "You win"
     
    elif battle.state == "lose":
        "You lose"
        
    else:
        "Draw"
        
    $ arena.reset()
        
    return
    

init -999 python:
    from copy import copy
    

##############################################################################
## Combat label

label combat(arena):
    
    $ arena.init()
    
    show screen battle_ui(arena)
    
    while arena.state not in ["win, lose","draw"]: 
        
        python:
            renpy.block_rollback()
            _actor = arena.get_turn()
            
            if _actor in arena.friends:
                _retun = renpy.call_screen("battle_command", arena)
            else:
                _return = _actor.choose_skill()
                
            _actor.use(_return, target)
            
            arena.check_state()
    
    hide screen battle_ui
    
    return

    
##############################################################################
## Battle screens

screen battle_ui(arena):
    
    zorder -1
    
    # show foes status
    
    # show friends status
    

screen battle_command(arena):
    
    tag menu
    modal True
    
    # commands
    
    # keys



##############################################################################
## Skill class.

init -3 python:

    class Skill(object):

        """
        Class that represents skill that is stored by actor object. It has follwing fields:
        
        name - skill name that is shown on the screen
        type - skill category
        value - quality of skill
        score - default score when it's added into actor
        info - description that is shown when an skill is focused
        """
        
        types = ["attack", "heal"]


        def __init__(self, name="", type=None, value=0, score=1, info=""):

            self.name = name
            self.type = type
            self.value = int(value)
            self.score = int(score)
            self.info = info
            
            
        def use(self, target):
            
            if self.type == "attack":
                target.health -= self.value
                
            elif self.type == "heal":
                target.health += self.value

            # write your own code
            
            return
            

##############################################################################
## Actor class.

    class Actor(object):

        """
        Class that performs skills. It has follwing fields:
        
        name - name of this actor
        skills - list of skill slots. item slot is a pair of ["skill name", score]. skills are stored as slot, not skill object. 
        and each attributes defined below
        """
        
        attributes = ["health"]

        def __init__(self, name, skills=None, **kwargs):

            self.name = name
            
            self.skills = []
            if skills:
                for i in skills:
                    self.add_skill(i)
                    
            for i in self.attributes:
                if i in kwargs.keys():
                    setattr(self, "max_"+i, kwargs[i])
                    setattr(self, i, kwargs[i])
                else:
                    setattr(self, "max_"+i, None)
                    setattr(self, i, None)
            
            
        def check_state(self):
            
            for i in self.attributes:
                attr = getattr(self, i)
                max = getattr(self, "max_"+i)
                if attr > max:
                    setattr(self, i, max)
                if attr < 0:
                    setattr(self, i, 0)
                    
                    
        def reset(eslf):
            
            for i in self.attributes:
                setattr(self, i, getattr(self, "max_"+i))
                
                
        ## bellow manage skills                    
        
        @classmethod
        def get_skill(self, name):
            # returns skill object from name

            if isinstance(name, Skill): return name
            elif name in dir(store.skill): return getattr(store.skill, name)
            elif name in dir(store.sk): return getattr(store.sk, name)
            elif name in dir(store): return getattr(store, name)


        def get_slot(self, skill):
            # returns first slot that has a same skill
            # None if inventory deosn't have this skill.

            if skill in self.skills:
                return skill
            for i in self.skills:
                if i[0] == skill:
                    return i
            return None


        def has_skill(self, skill):
            # returns True if inventory has this skill

            return skill in [i[0] for i in self.skills]


        def count_skill(self, skill):
            # returns sum of score of this skill

            return sum([i[1] for i in self.skills if i[0] == skill])


        def add_skill(self, skill, score = None, merge = True):
            # add an skill
            # if score is given, this score is used insted of skill's default value.
            # if merge is True, score is summed when inventory has same skill

            slot = self.get_slot(skill)
            score = score or self.get_skill(skill).score
            if slot and merge:
                slot[1] += score
            else:
                self.skills.append([skill, score])


        def remove_skill(self, skill):
            # remove an skill

            slot = self.get_slot(skill)
            if slot:
                self.skills.remove(slot)


        def score_skill(self, skill, score, remove = True, add = True):
            # changes score of skill
            # if remove is True, skill is removed when score reaches 0
            # if add is True, an skill is added when inventory hasn't this skill

            slot = self.get_slot(skill)
            if slot:
                slot[1] += score
                if remove and self.slot[1]<=0:
                    self.remove_skill(slot)
            elif add:
                self.add_skill(self, [skill, score])

                    
        def use_skill(self, skill, target):
            # use skill on target
            
            self.get_skill(skill).use(target)
            self.check_state()
            self.target.check_state()
            
                    
                    
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
            
            self.turn = 0
            self.order = []
            self.state = None
            
            
        def init():
            
            self.turn = 0
            self.state = 0
            self.order = self.friends+self.foes
            renpy.random.shuffle(self.order)
            
            
        def reset():
            
            for i in self.friends + self.foes:
                i.reset()
            
        
        def get_turn(self):
            
            actor = self.order.pop(0)
            self.order.append(actor)
            return actor
        
        
        def check_state(self):
            
            for i in self.friends:
                if i.health <=0:
                    return "lose"
                    
            for i in self.friends:
                if i.health <=0:
                    return "win"
                    
            return None
            
            
        def choose_skill(self):
            return renpy.random.choice([x[0] for x in self.skills])
            

##############################################################################
## Create namespace

init -999 python in skill:
    pass

init -999 python in sk:
    pass



        
