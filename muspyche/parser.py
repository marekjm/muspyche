import os
import re


from .models import *


DEBUG = False


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


