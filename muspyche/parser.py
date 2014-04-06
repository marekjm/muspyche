import html
import os
import re


DEBUG = False


class Tag:
    """Base class for various tags.
    Inheriting classes must override this all methods.
    """
    def __init__(self):
        pass

    def render(self):
        return ''


class Variable(Tag):
    """Class representing 'Variable' type of Mustache tag.
    """
    def __init__(self, key, escape=True, miss=True):
        self._key = key
        self._escaped = escape
        self._miss = miss

    def getkey(self):
        return self._key

    def render(self, context):
        s = ''
        if self._key not in context and not self._miss and self._key != '': raise KeyError('`{0}\' cannot be found in current context'.format(self._key))
        if self._key: s = (context[self._key] if self._key in context else '')
        if self._escaped: s = html.escape(str(s))
        return s


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

    def render(self, context):
        if DEBUG: print('context for section {0}: {1}'.format(self._name, context))
        s = ''
        if context == False or context == []:
            if DEBUG: print('context is empty')
            pass
        elif type(context) == list and len(context) > 0:
            if DEBUG: print('context is a list')
            for i in context:
                if DEBUG: print('  subcontext for section {0}:'.format(self._name), i)
                s += renderlist(self._template, i)
        elif type(context) == dict:
            if DEBUG: print('context is single dict')
            s = (self._template if type(self._template) == str else renderlist(self._template, context))
        else:
            raise TypeError('invalid type for context: expected list or dict but got {0}'.format(type(context)))
        if DEBUG: print('rendered:', repr(s))
        return s


class Close(Tag):
    """Class representing section closing tag.
    """
    def __init__(self, name):
        self._name = name

    def __repr__(self):
        return 'Close: {0}'.format(self._name)

    def getname(self):
        return self._name

    def render(self, context):
        return ''


class Inverted(Section):
    """Class represetnting 'Inverted Section' type of Mustache tag.
    """
    def render(self, context):
        s = ''
        if context == False or context == []: s = renderlist(self._template, context)
        return s


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

    def render(self, context):
        return self._text


class Partial(Tag):
    """Class representing 'Partial' type of Mustache tag.
    """
    pass


def gettag(s):
    """Returns a tuple: (tag-type, tag-name, whole-match).
    Searches from the very beginning of given string.
    """
    literal = re.compile('^({)(.*?)}}}').search(s)
    normal = re.compile('^([~&#^/>]?)(.*?)}}').search(s)
    comment = re.compile('^(!)(.*?)(.*\n)*}}').search(s)
    if comment is not None: match = comment
    elif literal is not None: match = literal
    elif normal is not None: match = normal
    else: match = None
    if match is None: raise Exception(s)
    return (match.group(1), match.group(2), match.group(0))

def quickparse(template, delimiters=('{{', '}}')):
    types = {'':  Variable,
             '~': Negated,
             '!': Comment,
             '{': Literal,
             '&': Literal,
             '#': Section,
             '^': Inverted,
             '/': Close,
             '>': Partial,
             }
    tree = []
    text = ''
    i = 0
    opened = False
    while i < len(template):
        if i+3 >= len(template): # this means template cannot include even one tag so there's no need for parsing
            text += template[i:]
            break
        if template[i:i+2] == delimiters[0]:
            if text:
                tree.append( TextNode(text) )
                text = ''
            i += 2
            tagtype, tagname, whole = gettag(template[i:])
            if tagtype == '!':
                tree.append( Comment() )
            elif tagtype == '#':
                tree.append( Section(tagname.strip(), []) )
            elif tagtype == '^':
                tree.append( Inverted(tagname.strip(), []) )
            elif tagtype == '~':
                tree.append( Negated(tagname.strip(), []) )
            elif tagtype == '/':
                tree.append( Close(tagname.strip()) )
            else:
                tree.append( types[tagtype](tagname.strip()) )
            i += len(whole)-1
        else:
            text += template[i]
        i += 1
    if text:
        tree.append( TextNode(text) )
        text = ''
    return tree

def _getWrapHead(tree):
    wrapper, name = None, ''
    name = tree[0].getname()
    wrapper = type(tree.pop(0))
    return (wrapper, name, tree)

def _wrap(tree, debug_prefix=''):
    wrapper, name, tree = _getWrapHead(tree)
    sprefix = debug_prefix + ('^' if wrapper == Inverted else '#') + name + ':'
    if DEBUG: print('{0} started wrapping (wrapper: {1})'.format(sprefix, wrapper))
    n, wrapped = (0, [])
    while n < len(tree):
        el = tree[n]
        prefix = '{0} {1}:'.format(sprefix, n)
        i = 1
        if type(el) in (Section, Inverted):
            if DEBUG: print(prefix, 'nested {0} with key {1}'.format(str(type(el))[8:-2], el.getname()))
            i, part = _wrap(tree[n:], debug_prefix=(prefix+' -> '))
            if DEBUG: print(prefix, 'jump is {0} and will land at element {1}'.format(i, tree[n+i]))
        else:
            if DEBUG: print(prefix, 'appending element {0} to wrapped list'.format(el))
            part = el
        wrapped.append(part)
        n += i
        last = wrapped[-1]
        if type(last) == Close and last.getname() == name:
            if DEBUG: print(prefix, 'closing after {0} elements(s)'.format(n))
            n += 1
            break
    if DEBUG: print('{0} finished wrapping'.format(sprefix))
    return (n, wrapper(name, wrapped[:-1]))

def assemble(tree):
    """Returns assembled tree.
    Assembling includes, e.g. wrapping sections into single elements.
    """
    assembled = []
    i = 0
    while i < len(tree):
        el = tree[i]
        if type(el) in [Section, Inverted]:
            n, part = _wrap(tree[i:])
        else:
            part = el
            n = 1
        assembled.append(part)
        i += n
    return assembled

def decomment(tree):
    return [el for el in tree if type(el) != Comment]

def getdebugstring(tree, indent=4):
    """Returns rendered string of elements in parsed template.
    """
    s = ''
    for el in tree:
        eltype = str(type(el))[8:-2]
        s += eltype
        if type(el) in [Section, Inverted, Close]:
            s += ': {0}'.format(el.getname())
            if type(el) in [Section, Inverted]:
                s += ' [\n' + getdebugstring(el._template) + ']'
        elif type(el) == Variable:
            s += ': {0}'.format(el.getkey())
        elif type(el) == TextNode:
            s += ': {0}'.format(repr(el._text))
        s += '\n'
    return s

def render(tree, context):
    """Renders parsed template.
    Returns string.
    """
    s = ''
    for elem in tree:
        if type(elem) in [Section, Inverted]: s += (elem.render(context[elem.getname()]) if elem.getname() in context else '')
        else: s += elem.render(context)
    return s

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
