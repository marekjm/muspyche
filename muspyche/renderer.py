"""This module holds the rendering code for Muspyche.
"""

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
    def render(self, context, global_context):
        s = ''
        current_context = context
        key = self._el._key
        if key.startswith('::'):
            key = key[2:]
            current_context = global_context
        if '.' in key:
            keyparts = key.split('.')
            key = keyparts.pop(-1)
            for part in keyparts:
                if part in current_context:
                    current_context = current_context[part]
                else:
                    current_context = {}
                    break
        if key not in current_context and not self._el._miss and key != '': raise KeyError('`{0}\' cannot be found in current context'.format(key))
        if key: s = (current_context[key] if key in current_context else '')
        if type(s) is not str: s = str(s)
        if self._el._escaped: s = html.escape(str(s))
        return s


class TextNodeEngine(BaseEngine):
    def render(self, context, global_context=None):
        return self._el._text


class SectionEngine(BaseEngine):
    def _getcontext(self, context):
        return (context[self._el.getname()] if (self._el.getname() in context) else [])

    def render(self, context, global_context):
        s = ''
        context = self._getcontext(context)
        if context == False or context == []:
            pass
        elif type(context) == list and len(context) > 0:
            for i in context:
                s += render(self._el._template, i, global_context)
        elif type(context) == dict:
            s = render(self._el._template, context, global_context)
        else:
            raise TypeError('invalid type for context: expected list or dict but got {0}'.format(type(context)))
        return s


class InvertedEngine(SectionEngine):
    def render(self, context, global_context):
        s = ''
        context = self._getcontext(context)
        if context == False or context == []: s = render(self._el._template, context, global_context)
        return s


class PartialEngine(BaseEngine):
    """Engine used to render partials.
    """
    def render(self, context, global_context):
        s = ''
        return s


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


def render(tree, context, global_context):
    """Renders string from raw list of nodes.
    """
    s = ''
    for el in tree:
        s += el.render(engine=Engine(el), context=context, global_context=global_context)
    return s
