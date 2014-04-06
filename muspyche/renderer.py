"""This module holds the rendering code for Muspyche.
"""

from .models import *


class BaseEngine:
    """Base class for rendering engines of Muspyche.
    """
    def __init__(self, element):
        self._el = element

    def render(self, context):
        s = ''
        return s


class VariableEngine:
    """Engine used to render variables.
    """
    def __init__(self, element):
        self._el = element

    def render(self, context):
        s = ''
        if self._el._key not in context and not self._el._miss and self._el._key != '': raise KeyError('`{0}\' cannot be found in current context'.format(self._el._key))
        if self._el._key: s = (context[self._el._key] if self._el._key in context else '')
        if self._el._escaped: s = html.escape(str(s))
        return s


class TextNodeEngine:
    def __init__(self, element):
        self._el = element

    def render(self, context):
        return self._el


def Engine(element):
    """Factory function for creating rendering engines.
    It accepts a single element as an argument and
    returns right class of engine.
    """
    engine = None
    if type(element) == Variable:
        engine = VariableEngine
    elif type(element) == TextNode:
        engine = TextNodeEngine
    else:
        raise TypeError('no suitable rendering engine for type {0} found'.format(type(element)))
    return engine


def renderlist(tree, context):
    """Renders string from raw list of nodes.
    """
    s = ''
    for el in tree:
        elrender = ''
        if type(el) in [Section, Inverted]:
            elrender = el.render(Engine, (context[el.getname()] if (el.getname() in context) else []))
        else:
            elrender = el.render(engine=Engine(el), context=context)
        s += elrender
    return s
