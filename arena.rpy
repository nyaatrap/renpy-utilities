## This file defines Actor and Arena class to add turn-based combat and competition.
## ターン制の戦闘や競争を行うためのアクタークラスとアリーナクラスを追加するファイルです。
## 基本的な枠組みしかありませんので、実用には改変する必要があります。

##############################################################################
## How to Use
##############################################################################

## まずアクターが使用する能力を Trait(name, type, effect, target, value, score, cost) で定義します。
## type は表示される能力のカテゴリーです。このデモでは "active" のみ有効です。
## effect は使用した時の効果です。"attack", "heal" 以外は Trait クラスに書き加えます。
## target は能力を使う相手で "friend" か "foe" があります。
## value は効果の能力を使用した時の効果の強さです。
## score, cost は使用回数がある能力に使います。デフォルトは1と0です。
## skill の名前空間も使えます。

define skill.attack = Trait("Attack", type="active", effect="attack", target="foe", value=5)
define skill.heal = Trait("Heal", type="active", effect="heal", target="friend", value=10, score=5, cost=1)

## 次にアクターを Actor(name, skills, hp) で定義します。
## skills は能力のリストで、skill. を外した文字列です。
## hp は能力値です。Actor クラスを書き換えることで追加できます。

default knight = Actor("Knight", skills=["attack"], hp=20)
default bishop = Actor("Bishop", skills=["attack", "heal"], hp=15)
default pawn = Actor("Pawn A", skills=["attack"], hp=10)

## actor.copy(name) で同じ能力のアクターを名前を変えてコピーします。
default pawn2 = pawn.copy("Pawn B")
default pawn3 = pawn.copy("Pawn C")

## 最後に競争に関するデータを保存するアリーナを定義します。
default arena = Arena()

## 以上で準備完了です。


## ゲームがスタートしたら jump sample_combat でここに飛んでください。

label sample_combat:

    ## 競争仲間と競争相手のアクターをリストとしてアリーナに追加します。

    $ arena.friends = [knight, bishop]
    $ arena.foes = [pawn, pawn2, pawn3]

    ## ここから競争開始。
    call _combat(arena)

    ## 競争が終わると結果を _return で知ることができます。
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
## Combat label

label _combat(arena):

    # initialize
    python:
        arena.init()
        _rollback = False
                
    show screen combat_ui(arena)

    while arena.state not in ["win", "lose", "draw"]:

        python:

            # get current actor to perform
            _actor = arena.get_turn()

            # set skill and target
            if _actor in arena.friends:
                _actor.skill = renpy.call_screen("choose_skill", _actor)
                _actor.target = renpy.call_screen("choose_target", targets = arena.get_targets(_actor))
            else:
                _actor.skill = _actor.choose_skill()
                _actor.target = _actor.choose_target(arena.get_targets(_actor))

            # perform skill
            _actor.use_skill()

            # update arena's state
            arena.update_state()

    hide screen combat_ui
    
    python:
        _return = arena.state
        arena.reset_state()
        _rollback = True
        renpy.block_rollback()
        
    return _return


##############################################################################
## combat screens

screen combat_ui(arena):

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
        for name, score, obj in actor.get_skills(types=["active"]):
            $ score_text = " ({}/{})".format(score, obj.score) if obj.cost else "" 
            textbutton "[obj.name][score_text]" action [Return(name) if score else NullAction()]


screen choose_target(targets):

    tag menu
    modal True

    # caption
    label "Choose target" align .5, .2

    # commands
    vbox align .5, .5:
        for i in targets:
            textbutton i.name action Return(i)


##############################################################################
## Arena class.

init -3 python:

    class Arena(object):

        """
        This class represents acting field for actors. It has the follwing fields:

        friends - list of playable actors
        foes - list of unplayable actors
        state - curernt state of arena. "win", "lose", "draw" ends combat, otherwise keep performing.
        """

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


        def reset_state(self):
            # reset actors's states

            for i in self.friends + self.foes:
                i.reset_state()


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


        def get_turn(self):
            # returns the next performer

            while True:
                actor = self.order.pop(0)
                self.order.append(actor)
                if actor.hp > 0:
                    return actor
            
            
        def get_targets(self, actor):
            # returns list of targets.
            
            obj = actor.get_skill(actor.skill)
            
            if not actor.skill or actor not in self.order:
                return []
            if actor in self.friends:
                return self.foes if obj.target=="foe" else self.friends 
            if actor in self.foes:
                return self.friends if obj.target=="foe" else self.foes 

                

##############################################################################
## Actor class.

    from collections import OrderedDict

    class Actor(object):

        """
        Class that performs skills. It has follwing fields:

        name - name of this actor
        skills - dict of {"skillname", score}
        attribute - there are many values defined by self.attr = value form
                attribute can be defined the blow
        default_attrribute - default value of attribute. if it's positive number, attribute's value is limited to this value.
        """

        # This will create self.hp and self.default_hp
        _attributes = ["hp"]
        
        # Define default skill categories
        _skill_types = ["active"]

        def __init__(self, name="", skills=None, skill_types = None, **kwargs):

            self.name = name
            self.skills = OrderedDict()
            if skills:
                for i in skills:
                    self.add_skill(i)            
            self.skill_types = skill_types or self._skill_types
            
            self.skill = None
            self.target = None

            # creates attributes as field value
            for i in self._attributes:
                if i in kwargs.keys():
                    setattr(self, "default_"+i, kwargs[i])
                    setattr(self, i, kwargs[i])
                else:
                    setattr(self, "default_"+i, None)
                    setattr(self, i, None)


        def copy(self, name=None):
            # Returns copy of actor, changing its name.

            from copy import deepcopy

            actor = deepcopy(self)
            if name:
                actor.name = name

            return actor


        def reset_state(self):
            # reset attributes

            for i in self._attributes:
                setattr(self, i, getattr(self, "default_"+i))

            self.skill = None
            self.target = None


        def update_state(self):
            # call this each turn to amend invalid attributes

            for i in self._attributes:
                attr = getattr(self, i)
                max = getattr(self, "default_"+i)
                if max > 0 and attr > max:
                    setattr(self, i, max)
                if attr < 0:
                    setattr(self, i, 0)
            

        @classmethod
        def get_skill(self, name):
            # returns skill object from name

            if isinstance(name, Trait): 
                return name
                
            elif isinstance(name, basestring):
                obj = getattr(store.skill, name, None) or getattr(store, name, None)
                if obj: 
                    return obj
                
            raise Exception("Trait '{}' is not defined".format(name))
                        

        def has_skill(self, name, score=None):
            # returns True if inventory has this skill whose score is higher than given.
            
            # check valid name or not
            self.get_skill(name)

            return name in [k for k, v in self.skills.items() if score==None or v >= score]


        def count_skill(self, name):
            # returns score of this skill
            
            if self.has_skill(name):
                return self.skills[name]
                
            
        def get_skills(self, score=None, types = None, rv=None):
            # returns list of (name, score, object) tuple in conditions
            # if rv is "name" or "obj", it returns them.
            
            skills = [k for k, v in self.skills.items() if score==None or v >= score]
            
            if types:
                skills = [i for i in skills if self.get_skill(i).type in types]
                
            if rv == "name":
                return skills
                
            elif rv == "obj":
                return [self.get_skill(i) for i in skills]
                
            return  [(i, self.skills[i], self.get_skill(i)) for i in skills]


        def add_skill(self, name, score = None):
            # add an skill
            # if score is given, this score is used instead of skill's default value.
            
            score = score or self.get_skill(name).score

            if self.has_skill(name):
                self.skills[name] += score
            else:
                self.skills[name] = score


        def remove_skill(self, name):
            # remove an skill

            if self.has_skill(name):
                del self.skills[name]


        def score_skill(self, name, score, remove = True):
            # changes score of name
            # if remove is True, skill is removed when score reaches 0

            self.add_skill(name, score)
            if remove and self.skills[name] <= 0:
                self.remove_skill(name)  


        def replace_skills(self, first, second):
            # swap order of two slots

            keys = list(self.skills.keys())
            values = list(self.skills.values())
            i1 = keys.index(first)
            i2 = keys.index(second)
            keys[i1], keys[i2] = keys[i2], keys[i1]
            values[i1], values[i2] = values[i2], values[i1]
            
            self.skills = OrderedDict(zip(keys, values))


        def sort_skills(self, order="name"):
            # sort slots
            
            skills = self.skills.items()

            if order == "name":
                skills.sort(key = lambda i: self.get_skill(i[0]).name)
            elif order == "type":
                skills.sort(key = lambda i: self.skill_types.index(self.get_skill(i[0]).type))
            elif order == "value":
                skills.sort(key = lambda i: self.get_skill(i[0]).value, reverse=True)
            elif order == "amount":
                skills.sort(key = lambda i: i[1], reverse=True)
                
            self.skills = OrderedDict(skills)


        def get_all_skills(self, namespace=store):
            # get all skill objects defined under namespace

            for i in dir(namespace):
                if isinstance(getattr(namespace, i), Trait):
                    self.add_skill(i)


        def use_skill(self):
            # use skill on target
            
            obj = self.get_skill(self.skill)
            target = self.target

            obj.use(target)
            
            if obj.cost:
                self.score_skill(self.skill, - obj.cost, remove=False)

                
        def choose_skill(self):
            # returns skill randomly

            return renpy.random.choice(self.get_skills(score=1, types=["active"], rv="name"))


        def choose_target(self, targets):
            # returns target randomly

            return renpy.random.choice([x for x in targets if x.hp>0])



##############################################################################
## Trait class.

    class Trait(object):

        """
        Class that represents skill that is stored by actor object. It has follwing fields:

        name - skill name that is shown on the screen
        type - skill category
        effect - effect on use.
        target - target of skill. if not "friend", "foe" is default
        value - quality of skill
        score - default amount of skill when it's added into actor
        cost - if not zero, using this skill reduces score.
        info - description that is shown when an skill is focused
        """


        def __init__(self, name="", type="", effect="", target="foe", value=0, score=1, cost=0, info=""):

            self.name = name
            self.type = type
            self.effect = effect
            self.target = target
            self.value = int(value)
            self.score = int(score)
            self.cost = int(cost)
            self.info = info
            

        def use(self, target):
            # use skill on target.
            
            if self.effect == "attack":
                target.hp -= self.value
                target.update_state()
                narrator ("{} loses {} HP".format(target.name, self.value))

            elif self.effect == "heal":
                target.hp += self.value
                target.update_state()
                narrator ("{} gains {} HP".format(target.name, self.value))

            return
            
            
##############################################################################
## Create namespace

init -999 python in skill:
    pass



