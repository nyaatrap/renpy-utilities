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
## デフォルトのポーズは、pose="フォルダー名"で指定します。
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
define equip_types = ["outfit_bottom", "outfit_top"]

## まずドールオブジェクトを Doll2(フォルダー名、 レイヤーのリスト、装備タイプのリスト、デフォルトの画像)
## で定義します。装備タイプはレイヤー名を使う必要があります。
default erin2 = Doll2(folder="erin", poses = ["stand"], layers=["base", "bottom", "top", "face"],
    equip_types = equip_types, namespace = "item", pose = "stand", base="base", face="happy")
image erin2 = LayeredDisplayable("erin2")

## 次にアイテムの保管者を定義します。
## getattr は Inventory が見つからない場合にエラーが起きないようにしています。
default closet = Inventory(item_types = equip_types, namespace="item") if getattr(store, "Inventory", None) else None

## 各アイテムを Item(名前、装備タイプ、効果) で namespace の名前空間で定義します。
## 変更するレイヤー="画像ファイル名"を与えます。

init python:
    if getattr(store, "Item", None):
        item.pleated_skirt = Item("Pleated Skirt", type="outfit_bottom", bottom = "pleated_skirt")
        item.buruma = Item("Buruma", type="outfit_bottom", bottom = "buruma")
        item.school_sailor = Item("School Sailer", type="outfit_top", top = "school_sailor")
        item.gym_shirt = Item("Gym Shirt", type="outfit_top", top = "gym_shirt")

## 以上で準備完了です。


## ゲームがスタートしたら jump sample_dressup でここに飛んでください。

label sample_dressup:

    ## equip_types に含まれる定義された全てのアイテムを closet に追加
    $ closet.get_all_items(types=equip_types)

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
        for i in doll.equipment.item_types:
            hbox:
                text i yoffset 8
                for name, score, obj in doll.equipment.get_items():
                    if obj.type == i:
                        textbutton "[obj.name]" action Function(doll.unequip_item, name, inv)

    # inv
    vbox xalign 1.0:
        label "Closet"
        for name, score, obj in inv.get_items():
            textbutton "[obj.name]" action Function(doll.equip_item, name, inv)

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
        equipment - an object of Inventory class
        equip_types is passed to its item_types
        this inventory can have only one item per each item type
        """

        def __init__(self, folder="", poses = None, layers = None, pose = None, equip_types = None, namespace = None, **kwargs):

            super(Doll2, self).__init__(folder, poses, layers, pose, **kwargs)

            self.equip_types = equip_types
            self.equipment = Inventory(item_types=equip_types, namespace = namespace)


        def equip_item(self, name, inv):
            # equip an item from inv

            for i, score, obj in self.equipment.get_items():
                if obj.type == inv.get_item(name).type:
                   self.equipment.give_item(i, inv)
            inv.give_item(name, self.equipment)
            self.update_layers()


        def unequip_item(self, name, inv):
            # remove item in this equip type then add this to inv

            self.equipment.give_item(name, inv)
            self.update_layers()


        def equip_all_items(self, inv):
            # equip all slot randomly

            items = list(inv.items.keys())
            renpy.random.shuffle(items)

            for i in items:
                obj = inv.get_item(i)
                if obj.type in self.equip_types and not self.equipment.get_items(obj.type):
                    self.equip_item(i, inv)


        def unequip_all_items(self, inv):
            # remove all items

            for i in self.equipment.get_items(rv="name"):
                self.unequip_item(i, inv)


        def update_layers(self):
            # call this method each time to change layers

            self.reset_layers(False, False)

            for name, score, obj in self.equipment.get_items():
                for i in self.layers:
                    if getattr(obj, i, None):
                        setattr(self, i, getattr(obj, i))



