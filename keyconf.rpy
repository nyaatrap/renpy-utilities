# This file modifies key bindings.
# マウス・キーボード・ゲームパッドの割り当てを追加・変更するファイルです。
# https://www.renpy.org/doc/html/keymap.html


################################################################################
# This block overwrites ren'py's default keymaps
# 次の init 1 python は、個々のキーと機能の割り当てを上書き・変更します。
# 必要な機能があれば、アンコメント（冒頭の # を削除）して有効化してください。

init 1 python:

    # Allow reading game with mouse wheel down
    # マウスホイール下回転で読み進められるようにします。
    config.keymap['dismiss'].append('mousedown_5')

    # Allow viewport scrolling by pageup/pagedown
    # viewport を pageup や pagedown でスクロールできるようにします。
    config.keymap['viewport_up'].extend(['K_PAGEUP', 'repeat_K_PAGEUP'])
    config.keymap['viewport_down'].extend(['K_PAGEDOWN', 'repeat_K_PAGEDOWN'])

    # Bind 'a' to toggle_afm
    # オート機能を a に割り当てます。
    config.keymap["toggle_afm"] = ['a']

    # Bind 's' to toggle_skip
    # スキップ機能を s に追加します。
    # config.keymap['toggle_skip'].append('s')

    # Bind 'F12' to screenshot
    # スクリーンショット機能を F12 に追加します。
    # config.keymap['screenshot'].append('K_F12')

    # Change the space key from 'dismiss' into 'hide windows'
    # スペースキーを、読み進めからウィンドウ非表示に変更します。
    # config.keymap['dismiss'].remove('K_SPACE')
    # config.keymap['hide_windows'].append('K_SPACE')

    # Swap right click and middle click
    # 右クリックのメニュー表示機能と、中クリックのウィンドウ非表示機能を入れ替えます。
    # config.keymap['hide_windows'].remove('mouseup_2')
    # config.keymap['game_menu'].remove('mouseup_3')
    # config.keymap['game_menu'].append('mouseup_2')
    # config.keymap['hide_windows'].append('mouseup_3')

    # Disable key bindings that is not used a lot.
    # 打ち間違えしやすいキーの割り当てを解除します。
    # config.keymap['self_voicing'].remove('v')
    # config.keymap['toggle_fullscreen'].remove('f')
    # config.keymap['screenshot'].remove('s')
    # config.keymap['hide_windows'].remove('h')

    # Make button action immediately when pressed.
    # 以下は、マウスボタンが離したときではなく、押した時に即反応するようにします。
    # 一般的には推奨されません。
    # config.keymap['button_ignore'].remove('mousedown_1')
    # config.keymap['button_select'].remove('mouseup_1')
    # config.keymap['button_select'].append('mousedown_1')
    # config.keymap['dismiss'].remove('mouseup_1')
    # config.keymap['dismiss'].append('mousedown_1')

    # These bind functions into gemepads.
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


################################################################################]
# This block defines new functions for keymap.
# To bind a new key name to a new function, define its function then bind it to key name.
# 次の init python ブロックは、デフォルトで用意されていない機能を定義しています。
# まず関数を定義してから、キーとして使う名前に割り当てます。

init 1 python:

    # Add 'history' key name.
    # ヒストリー機能が使えるように、割り当てに使う名前 'history' を追加します。
    def _show_history():
        if not renpy.context()._menu:
            renpy.call_in_new_context("_game_menu", _game_menu_screen="history")
                
    config.underlay.append(renpy.Keymap(history = _show_history))
    config.keymap["history"] = []

    # Replace rollback with history
    # ロールバックをヒストリーと置き換えます。
    # config.keymap["rollback"] = []
    # config.keymap["history"] = [ 'K_PAGEUP', 'repeat_K_PAGEUP', 'K_AC_BACK', 'mousedown_4' ]


    # This example adds a function that changes Language from None to 'English'.
    # 次の例は、基本言語（None で定義された言語）と英語を入れ替える機能を追加しています。
    def _toggle_language():
        if _preferences.language=="english":
            renpy.change_language(None)
        else:
            renpy.change_language("english")
        return

    config.underlay.append(renpy.Keymap(toggle_language = _toggle_language))
    config.keymap["toggle_language"] = []

