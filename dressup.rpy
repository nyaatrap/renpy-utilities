## This file provides layered sprites for dressup games
## このファイルは、ドレスアップゲームに使える多層レイヤーのスプライト（立ち絵）を提供します。


################################################################################
## 使い方

## まずアクターオブジェクトを Actor(フォルダー名, 各レイヤーのフォルダー名、デフォルトの画像) の形で定義します。
default Erin = Actor("images/erin", layers=["base", "face"], base="base", face="wink")

## さきほど定義したアクターオブジェクトを""で囲み LayeredDisplayable に渡して画像を定義します。
image erin = LayeredDisplayable("Erin")

## 以上で準備完了です。

## ゲームがスタートしたら、 イメージで定義した画像を表示します。
# show erin

# 表示した画像は $ actor.layer = "filename" の形で、各レイヤーを切り変えることができます。
# 下の例では face レイヤーの画像を "angry.png" に変更します。
# $ Erin.face = "angry"


################################################################################
## 定義

init -1 python:

    class Actor(object):

        # class that stores layer infomation

        # スプライトに使うレイヤーを下から順番に定義します。
        _layers = ["base", "feet", "under", "bottom", "top", "adorn", "face"]

        def __init__(self, folder, layers = None, **kwargs):
            self.folder = folder
            self.layers = layers or self._layers
            for i in self.layers:
                if i in kwargs.keys():
                    setattr(self, i, kwargs[i])
                else:
                    setattr(self, i, None)


    def _draw_actor(st, at, actor):

        # function that is used for dynamic displayable.

        layers=[]
        if actor in dir(store) :
            actor = getattr(store, actor)
            folder = actor.folder

            for i in actor.layers:
                if getattr(actor, i) and renpy.loadable("{}/{}/{}.png".format(folder, i, getattr(actor, i))):
                    layers.append("{}/{}/{}.png".format(folder, i, getattr(actor, i)))

        return Fixed(*layers, fit_first=True), None


    def LayeredDisplayable(actor):
        return DynamicDisplayable(_draw_actor, actor)

