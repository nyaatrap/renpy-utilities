## This file provides inventory system.
## アイテムの売買や管理を行う機能を追加するファイルです。
## 多少の改変でスキルやクエストなど様々な要素の管理に汎用的に使えます。

##############################################################################
## How to Use
##############################################################################

## まずアイテムオブジェクトを Item(name, type, value, score, cost, info) で定義します。
## name は表示される名前、type はカテゴリー、value は価格です。
## score はアイテムを追加時のデフォルトの個数で、省略すると１になります。
## cost が 1（デフォルト）の場合、アイテム使用時に個数が一つ減ります。
## info はマウスフォーカスした時に表示される情報です。
## item の名前空間を使う事もできます。

define item.apple = Item("Apple", type="food", value=10, info="This is an apple")
define item.orange = Item("Orange", type="food", value=20)
define item.knife = Item("Knife", type="supply", value=50)
define item.dress = Item("Dress", type="outfit", value=100)

## それから所持者を Inventory(currency, tradein, infinite, item_types, items) で定義します。
## currency は所持金、tradein はその所持者が下取りする時の価格比です。
## infinite を True にすると所持金と在庫が無限になります。
## item_types はアイテム画面でカテゴリー分けされるアイテムタイプのリストです。
## items は所持アイテムの配列で [[アイテム, 個数], [アイテム, 個数],,,] の形になります。

define item_types = ["supply", "food", "outfit"]
default housewife = Inventory(currency=1000, item_types = item_types)
default merchant = Inventory(tradein=.25, infinite=True, item_types = item_types)


## ゲームがスタートしたら jump sample_inventory でここに飛んでください。

label sample_inventory:

    ## add_item(item, score) でアイテムを追加します。個数を指定する場合は引数 score を使います。
    ## item は item. を外した文字列です。
    $ housewife.add_item("apple", score=2)

    ## get_all_items(namespace) で名前空間で定義したすべてのアイテムを自動的に追加します。
    $ merchant.get_all_items(store.item)

    ## 他に以下のメソッドがあります。
    ## has_item(item) - 所持していれば True を返します。
    ## count_item(item) - 所持している合計の個数を返します。
    ## remove_item(item) - 所持していれば、そのアイテムを奪います。
    ## score_item(item, score) - 所持している個数を変更します。
    ## buy_item(item, score) - 所持金が足りていれば、それを消費してアイテムを追加します。
    ## sell_item(item, buyer) - アイテムを buyer に売却し、所持金を受け取ります。
    ## give_item(item, getter) - アイテムを getter に渡します。
    ## use_item(item, target) - アイテムを target に使用します。効果は各アイテムごと定義してください。


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

    # frame size
    python:
        width = config.screen_width*3//4
        height = config.screen_height//2

    # unselect item on show
    on "show" action SetField(inv, "selected", None)

    vbox:
        # screen title
        label title text_size gui.title_text_size

        # currency. when seller (inv) is an infinite inventory, show buyer's currency
        $ currency = inv.currency if not inv.infinite else buyer.currency
        text "Currency:[currency:>5]" xalign .5

        null height 20

        # sort buttons
        text "Sort by"
        for i in ["name", "type", "price", "amount"]:
            textbutton i.capitalize():
                action Function(inv.sort_items, order=i)

    vbox align .5,.6:

        # category tabs
        hbox style_prefix "radio":

            for i in ["all"] + inv.item_types:
                textbutton i.capitalize():
                    action SetScreenVariable("tab", i)

        # item slots
        frame xysize width, height:

            vpgrid style_prefix "item":
                cols 4 mousewheel True draggable True scrollbars "vertical"

                for i, v in inv.items.items():
                        
                    $ obj = inv.get_item(i)
                    $ price = int(obj.value*v*(buyer.tradein if buyer else inv.tradein))

                    if tab in [obj.type, "all"]:
                        
                        textbutton "[obj.name] x[v] ([price])":
                            selected inv.selected == i
                            hovered tt.Action(obj.info)

                            # sell/buy
                            if buyer:
                                action Function(inv.sell_item, name=i, buyer=buyer)

                            # reorder after selected
                            elif inv.selected:
                                action [Function(inv.replace_items, first=i, second=inv.selected),
                                        SetField(inv, "selected", None)]

                            # reorder before selecting
                            else:
                                action SetField(inv, "selected", i)

                            # This action uses item.
                            # action Function(inv.use_item, name=i, target=?)

        # information window
        frame xysize width, height//2:
            text tt.value

    textbutton "Return" action Return() yalign 1.0

    key "game_menu" action [SetField(inv, "selected", None) if inv.selected else Return()]


style item_button:
    xsize 250


##############################################################################
## Inventory class.

init -3 python:
    
    from collections import OrderedDict

    class Inventory(object):

        """
        Class that stores items. It has following fields:

        currency - score of money this object has
        tradein - when someone buyoff items to this inventory, value is reduced by this value
        infinite - if true, its currency and amont of items are infinite, like NPC merchant.
        item_types - list of item type that are grouped up as tab in the inventory screen.
        items - dictionary of {"item name": score}.
        selected - selected slot in a current screen.
        """

        # Define default item categories
        _item_types = []

        def __init__(self, currency = 0, tradein = 1.0, infinite = False, item_types=None, items=None):

            self.currency = int(currency)
            self.tradein = float(tradein)
            self.infinite = infinite
            self.item_types = item_types or self._item_types
            self.items = OrderedDict()
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
            else: raise Exception("Item '{}' is not defined".format(name))
            
            
        def get_items(self, types = None, check_score=False):
            # returns list of item objects
            # if types is given it only returns in this types
            
            items = [self.get_item(k) for k, v in self.items.items() if not check_score or v > 0]
            
            return items if not type else  [i for i in items if i.type in types] 
            

        def has_item(self, name, check_score=False):
            # returns True if inventory has this item
            
            # check valid name or not
            self.get_item(name)

            return name in [k for k, v in self.items.items() if not check_score or v > 0]


        def count_item(self, name):
            # returns sum of score of this item
            
            if self.has_item(name):
                return self.items[name]


        def add_item(self, name, score = None):
            # add an item
            # if score is given, this score is used instead of item's default value.
            
            score = score or self.get_item(name).score

            if self.has_item(name):
                self.items[name] += score
            else:
                self.items[name] = score


        def remove_item(self, name):
            # remove an item

            if self.has_item(name):
                del self.items[name]


        def score_item(self, name, score, remove = True):
            # changes score of name
            # if remove is True, item is removed when score reaches 0

            self.add_item(name, score)
            if remove and self.items[name] <= 0:
                self.remove_item(name)  


        def buy_item(self, name, score = None):
            # buy an item

            score = score or self.get_item(name).score
            value = self.get_item(name).value*score
            
            if not self.infinite and self.currency >= value:
                self.add_item(name, score)
                self.currency -= value


        def sell_item(self, name, buyer):
            # remove an item then add this item to buyer for money
            
            if self.has_item(name):

                score = self.get_item(name).score if self.infinite else self.items[name]
                value = self.get_item(name).value*score
                
                buyer.buy_item(name, score)
                
                if buyer.infinite or buyer.currency >= value:
                    if not self.infinite:
                        self.currency += int(value*buyer.tradein)
                        self.remove_item(name)


        def give_item(self, name, getter):
            # remove an item slot then add this name to getter

            if self.has_item(name):
                
                getter.add_items(name)
                self.remove_items(name)


        def replace_items(self, first, second):
            # swap order of two slots

            keys = list(self.items.keys())
            values = list(self.items.values())
            i1 = keys.index(first)
            i2 = keys.index(second)
            keys[i1], keys[i2] = keys[i2], keys[i1]
            values[i1], values[i2] = values[i2], values[i1]
            
            self.items = OrderedDict(zip(keys, values))


        def sort_items(self, order="name"):
            # sort slots
            
            items = self.items.items()

            if order == "name":
                items.sort(key = lambda i: self.get_item(i[0]).name)
            elif order == "type":
                items.sort(key = lambda i: self.item_types.index(self.get_item(i[0]).type))
            elif order == "price":
                items.sort(key = lambda i: self.get_item(i[0]).value, reverse=True)
            elif order == "amount":
                items.sort(key = lambda i: i[1], reverse=True)
                
            self.items = OrderedDict(items)


        def get_all_items(self, namespace=store):
            # get all Item objects defined under namespace

            for i in dir(namespace):
                if isinstance(getattr(namespace, i), Item):
                    self.add_item(i)


        def use_item(self, name, target):
            # uses item on target

            obj = self.get_item(name)
            
            obj.use(target)
            
            if obj.cost:
                self.score_item(slot, -obj.cost)


##############################################################################
## Item class.

    class Item(object):

        """
        Class that represents item that is stored by inventory object. It has following fields:

        name - item name that is shown on the screen
        type - item category
        effect - effect on use.
        value - price that is used for trading
        score - default amount of item when it's added into inventory
        cost - if not zero, useing this item reduces score.
        info - description that is shown when an item is focused
        """


        def __init__(self, name="", type="", effect="", value=0, score=1, cost=1, info=""):

            self.name = name
            self.type = type
            self.effect = effect
            self.value = int(value)
            self.score = int(score)
            self.cost = int(cost)
            self.info = info


        def use(self, target):

            # if self.effect == xxx:
            #   do something

            return


##############################################################################
## Create namespace

init -999 python in item:
    pass


