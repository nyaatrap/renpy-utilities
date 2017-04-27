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
## trait の名前空間も使えます。

define trait.attack = Trait("Attack", type="active", effect="attack", target="foe", value=5)
define trait.heal = Trait("Heal", type="active", effect="heal", target="friend", value=10, score=5, cost=1)

## 次にアクターを Actor(name, traits, hp) で定義します。
## traits は能力のリストで、trait. を外した文字列です。
## hp は能力値です。Actor クラスを書き換えることで追加できます。

default knight = Actor("Knight", traits=["attack"], hp=20)
default bishop = Actor("Bishop", traits=["attack", "heal"], hp=15)
default pawn = Actor("Pawn A", traits=["attack"], hp=10)

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

            # set trait and target
            if _actor in arena.friends:
                _actor.trait = renpy.call_screen("choose_trait", _actor)
                _actor.target = renpy.call_screen("choose_target", targets = arena.get_targets(_actor))
            else:
                _actor.trait = _actor.choose_trait()
                _actor.target = _actor.choose_target(arena.get_targets(_actor))

            # perform trait
            _actor.use_trait()

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


screen choose_trait(actor):

    tag menu
    modal True

    # caption
    label "[actor.name]'s turn" align .5, .2

    # commands
    vbox align .5, .5:
        for name, score, obj in actor.get_traits(types=["active"]):
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
            
            obj = actor.get_trait(actor.trait)
            
            if not actor.trait or actor not in self.order:
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
        Class that performs traits. It has follwing fields:

        name - name of this actor
        traits - dict of {"traitname", score}
        attribute - there are many values defined by self.attr = value form
                attribute can be defined the blow
        default_attrribute - default value of attribute. if it's positive number, attribute's value is limited to this value.
        """

        # This will create self.hp and self.default_hp
        _attributes = ["hp"]
        
        # Define default trait categories
        _trait_types = ["active"]

        def __init__(self, name="", traits=None, trait_types = None, **kwargs):

            self.name = name
            self.traits = OrderedDict()
            if traits:
                for i in traits:
                    self.add_trait(i)            
            self.trait_types = trait_types or self._trait_types
            
            self.trait = None
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

            self.trait = None
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
        def get_trait(self, name):
            # returns trait object from name

            if isinstance(name, Trait): 
                return name
                
            elif isinstance(name, basestring):
                obj = getattr(store.trait, name, None) or getattr(store, name, None)
                if obj: 
                    return obj
                
            raise Exception("Trait '{}' is not defined".format(name))
                        

        def has_trait(self, name, score=None):
            # returns True if inventory has this trait whose score is higher than given.
            
            # check valid name or not
            self.get_trait(name)

            return name in [k for k, v in self.traits.items() if score==None or v >= score]


        def count_trait(self, name):
            # returns score of this trait
            
            if self.has_trait(name):
                return self.traits[name]
                
            
        def get_traits(self, score=None, types = None, rv=None):
            # returns list of (name, score, object) tuple in conditions
            # if rv is "name" or "obj", it returns them.
            
            traits = [k for k, v in self.traits.items() if score==None or v >= score]
            
            if types:
                traits = [i for i in traits if self.get_trait(i).type in types]
                
            if rv == "name":
                return traits
                
            elif rv == "obj":
                return [self.get_trait(i) for i in traits]
                
            return  [(i, self.traits[i], self.get_trait(i)) for i in traits]


        def add_trait(self, name, score = None):
            # add an trait
            # if score is given, this score is used instead of trait's default value.
            
            score = score or self.get_trait(name).score

            if self.has_trait(name):
                self.traits[name] += score
            else:
                self.traits[name] = score


        def remove_trait(self, name):
            # remove an trait

            if self.has_trait(name):
                del self.traits[name]


        def score_trait(self, name, score, remove = True):
            # changes score of name
            # if remove is True, trait is removed when score reaches 0

            self.add_trait(name, score)
            if remove and self.traits[name] <= 0:
                self.remove_trait(name)  


        def replace_traits(self, first, second):
            # swap order of two slots

            keys = list(self.traits.keys())
            values = list(self.traits.values())
            i1 = keys.index(first)
            i2 = keys.index(second)
            keys[i1], keys[i2] = keys[i2], keys[i1]
            values[i1], values[i2] = values[i2], values[i1]
            
            self.traits = OrderedDict(zip(keys, values))


        def sort_traits(self, order="name"):
            # sort slots
            
            traits = self.traits.items()

            if order == "name":
                traits.sort(key = lambda i: self.get_trait(i[0]).name)
            elif order == "type":
                traits.sort(key = lambda i: self.trait_types.index(self.get_trait(i[0]).type))
            elif order == "value":
                traits.sort(key = lambda i: self.get_trait(i[0]).value, reverse=True)
            elif order == "amount":
                traits.sort(key = lambda i: i[1], reverse=True)
                
            self.traits = OrderedDict(traits)


        def get_all_traits(self, namespace=store):
            # get all trait objects defined under namespace

            for i in dir(namespace):
                if isinstance(getattr(namespace, i), Trait):
                    self.add_trait(i)


        def use_trait(self):
            # use trait on target
            
            obj = self.get_trait(self.trait)
            target = self.target

            obj.use(target)
            
            if obj.cost:
                self.score_trait(self.trait, - obj.cost, remove=False)

                
        def choose_trait(self):
            # returns trait randomly

            return renpy.random.choice(self.get_traits(score=1, types=["active"], rv="name"))


        def choose_target(self, targets):
            # returns target randomly

            return renpy.random.choice([x for x in targets if x.hp>0])



##############################################################################
## Trait class.

    class Trait(object):

        """
        Class that represents trait that is stored by actor object. It has follwing fields:

        name - trait name that is shown on the screen
        type - trait category
        effect - effect on use.
        target - target of trait. if not "friend", "foe" is default
        value - quality of trait
        score - default amount of trait when it's added into actor
        cost - if not zero, using this trait reduces score.
        info - description that is shown when an trait is focused
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
            # use trait on target.
            
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

init -999 python in trait:
    pass



