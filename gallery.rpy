﻿## This file implements integrated gallery that searches images and music automatically.
## 視聴済みの画像や音楽を自動的に検索・追加する、統合型のギャラリーを追加するファイルです。

## screens.rpy の navigation に以下の文を追加すると、ギャラリーがゲームメニューに追加されます。
## textbutton _("ギャラリー") action ShowMenu("gallery")

## このギャラリーは視聴済みの画像と音楽を自動的に検索・追加します。
## また config.developer が True（ビルド前）の場合は視聴に関わらず追加されます。
## 下の変数を設定すると追加する画像・音楽とその順番を手動で指定できます。

## ギャラリーに使いたい画像のタグのリスト
define gallery.image_tags = []

## ジュークボックスに入れたい音楽のフォルダ
define gallery.music_folder = "music"

## ジュークボックスに入れたい音楽のファイル名のリスト
define gallery.music_tracks = []


## Gallery screen #################################################################
##
## Game menus for image gallery.
## These screens overwrite default gallery.


## Screen that shows image thumbnails and jukebox
screen gallery():

    tag menu

    use game_menu(_("Gallery")):

        hbox spacing 32:

            # image gallery
            vpgrid cols 4 spacing 8 mousewheel True scrollbars "vertical" side_spacing 8:

                # thumbnail size
                python:
                    width = config.screen_width//8
                    height = config.screen_height//8

                for i in gallery.images.keys():

                    ## If there is a seen image in a tag, show the first image.
                    if gallery.images[i]:
                        button xysize width, height:
                            background Transform(gallery.images[i][0],  size = (width, height))
                            action [With(gallery.trans), Show("_gallery", images=gallery.images[i])]

                    ## Otherwise show blank image
                    else:
                        add Solid("#999") size width, height


            # jukebox
            frame:
                vbox:

                    label "Jukebox" xalign .5

                    hbox style_prefix "jukebox":
                        textbutton "PREV" action gallery.jukebox.Previous()
                        textbutton "PAUSE" action PauseAudio("music", value="toggle")
                        textbutton "PLAY" action gallery.jukebox.TogglePlay()
                        textbutton "NEXT" action gallery.jukebox.Next()

                    hbox style_prefix "jukebox":
                        textbutton "REPEAT" action gallery.jukebox.ToggleLoop()
                        textbutton "SINGLE" action gallery.jukebox.ToggleSingleTrack()
                        textbutton "SHUFFLE" action gallery.jukebox.ToggleShuffle()

                    # show duration
                    bar value AudioPositionValue() ysize 20

                    null height 8

                    # show tracks
                    viewport mousewheel True scrollbars "vertical":
                        vbox:
                            for k, v in gallery.tracks.items():
                                if gallery.jukebox.is_unlocked(v):
                                    textbutton k action gallery.jukebox.Play(v)


style jukebox_button_text:
    size 20


## Screen that shows actual images
screen _gallery(images):

    default page = 0

    add "black"
    if images:
        add images[page] align (.5, .5)

    if page < len(images)-1:
        key "button_select" action [With(gallery.trans), SetScreenVariable("page", page + 1)]
    else:
        key "button_select" action [With(gallery.trans), Hide("_gallery")]

    key "game_menu" action [With(gallery.trans), Hide("_gallery")]


##############################################################################
## Definition


init 1900 python in gallery:

    from collections import OrderedDict
    from store import *
    import os

    # transition for gallery
    trans = Dissolve(.25)

    ## Create dictionary whose keys are image tags and values are list of seen images
    ## gallery.images = {"girl":["girl happy", "girl angry"], "boy":["boy happy", "boy angry"],,,}

    images = OrderedDict()

    for i in image_tags or renpy.get_available_image_tags():
        images.setdefault(i, [])

        for j in renpy.get_available_image_attributes(i):
            image = i+ " "+" ".join(j)
            if renpy.seen_image(image) or config.developer:
                images[i].append(image)


    ## Create dictionary then add this into MusicRoom
    ## gallery.tracks = {"filename1": "music/filename1.ogg" , "filename2":"music/filename2.ogg",,,}

    jukebox = MusicRoom(fadeout=.5)
    tracks = OrderedDict()
    music_folder = music_folder or ""

    for i in music_tracks or renpy.list_files():
        if i.startswith(music_folder+"/"):
            track = music_folder+"/"+i if music_tracks else i
            title = os.path.splitext(i.replace(music_folder+"/", ""))[0].capitalize()
            jukebox.add(track, always_unlocked=config.developer)
            tracks[title] = track

