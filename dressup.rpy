## This file adds Doll class and LayeredDisplayable that provides layered sprites.
## 多層レイヤーのスプライトを提供する Doll クラスと LayeredDisplayable を追加するファイルです。
## Inventory クラスと組み合わせることでドレスアップゲームなども作ることもできます。

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
default erin = Doll("erin", layers=["base", "face"], base="base", face="happy")

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
    
    ## reset() でデフォルトの状態に戻します。
    $ erin.reset()
    pause

    return


##############################################################################
## 応用

## inventory からアイテムを受け取って装備することで、レイヤーを切り替えることもできます。
## この機能を使うためには inventory.rpy が必要です。

## まずドールオブジェクトを Doll2(フォルダー名、 レイヤーのリスト、装備タイプのリスト、デフォルトの画像)
## で定義します。装備タイプはレイヤー名を使う必要があります。
default erin2 = Doll2("erin", layers=["base", "bottom", "top", "face"], equip_types = ["bottom", "top"], base="base", face="happy")
image erin2 = LayeredDisplayable("erin2")

## 次にアイテムの保管者を定義します。
## inventory.rpy がなくてもエラーにならないように、コメントアウトしています。
#default closet = Inventory()

## 各アイテムを Item(名前、装備タイプ、効果) で定義します。item の名前空間も使えます。
## 装備タイプがフォルダ名、効果がそのフォルダの画像ファイル名になるようにします。
#define item.pleated_skirt = Item("Pleated Skirt", type="bottom", effect = "pleated_skirt")
#define item.buruma = Item("Buruma", type="bottom", effect = "buruma")
#define item.school_sailor = Item("School Sailer", type="top", effect = "school_sailor")
#define item.gym_shirt = Item("Gym Shirt", type="top", effect = "gym_shirt")

## 以上で準備完了です。


## ゲームがスタートしたら jump sample_dressup でここに飛んでください。

label sample_dressup:

    ## item で定義された全てのアイテムを closet に追加
    $ closet.get_all_items(store.item)

    ## 次の命令はロールバックをブロックして、ゲームの全ての変化をセーブできるようにします。
    ## （デフォルトでは現在の入力待ちの開始時点のみをセーブするので必要になります。）
    $ block()
    
    ## dressup スクリーンを（"画像"、ドール、保管者）で呼び出します。
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
        for i in doll.equip_types:
            hbox:
                text i yoffset 8
                if doll.equips.get(i):
                    $ name = inv.get_item(doll.equips[i]).name
                    textbutton name action Function(doll.unequip_item, i, inv)

    # inv
    vbox xalign 1.0:
        label "Closet"
        for i in inv.items.keys():
            $ name = inv.get_item(i).name
            textbutton name action Function(doll.equip_item, i, inv)

    vbox yalign 1.0:
        textbutton "Auton" action Function(doll.equip_all_items, inv)
        textbutton "Reset" action Function(doll.unequip_all_items, inv)
        textbutton "Return" action Return()


##############################################################################
## Definitions
##############################################################################

##############################################################################
## Doll class

init -3 python:

    class Doll(object):

        """
        class that stores equips and layer infomation. It has the following fields:

        folder - folder name that this doll's images are stored.
        layers - folder names that this doll's each layer images are stored.

        It also has fields as same as layer names. For example, self.base=None
        These field values are filenames of each layer.
        """

        # Define default layers from bottom.
        # デフォルトのレイヤーを下から順番に定義します。
        _layers = ["base", "feet", "bottom", "top", "face"]


        def __init__(self, folder="", layers = None, **kwargs):

            self.folder = folder
            self.layers = layers or self._layers

            # set default image on each layer
            for i in self.layers:
                if i in kwargs.keys():
                    setattr(self, "_"+i, kwargs[i])
                    setattr(self, i, kwargs[i])
                else:
                    setattr(self, "_"+i, None)
                    setattr(self, i, None)

            # dictionary whose keys are layer names and values are lists of images
            self.images = {}            
            for i in self.layers:
                self.images.setdefault(i, [])                
            for i in renpy.list_files():
                for j in self.layers:
                    if self.folder and i.startswith(self.folder+"/"+j):
                        self.images[j].append(i.replace(self.folder+"/"+j+"/", "").replace(".png", ""))
                        
                        
        def reset(self):
            # reset layers to the default
            
            for i in self.layers:
                setattr(self, i, getattr(self, "_"+i))


        @staticmethod
        def draw_doll(st, at, doll, flatten=False, kwargs=None):
            # Function that is used for dynamic displayable.

            layers=[]
            
            if doll in dir(store) :
                doll = getattr(store, doll)
                folder = doll.folder

                for layer in doll.layers:
                    if kwargs:
                        item = kwargs.get(layer) or getattr(doll, layer)
                    else:
                        item = getattr(doll, layer)
                    if item:
                        image = "{}/{}/{}.png".format(folder, layer, item)
                        if renpy.loadable(image):
                            layers.append(image)

            if flatten:
                return Flatten(Fixed(*layers, fit_first=True)), None
            else:
                return Fixed(*layers, fit_first=True), None


##############################################################################
## Displayable

    def LayeredDisplayable(doll, flatten =False, **kwargs):
        """
        Function that returns displayable that composite image files.
        If flatten is true, image is flatten to render alpha properly.
        If kwargs is given, given file is always used.
        """

        return DynamicDisplayable(Doll.draw_doll, doll, flatten, kwargs)


##############################################################################
## Doll2 class
        
init -2 python:
    
    class Doll2(Doll):
        
        """
        Class that adds equipments on doll calss. It adds following fields:
        equip_types - layer and type names that can be equipped when inventory system is using.
        equips - dictonary of {"type": "name"}        
        """

        # Define default eqippable item types
        # デフォルトの装備できるアイテムのタイプを定義します。
        _equip_types = ["feet", "bottom", "top"]

        def __init__(self, folder="", layers = None, equip_types = None, **kwargs):
            
            super(Doll2, self).__init__(folder, layers, **kwargs)
            
            self.equip_types = equip_types or self._equip_types
            
            # dictionary whose keys are item types and values are list [item, score]
            self.equips = {}            
            for i in self.equip_types:
                self.equips.setdefault(i, None)


        def equip_item(self, name, inv):
            # equip an item from inv

            type = inv.get_item(name).type
            
            if type in self.equip_types:
                
                if self.equips.get(type):
                    self.unequip_item(type, inv)
                    
                self.equips[type] = name
                inv.score_item(name, -1)
                
                self.update(inv)


        def unequip_item(self, type, inv):
            # remove item in this equip type then add this to inv

            if self.equips.get(type):
                
                inv.score_item(self.equips[type], 1)
                self.equips[type] = None
                
                self.update(inv)


        def equip_all_items(self, inv):
            # equip all slot randomly
            
            items = list(inv.items.keys())
            renpy.random.shuffle(items)

            for i in items:
                obj = inv.get_item(i)
                if obj.type in self.equip_types and not self.equips.get(obj.type):
                    self.equip_item(i, inv)


        def unequip_all_items(self, inv):
            # remove all items

            for i in self.equip_types:
                self.unequip_item(i, inv)


        def update(self, inv):
            # call this method each time to change layers

            for i in self.layers:
                if i in self.equip_types:
                    if self.equips.get(i):
                        obj = inv.get_item(self.equips.get(i))
                        if obj.effect:
                            setattr(self, i, obj.effect)
                        else:
                            setattr(self, i, getattr(self, "_"+i))
                    else:
                        setattr(self, i, getattr(self, "_"+i))
                
                        
                        
