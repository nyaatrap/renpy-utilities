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



