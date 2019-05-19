## This file modifies transforms and transitions.
## 様々な transform（画像変換）や transition（画像遷移）を追加・変更するファイルです。

## このファイルは gui や画像定義に使えるように、それらのどのファイルよりも先に実行しなければなりません。

init offset = -3

##############################################################################
# Transforms
##############################################################################

## https://www.renpy.org/doc/html/transforms.html
## https://www.renpy.org/doc/html/atl.html#atl

## transform（画像変換）は画像を変換して表示する関数のことです。
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


##############################################################################
## Positions
## 以下の transform は立ち絵を表示する位置を定義します。
## on show は画像を初めて表示する時、on replace は表示してある画像を動かす時に使われます。

## 立ち絵のアンカーを小数で定義します。
define stand_anchor = (.5, .5)

## 座標の移動にかかる時間を小数で定義します。
define move_time = .5

## 共通するコードを先に定義しておきます。
transform position(x=.5, y=.5, t=move_time, a=stand_anchor):
    on show:
        anchor a pos (x, y)
    on replace:
        anchor a alpha 1.0
        ease t pos (x, y)

## 実際に使うポジションを定義します。
## 以下は例です。使いやすい名前に書き換えてください。

# 中央へ表示または移動する。
transform move_center:
    position (.5)

# 右へ表示または移動する。
transform move_right:
    position (.8)

# 左へ表示または移動する。
transform move_left:
    position (.2)


##############################################################################
## Animations
## 以下の transform は画像にアニメーションを加えます。
## アニメーションと同時に位置を指定する場合は show 画像 at animation, position の順で指定します。
## 例：show girl at inR, move_center

## アニメーションの動きの大きさを整数で定義します。
## 全身の立ち絵のサイズの20分の１くらいが目安です。
define move_size =32

##  左から現れるアニメーション。
transform inL(t=move_time/2, d=move_size, a=stand_anchor):
    anchor a alpha .0 xoffset -d
    easein t alpha 1.0 xoffset 0

##  右から現れるアニメーション。
transform inR(t=move_time/2, d=move_size, a=stand_anchor):
    anchor a alpha .0 xoffset d
    easein t alpha 1.0 xoffset 0

## 左に消えるアニメーション。
## hide は at 節を使えないため show 画像 at transform を使います。
transform outL(t=move_time/2, d=move_size, a=stand_anchor):
    on hide:
        anchor a
        easeout t alpha .0 xoffset -d
        xoffset 0

## 右に消えるアニメーション。
transform outR(t=move_time/2, d=move_size, a=stand_anchor):
    on hide:
        anchor a
        easeout t alpha .0 xoffset d
        xoffset 0

## 軽くホップするアニメーション。
transform hop(t=move_time/2, d=move_size, a=stand_anchor):
    anchor a alpha 1.0
    ease t/2 yoffset -d
    ease t/2 yoffset 0

## 二回連続してホップするアニメーション。
transform doublehop(t=move_time, d=move_size, a=stand_anchor):
    anchor a alpha 1.0
    ease t/4 yoffset -d
    ease t/4 yoffset 0
    ease t/4 yoffset -d
    ease t/4 yoffset 0

## 軽くかがむアニメーション。
transform bow(t=move_time, d=move_size, a=stand_anchor):
    anchor a alpha 1.0
    ease t/2 yoffset d
    ease t/2 yoffset 0

## 左右に二回揺れるアニメーション。
transform wag(t=move_time, d=move_size, a=stand_anchor):
    anchor a alpha 1.0
    easein t/6 xoffset d/2
    ease t/3 xoffset -d/2
    easein t/3 xoffset d/4
    easein t/6 xoffset 0

## 素早く左に避けるアニメーション。
transform swayL(t=move_time/2, d=move_size, a=stand_anchor):
    anchor a alpha 1.0
    ease t/3 xoffset -d*4
    ease t*2/3 xoffset 0

## 素早く右に避けるアニメーション。
transform swayR(t=move_time/2, d=move_size, a=stand_anchor):
    anchor a alpha 1.0
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
transform shake(t=move_time, d=move_size, a=stand_anchor):
    anchor a alpha 1.0
    function renpy.curry(_shake_function)(dt=t, dist=d*2)
    xoffset 0 yoffset 0


##############################################################################
# Transitions
##############################################################################

## https://www.renpy.org/doc/html/transitions.html

## transition（画面遷移）は二つの画面の移り変わりを表示する関数です。
## 基本的な使い方は show 画像 with transform の形ですが、 with の代わりに
## $renpy.transition(transition, layer="master") を show 画像の前に使う方法で、
## 効果終了までの待ち時間がなくなりレイヤーも指定できるようになります。


## 基本的なトランジション。
## デフォルトで定義されているものはコメントアウトしてあるので、
## 変更したい場合のみアンコメントしてください。

define flash = Fade(.15, 0, .3, color="#fff")
#define fade = Fade(.5, 0, .5)
#define dissolve = Dissolve(0.5)
#define pixellate = Pixellate(1.0, 5)

#define vpunch = Move((0, 10), (0, -10), .10, bounce=True, repeat=True, delay=.275)
#define hpunch = Move((15, 0), (-15, 0), .10, bounce=True, repeat=True, delay=.275)

#define blinds = ImageDissolve(im.Tile("blindstile.png"), 1.0, 8)
#define squares = ImageDissolve(im.Tile("squarestile.png"), 1.0, 256)


## 以下はデフォルトで定義されている CropMove を ImageDissolve で再定義します。
## ワイプする二つの画像の間がディゾルブで混じり合うようになります。
## ImageDissolve を使用するには白から黒に移り変わる画像が必要です。

#define wipedown = ImageDissolve("transitions/wipedown.png", .5, ramplen=32)
#define wipeup = ImageDissolve("transitions/wipedown.png", .5,  ramplen=32, reverse=True)
#define wiperight = ImageDissolve("transitions/wiperight.png", .5, ramplen=32)
#define wipeleft = ImageDissolve("transitions/wiperight.png", .5,  ramplen=32, reverse=True)

#define irisout = ImageDissolve("transitions/irisout.png", .5,  ramplen=32)
#define irisin = ImageDissolve("transitions/irisout.png", .5,  ramplen=32,reverse=True)


## 新しい transition は通常 transition クラスのインスタンスとして定義しますが、transform
## ステートメントでも定義することができます。transform で定義する場合は、引数に
## old_widget（変化前の画面）と new_widget（変化後の画面）が必要になります。

## 新しい画面が上から落ちてきてバウンドするトランジション。
transform fallin(t=1.0, old_widget, new_widget):
    delay t

    contains:
        old_widget

    contains:
        new_widget
        yanchor 1.0 ypos 0
        easein_bounce t yalign 1.0

