from django import template
from django.template.base import TemplateSyntaxError
from django.template.base import Node, NodeList

from dolphin import flipper

register = template.Library()

class IfActiveNode(Node):
    child_nodelists = ('nodelist_true', 'nodelist_false')

    def __init__(self, key, other_args, nodelist_true, nodelist_false):
        self.key = key
        self.nodelist_true, self.nodelist_false = nodelist_true, nodelist_false
        self.other_args = other_args
        #TODO - other args

    def __repr__(self):
        return "<IfEqualNode>"

    def render(self, context):
        key = self.key.resolve(context, True)
        #TODO - fix other_args here?
        if flipper.is_active(key):
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
    #todo - other_args?
    other_args = [parser.compile_filter(bit) for bit in bits[2:]]
    return IfActiveNode(val1, other_args, nodelist_true, nodelist_false)
ifactive = register.tag(ifactive)

@register.simple_tag(takes_context=True)
def active_tags(context):
    req = context.get('request', None)
    return ",".join(ff.name for ff in flipper.active_tags(request=req))
