## This file contains additional statements
## Ren'Py に新しいステートメント（命令文）を追加するファイルです。
## https://www.renpy.org/doc/html/cds.html

## このファイルは、数字や_など他のファイルよりも優先される頭文字で命名する必要があります。
python early:

##############################################################################
## hardpause

## The new hardpause statement is same statement to renpy.pause(delay, hard=True)
## if delay is ommited, .5 is used
## 通常の pause ステートメントと似ていますが、クリックしてもスキップされません。

    def parse_hardpause(lex):
        delay = lex.float()
        return delay

    def execute_hardpause(obj):
        renpy.pause(float(obj) if obj else .5, hard=True)

    renpy.register_statement("hardpause", parse=parse_hardpause, execute=execute_hardpause)


##############################################################################
## trans

## The new trans statement causes transition at the next interaction.
## it's followed by transtion, and optinally takes onlayer argument.
## by default, 'trans Dissolve(.25) onlayer master' is used without arguments.
## renpy.transition のショートカットです。with と似ていますが表示する画像の直前で使います。

    def parse_trans(lex):
        trans = lex.simple_expression()
        if lex.keyword('onlayer'):
            layer = lex.simple_expression()
        else:
            layer = "master"
        return (trans, layer)

    def execute_trans(obj):
        trans, layer = obj
        if trans:
            trans = eval(trans)
        else:
            trans = Dissolve(.25)
        if layer == "all":
            renpy.transition(trans)
        else:
            renpy.transition(trans, layer=layer)

    def lint_trans(obj):
        trans, layer = obj
        try:
            eval(trans)
        except:
            if trans != None:
                renpy.error("Transition %s is not defined" % trans)

    renpy.register_statement("trans", parse=parse_trans, lint=lint_trans, execute=execute_trans)


##############################################################################
## hide

## The new hide statement overwrites default hide statement.
## it allows to add at clause. If at transform is added, it's equivalent to:
## show image at transform
## hide image
## hide ステートメントが at 節を使えるように拡張します。

    def parse_hide(lex):
        import renpy.parser
        image_name, expression, tag, at_list, layer, zorder, behind = renpy.parser.parse_image_specifier(lex)
        return (image_name,expression, tag, at_list, layer, zorder, behind)

    def execute_hide(imspec):
        image_name, expression, tag, at_list, layer, zorder, behind = imspec

        if at_list:
            _at_list = [eval(i) for i in at_list]
            renpy.show(image_name, at_list=_at_list, layer=layer, what=expression, tag=tag)
        if tag:
            renpy.hide(tag, layer=layer)
        else:
            renpy.hide(image_name, layer=layer)

    def lint_hide(imspec):
        image_name, expression, tag, at_list, layer, zorder, behind = imspec
        if at_list:
            for i in at_list:
               try:
                   eval(i)
               except:
                   renpy.error("Transform %s is not defined" % i)
        if not renpy.has_image(image_name):
            renpy.error("Image %s is not defined" % image_name)

    renpy.register_statement("hide", parse=parse_hide, lint=lint_hide, execute=execute_hide)


##############################################################################
## showith

## The showith statement causes dissolve transition at the next interaction.
## The following statement moves girl, then changes her face with dissolve.
## showith girl at move
## girl happy "message"
## 直後のセリフでの表情変化が dissolve になります。
## trans を間に挟むのと同じ効果です。

    def parse_showith(lex):
        import renpy.parser
        image_name, expression, tag, at_list, layer, zorder, behind = renpy.parser.parse_image_specifier(lex)
        return (image_name,expression, tag, at_list, layer, zorder, behind)

    def execute_showith(imspec):
        image_name, expression, tag, at_list, layer, zorder, behind = imspec

        if at_list:
            _at_list = [eval(i) for i in at_list]
        else:
            _at_list = None
        renpy.show(image_name, at_list=_at_list, layer=layer, what=expression, tag=tag)
        renpy.with_statement(None)
        renpy.transition(Dissolve(.25), layer="master")

    def lint_showith(imspec):
        image_name, expression, tag, at_list, layer, zorder, behind = imspec
        if at_list:
            for i in at_list:
               try:
                   eval(i)
               except:
                   renpy.error("Transform %s is not defined" % i)
        if not renpy.has_image(image_name):
            renpy.error("Image %s is not defined" % image_name)

    renpy.register_statement("showith", parse=parse_showith, lint=lint_showith, execute=execute_showith)
    

##############################################################################
## scene 

## By default, the scene statement clears only the master layer.
## This makes the scene statement clears all layers except ovelay.
## scene ステートメントが overlay 以外の全ての消去するように拡張します。


init -999 python:
    
    def _scene_all_layers(layer = None):
        
        if layer:
            renpy.scene(layer)
        else:
            for i in config.layers[:-1]:
                renpy.scene(layer = i)
                
    config.scene = _scene_all_layers
    

##############################################################################
## show

## This adds dissolve effect between images when images with the same tag are changed. 
## This is useful to change expression.
## show ステートメントを表情変化などに使った時 dissolve で変化するようにします。
        
    
    def _show_dissolve(name, at_list=[], layer='master', what=None, zorder=0, tag=None, behind=None, atl=None):
        
        # If an image has tag and it's showing, use dissolve effect.
        if len(name)>1 and renpy.showing(name[0], layer = layer):
            renpy.show(name[0], at_list, layer, what, zorder, tag, behind,atl)
            renpy.with_statement(None)
            renpy.transition(Dissolve(.3, alpha=True), layer)
            
        renpy.show(name, at_list, layer, what, zorder, tag, behind,atl)

    config.show = _show_dissolve

