## This file provides inventory system.
## アイテムの売買や管理を行う機能を追加するファイルです。
## 多少の改変でスキルやクエストなど様々な要素の管理に汎用的に使えます。

##############################################################################
## How to Use
##############################################################################

## まずアイテムオブジェクトを Item(name, type, value, score, cost, stack, info) で定義します。
## name は表示される名前、type はカテゴリー、value は価格です。
## score はアイテムを追加時のデフォルトの個数で、省略すると１になります。
## cost が 1（デフォルト）の場合、アイテム使用時に個数が一つ減ります。
## stack が true（デフォルト）の場合、アイテム追加時に個数が加算されます。
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

default housewife = Inventory(currency=1000)
default merchant = Inventory(tradein=.25, infinite=True, item_types=["supply", "food", "outfit"])


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

                for slot in inv.items:

                    python:
                        obj = inv.get_item(slot[0])
                        amount = slot[1]
                        price = int(obj.value*slot[1]*(buyer.tradein if buyer else inv.tradein))

                    if tab in [obj.type, "all"]:
                        textbutton "[obj.name] x[amount] ([price])":
                            selected inv.selected == slot
                            hovered tt.Action(obj.info)

                            # sell/buy
                            if buyer:
                                action Function(inv.sell_item, slot=slot, buyer=buyer)

                            # reorder after selected
                            elif inv.selected:
                                action [Function(inv.replace_items, first=slot, second=inv.selected),
                                        SetField(inv, "selected", None)]

                            # reorder before selecting
                            else:
                                action SetField(inv, "selected", slot)

                            # This action uses item.
                            # action Function(inv.use_item, slot=slot, target=?)

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

    class Inventory(object):

        """
        Class that stores items. It has following fields:

        currency - score of money this object has
        tradein - when someone buyoff items to this inventory, value is reduced by this value
        infinite - if true, its currency and amont of items are infinite, like NPC merchant.
        item_types - list of item type that are grouped up as tab in the inventory screen.
        items - list of item slots. item slot is a pair of ["item name", score]. items are stored as slot, not item object.
                in this class, variable 'slot' means this pair, 'name' means slot[0], and 'score' mean slot[1].
        selected - selected slot in a current screen.
        """

        # Define default item categories
        _item_types = []

        def __init__(self, currency = 0, tradein = 1.0, infinite = False, item_types=None, items=None):

            self.currency = int(currency)
            self.tradein = float(tradein)
            self.infinite = infinite
            self.item_types = item_types or self._item_types
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


        def get_slot(self, name):
            # returns first slot that has this item

            if name in self.items:
                return name
            for i in self.items:
                if i[0] == name:
                    return i
            return None


        def has_item(self, name):
            # returns True if inventory has this item

            return name in [i[0] for i in self.items]


        def count_item(self, name):
            # returns sum of score of this item

            return sum([i[1] for i in self.items if i[0] == name])


        def add_item(self, name, score = None):
            # add an item
            # if score is given, this score is used instead of item's default value.

            slot = self.get_slot(name)
            score = score or self.get_item(name).score
            if slot and self.get_item(name).stack:
                slot[1] += score
            else:
                self.items.append([name, score])


        def remove_item(self, name):
            # remove an item

            slot = self.get_slot(name)
            if slot:
                self.items.remove(slot)


        def score_item(self, slot, score, remove = True):
            # changes score of item slot
            # if remove is True, item is removed when score reaches 0

            slot = self.get_slot(slot)
            if slot:
                slot[1] += score
                if remove and slot[1]<=0:
                    self.remove_item(slot)


        def buy_item(self, name, score = None):
            # buy an item
            # return True if trade is succeeded

            score = score or self.get_item(name).score
            value = self.get_item(name).value*score
            if self.infinite:
                return True
            elif self.currency >= value:
                self.add_item(name, score)
                self.currency -= value
                return True


        def sell_item(self, slot, buyer, merge=True):
            # remove an item slot then add this item to buyer for money

            slot = self.get_slot(slot)
            name = slot[0]
            score = self.get_item(name).score if self.infinite else slot[1]
            rv = buyer.buy_item(name, score)
            if rv and not self.infinite:
                value = self.get_item(name).value*score
                self.currency += int(value*buyer.tradein)
                self.items.remove(slot)


        def give_item(self, slot, getter):
            # remove an item slot then add this name to getter

            slot = self.get_slot(slot)
            name = slot[0]
            if getter.has_item(name) and self.get_item(name).stack:
                getter.score_item(name, slot[1])
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
                self.items.sort(key = lambda slot: self.get_item(slot[0]).name)
            elif order == "type":
                self.items.sort(key = lambda slot: self.item_types.index(self.get_item(slot[0]).type))
            elif order == "price":
                self.items.sort(key = lambda slot: self.get_item(slot[0]).value, reverse=True)
            elif order == "amount":
                self.items.sort(key = lambda slot: slot[1], reverse=True)


        def get_all_items(self, namespace=store):
            # get all Item objects defined under namespace

            for i in dir(namespace):
                if isinstance(getattr(namespace, i), Item):
                    self.add_item(i)


        def use_item(self, slot, target):
            # uses item slot on target

            slot = self.get_slot(slot)
            name = slot[0]
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
        value - price that is used for trading
        score - default amount of item when it's added into inventory]
        stack - if true, this item raises score insted when same item is added.
        consume - if true, useing this item reduces one score.
        info - description that is shown when an item is focused
        """


        def __init__(self, name="", type="", value=0, score=1, cost=1, stack=True, info=""):

            self.name = name
            self.type = type
            self.value = int(value)
            self.score = int(score)
            self.cost = int(cost)
            self.stack = True if stack else False
            self.info = info


        def use(self, target):

            # write your own code

            return


##############################################################################
## Create namespace

init -999 python in item:
    pass


