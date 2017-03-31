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
This file implements integrated gallery that serches images and music automatically.   
視聴済みの画像や音楽を自動的に検索・追加する、統合型のギャラリーを追加するファイルです。   

## _statements.rpy
This file contains additional statements   
Ren'Py に新しいステートメント（命令文）を追加するファイルです。   

## dressup.rpy
This file adds Doll class and LayeredDisplayable that provides layered sprites.   
多層レイヤーのスプライトを提供する Doll クラスと LayeredDisplayable を追加するファイルです。   
Inventory クラスと組み合わせることでドレスアップゲームなども作ることもできます。   

## inventory.rpy
This file provides inventory system.   
アイテムの売買や管理を行う機能を追加するファイルです。   
多少の改変でスキルやクエストなど様々な要素の管理に汎用的に使えます。   

## arena.rpy
This file defines Actor and Arena class to add turn-based combat and competition.   
ターン制の戦闘や競争を行うためのアクタークラスとアリーナクラスを追加するファイルです。   
基本的な枠組みしかありませんので、実用には改変する必要があります。   

## tilemap.rpy
This file defines Tilemap class that create single map from small tile images.   
小さな画像を並べて一枚の画像にする Tilemap クラスを追加するファイルです。   

## adventure.rpy
This file provides adventure game framework that uses event maps.   
イベントを配置した２Dマップを探索するアドベンチャーゲームのフレームワークを追加するファイルです。   
ラベルをオブジェクトとのペアで管理することで、マップ上にイベントとして配置して呼び出すことができます。   
RPGからSLGまで様々に使えるように汎用性を高くしてありますが、その分コードは少し複雑になっています。   

## tilemap_explore.rpy
This file adds tilemap exploring function into adventure framework.   
This framework requres tilemap.rpy and adventure.rpy.   
adventure にタイルマップを探索する機能を追加するファイルです。   
tilemap.rpy と adventure.rpy が必要になります。

## dungeon_crawl.rpy
This file adds pseudo-3D dungeon crawling function into adventurer framework.   
To play the sample game, download the cave folder then place it in the images directory.   
adventure に疑似３Dダンジョン探索機能を追加するファイルです。   
サンプルを実行するには images/cave フォルダーの画像をダウンロードする必要があります。   
