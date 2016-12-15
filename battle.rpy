## This file defines Battler and Battlefield class

##############################################################################
## Battle label

label battle(enemy, ally):
    
    $ battle = Battlefield(enemy, ally)
    
    while not battle.end:
        pass
    
    $ del battle
    
    return


##############################################################################
## Battler class.

init -3 python:       

    class Battler(object):
        
        ''' This class represents an unit in battle field'''                
        
        attributes = ["health", "power"]        
        
        def __init__(self, name="", **kwargs):
            
            # Defaults 
            self.name = name
            
            # Set default attributes
            for i in self.attributes:
                if i in kwargs.keys():
                    setattr(self, i, kwargs[i])
                else:
                    setattr(self, i, 0)
                    
                    
##############################################################################
## Battlefieald class.

    class Battlefield(object):
        
        ''' This class represents battle field'''
        
        def __init__(self, enemy=None, ally=None):
            
            self.enemy = enemy or []
            self.ally = ally or []
            
            self.turn = 0
            self.order = []
            
        @property
        def end(self):
            return
            
            
        
