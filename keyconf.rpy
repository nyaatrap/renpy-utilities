# This file modifies key bindings.
# このファイルはキーの割り当てを変更します。
# https://www.renpy.org/doc/html/keymap.html


################################################################################
# 次の init python ブロックは、デフォルトで用意されていない機能を定義しています。
# 必要な機能のみアンコメントしてください。割り当てに使う名前を定義した場合は
# 後で必ず何らかのキーを割り振る必要があります。

init python:
    
    # 文字自動送り機能が使えるように、割り当てに使う名前 'toggle_afm' を追加します。
    config.underlay.append(renpy.Keymap(toggle_afm = Preference("auto-forward", "toggle")))
    
    # ヒストリー機能が使えるように、割り当てに使う名前 'history' を追加します。
    # config.underlay.append(renpy.Keymap(history = ShowMenu("history")))
    
    
    # 独自の新しい機能を追加したい場合には、まず関数を定義してから割り当てに使う名前を追加します。    
    # 次の例は、基本言語（None で定義された言語）と英語を入れ替える機能を追加しています。
    
    def _toggle_language():
        if _preferences.language=="english":
            renpy.music.play("click", channel="audio")
            renpy.change_language(None)
        else:
            renpy.music.play("click", channel="audio")
            renpy.change_language("english")
        return        
        
    # config.underlay.append(renpy.Keymap(toggle_language = _toggle_language))
    

################################################################################
# 次の init 1 python は、個々のキーと機能の割り当てを上書き・変更します。
# 必要な機能があれば、アンコメント（冒頭の # を削除）して有効化してください。

init 1 python:
    
    # マウスホイール下回転で読み進められるようにします。
    config.keymap['dismiss'].append('mousedown_5')
    
    # viewport を pageup や pagedown でスクロールできるようにします。
    config.keymap['viewport_up'].extend(['K_PAGEUP', 'repeat_K_PAGEUP'])
    config.keymap['viewport_down'].extend(['K_PAGEDOWN', 'repeat_K_PAGEDOWN'])    
    
    # ロールバックをヒストリーと置き換えます。
    # config.keymap["rollback"] = []
    # config.keymap["history"] = [ 'K_PAGEUP', 'repeat_K_PAGEUP', 'K_AC_BACK', 'mousedown_4' ]
    
    # オート機能を a に割り当てます。
    config.keymap["toggle_afm"] = ['a']
    
    # スキップ機能を s に追加します。
    # config.keymap['toggle_skip'].append('s')
        
    # スクリーンショット機能を F12 に追加します。
    # config.keymap['screenshot'].append('K_F12')
    
    # 上で定義した言語入れ替え機能を F2 に割り当てます。
    # config.keymap["toggle_language"] = 'K_F2'     
    
    # スペースキーを、読み進めからウィンドウ非表示に変更します。
    # config.keymap['dismiss'].remove('K_SPACE')
    # config.keymap['hide_windows'].append('K_SPACE')
    
    # 右クリックのメニュー表示機能と、中クリックのウィンドウ非表示機能を入れ替えます。
    # config.keymap['hide_windows'].remove('mouseup_2')
    # config.keymap['game_menu'].remove('mouseup_3')
    # config.keymap['game_menu'].append('mouseup_2')
    # config.keymap['hide_windows'].append('mouseup_3')    
    
    # 打ち間違えしやすいキーの割り当てを解除します。
    # config.keymap['self_voicing'].remove('v')
    # config.keymap['toggle_fullscreen'].remove('f')
    # config.keymap['screenshot'].remove('s')
    # config.keymap['hide_windows'].remove('h')    
    
    # 以下は、マウスボタンが離したときではなく、押した時に即反応するようにします。
    # 一般的には推奨されません。
    # config.keymap['button_ignore'].remove('mousedown_1')
    # config.keymap['button_select'].remove('mouseup_1')
    # config.keymap['button_select'].append('mousedown_1')
    # config.keymap['dismiss'].remove('mouseup_1')
    # config.keymap['dismiss'].append('mousedown_1')        
    
    # 以下は、ゲームパッドにデフォルトで定義されていない機能を割り当てます。
    config.pad_bindings["pad_a_press"] = [ "dismiss", "button_select", "bar_activate", "bar_deactivate"]
    config.pad_bindings["pad_b_press"] = [ "button_alternate", "game_menu", "bar_deactivate" ]
    config.pad_bindings["pad_x_press"] = [ "toggle_skip" ] #or  [ "toggle_afm" ] 
    config.pad_bindings["pad_y_press"] = [ "hide_windows" ]
    config.pad_bindings["pad_leftshoulder_press"] =[ "rollback", "viewport_up" ] #or [ "history", "viewport_up" ]
    config.pad_bindings["pad_rightshoulder_press"] = [ "rollforward","viewport_down"]
    config.pad_bindings["pad_lefttrigger_pos"] = [ "skip" ]
    config.pad_bindings["pad_lefttrigger_zero"] = [ "stop_skipping" ]
    config.pad_bindings["pad_righttrigger_pos"] = [ "dismiss" ]
    
