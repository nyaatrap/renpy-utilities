## This file provides inventory system.
## このファイルはアイテムの管理や売買を行う機能を追加します。

##############################################################################
## 使い方

## まずアイテムを Item(名前、カテゴリー、価格）で定義します。
## 他の変数と衝突しないように item の名前空間を使うといいでしょう。

define item.apple = Item("Apple", "food", 10)
define item.orange = Item("Orange", "food", 20)
define item.knife = Item("Knife", "supply", 50)

## 次に管理者を Inventory(所持金) で定義します。
## tradein はその管理者が下取りする時の価格比です。
## infinite を True にすると所持金と在庫が無限になります。

default player = Inventory(currency=1000)
default merchant = Inventory(tradein=.25, infinite=True)


label start:
    
    ## add_item でアイテムを追加します。個数を指定する場合は引数 amount を使います。
    $player.add_item(item.apple, amount=2)    
    
    ## 他に has_item、count_item、remove_item、score_item、buy_item などがあります。
    
    ## get_all_items(store.名前空間)ですべてのアイテムを自動的に追加します。
    $merchant.get_all_items(store.item)
    
    while True:
        menu:
            
            "show inventory":
                ## アイテムを見たり整理したい時は inventory(表示する管理者) を表示します
                ## この状態でアイテムをクリックすると、スロットの入替えモードになります。
                call screen inventory(player)
                
            "buy items":
                ## アイテム買いたい時は inventory(売り手の管理者、買い手の管理者) を表示します
                call screen inventory(merchant, buyer=player, title="Buy")
                
            "sell items":
                ## アイテム売りたい時も inventory(売り手の管理者、買い手の管理者) を表示します
                ## 売買の相手が逆転するだけですが、スクリーンタイトルを変えています。
                call screen inventory(player, buyer=merchant, title="Sell")
        
                
##############################################################################
## Inventory Screen

## screen that shows inventory
## inv is an inventory object that has items on the screen
## if buyer is given, it's trade mode.
## otherwise, it's stock mode that can reorder items slots  

screen inventory(inv, buyer=None, title="Inventory"):
    
    # screen variables
    default tab = "all"
    default info = ""
    
    # unselect item on show
    on "show" action SetField(inv, "selected", None)
    
    vbox:
        # screen title
        label title text_size gui.title_text_size             
        
        # currency. when seller (inv) is not player, show buyer's (player's) currency
        $ currency = inv.currency if not inv.infinite else buyer.currency
        text "currency: [currency:>6]" xalign .5
    
    vbox align .5,.5:
        
        # category tabs
        hbox style_prefix "radio":
            
            for i in ["all"] + Item.types:
                textbutton i.capitalize():
                    action SetScreenVariable("tab", i)
                
        # item slots
        frame xysize 800, 500:
                        
            vpgrid style_prefix "item":
                cols 4 mousewheel True draggable True scrollbars "vertical" 
                
                for slot in inv.items:
                    
                    python:
                        item = slot[0]
                        amount = slot[1]
                        price = int(slot[0].price*slot[1]*(buyer.tradein if buyer else inv.tradein))
                            
                    if tab in [item.type, "all"]:
                        textbutton "[item.name] x[amount] ([price])":                                      
                            selected inv.selected == slot
                            
                            # sell/buy
                            if buyer:
                                action Function(inv.sell_item, slot=slot, buyer=buyer)
                                
                            # reorder after selected
                            elif inv.selected:
                                action [Function(inv.replace_items, first=slot, second=inv.selected), SetField(inv, "selected", None)]
                                
                            # reorder before selecting
                            else:
                                action SetField(inv, "selected", slot)
                                
    textbutton "Return" action Return() yalign 1.0
            
    key "game_menu" action [SetField(inv, "selected", None) if inv.selected else Return()]
        
                    
style item_button:
    xsize 200
                

##############################################################################
## Item class.

init -1 python:

    class Item(object):
        
        """
        Class that represents item that is stored by party object. It has follwing fields:
        name - item name that is shown on the screen
        type - item category
        price - amount of currency for trading
        amount - default amount of item when it's added into inventory
        info - description that is shown when an item is focused
        """
        
        types = ["supply", "food"]
        
        
        def __init__(self, name="", type=None, price=0, amount=1, info=""):
            
            self.name = name
            self.type = type
            self.price = int(price)
            self.amount = int(amount)
            self.info = info
                        
        
##############################################################################
## Inventory class.

    class Inventory(object):
        
        """
        class that stores items. It has follwing fields:
        currency - amount of money this object has
        tradein - when someone buyoff items to this inventory, price is reduced by this value
        infinite - if true, its currency and amont of items arer infinite, like NPC merchant. 
        items - list of item slots. items slot is a pair of [item, amount]. items are stored as slot, not item.
        selected - selected slot in a current screen.
        """
        
        def __init__(self, currency = 0, tradein = 1.0, infinite = False, items=None):
         
            self.currency = int(currency)
            self.tradein = float(tradein)
            self.infinite = infinite
            self.items = []
            if items:
                for i in items:
                    self.add_item(i)         
            self.selected = None
            
            
        def has_item(self, item):
            #returns True if inventory has this item
            
            return item in [i[0] for i in self.items]
                        
            
        def count_item(self, item):
            # returns sum of amount of this item
            
            return sum([i[1] for i in self.items if i[0] == item])
                                        
                            
        def get_slot(self, item):
            # returns item slot that has a same item
            # None if inventory deosn't have this item. 
            
            if item in self.items:
                return item            
            for i in self.items:
                if i[0] == item:
                    return i                        
            return None
                            
            
        def add_item(self, item, amount = None, merge = True):
            # add an item
            # if amount is given, this amount is used insted of iten't default
            # if merge is True, amount is summed when inventory has same item
                        
            slot = self.get_slot(item)
            amount = amount if amount != None else item.amount
            if slot and merge:
                slot[1] += amount
            else:
                self.items.append([item, amount])
                
            
        def remove_item(self, item):
            # remove an item
            # return true if remove is succeeded
                
            slot = self.get_slot(item)
            if slot:
                self.items.remove(slot)
                return True
                
                                    
        def score_item(self, item, amount, remove = True, add = True):
            # changes amount of item
            # if remove is True, item is removed when amount reaches 0
            # if add is True, an item is added when inventory hasn't this item
            
            slot = self.get_slot(item)
            if slot:
                slot[1] += amount
                if remove and self.slot[1]<=0:
                    self.remove_item(slot)
            elif add:
                self.add_item(self, [item, amount])
                
                
        def buy_item(self, item, amount = None, merge=True):
            # buy an item 
            # return True if trade is succeeded
            
            amount = amount if amount != None else item.amount
            price = item.price*amount
            if self.infinite:
                return True
            elif self.currency >= price:
                self.add_item(item, amount = amount, merge=merge)
                self.currency -= price
                return True
                
                        
        def sell_item(self, slot, buyer, merge=True):
            # remove an item slot then add this item to buyer
            # return True if trade is succeeded
            
            amount = slot[0].amount if self.infinite else slot[1]
            rv = buyer.buy_item(slot[0], amount = amount, merge=merge)
            if rv and not self.infinite:
                price = slot[0].price*amount
                self.currency += int(price*buyer.tradein)
                self.items.remove(slot)
                                                    
                
        def replace_items(self, first, second):
            #swap order of two slots
            
            i1 = self.items.index(first)
            i2 = self.items.index(second)            
            self.items[i1], self.items[i2] = self.items[i2], self.items[i1]   
                        
            
        def sort_items(self, order="name"):            
            # sort slots
            
            if order == "name":
                self.items.sort(key = lambda item: item[0].name)
            if order == "type":
                self.items.sort(key = lambda item: item[0].type)
            if order == "price":
                self.items.sort(key = lambda item: item[0].price, reverse=True)
            if order == "amount":
                self.items.sort(key = lambda item: item[1], reverse=True)
                
                
        def get_all_items(self, namespace=store):
            # get all Item objects define under namespace
            
            for i in dir(namespace):
                if isinstance(getattr(namespace, i), Item):
                    self.add_item(getattr(namespace, i))
                    
                
            
