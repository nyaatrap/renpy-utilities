# Renpy Utilities

This repository has files that is useful for Ren'Py.
All files in this repository are in the public domain.

このリポジトリは Ren'Py に有用な様々なファイルをアップロードしています。
基本的に一覧の下に行くほど複雑で上級者向けになります。
各ファイルの詳しい説明は、ファイル自体にコメントとして埋め込まれています。
本リポジトリに含まれるファイルは全てパブリックドメインです。


## keyconf.rpy
This file modifies key bindings.

マウス・キーボード・ゲームパッドの割り当てを追加・変更するファイルです。

## animation.rpy
This file modifies transforms and transitions.

様々な transform（画像変換）や transition（画像遷移）を追加・変更するファイルです。

## gallery.rpy
This file implements integrated gallery that searches images and music automatically.

視聴済みの画像や音楽を自動的に検索・追加する、統合型のギャラリーを追加するファイルです。

## _statements.rpy
This file contains additional statements

Ren'Py に新しいステートメント（命令文）を追加するファイルです。

## inventory.rpy
This file provides inventory system.

アイテムの売買や管理を行う機能を追加するファイルです。
スキルやクエストなど様々な要素の管理にも汎用的に使えます。

## dressup.rpy
This file adds Doll class and LayeredDisplayable that provides layered sprites.

多層レイヤーのスプライトを提供する Doll クラスと LayeredDisplayable を追加するファイルです。
Doll クラスは Inventory クラスを所有し、所持アイテムに応じて自動的にレイヤーが変化します。
Inventory.rpy が必要になります。

## arena.rpy
This file defines Actor and Arena class to add turn-based combat and competition.

ターン制の戦闘や競争を行うためのアクタークラスとアリーナクラスを追加するファイルです。
Actor クラスは Inventory を継承し、Item をスキルのように扱います。
Inventory.rpy が必要になります。

## tilemap.rpy
This file defines Tilemap class that create single map from small tile images.

小さな画像を並べて一枚の画像にする Tilemap クラスを追加するファイルです。

## adventure.rpy
This file provides adventure game framework that uses event maps.

イベントを配置した２Dマップを探索するアドベンチャーゲームのフレームワークを追加するファイルです。
ラベルをオブジェクトとのペアで管理することで、マップ上にイベントとして配置して呼び出すことができます。

## adventure_tilemap.rpy
This file adds tilemap exploring function into adventure framework.
This framework requires tilemap.rpy and adventure.rpy.

adventure にタイルマップを探索する機能を追加するファイルです。
tilemap.rpy と adventure.rpy が必要になります。

## adventure_dungeon.rpy
This file adds pseudo-3D dungeon crawling function into adventurer framework.
This framework requires adventure.rpy, tilemap.rpy, and adventure_tilemap.rpy.
To play the sample game, download the dungeon folder then place it in the game directory.
To show sample dungeon correctly, set screen size 800x600.

adventure に疑似３Dダンジョン探索機能を追加するファイルです。
adventure.rpy, tilemap.rpy, adventure_tilemap.rpy が必要になります。
サンプルを実行するには dungeon フォルダーの画像をダウンロードして game ディレクトリに配置する必要があります。
サンプルを正しく表示するには、スクリーンサイズを 800x600 に設定する必要があります。
