## This file adds Doll class and LayeredDisplayable that provides layered sprites.
## 多層レイヤーのスプライトを提供する Doll クラスと LayeredDisplayable を追加するファイルです。
## Doll クラスは Inventory クラスを所有し、所持アイテムに応じて自動的にレイヤーが変化します。
## Inventory.rpy が必要になります。

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
#         ├bottom
#         │    ├dress.png
#         │    └swimsuit.png
#         ├top
#         │    ├dress.png
#         │    └swimsuit.png
#         └face
#             ├happy.png
#             └angry.png

## まず上のフォルダを反映するように、ポーズとレイヤーのリストを定義しておきます
define poses = ["stand"]
define layers = ["base", "bottom", "top", "face"]

## それからドールオブジェクトを Doll(image, folder, poses, layers, デフォルトのポーズ、デフォルトの画像) の形で default で定義します。
## image は下で定義する image のタグになります。
## デフォルトのポーズは、pose="フォルダー名"で指定します。
## デフォルトの画像は、フォルダー名="ファイル名（拡張子なし）"で指定します。base 以外は省略可能です。
default erin = Doll(image="erin", folder="erin", poses = poses, layers= layers,
    pose = "stand", base="base", bottom="buruma", top="gym_shirt", face="happy")


## 次に、上で定義するドールオブジェクトを""で囲み LayeredDisplayable に渡して画像を定義します。
image erin = LayeredDisplayable("erin")

## layer="画像" を指定すると、各レイヤーの状態が固定されます。
image erin happy= LayeredDisplayable("erin", face="happy")
image erin angry= LayeredDisplayable("erin", face="angry")

## 以上で準備完了です。


## ゲームがスタートしたら jump sample_doll でここに飛んでください。

label sample_doll:
    ## ゲームがスタートしたら、 イメージで定義した画像を表示します。
    show erin
    pause

    ## 表示した画像は $ doll.layer = "filename" の形で、各レイヤーの画像を切り変えることができます。
    ## 下の例では outfit レイヤーの画像を "dress.png", face レイヤーの画像を "angry.png" に変更します。
    $ erin.top = "school_sailor"
    $ erin.face = "angry"
    pause

    ## 同じタグの画像を別に定義しておけば、dissolve で表情変化をさせることが出来ます。
    show erin happy
    with dissolve
    pause

    ## 属性を渡さない場合は元の画像に戻ります。
    show erin:
        ease .5 xalign 0.0
    pause

    ## reset_layers() でデフォルトの状態に戻します。
    $ erin.reset_layers()
    pause

    return


##############################################################################
## 応用

## inventory からアイテムを受け取って装備することで、レイヤーを切り替えることもできます。
## この機能を使うためには inventory.rpy が必要です。

## まず、装備可能なアイテムのカテゴリーを定義しておきます。
define equip_types = ["bottom", "top"]

## 次に各アイテム Item(名前、装備タイプ、各レイヤーのプロパティ) で定義します。
## doll に与える namespace の名前空間で定義する必要があります。
## 各プロパティーには、変更するレイヤー="画像ファイル名"を与えます。

init python:
    item.pleated_skirt = Item("Pleated Skirt", type="bottom", bottom = "pleated_skirt")
    item.buruma = Item("Buruma", type="bottom", bottom = "buruma")
    item.school_sailor = Item("School Sailer", type="top", top = "school_sailor")
    item.gym_shirt = Item("Gym Shirt", type="top", top = "gym_shirt")


## ドールオブジェクトを Doll(image, folder, poses, layers, equip_types, namespace, items, デフォルトのポーズ、デフォルトの画像) で定義します。
default erin2 = Doll(image = "erin2", folder="erin", poses = ["stand"], layers=["base", "bottom", "top", "face"],
    equip_types = equip_types, namespace = "item", pose = "stand", base="base", face="happy")

## 上で定義するドールオブジェクトを""で囲み LayeredDisplayable に渡して画像を定義します。
image erin2 = LayeredDisplayable("erin2")

## 最後にアイテムの保管者を定義します。
default closet = Inventory(item_types = equip_types, namespace="item")


## 以上で準備完了です。


## ゲームがスタートしたら jump sample_dressup でここに飛んでください。

label sample_dressup:

    ## equip_types に含まれる定義された全てのアイテムを closet に追加
    $ closet.add_all_items()

    ## 次の命令はロールバックをブロックして、ゲームの全ての変化をセーブできるようにします。
    ## （デフォルトでは現在の入力待ちの開始時点のみをセーブするので必要になります。）
    $ block()

    ## dressup スクリーンを（ドール、保管者）で呼び出します。
    call screen dressup(erin2, closet)

    show erin2

    "How do I look?"

    return


##############################################################################
## Dressup screen

screen dressup(doll, inv):

    # image
    add doll.image at center

    # doll
    vbox:
        label "Equipped"
        for i in doll.equip_types:
            hbox:
                text i yoffset 8
                for name, score, obj in doll.equipment.get_items(types=[i]):
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

init -5 python:

    class Doll(object):

        """
        class that stores equips and layer information. It has the following fields:

        image - image tag that this object linked to.
        folder - folder name that this doll's images are stored.
        poses - folder names that this doll's each layer group are store
        pose - current pose that determines which layer group is used.
        layers - folder names that this doll's each layer image are stored.
        substitution - dictionary {"pose1":"pose2"}. if images are not found in pose1, it searches in pose2.
        images - dictionary whose keys are layer names and values are lists of images

        It also has fields as same as layer names. For example, self.base=None
        default values are stored in default_layername. For example, self.default_base=None
        if also has state property of each layer. For example, self.base_state=None
        if layer_state is not None, it used as suffix of filename.
        These field values are filenames of each layer.

        equipment - an object of Inventory class
            this inventory can have only one item per each item type
        equip_types is passed to its item_types
        items are added using by add_items methods
        """

        # Define default layers from bottom.
        # デフォルトのレイヤーを下から順番に定義します。
        _poses = ["stand"]
        _layers = ["base", "feet", "bottom", "top", "face"]


        def __init__(self, image = "",folder="", poses = None, layers = None, pose = None, substitution = None,
            equip_types = None, namespace = None, items=None, **kwargs):

            self.image = image
            self.folder = folder
            self.poses = poses or self.default_poses
            self.layers = layers or self._layers
            self.default_pose = pose or self.default_poses[0]
            self.pose = self.default_pose
            self.substitution = None

            self.equip_types = equip_types or None
            self.equipment = Inventory(item_types=equip_types, namespace = namespace, items=items) if equip_types else None

            # set default image on each layer
            for i in self.layers:
                setattr(self, i+"_state", None)
                if i in kwargs.keys():
                    setattr(self, "default_"+i, kwargs[i])
                    setattr(self, i, kwargs[i])
                else:
                    setattr(self, "default_"+i, None)
                    setattr(self, i, None)

            self.images = {}
            for i in self.layers:
                self.images.setdefault(i, [])
            for i in renpy.list_files():
                for j in self.layers:
                    if self.folder and i.startswith(self.folder+"/"+j):
                        self.images[j].append(i.replace(self.folder+"/"+j+"/", "").replace(".png", ""))

            self.update_layers()


        def get_center(self, doll=None, width=None, height=None, layer='master'):
            tag = doll.image if doll else self.image
            rv = renpy.get_image_bounds(tag, width, height, layer)
            if rv:
                x, y, width, height = rv
                return int((x+width)/2), int((y+height)/2)


        def get_distance(self, target, doll=None, width=None, height=None, layer='master'):
            doll = doll or self
            pos1 = self.get_center(doll, width, height, layer)
            pos2 = self.get_center(target, width, height, layer)
            if pos1 and pos2:
                return pos2[0]-pos1[0], pos2[1]-pos1[1]


        def reset_layers(self, reset_pose=True, reset_layer_state=True):
            # reset layers to the default

            for i in self.layers:
                setattr(self, i, getattr(self, "default_"+i))
                if reset_layer_state:
                    setattr(self, i+"_state", None)
            if reset_pose:
                self.pose = self.default_pose


        def equip_item(self, name, inv, reset_layer_state=True):
            # equip an item from inv

            for i, score, obj in self.equipment.get_items():
                if obj.type == inv.get_item(name).type:
                   self.unequip_item(i, inv, reset_layer_state)

            inv.give_item(name, self.equipment)
            self.update_layers()


        def unequip_item(self, name, inv, reset_layer_state=True):
            # remove item in this equip type then add this to inv

            if reset_layer_state:
                for i in self.layers:
                    if getattr(self.equipment.get_item(name), i, None):
                        setattr(self, i+"_state", None)

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


        def update_layers(self, reset_pose=False, reset_layer_state=False):
            # call this method each time to change layers

            self.reset_layers(reset_pose, reset_layer_state)

            if self.equipment:
                for name, score, obj in self.equipment.get_items():
                    for i in self.layers:
                        if getattr(obj, i, None):
                            setattr(self, i, getattr(obj, i))


        @staticmethod
        def draw_doll(st, at, doll, flatten=False, **kwargs):
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
                    elif pose in doll.substitution.keys():
                        sb = doll.substitution[pose]
                        image = "{}/{}/{}/{}{}.png".format(folder, sb, layer, item, state)
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

        return DynamicDisplayable(Doll.draw_doll, doll, flatten, **kwargs)


