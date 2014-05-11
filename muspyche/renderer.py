"""This module holds the rendering code for Muspyche.
"""

import re

from . import util
from . import parser
from .models import *


class BaseEngine:
    """Base class for rendering engines of Muspyche.

    Subclasses must override its render method.
    """
    def __init__(self, element):
        self._el = element

    def render(self, context):
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
    def render(self, context):
        return self._el._text


class NewlineEngine(TextNode):
    def render(self, newline):
        return (self._text._text if newline is None else newline)


class SectionEngine(BaseEngine):
    def render(self, context, lookup, missing, newline):
        s = ''
        name = self._el.getname()
        context.adjust(name)
        if context.current() == False or context.current() == []:
            pass
        elif type(context.current()) == list and len(context.current()) > 0:
            listed = context.current()
            for i in range(len(listed)):
                context.adjust('[{}]'.format(i))
                s += render(self._el._template, context, lookup, missing, newline)
                context.restore()
        elif type(context.current()) == dict:
            s = render(self._el._template, context, lookup, missing, newline)
        elif type(context.current()) is bool and context.current() == True:
            s = render(self._el._template, context, lookup, missing, newline)
        elif bool(context.current()) == False:
            pass
        else:
            raise TypeError('invalid type for context: expected list or dict but got {0}'.format(type(context.current())))
        context.restore()
        return s


class InvertedEngine(SectionEngine):
    def render(self, context, lookup, missing, newline):
        s = ''
        context.adjust(self._el.getname())
        if context.current() == False or context.current() == [] or context.current() == '': s = render(self._el._template, context, lookup, missing, newline)
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

    def render(self, context, lookup, missing, newline):
        return render(self._el._template, context, lookup, missing, newline)


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
    elif type(element) == Newline:
        engine = NewlineEngine
    elif type(element) == Section:
        engine = SectionEngine
    elif type(element) == Inverted:
        engine = InvertedEngine
    elif type(element) == Partial:
        engine = PartialEngine
    else:
        raise TypeError('no suitable rendering engine for type {0} found'.format(type(element)))
    return engine


class Renderer:
    """Object that will render render parsed tree.
    """
    def __init__(self, tree, context, lookup=[], missing=False, newline=None):
        self._tree, self._context = tree, context
        self._lookup, self._missing = lookup, missing
        self._newline = newline
        self._post = []

    def addpost(self, regex, callback):
        """Post-render callbacks are used with partials.
        When a partial is rendered, its path is checked against regexes in post list.
        When a match is found, rendered text is passed to the callback function and
        returned text is stored as a rendered result.
        One regex may have multiple callbacks; they will be run against the text in order they are found on the list.

        This is useful e.g. when you have Markdown documents as partials as you can convert them to HTML.
        """
        self._post.append( (regex, callback) )
        return self

    def _partialPostRender(self, path, text):
        """Applies post-renderers to a text.
        """
        for regex, callback in self._post:
            if re.compile(regex).match(path): text = callback(text)
        return text

    def render(self):
        """Renders parsed tree.
        """
        rendered = ''
        for el in self._tree:
            engine = Engine(el)
            if type(el) in [Section, Inverted]:
                s = el.render(engine=engine, context=self._context, lookup=self._lookup, missing=self._missing, newline=self._newline)
            elif type(el) is Partial:
                s = el.render(engine=engine, context=self._context, lookup=self._lookup, missing=self._missing, newline=self._newline)
                s = self._partialPostRender(el.getpath(), s)
            elif type(el) is Newline:
                s = el.render(engine, self._newline)
            else:
                s = el.render(engine=engine, context=self._context)
            rendered += s
        return rendered

def render(tree, context, lookup, missing=False, newline=None):
    """Renders string from raw list of nodes.
    """
    return Renderer(tree, context, lookup, missing, newline).render()
