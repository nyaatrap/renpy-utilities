## This file adds Doll class and LayeredDisplayable that provides layered sprites.
## 多層レイヤーのスプライトを提供する Doll クラスと LayeredDisplayable を追加するファイルです。
## Inventory クラスと組み合わせることでドレスアップゲームなども作ることもできます。

##############################################################################
## How to Use
##############################################################################

##############################################################################
## 基本

## 事前に以下のような構成のフォルダーを用意しておきます。

# dollname
#     └stand
#         ├base
#         │    └base.png
#         ├outfit
#         │    ├dress.png
#         │    └swimsuit.png
#         └face
#             ├happy.png
#             └angry.png


## それからドールオブジェクトを Doll(フォルダー名、各ポーズのフォルダー名のリスト、各レイヤーのフォルダー名のリスト、デフォルトの画像)
## の形で定義します。各レイヤーの状態を保存できるように、default を使います。
## layers のパラメーターを省略すると ["base", "feet", "bottom", "top", "face"] がデフォルトで使われます。
## デフォルトのポーズは、pose="ファイル名"で指定します。base 以外は省略可能です。
## デフォルトの画像は、フォルダー名="ファイル名（拡張子なし）"で指定します。base 以外は省略可能です。
default erin = Doll(folder="erin", poses = ["stand"], layers=["base", "outfit", "face"], pose = "stand", base="base", outfit="dress", face="happy")

## 次に、さきほど定義したドールオブジェクトを""で囲み LayeredDisplayable に渡して画像を定義します。
image erin auto= LayeredDisplayable("erin")

## layer="画像" を指定すると、各レイヤーの状態が固定されます。
image erin happy= LayeredDisplayable("erin", face="happy")
image erin angry= LayeredDisplayable("erin", face="angry")

## 以上で準備完了です。


## ゲームがスタートしたら jump sample_doll でここに飛んでください。

label sample_doll:
    ## ゲームがスタートしたら、 イメージで定義した画像を表示します。
    show erin auto
    pause

    ## 表示した画像は $ doll.layer = "filename" の形で、各レイヤーの画像を切り変えることができます。
    ## 下の例では outfit レイヤーの画像を "dress.png", face レイヤーの画像を "angry.png" に変更します。
    $ erin.outfit = "dress"
    $ erin.face = "angry"
    pause

    ## 同じタグの画像を別に定義しておけば、dissolve で表情変化をさせることが出来ます。
    show erin happy
    with dissolve
    pause

    ## reset_layers() でデフォルトの状態に戻します。
    $ erin.reset_layers()
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
## getattr は Inventory が見つからない場合にエラーが起きないようにしています。
default closet = Inventory() if getattr(store, "Inventory", None) else None

## 各アイテムを Item(名前、装備タイプ、効果) で定義します。item の名前空間も使えます。
## 装備タイプがフォルダ名、効果がそのフォルダの画像ファイル名になるようにします。
init python:
    if getattr(store, "Item", None):
        item.pleated_skirt = Item("Pleated Skirt", type="bottom", effect = "pleated_skirt")
        item.buruma = Item("Buruma", type="bottom", effect = "buruma")
        item.school_sailor = Item("School Sailer", type="top", effect = "school_sailor")
        item.gym_shirt = Item("Gym Shirt", type="top", effect = "gym_shirt")

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
        textbutton "Auto" action Function(doll.equip_all_items, inv)
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
        class that stores equips and layer information. It has the following fields:

        folder - folder name that this doll's images are stored.
        poses - folder names that this doll's each layer group are store
        pose - current pose that determines which layer group is used.
        layers - folder names that this doll's each layer image are stored.
        images - dictionary whose keys are layer names and values are lists of images

        It also has fields as same as layer names. For example, self.base=None
        default values are stored in _layername. For example, self._base=None
        if also has state property of each layer. For example, self.base_state=None
        if layer_state is not None, it used as suffix of filename.
        These field values are filenames of each layer.
        """

        # Define default layers from bottom.
        # デフォルトのレイヤーを下から順番に定義します。
        _poses = ["stand"]
        _layers = ["base", "feet", "bottom", "top", "face"]


        def __init__(self, folder="", poses = None, layers = None, pose = None, **kwargs):

            self.folder = folder
            self.poses = poses or self._poses
            self.layers = layers or self._layers
            self._pose = pose or self._poses[0]
            self.pose = self._pose

            # set default image on each layer
            for i in self.layers:
                setattr(self, i+"_state", None)
                if i in kwargs.keys():
                    setattr(self, "_"+i, kwargs[i])
                    setattr(self, i, kwargs[i])
                else:
                    setattr(self, "_"+i, None)
                    setattr(self, i, None)

            self.images = {}
            for i in self.layers:
                self.images.setdefault(i, [])
            for i in renpy.list_files():
                for j in self.layers:
                    if self.folder and i.startswith(self.folder+"/"+j):
                        self.images[j].append(i.replace(self.folder+"/"+j+"/", "").replace(".png", ""))


        def reset_layers(self, pose=True, state=True):
            # reset layers to the default

            for i in self.layers:
                setattr(self, i, getattr(self, "_"+i))
                if state:
                    setattr(self, i, None)
            if pose:
                self.pose = self._pose


        @staticmethod
        def draw_doll(st, at, doll, flatten=False, suffix="", **kwargs):
            # Function that is used for dynamic displayable.

            doll = getattr(store, doll, None)

            if not doll:
                return Null(), None

            layers=[]
            folder = doll.folder
            pose = doll.pose

            for layer in doll.layers:
                item = kwargs.get(layer) or getattr(doll, layer)
                state = getattr(doll, layer+"_state") or ""
                if item:
                    image = "{}/{}/{}/{}{}.png".format(folder, pose, layer, item, state)
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

        return DynamicDisplayable(Doll.draw_doll, doll, flatten,
        **kwargs)


##############################################################################
## Doll2 class

init -2 python:

    class Doll2(Doll):

        """
        Class that adds equipments on doll class. It adds following fields:
        equip_types - layer and type names that can be equipped when inventory system is using.
        equips - dictionary of {"type": "name"}
        """

        # Default equipable item types. It's used when item_types are not defined.
        # デフォルトの装備できるアイテムのタイプを定義します。
        _equip_types = []

        def __init__(self, folder="", layers = None, equip_types = None, **kwargs):

            super(Doll2, self).__init__(folder, layers, **kwargs)

            self.equip_types = equip_types or self._equip_types

            # dictionary whose keys are item types and values are item names
            self.equips = {}
            for i in self.equip_types:
                self.equips.setdefault(i, None)


        def has_equip(self, name):
            # returns True if doll equipped this item.

            # check valid name or not
            Inventory.get_item(name)

            return name in [v for k, v in self.equips.items()]


        def has_equips(self, name):
            # returns True if doll equipped these items.
            # "a, b, c" means a and b and c, "a | b | c" means a or b or c.

            separator = "|" if name.count("|") else ","
            names = name.split(separator)
            for i in names:
                i = i.strip()
                if separator == "|" and self.has_equip(i):
                    return True
                elif separator == "," and not self.has_equip(i):
                    return False

            return True if separator == ","  else False


        def equip_item(self, name, inv):
            # equip an item from inv

            type = inv.get_item(name).type

            if type in self.equip_types:

                if self.equips.get(type):
                    self.unequip_item(type, inv)

                self.equips[type] = name
                inv.score_item(name, -1)

                self.update_layers(inv)


        def unequip_item(self, type, inv):
            # remove item in this equip type then add this to inv

            if self.equips.get(type):

                inv.score_item(self.equips[type], 1)
                self.equips[type] = None

                self.update_layers(inv)


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


        def update_layers(self, inv):
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



