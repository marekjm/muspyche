"""This module contains models of tags generated by the parser and
used by the renderer.
"""


import html


def renderlist(tree, context):
    """Renders string from raw list of nodes.
    """
    s = ''
    for el in tree:
        elrender = ''
        if type(el) in [Section, Inverted]:
            elrender = el.render( (context[el.getname()] if (el.getname() in context) else []) )
        else:
            elrender = el.render(context)
        s += elrender
    return s


class Tag:
    """Base class for various tags.
    """
    def __init__(self):
        pass

    def render(self, engine, context):
        return engine(self).render(context)


class Variable(Tag):
    """Class representing 'Variable' type of Mustache tag.
    """
    def __init__(self, key, escape=True, miss=True):
        self._key = key
        self._escaped = escape
        self._miss = miss

    def getkey(self):
        return self._key


class Literal(Variable):
    """Class representing unescaped variable.
    It is a wrapper returning Variable objects with `escape` param
    set to False.
    """
    def __new__(self, key):
        return Variable(key, escape=False)


class Section(Tag):
    """Class representing 'Section' type of Mustache tag.
    """
    def __init__(self, name, tmplt, *args):
        self._name = name
        self._template = tmplt

    def getname(self):
        return self._name


class Inverted(Section):
    """Class represetnting 'Inverted Section' type of Mustache tag.
    """
    pass


class Close(Tag):
    """Class representing section closing tag.
    """
    def __init__(self, name):
        self._name = name

    def getname(self):
        return self._name

    def render(self, context):
        return ''


class Negated(Section):
    """Class representing 'Negated' (think about it as 'inverted variable') type of Mustache tag.
    Note that this feature is non-standard and
    is not described in official Mustache spec.
    """
    pass


class Comment(Tag):
    """Class representing 'Comment' type of Mustache tag.
    """
    def render(self, *args, **kwargs):
        return ''


class TextNode(Tag):
    """Class representing plain text node.
    """
    def __init__(self, text):
        self._text = text


class Partial(Tag):
    """Class representing 'Partial' type of Mustache tag.
    """
    def __init__(self, path):
        self._path = path
