## This file provides inventory system.
## このファイルはアイテムの管理や売買を行う機能を追加します。

##############################################################################
## How to Use
##############################################################################

## まずアイテム画面に表示されるアイテムのタイプを定義します。
define gui.item_types = ["supply", "food", "outfit"]

## 次にアイテムオブジェクトを Item(name, type, price, amount, info) で定義します。
## name は表示される名前、type はカテゴリー、price は価格です。
## amount はアイテムを追加時のデフォルトの個数で、省略すると１になります。
## info はマウスフォーカスした時に表示される情報です。
## 他の変数と衝突しないように item の名前空間を使うといいでしょう。

define item.apple = Item("Apple", type="food", price=10, info="This is an apple")
define item.orange = Item("Orange", type="food", price=20)
define item.knife = Item("Knife", type="supply", price=50)
define item.dress = Item("Dress", type="outfit", price=100)

## 最後に所持者を Inventory(currency, tradein, infinite, items) で定義します。
## currency は所持金、tradein はその所持者が下取りする時の価格比です。
## infinite を True にすると所持金と在庫が無限になります。
## items は所持アイテムの配列で [[アイテム, 個数], [アイテム, 個数],,,] の形になります。

default housewife = Inventory(currency=1000)
default merchant = Inventory(tradein=.25, infinite=True)


## ゲームがスタートしたら、jump inventory でここに飛んでください。

label inventory:

    ## add_item(item, amount) でアイテムを追加します。個数を指定する場合は引数 amount を使います。
    $ housewife.add_item(item.apple, amount=2)
    ## ""で囲んだ文字列でも追加できます。その場合は item. を外すことができます。
    $ housewife.add_item("orange")

    ## get_all_items(namespace) で名前空間で定義したすべてのアイテムを自動的に追加します。
    $ merchant.get_all_items(store.item)

    ## 他に以下のメソッド（）があります。
    ## has_item(item) - 所持していれば True を返します。
    ## count_item(item) - 所持している合計の個数を返します。
    ## remove_item(item) - 所持していれば、そのアイテムを奪います。
    ## score_item(item, amount) - 所持している個数を変更します。
    ## buy_item(item, amount) - 所持金が足りていれば、それを消費してアイテムを追加します。


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
        for i in ["name", "type", "price", "amount"]:
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
                        amount = slot[1]
                        price = int(slot[0].price*slot[1]*(buyer.tradein if buyer else inv.tradein))

                    if tab in [item.type, "all"]:
                        textbutton "[item.name] x[amount] ([price])":
                            selected inv.selected == slot
                            hovered tt.Action(item.info)

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
        Class that represents item that is stored by party object. It has follwing fields:
        
        name - item name that is shown on the screen
        type - item category
        price - amount of currency for trading
        amount - default amount of item when it's added into inventory
        info - description that is shown when an item is focused
        """


        def __init__(self, name="", type=None, price=0, amount=1, info=""):

            self.name = name
            self.type = type
            self.price = int(price)
            self.amount = int(amount)
            self.info = info


        @staticmethod
        def get(name):
            # make string into item object

            if isinstance(name, Item):
                return name
            try:
                return getattr(store.item, name)
            except AttributeError:
                return getattr(store, name)


##############################################################################
## Inventory class.

    class Inventory(object):

        """
        Class that stores items. It has follwing fields:
        
        currency - amount of money this object has
        tradein - when someone buyoff items to this inventory, price is reduced by this value
        infinite - if true, its currency and amont of items are infinite, like NPC merchant.
        items - list of item slots. item slot is a pair of [item, amount]. items are stored as slot, not item.
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
            # returns True if inventory has this item

            item = Item.get(item)
            return item in [i[0] for i in self.items]


        def count_item(self, item):
            # returns sum of amount of this item

            item = Item.get(item)
            return sum([i[1] for i in self.items if i[0] == item])


        def get_slot(self, item):
            # returns item slot that has a same item
            # None if inventory deosn't have this item.

            item = Item.get(item)
            if item in self.items:
                return item
            for i in self.items:
                if i[0] == item:
                    return i
            return None


        def add_item(self, item, amount = None, merge = True):
            # add an item
            # if amount is given, this amount is used insted of item's default value.
            # if merge is True, amount is summed when inventory has same item

            item = Item.get(item)
            slot = self.get_slot(item)
            amount = amount if amount != None else item.amount
            if slot and merge:
                slot[1] += amount
            else:
                self.items.append([item, amount])


        def remove_item(self, item):
            # remove an item

            item = Item.get(item)
            slot = self.get_slot(item)
            if slot:
                self.items.remove(slot)


        def score_item(self, item, amount, remove = True, add = True):
            # changes amount of item
            # if remove is True, item is removed when amount reaches 0
            # if add is True, an item is added when inventory hasn't this item

            item = Item.get(item)
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

            item = Item.get(item)
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

            amount = slot[0].amount if self.infinite else slot[1]
            rv = buyer.buy_item(slot[0], amount = amount, merge=merge)
            if rv and not self.infinite:
                price = slot[0].price*amount
                self.currency += int(price*buyer.tradein)
                self.items.remove(slot)


        def replace_items(self, first, second):
            # swap order of two slots

            i1 = self.items.index(first)
            i2 = self.items.index(second)
            self.items[i1], self.items[i2] = self.items[i2], self.items[i1]


        def sort_items(self, order="name"):
            # sort slots

            if order == "name":
                self.items.sort(key = lambda item: item[0].name)
            elif order == "type":
                self.items.sort(key = lambda item: gui.item_types.index(item[0].type))
            elif order == "price":
                self.items.sort(key = lambda item: item[0].price, reverse=True)
            elif order == "amount":
                self.items.sort(key = lambda item: item[1], reverse=True)


        def get_all_items(self, namespace=store):
            # get all Item objects defined under namespace

            for i in dir(namespace):
                if isinstance(getattr(namespace, i), Item):
                    self.add_item(getattr(namespace, i))



##############################################################################
## Create namespace

init -999 python in item:
    pass


