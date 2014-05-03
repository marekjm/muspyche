"""This module holds the rendering code for Muspyche.
"""

from . import util
from . import parser
from .models import *


class BaseEngine:
    """Base class for rendering engines of Muspyche.

    Subclasses must override its render method.
    """
    def __init__(self, element):
        self._el = element

    def render(self, context, global_context):
        """Template .render() method for rendering engines.

        All methods overriding this one in subclasses must accept
        `context` and `global_context` parameters, both of which are dictionaries
        containing contexts.
        """
        s = ''
        return s


class VariableEngine(BaseEngine):
    """Engine used to render variables.
    """
    def render(self, context):
        key = self._el._key
        return context.get(key=key, escape=self._el._escaped)


class TextNodeEngine(BaseEngine):
    def render(self, context, global_context=None):
        return self._el._text


class SectionEngine(BaseEngine):
    def render(self, context, lookup, missing):
        s = ''
        name = self._el.getname()
        context.adjust(name)
        if context.current() == False or context.current() == []:
            pass
        elif type(context.current()) == list and len(context.current()) > 0:
            listed = context.current()
            for i in range(len(listed)):
                context.adjust('[{}]'.format(i))
                s += render(self._el._template, context, lookup, missing)
                context.restore()
        elif type(context.current()) == dict:
            s = render(self._el._template, context, lookup, missing)
        elif type(context.current()) is bool and context.current() == True:
            s = render(self._el._template, context, lookup, missing)
        elif bool(context.current()) == False:
            pass
        else:
            raise TypeError('invalid type for context: expected list or dict but got {0}'.format(type(context.current())))
        context.restore()
        return s


class InvertedEngine(SectionEngine):
    def render(self, context, lookup, missing):
        s = ''
        context.adjust(self._el.getname())
        if context.current() == False or context.current() == [] or context.current() == '': s = render(self._el._template, context, lookup, missing)
        context.restore()
        return s


class PartialEngine(BaseEngine):
    """Engine used to render partials.
    """
    def resolve(self, lookup, missing):
        """Resolves partial.
        """
        found, path = parser._findpath(self._el.getpath(), lookup, missing)
        template = parser.parse((util.read(path) if found else ''))
        self._el._template = template
        return self

    def render(self, context, lookup, missing):
        return render(self._el._template, context, lookup, missing)


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
    elif type(element) == Section:
        engine = SectionEngine
    elif type(element) == Inverted:
        engine = InvertedEngine
    elif type(element) == Partial:
        engine = PartialEngine
    else:
        raise TypeError('no suitable rendering engine for type {0} found'.format(type(element)))
    return engine


def render(tree, context, lookup, missing=False):
    """Renders string from raw list of nodes.
    """
    s = ''
    for el in tree:
        engine = Engine(el)
        if type(el) in [Section, Inverted]: s += el.render(engine=engine, context=context, lookup=lookup, missing=missing)
        elif type(el) is Partial: s += el.render(engine=engine, context=context, lookup=lookup, missing=missing)
        else: s += el.render(engine=engine, context=context)
    return s
