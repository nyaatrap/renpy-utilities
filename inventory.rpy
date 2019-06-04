## This file provides inventory system.
## アイテムの売買や管理を行う機能を追加するファイルです。
## スキルやクエストなど様々な要素の管理にも汎用的に使えます。

##############################################################################
## How to Use
##############################################################################

## まず最初に、管理するアイテムのタイプのリストを作成します。
define item_types = ["supply", "food", "outfit"]

## それから各アイテムを Item(name, type, value, score, max_score, cost, order, prereqs, info) で定義します。
## name は表示される名前、type はカテゴリー、value は価格です。
## score はアイテムを追加時のデフォルトの個数で、省略すると１になります。
## max_score は所持できるアイテムの最大数で、省略すると無限大になります(=0)。
## cost が 1（デフォルト）の場合、アイテム使用時に個数が一つ減ります。
## order はデフォルトのソート順を決めたい時に使います。
## prereqs はそのアイテムを購入するときに消費するアイテムです。
## info はマウスフォーカスした時に表示される情報です。
## inventory に与える namespace の名前空間で定義する必要があります。

define item.apple = Item("Apple", type="food", value=10, info="apple")
define item.orange = Item("Orange", type="food", value=20, info="orange")
define item.knife = Item("Knife", type="supply", value=50, info="knife")
define item.dress = Item("Dress", type="outfit", value=100, info="dress")
define item.juice = Item("Juice", type="food", value=30, prereqs="orange:1, apple:2", info="It requires two oranges and one apple")

## 最後にアイテムの管理者を Inventory(currency, item_types, namespace, tradein, infinite, recharge, removable, items) で定義します。
## currency は所持金です。
## item_types は上で定義したアイテムタイプのリストで、アイテム画面でのカテゴリー分けに使用します。
## カテゴリーに合わないタイプのアイテムも入手可能ですが、画面には表示されません。
## namespace を設定すると、その管理者が扱うアイテムを名前空間ごとに分けることが出来ます。
## tradein はその所持者が下取りする時の価格比です。
## infinite を True にすると所持金が無限になります。
## recharge を True にすると、常に在庫が補充されます。
## removable を False にすると、在庫がゼロになってもアイテム覧から消去されません。

default housewife = Inventory(currency=1000, item_types = item_types, namespace = "item")
default merchant = Inventory(item_types = item_types, namespace = "item", tradein=.25, infinite=True, recharge=True, removable=False)


## ゲームがスタートしたら jump sample_inventory でここに飛んでください。

label sample_inventory:

    ## add_item(item, score) でアイテムを追加します。個数を指定する場合は引数 score を使います。
    ## item は item. を外した文字列です。
    $ housewife.add_item("apple", score=2)

    ## get_all_items(types) で名前空間で定義したすべてのアイテムのうち、タイプが合致するものを自動的に追加します。
    $ merchant.get_all_items()

    ## 他に以下のメソッドがあります。
    ## has_item(item) - 所持していれば True を返します。
    ## count_item(item) - 所持している合計の個数を返します。
    ## charge_item(item) - 所持しているアイテムを最大数までチャージします。
    ## charge_all_items() - 所持しているすべてのアイテムを最大数までチャージします。
    ## add_items(items, score) - "a,b,c" のように複数のアイテム名与えると、その全てのアイテムを追加できます。
    ## remove_item(item) - 所持していれば、そのアイテムを消去します。
    ## remove_items(items) - "a,b,c" のように複数のアイテム名与えると、所持していれば、そのアイテムを消去します。
    ## score_item(item, score) - 所持している個数を変更します。
    ## buy_item(item, score) - 所持金と要求アイテムが足りていれば、それを消費してアイテムを追加します。
    ## can_buy_item(item, score) - アイテムが購入可能かどうか調べます。
    ## sell_item(item, buyer, score) - アイテムを buyer に売却し、所持金を受け取ります。
    ## give_item(item, getter, score) - アイテムを getter に渡します。
    ## use_item(item, target, cost="cost") - アイテムを target に使用します。効果は各アイテムごと定義してください。
    ## can_use_item(item, target, cost="cost") - アイテムが使用可能かどうか調べます。アイテムごとに定義してください。
    ## get_items(types, score) - score 以上で types に含まれるアイテムのリストを (name, score, obj) のタプルで返します。


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

            "return":
                $ renpy.full_restart()


##############################################################################
## Definitions
##############################################################################

init python:

    def block():
        # blocks rollback then allows saving data in the current interaction

        config.skipping = None
        renpy.checkpoint()
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

    if title=="Buy":
        default confirm_message = "Are you sure to buy it?"
    else:
        default confirm_message = "Are you sure to sell it?"

    default notify_message = "You don't have money or required items"

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

        null height 60

        # sort buttons
        text "Sort by"
        for i in ["name", "type", "value", "amount", "order"]:
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
                cols 2 mousewheel True draggable True scrollbars "vertical"

                for name, score, obj in inv.get_items(types=[tab] if tab != "all" else inv.item_types):

                    $ price = int(obj.value*score*(buyer.tradein if buyer else inv.tradein))

                    textbutton "[obj.name] x[score] ([price])":
                        selected inv.selected == name
                        tooltip obj.info

                        # Sell/buy mode
                        if buyer:
                            if buyer.can_buy_item(name):
                                action Confirm(confirm_message, Function(inv.sell_item, name=name, buyer=buyer))
                            else:
                                action Notify(notify_message)

                        # Arrange mode
                        else:

                            # reorder after selected
                            if inv.selected:
                                action [Function(inv.replace_items, first=name, second=inv.selected),
                                        SetField(inv, "selected", None)]

                            # reorder before selecting
                            else:
                                action SetField(inv, "selected", name)

                            # This action uses item.
                            # action Function(inv.use_item, name=name, target=?)

        null height 10

        # information window
        frame xysize width, height//3:
            $ tooltip = GetTooltip() or ""
            text [tooltip]

    textbutton "Return" action Return() yalign 1.0

    key "game_menu" action [SetField(inv, "selected", None) if inv.selected else Return()]


style item_button:
    xsize 250


##############################################################################
## Inventory class.

init -10 python:

    from collections import OrderedDict

    class Inventory(object):

        """
        Class that stores items. It has following fields:

        currency - score of money this object has.
        item_types - list of item type that are grouped up as tab in the inventory screen.
        namespace - if given, items defined in this name space are used
        tradein - when someone buyoff items to this inventory, value is reduced by this value
        infinite - if True, currency is infinite.
        recharge - if True, an item score is charged at max_score (or 1) when its score is changed
        removable = if False, an item is not removed when score reached at 0.
        items - ordered dictionary of {"item name": score}.
        selected - selected slot in a current screen.
        """


        def __init__(self, currency = 0, item_types= None, namespace=None, tradein = 1.0, infinite = False, recharge=False, removable = True, items=None):

            self.currency = int(currency)
            self.item_types = item_types or []
            self.namespace = getattr(store, namespace) if namespace else store
            self.tradein = float(tradein)
            self.infinite = infinite
            self.recharge = recharge
            self.removable = removable
            self.items = OrderedDict()
            if items:
                self.add_items(items)
            self.selected = None


        def get_item(self, name):
            # returns item object from name

            if isinstance(name, Item):
                return name

            elif isinstance(name, basestring):
                obj = getattr(self.namespace, name, None)
                if obj:
                    return obj

            raise Exception("Item '{}' is not defined".format(name))


        def has_item(self, name, score=None):
            # returns True if inventory has this item whose score is higher than given.

            # check valid name or not
            self.get_item(name)

            return name in [k for k, v in self.items.items() if score==None or v >= score]


        def has_items(self, name, score=None):
            # returns True if inventory has these items whose score is higher than give.
            # "a, b, c" means a and b and c, "a | b | c" means a or b or c.

            separator = "|" if name.count("|") else ","
            names = name.split(separator)
            for i in names:
                i = i.strip()
                if separator == "|" and self.has_item(i, score):
                    return True
                elif separator == "," and not self.has_item(i, score):
                    return False

            return True if separator == ","  else False


        def count_item(self, name):
            # returns score of this item

            if self.has_item(name):
                return self.items[name]


        def get_items(self, types = None, score=None, rv=None):
            # returns list of (name, score, object) tuple in conditions
            # if rv is "name" or "obj", it returns them.

            items = [k for k, v in self.items.items() if score==None or v >= score]

            types = types or self.item_types
            items = [i for i in items if self.get_item(i).type in types]

            if rv == "name":
                return items

            elif rv == "obj":
                return [self.get_item(i) for i in items]

            return  [(i, self.items[i], self.get_item(i)) for i in items]


        def charge_item(self, name):
            # changes score of name to its maximum value

            if self.has_item(name):
                self.items[name] = max(self.get_item(name).max_score, 1)


        def charge_all_items(self):
            # charges all items in self.items.

            for i in self.items.keys():
                self.charge_item(i)


        def add_item(self, name, score = None):
            # add an item
            # if score is given, this score is used instead of item's default value.

            score = score or self.get_item(name).score
            max_score = self.get_item(name).max_score

            if self.has_item(name):
                self.items[name] += score
            else:
                self.items[name] = score

            if max_score > 0:
                self.items[name] = min(self.items[name], max_score)

            if self.recharge:
                self.charge_item(name)


        def add_items(self, items, score=None):
            # add items

            for i in items.split(","):
                i = i.strip()
                score = score or self.get_item(i).score
                self.add_item(i, score=score)


        def remove_item(self, name):
            # remove an item

            if self.has_item(name):
                del self.items[name]


        def remove_items(self, items):
            # remove items

            for i in items.split(","):
                i = i.strip()
                self.remove_item(i)


        def score_item(self, name, score):
            # changes score of name

            self.add_item(name, score)
            if self.removable and self.items[name] <= 0:
                self.remove_item(name)


        def buy_item(self, name, score = None, prereqs=True):
            # buy an item
            # if prereqs is True, it requires items listed in prereqs

            score = score or self.get_item(name).score
            value = self.get_item(name).value*score
            prereqs = self.get_item(name).prereqs

            if self.infinite or self.currency >= value:

                if prereqs:
                    for k,v in prereqs.items():
                        if not self.has_item(k, score=v*score):
                            break
                    else:
                        self.add_item(name, score)
                        for k,v in prereqs.items():
                            self.score_item(k, score=-v*score)
                        if not self.infinite:
                            self.currency -= value

                else:
                    self.add_item(name, score)
                    if not self.infinite:
                        self.currency -= value


        def can_buy_item(self, name, score = None, prereqs=True):
            # returns True if this item can be bought

            score = score or self.get_item(name).score
            value = self.get_item(name).value*score
            prereqs = self.get_item(name).prereqs

            if self.infinite:
                return True

            if self.currency < value:
                return False

            if prereqs:
                for k,v in prereqs.items():
                    if not self.has_item(k, score=v*score):
                        return False

            return True


        def sell_item(self, name, buyer, score = None, prereqs=True):
            # remove an item then add this item to buyer for money

            if self.has_item(name):

                score = score or self.get_item(name).score
                value = self.get_item(name).value*score

                buyer.buy_item(name, score, prereqs)

                if buyer.infinite or buyer.currency >= value:
                    self.score_item(name, score=-score)
                    if not self.infinite:
                        self.currency += int(value*buyer.tradein)


        def give_item(self, name, getter, score=None):
            # remove an item slot then add this name to getter

            score = score or self.get_item(name).score

            if self.has_item(name, score):

                getter.score_item(name, score)
                self.score_item(name, -score)


        def replace_items(self, first, second):
            # swap order of two slots

            keys = list(self.items.keys())
            values = list(self.items.values())
            i1 = keys.index(first)
            i2 = keys.index(second)
            keys[i1], keys[i2] = keys[i2], keys[i1]
            values[i1], values[i2] = values[i2], values[i1]

            self.items = OrderedDict(zip(keys, values))


        def sort_items(self, order="order"):
            # sort slots

            items = self.items.items()

            if order == "name":
                items.sort(key = lambda i: self.get_item(i[0]).name)
            elif order == "type":
                items.sort(key = lambda i: self.item_types.index(self.get_item(i[0]).type))
            elif order == "value":
                items.sort(key = lambda i: self.get_item(i[0]).value, reverse=True)
            elif order == "amount":
                items.sort(key = lambda i: i[1], reverse=True)
            elif order == "order":
                items.sort(key = lambda i: self.get_item(i[0]).order)

            self.items = OrderedDict(items)


        def get_all_items(self, types=None, charge=True, sort="order"):
            # get all Item objects defined under namespace

            types = types or self.item_types

            for i in dir(self.namespace):
                if isinstance(getattr(self.namespace, i), Item):
                    if self.get_item(i).type in types:
                        self.add_item(i)
                        if charge:
                            self.charge_item(i)

            self.sort_items(order=sort)


        def use_item(self, name, target=None, cost="cost"):
            # uses item on target

            obj = self.get_item(name)

            obj.use(target)

            if cost=="cost" and obj.cost:
                self.score_item(name, -obj.cost)

            elif cost=="value" and obj.value and not self.infinite:
                self.currency -= value


        def can_use_item(self, name, target=None, cost="cost"):
            # returns True if inv can use this item

            obj = self.get_item(name)

            if cost=="cost" and self.count_item(name) > obj.cost:
                return True
            elif cost=="value" and (self.currency > obj.value or self.infinite):
                return True
            return False


##############################################################################
## Item class.

    class Item(object):

        """
        Class that represents item that is stored by inventory object. It has following fields:

        name - item name that is shown on the screen
        type - item category
        value - price that is used for trading
        score - default amount of item when it's added into inventory
        max_score - maximum score. Score higher than this is ignored. 0 is infinite.
        cost - if not zero, using this item reduces score.
        order - if integer is given, item can be sorted by this number.
        prereqs - required items to buy. This should be given in strings like "itemA:1, itemB:2"
        info - description that is shown when an item is focused
        """


        def __init__(self, name="", type="", value=0, score=1, max_score = 0, cost=1, order=0, prereqs=None, info="", **kwargs):

            self.name = name
            self.type = type
            self.value = int(value)
            self.score = int(score)
            self.max_score = int(max_score)
            self.cost = int(cost)
            self.order = int(order)

            self.prereqs = {}
            if prereqs:
                for i in [x.split(":") for x in prereqs.split(",")]:
                    self.prereqs.setdefault(i[0].strip(), int(i[1]))
            self.info = info

            for i in kwargs.keys():
                setattr(self, i, kwargs[i])


        def use(self, target=None):

            # if self.keyword == xxx:
            #   do something

            return

