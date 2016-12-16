## This file provides layered sprites for dressup games
## このファイルは、ドレスアップゲームに使える多層レイヤーのスプライト（立ち絵）を提供します。

##############################################################################
## How to Use
##############################################################################

##############################################################################
## 基本

## 事前に以下のような構成のフォルダーを用意しておきます。

## name
##  ├base
##  │ └base.png
##  └face
##      └happy.png
##      └angry.png


## それからドールオブジェクトを Doll(フォルダー名、各レイヤーのフォルダー名のリスト、デフォルトの画像)
## の形で定義します。各レイヤーの状態を保存できるように、default を使います。
## layers のパラメーターを省略すると ["base", "feet", "bottom", "top", "face"] がデフォルトで使われます。
## デフォルトの画像は、フォルダー名="ファイル名（拡張子なし）"で指定します。これも省略可能です。
default erin = Doll("images/erin", layers=["base", "face"], base="base", face="happy")

## 次に、さきほど定義したドールオブジェクトを""で囲み LayeredDisplayable に渡して画像を定義します。
image erin = LayeredDisplayable("erin")

## 以上で準備完了です。


## ゲームがスタートしたら jump sample_doll でここに飛んでください。

label sample_doll:
    ## ゲームがスタートしたら、 イメージで定義した画像を表示します。
    show erin
    pause

    ## 表示した画像は $ doll.layer = "filename" の形で、各レイヤーの画像を切り変えることができます。
    ## 下の例では face レイヤーの画像を "angry.png" に変更します。
    $ erin.face = "angry"
    pause

    return


##############################################################################
## 応用

## inventory からアイテムを受け取って装備することで、レイヤーを切り替えることもできます。
## この機能を使うためには inventory.rpy が必要です。

## まずドールオブジェクトを Doll(フォルダー名、 レイヤーのリスト、装備タイプのリスト、デフォルトの画像)
## で定義します。装備タイプはレイヤー名を使う必要があります。
default erin2 = Doll("images/erin", layers=["base", "bottom", "top", "face"], types = ["bottom", "top"], base="base", face="happy")
image erin2 = LayeredDisplayable("erin2")

## 次にアイテムの保管者を定義します。
## inventory.rpy がなくてもエラーにならないように、コメントアウトしています。
#default closet = Inventory()

## 各アイテムを Item(名前、装備タイプ) で定義します。it, item の名前空間も使えます。
## 名前がファイル名、タイプがフォルダ名になるようにします。
#define item.pleated_skirt = Item("Pleated Skirt", type="bottom")
#define item.buruma = Item("Buruma", type="bottom")
#define item.school_sailor = Item("School Sailer", type="top")
#define item.gym_shirt = Item("Gym Shirt", type="top")

## 以上で準備完了です。


## ゲームがスタートしたら jump sample_dressup でここに飛んでください。

label sample_dressup:

    # it で定義された全てのアイテムを closet に追加
    $ closet.get_all_items(store.item)
    
    # dressup スクリーンを（"画像"、ドール、保管者）で呼び出します。
    call screen dressup("erin2", erin2, closet)

    show erin2

    "How do I look?"

    return


##############################################################################
## Dressup screen

screen dressup(im, doll, inv):

    # image
    add im at center

    # doll
    vbox:
        label "Equipped"
        for i in doll.types:
            hbox:
                text i yoffset 8
                if doll.equips.get(i):
                    $ name = inv.get_item(doll.equips[i][0]).name
                    textbutton name action Function(doll.unequip_item, i, inv)

    # inv
    vbox xalign 1.0:
        label "Closet"
        for i in inv.items:
            $ item = i[0]
            $ name = inv.get_item(item).name
            textbutton name action Function(doll.equip_item, i, inv)

    textbutton "Return" action Return() yalign 1.0


##############################################################################
## Definitions
##############################################################################

##############################################################################
## Doll class

init -3 python:

    class Doll(object):

        """
        class that stores equips and layer infomation. It has the following fields:
        
        folder - dolfer name that this doll's images are stored.
        layers - folder names that this doll's each layer images are stored.
        types - layer and type names that can be equipped when inventory system is using.
        
        It also has fields as same as layer names for example, self.base=None
        These fields vlues are filenames of each layer.
        """

        # デフォルトのレイヤーを下から順番に定義します。
        _layers = ["base", "feet", "bottom", "top", "face"]

        # 装備できるアイテムのタイプを定義します。
        _types = ["feet", "bottom", "top"]


        def __init__(self, folder, layers = None, types = None, **kwargs):

            self.folder = folder
            self.layers = layers or self._layers
            self.types = types or self._types

            # set default image on each layer
            for i in self.layers:
                if i in kwargs.keys():
                    setattr(self, i, kwargs[i])
                else:
                    setattr(self, i, None)

            # dictionary whose keys are item types and values are list [item, amount]
            self.equips = {}
            for i in self.types:
                self.equips.setdefault(i, None)

            # dictionary whose keys are layer names and values are lists of images
            self.images = {}
            for i in self.layers:
                self.images.setdefault(i, [])
            for i in renpy.list_files():
                for j in self.layers:
                    if i.startswith(self.folder+"/"+j):
                        self.images[j].append(i.replace(self.folder+"/"+j+"/", "").replace(".png", ""))


        @staticmethod
        def draw_doll(st, at, doll):
            # Function that is used for dynamic displayable.

            layers=[]
            if doll in dir(store) :
                doll = getattr(store, doll)
                folder = doll.folder

                for i in doll.layers:
                    if getattr(doll, i) and renpy.loadable("{}/{}/{}.png".format(folder, i, getattr(doll, i))):
                        layers.append("{}/{}/{}.png".format(folder, i, getattr(doll, i)))

            return Fixed(*layers, fit_first=True), None


        # the following methods are used with inventory class
        # if you don't use inventory, ignore them


        def equip_item(self, slot, inv, merge=True):
            # equip item slot in this type from inv

            if slot:
                type = inv.get_item(slot[0]).type
                if type in self.types:
                    if self.equips.get(type):
                        self.unequip_item(type, inv, merge)
                    self.equips[type] = slot
                    inv.items.remove(slot)
                    self.update()
            else:
                raise Exception("Couldn't find this item in inventory")


        def unequip_item(self, type, inv, merge=True):
            # remove item slot in this type then add this to inv

            slot = self.equips.get(type)
            if slot:
                self.equips[type] = None
                inv.add_item(slot[0], slot[1], merge)
                self.update()
            else:
                raise Exception("Couldn't find this item type in equips")


        def unequip_all_items(self, inv, merge=True):
            # remove all items

            for i in self.types:
                self.unequip_item(i, inv, merge)


        def update(self):
            # call this method each time to change layers

            for i in self.layers:
                if i in self.types:
                    slot = self.equips.get(i)
                    if slot:
                        setattr(self, i, slot[0])
                    else:
                        setattr(self, i, None)


##############################################################################
## Displayable

    def LayeredDisplayable(doll):
        return DynamicDisplayable(Doll.draw_doll, doll)


