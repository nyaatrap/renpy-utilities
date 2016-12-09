## This file defines transforms.
## このファイルは transform（変形・変換）を定義します。
## https://www.renpy.org/doc/html/transforms.html
## https://www.renpy.org/doc/html/atl.html#atl

## transform とは画像を変換して表示する関数のことです。
## 一番簡単な使い方は画像の表示位置を指定する方法です。
## その他にもアニメーションや画像自体の変更も行えます。

## 基本的な使い方は show 画像 at transform の形ですが
## show 画像 at transformA, transformB のように組み合わせることもできます。
## 組み合わせる時は、原則的に座標を指定する transform を後にします。

## また、本来が関数なので引数を付けて show 画像 at transform(pos=x, time=t) としたり
## displayable（表示可能オブジェクト）を直接引数にして image x = transform(displayable)
## のように定義に組み込んで使うこともできます。

## 新しい transform は transform ステートメントか、python の関数定義で追加できます。
## どちらもグローバルスコープの変数になるため、他の変数との衝突に注意してください。


## このファイルは gui や画像定義に使えるように、それらのどのファイルよりも先に実行しなければなりません。

init offset = -3


##############################################################################
## Positions
## 以下の transform は画像を表示する位置を定義します。ほとんどはデフォルトで定義されていますが、
## 表示済みの画像の座標を変える時には、時間を掛けて移動するように拡張しています。
## on show は画像を初めて表示する時、on replace は表示してある画像を動かす時に使われます。


init python:
    ## 座標の移動にかかる時間を小数で定義します。
    base_time = .5


## 中央に下揃えで表示する。
transform center(t=base_time):
    on show:
        anchor (.5, 1.0) pos (.5, 1.0)
    on replace:
        alpha 1.0
        ease t anchor (.5, 1.0) pos (.5, 1.0)

## 左に下揃えで表示する。
transform left(t=base_time):
    on show:
        anchor (.0, 1.0) pos (.0, 1.0)
    on replace:
        alpha 1.0
        ease t anchor (.0, 1.0) pos (.0, 1.0)

## 右に下揃えで表示する。
transform right(t=base_time):
    on show:
        anchor (1.0, 1.0) pos (1.0, 1.0)
    on replace:
        alpha 1.0
        ease t anchor (1.0, 1.0) pos (1.0, 1.0)

## 中央左寄りに下揃えで表示する。
transform centerL(t=base_time):
    on show:
        anchor (.25, 1.0) pos (.25, 1.0)
    on replace:
        alpha 1.0
        ease t anchor (.25, 1.0) pos (.25, 1.0)

## 中央右寄りに下揃えで表示する。
transform centerR(t=base_time):
    on show:
        anchor (.75, 1.0) pos (.75, 1.0)
    on replace:
        alpha 1.0
        ease t anchor (.75, 1.0) pos (.75, 1.0)

## 画面の左外に下揃えで表示する。
transform offscreenleft(t=base_time):
    on show:
        anchor (1.0, 1.0) pos (.0, 1.0)
    on replace:
        alpha 1.0
        ease t anchor (1.0, 1.0) pos (.0, 1.0)

## 画面の右外に下揃えで表示する。
transform offscreenright(t=base_time):
    on show:
        anchor (.0, 1.0) pos (1.0, 1.0)
    on replace:
        alpha 1.0
        ease t anchor (.0, 1.0) pos (1.0, 1.0)

## 中央に表示する。
transform truecenter(t=base_time):
    on show:
        anchor (.5, .5) pos (.5, .5)
    on replace:
        alpha 1.0
        ease t anchor (.5, .5) pos (.5, .5)

## 左に表示する。
transform trueleft(t=base_time):
    on show:
        anchor (.0, .5) pos (.0, .5)
    on replace:
        alpha 1.0
        ease t anchor (.0, .5) pos (.0, .5)

## 右に表示する。
transform trueright(t=base_time):
    on show:
        anchor (1.0, .5) pos (1.0, .5)
    on replace:
        alpha 1.0
        ease t anchor (1.0, .5) pos (1.0, .5)

## x, y に表示する。
transform position(x=.5, y=.5, t=base_time):
    on show:
        anchor (.5, .5) pos (x, y)
    on replace:
        alpha 1.0
        ease t anchor (.5, .5) pos (x, y)

## ズームを変更します。パラメーター z は拡大率です。
## この transform は他のポジションと組み合わせて使います。
transform zoom(z=1.0, t=base_time):
    on show:
        zoom z
    on replace:
        alpha 1.0
        ease t zoom z


## デフォルトではこの他に default、reset、top、topleft、topright が定義されていますが
## 使用頻度が低い為ここでは再定義していません。必要な場合は上記を参考に定義してください。


##############################################################################
## Animations
## 以下の trasnform は画像にアニメーションを加えます。
## アニメーションと同時に位置を指定する場合は show 画像 at animation, position の順で指定します。


init python:
    ## アニメーションの動きの大きさを整数で定義します。
    ## 全身の立ち絵のサイズの20分の１くらいが目安です。
    base_offset =32

##  左から現れるアニメーション。
transform inL(t=base_time/2, d=base_offset):
    alpha .0 xoffset -d
    easein t alpha 1.0 xoffset 0

##  右から現れるアニメーション。
transform inR(t=base_time/2, d=base_offset):
    alpha .0 xoffset d
    easein t alpha 1.0 xoffset 0

## 左に消えるアニメーション。
## hide は at 節を使えないため show 画像 を使います。
transform outL(t=base_time/2, d=base_offset):
    easeout t alpha .0 xoffset -d
    xoffset 0

## 右に消えるアニメーション。
transform outR(t=base_time/2, d=base_offset):
    easeout t alpha .0 xoffset d
    xoffset 0

## 軽くホップするアニメーション。
transform hop(t=base_time/2, d=base_offset):
    alpha 1.0
    ease t/2 yoffset -d
    ease t/2 yoffset 0

## 二回連続してホップするアニメーション。
transform doublehop(t=base_time, d=base_offset):
    alpha 1.0
    ease t/4 yoffset -d
    ease t/4 yoffset 0
    ease t/4 yoffset -d
    ease t/4 yoffset 0

## 軽くかがむアニメーション。
transform bow(t=base_time, d=base_offset):
    alpha 1.0
    ease t/2 yoffset d
    ease t/2 yoffset 0

## 左右に二回揺れるアニメーション。
transform wag(t=base_time, d=base_offset):
    alpha 1.0
    easein t/6 xoffset d/2
    ease t/3 xoffset -d/2
    easein t/3 xoffset d/4
    easein t/6 xoffset 0

## 素早く左に避けるアニメーション。
transform swayL(t=base_time/2, d=base_offset):
    alpha 1.0
    ease t/3 xoffset -d*4
    ease t*2/3 xoffset 0

## 素早く右に避けるアニメーション。
transform swayR(t=base_time/2, d=base_offset):
    alpha 1.0
    ease t/3 xoffset d*4
    ease t*2/3 xoffset 0


## 衝撃を受けたように振動するアニメーション。
## 先に python で揺れを計算する関数を定義します。
init python:

    def _shake_function(trans, st, at, dt=.5, dist=64):
        #dt is duration timebase, dist is maximum shake distance in pixel
        if st <= dt:
            trans.xoffset = int((dt-st)*dist*(.5-renpy.random.random())*2)
            trans.yoffset = int((dt-st)*dist*(.5-renpy.random.random())*2)
            return 1.0/60
        else:
            return None

## 実際の振動アニメーション。
transform shake(t=base_time, d=base_offset):
    alpha 1.0
    function renpy.curry(_shake_function)(dt=t, dist=d*2)
    xoffset 0 yoffset 0
    
