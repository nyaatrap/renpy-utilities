## This file provides inventory system.
## このファイルはアイテムの管理や売買を行う機能を追加します。

##############################################################################
## How to Use
##############################################################################

## まずアイテム画面に表示されるアイテムのタイプを定義します。
define gui.item_types = ["supply", "food", "outfit"]

## 次にアイテムオブジェクトを Item(name, type, value, score, info) で定義します。
## name は表示される名前、type はカテゴリー、value は価格です。
## score はアイテムを追加時のデフォルトの個数で、省略すると１になります。
## info はマウスフォーカスした時に表示される情報です。
## item の名前空間を使う事もできます。

define item.apple = Item("Apple", type="food", value=10, info="This is an apple")
define item.orange = Item("Orange", type="food", value=20)
define item.knife = Item("Knife", type="supply", value=50)
define item.dress = Item("Dress", type="outfit", value=100)

## 最後に所持者を Inventory(currency, tradein, infinite, items) で定義します。
## currency は所持金、tradein はその所持者が下取りする時の価格比です。
## infinite を True にすると所持金と在庫が無限になります。
## items は所持アイテムの配列で [[アイテム, 個数], [アイテム, 個数],,,] の形になります。

default housewife = Inventory(currency=1000)
default merchant = Inventory(tradein=.25, infinite=True)


## ゲームがスタートしたら jump sample_inventory でここに飛んでください。

label sample_inventory:

    ## add_item(item, score) でアイテムを追加します。個数を指定する場合は引数 score を使います。
    ## item は item. を外した文字列です。
    $ housewife.add_item("apple", score=2)

    ## get_all_items(namespace) で名前空間で定義したすべてのアイテムを自動的に追加します。
    $ merchant.get_all_items(store.item)

    ## 他に以下のメソッド（）があります。
    ## has_item(item) - 所持していれば True を返します。
    ## count_item(item) - 所持している合計の個数を返します。
    ## remove_item(item) - 所持していれば、そのアイテムを奪います。
    ## score_item(item, score) - 所持している個数を変更します。
    ## buy_item(item, score) - 所持金が足りていれば、それを消費してアイテムを追加します。


    while True:

        ## 次の命令はロールバックをブロックして、ゲームの全ての変化をセーブできるようにします。
        ## （デフォルトでは現在の入力待ちの開始時点のみをセーブするので必要になります。）
        $ block()

        menu:

            ## call screen inventory(inv, buyer, title) でアイテムの一覧を表示します。

            "show inventory":
                ## アイテムを見たり整理したい時は inventory(表示する所持者) を使います。
                ## この状態でアイテムをクリックすると、スロットの入替えモードになります。
                $ block()
                call screen inventory(housewife)

            "buy items":
                ## アイテム買いたい時は inventory(売り手の所持者、買い手の所持者) を使います。
                $ block()
                call screen inventory(merchant, buyer=housewife, title="Buy")

            "sell items":
                ## アイテム売りたい時も inventory(売り手の所持者、買い手の所持者) を使います。
                ## 売買の相手が逆転するだけですが、スクリーンタイトルを変えています。
                $ block()
                call screen inventory(housewife, buyer=merchant, title="Sell")


##############################################################################
## Definitions
##############################################################################
                
init python:    

    def block():
        # blocks rollback then allows saving data in the current interaction
        
        renpy.block_rollback()
        renpy.retain_after_load()
        

##############################################################################
## Inventory Screen

## screen that shows inventory
## inv is an inventory object that has items on the screen
## if buyer is given, it's trade mode.
## otherwise, it's stock mode that can reorder item slots

screen inventory(inv, buyer=None, title="Inventory"):

    # screen variables
    default tab = "all"
    default tt = Tooltip("")

    # unselect item on show
    on "show" action SetField(inv, "selected", None)

    vbox:
        # screen title
        label title text_size gui.title_text_size

        # currency. when seller (inv) is an infinite inventory, show buyer's currency
        $ currency = inv.currency if not inv.infinite else buyer.currency
        text "currency: [currency:>6]" xalign .5
        
        null height 20
        
        # sort buttons
        text "Sort by"
        for i in ["name", "type", "value", "score"]:
            textbutton i.capitalize():
                action Function(inv.sort_items, order=i)

    vbox align .5,.5:

        # category tabs
        hbox style_prefix "radio":

            for i in ["all"] + gui.item_types:
                textbutton i.capitalize():
                    action SetScreenVariable("tab", i)

        # item slots
        frame xysize 800, 400:

            vpgrid style_prefix "item":
                cols 4 mousewheel True draggable True scrollbars "vertical"

                for slot in inv.items:

                    python:
                        item = slot[0]
                        score = slot[1]
                        obj = inv.get_item(item)
                        value = int(obj.value*slot[1]*(buyer.tradein if buyer else inv.tradein))

                    if tab in [obj.type, "all"]:
                        textbutton "[obj.name] x[score] ([value])":
                            selected inv.selected == slot
                            hovered tt.Action(obj.info)

                            # sell/buy
                            if buyer:
                                action Function(inv.sell_item, slot=slot, buyer=buyer)

                            # reorder after selected
                            elif inv.selected:
                                action [Function(inv.replace_items, first=slot, second=inv.selected), SetField(inv, "selected", None)]

                            # reorder before selecting
                            else:
                                action SetField(inv, "selected", slot)

        # information window
        frame xysize 800, 150:
            text tt.value

    textbutton "Return" action Return() yalign 1.0

    key "game_menu" action [SetField(inv, "selected", None) if inv.selected else Return()]


style item_button:
    xsize 200


##############################################################################
## Item class.

init -3 python:

    class Item(object):

        """
        Class that represents item that is stored by inventory object. It has following fields:
        
        name - item name that is shown on the screen
        type - item category
        value - score of currency for trading
        score - default score of item when it's added into inventory
        info - description that is shown when an item is focused
        """


        def __init__(self, name="", type=None, value=0, score=1, info=""):

            self.name = name
            self.type = type
            self.value = int(value)
            self.score = int(score)
            self.info = info            
            

        def use(self, target):
            
            # write your own code
            
            return            
            

##############################################################################
## Inventory class.

    class Inventory(object):

        """
        Class that stores items. It has following fields:
        
        currency - score of money this object has
        tradein - when someone buyoff items to this inventory, value is reduced by this value
        infinite - if true, its currency and amont of items are infinite, like NPC merchant.
        items - list of item slots. item slot is a pair of ["item name", score]. items are stored as slot, not item object. 
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
            

        @classmethod
        def get_item(self, name):
            # returns item object from name

            if isinstance(name, Item): return name
            elif name in dir(store.item): return getattr(store.item, name)
            elif name in dir(store): return getattr(store, name)


        def get_slot(self, item):
            # returns first slot that has a same item
            # None if inventory deosn't have this item.

            if item in self.items:
                return item
            for i in self.items:
                if i[0] == item:
                    return i
            return None


        def has_item(self, item):
            # returns True if inventory has this item

            return item in [i[0] for i in self.items]


        def count_item(self, item):
            # returns sum of score of this item

            return sum([i[1] for i in self.items if i[0] == item])


        def add_item(self, item, score = None, merge = True):
            # add an item
            # if score is given, this score is used insted of item's default value.
            # if merge is True, score is summed when inventory has same item

            slot = self.get_slot(item)
            score = score or self.get_item(item).score
            if slot and merge:
                slot[1] += score
            else:
                self.items.append([item, score])


        def remove_item(self, item):
            # remove an item

            slot = self.get_slot(item)
            if slot:
                self.items.remove(slot)


        def score_item(self, item, score, remove = True, add = True):
            # changes score of item
            # if remove is True, item is removed when score reaches 0
            # if add is True, an item is added when inventory hasn't this item

            slot = self.get_slot(item)
            if slot:
                slot[1] += score
                if remove and self.slot[1]<=0:
                    self.remove_item(slot)
            elif add:
                self.add_item(self, [item, score])
            
            
        def use_item(self, item, target):
            # uses item on target
            
            self.get_item(item).use(target)


        def buy_item(self, item, score = None, merge=True):
            # buy an item
            # return True if trade is succeeded

            score = score or self.get_item(item).score
            value = self.get_item(item).value*score
            if self.infinite:
                return True
            elif self.currency >= value:
                self.add_item(item, score, merge)
                self.currency -= value
                return True


        def sell_item(self, slot, buyer, merge=True):
            # remove an item slot then add this item to buyer for money

            score = self.get_item(slot[0]).score if self.infinite else slot[1]
            rv = buyer.buy_item(slot[0], score, merge)
            if rv and not self.infinite:
                value = self.get_item(slot[0]).value*score
                self.currency += int(value*buyer.tradein)
                self.items.remove(slot)
                
                
        def give_item(self, slot, getter, merge=True):
            # remove an item slot then add this item to getter
            
            if merge and getter.has_item(slot[0]):
                getter.score_item(slot[0], slot[1])
            else:
                getter.items.append(slot)
            self.items.remove(slot)            


        def replace_items(self, first, second):
            # swap order of two slots

            i1 = self.items.index(first)
            i2 = self.items.index(second)
            self.items[i1], self.items[i2] = self.items[i2], self.items[i1]


        def sort_items(self, order="name"):
            # sort slots            

            if order == "name":
                self.items.sort(key = lambda item: self.get_item(item[0]).name)
            elif order == "type":
                self.items.sort(key = lambda item: gui.item_types.index(self.get_item(item[0]).type))
            elif order == "value":
                self.items.sort(key = lambda item: self.get_item(item[0]).value, reverse=True)
            elif order == "score":
                self.items.sort(key = lambda item: self.get_item(item[1]), reverse=True)


        def get_all_items(self, namespace=store):
            # get all Item objects defined under namespace

            for i in dir(namespace):
                if isinstance(getattr(namespace, i), Item):
                    self.add_item(i)



##############################################################################
## Create namespace

init -999 python in item:
    pass


