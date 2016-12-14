## This file provides layered sprites for dressup games
## このファイルは、ドレスアップゲームに使える多層レイヤーのスプライト（立ち絵）を提供します。

##############################################################################
## How to Use
##############################################################################

## 事前に以下のような構成のフォルダーを用意しておきます。

## name
##  ├base
##  │ └base.png    
##  └face
##      └happy.png
##      └angry.png


## それからドールオブジェクトを Doll(フォルダー名, 各レイヤーのフォルダー名のリスト、デフォルトの画像) 
## の形で定義します。各レイヤーの状態を保存できるように、default を使います。
## layers のパラメーターを省略すると、 ["base", "feet", "bottom", "top", "face"] がデフォルトで使われます。
## デフォルトの画像は、フォルダー名="ファイル名（拡張子なし）"で指定します。これも省略可能です。
default Erin = Doll("images/erin", layers=["base", "face"], base="base", face="happy")

## 次に、さきほど定義したドールオブジェクトを""で囲み LayeredDisplayable に渡して画像を定義します。
image erin = LayeredDisplayable("Erin")

## 以上で準備完了です。


## ゲームがスタートしたら、 イメージで定義した画像を表示します。
# show erin

# 表示した画像は $ doll.layer = "filename" の形で、各レイヤーの画像を切り変えることができます。
# 下の例では face レイヤーの画像を "angry.png" に変更します。
# $ Erin.face = "angry"


##############################################################################
## Definitions
##############################################################################

init -3 python:

    class Doll(object):

        '''class that stores layer infomation'''

        # デフォルトのレイヤーを下から順番に定義します。
        _layers = ["base", "feet", "bottom", "top", "face"]

        def __init__(self, folder, layers = None, **kwargs):
            
            self.folder = folder
            self.layers = layers or self._layers
            for i in self.layers:
                if i in kwargs.keys():
                    setattr(self, i, kwargs[i])
                else:
                    setattr(self, i, None)
                    
            # dictionary whose keys are layer names and values are lists of images
            self.images = {}            
            for i in self.layers:
                self.images.setdefault(i, [])                
            for i in renpy.list_files():
                for j in self.layers:
                    if i.startswith(self.folder+"/"+j):
                        self.images[j].append(i.replace(self.folder+"/"+j+"/", "").replace(".png", ""))


    def _draw_doll(st, at, doll):

        '''Function that is used for dynamic displayable.'''

        layers=[]
        if doll in dir(store) :
            doll = getattr(store, doll)
            folder = doll.folder

            for i in doll.layers:
                if getattr(doll, i) and renpy.loadable("{}/{}/{}.png".format(folder, i, getattr(doll, i))):
                    layers.append("{}/{}/{}.png".format(folder, i, getattr(doll, i)))

        return Fixed(*layers, fit_first=True), None


    def LayeredDisplayable(doll):
        return DynamicDisplayable(_draw_doll, doll)

