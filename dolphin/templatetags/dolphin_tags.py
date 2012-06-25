from django import template
try:
    from django.template import TemplateSyntaxError, Node, NodeList
except ImportError:
    from django.template.base import TemplateSyntaxError, Node, NodeList

from dolphin import flipper

register = template.Library()


class IfActiveNode(Node):
    child_nodelists = ('nodelist_true', 'nodelist_false')

    def __init__(self, key, other_args, nodelist_true, nodelist_false):
        self.key = key
        self.nodelist_true, self.nodelist_false = nodelist_true, nodelist_false
        self.other_args = other_args

    def __repr__(self):
        return "<IfEqualNode>"

    def render(self, context):
        key = self.key.resolve(context, True)
        args = []
        kwargs = {}
        for arg in self.other_args:
            #resolve other_args
            arg = arg.resolve(context, True)
            if '=' in arg:
                k, v = arg.split('=')
                kwargs[k] = v
            else:
                args.append(arg)

        if flipper.is_active(key, *args, **kwargs):
            return self.nodelist_true.render(context)
        return self.nodelist_false.render(context)


def ifactive(parser, token):
    bits = list(token.split_contents())
    if len(bits) < 2:
        raise TemplateSyntaxError("%r takes at least one argument" % bits[0])
    end_tag = 'end' + bits[0]
    nodelist_true = parser.parse(('else', end_tag))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse((end_tag,))
        parser.delete_first_token()
    else:
        nodelist_false = NodeList()
    val1 = parser.compile_filter(bits[1])
    other_args = [parser.compile_filter(bit) for bit in bits[2:]]
    return IfActiveNode(val1, other_args, nodelist_true, nodelist_false)
ifactive = register.tag(ifactive)

class ActiveTagNode(template.Node):
    def render(self, context):
        req = context.get('request', None)
        return ",".join(ff.name for ff in flipper.active_flags(request=req))

def active_flags(parser, token):
    return ActiveTagNode()

register.tag('active_flags', active_flags)

