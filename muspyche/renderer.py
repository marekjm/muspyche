"""This module holds the rendering code for Muspyche.
"""

from .models import *


class Engine:
    """Rendering engine of Muspyche.
    """
    def __init__(self, element):
        self._el = element

    def render(self, context):
        s = ''
        return s


def renderlist(tree, context):
    """Renders string from raw list of nodes.
    """
    s = ''
    for el in tree:
        elrender = ''
        if type(el) in [Section, Inverted]:
            elrender = el.render(Engine, (context[el.getname()] if (el.getname() in context) else []))
        else:
            elrender = el.render(context)
        s += elrender
    return s
