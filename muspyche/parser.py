import os
import re


from .models import *
from . import util


WARN = 0
DEBUG = 0
QUICKTEST = 0


def gettag(s):
    """Returns a tuple: (tag-type, tag-name, whole-match).
    Searches from the very beginning of given string.
    """
    literal = re.compile('^({)(.*?)}}}').search(s)
    normal = re.compile('^([@&#^/<>]?)(.*?)}}').search(s)
    comment = re.compile('^(!)(.*?)(.*\n)*}}').search(s)
    if comment is not None: match = comment
    elif literal is not None: match = literal
    elif normal is not None: match = normal
    else: match = None
    if match is None: raise Exception(repr(s))
    return (match.group(1), match.group(2).strip(), match.group(0))

def rawparse(template):
    """Split template into a list of nodes.
    """
    types = {'':  Variable,
             '!': Comment,
             '{': Literal,
             '&': Literal,
             '#': Section,
             '^': Inverted,
             '/': Close,
             '>': Partial,
             '<': Injection,
             '@': Hook,
             }
    tree = []
    text = ''
    i = 0
    opened = False
    template = template.replace('\r\n', '\n')
    while i < len(template):
        if template[i:i+2] == '{{':
            if text:
                tree.append( TextNode(text) )
                text = ''
            i += 2
            tagtype, tagname, whole = gettag(template[i:])
            if tagtype == '!':
                n = 1
                while i+n < len(template):
                    if template[i+n:].startswith('}}'):
                        n += 2
                        break
                    n += 1
                whole = ' ' * n
            elif tagtype == '#':
                tree.append( Section(tagname.strip(), []) )
            elif tagtype == '^':
                tree.append( Inverted(tagname.strip(), []) )
            elif tagtype == '<':
                tree.append( Injection(tagname.strip(), []) )
            elif tagtype == '/':
                tree.append( Close(tagname.strip()) )
            else:
                tree.append( types[tagtype](tagname.strip()) )
            i += len(whole)-1
        elif template[i] == '\n' or template[i:i+2] == '\r\n':
            if text:
                tree.append( TextNode(text) )
                text = ''
            tree.append( Newline(template[i]) )
        else:
            text += template[i]
        i += 1
    if text:
        tree.append( TextNode(text) )
        text = ''
    return tree

def _findpath(partial, lookup, missing):
    """This function tries to find a file matching given partial or injection name and
    return path to it.

    :param partial: name of the partial or injection given in template
    :param lookup: list of directories in which lookup for partials should be done
    :param missing: whether to allow missing partials or not

    Params explained:

    `lookup`: list[str]
        This is a list of directories which Muspyche will check when looking for partials that
        were not found in '.' directory.

    `missing`: bool
        Specify whether to allow missing partials (true) or not (false).
        If allowed, missing partials are represented by empty string.
        If not missing partials are not allowed and a partial cannot be found
        an exception is raised.

    Lookup sequence:

    Let given path be named `partial_path`, and current lookup path be named `lookup_path`.
    First lookup path is always '.' - current working directory.
    The sequence consists of following steps and is repeated for every lookup path:

        0.  lookup_path/partial_path
        1.  lookup_path/partial_path.mustache
        2.  lookup_path/partial_path/template.mustache

    Iterating over lookup paths stops after first match is found.
    """
    found, path = (False, partial)
    lookup.insert(0, '.')
    for base in lookup:
        trypath = os.path.join(base, path)
        if os.path.isfile(trypath):
            path = trypath
            found = True
            break
        trypath = '.'.join([os.path.join(base, path), 'mustache'])
        if os.path.isfile(trypath):
            path = trypath
            found = True
            break
        trypath = os.path.join(base, path, 'template.mustache')
        if os.path.isfile(trypath):
            path = trypath
            found = True
            break
    if not found and not missing:
        raise OSError('partial or injection could not be resolved: invalid path: {0}'.format(path))
    return (found, path)

def _resolvepartial(element, lookup, missing):
    """This function tries to find a file matching given partial path and
    return it as a parsed list.

    :param element: object representing Mustache partial element
    :param lookup: list of directories in which lookup for partials should be done
    :param missing: whether to allow missing partials or not
    """
    found, path = _findpath(element.getpath(), lookup, missing)
    if found: template = util.read(path)
    else: template = ''
    return expandpartials(rawparse(template), lookup, missing)

def expandpartials(tree, lookup=[], missing=False):
    """This function expands partials.

    :param tree: parse tree of Mustache nodes
    :param lookup: list of directories in which lookup for partials should be done
    :param missing: whether to allow missing partials or not
    """
    expanded = []
    for el in tree:
        if type(el) == Partial:
            expanded.extend(_resolvepartial(el, lookup, missing))
        else:
            expanded.append(el)
    return expanded

def _resolveinjection(element, lookup, missing):
    """This function tries to find a file matching given partial path and
    return it as a parsed list.

    :param element: object representing Mustache partial element
    :param lookup: list of directories in which lookup for partials should be done
    :param missing: whether to allow missing partials or not
    """
    found, path = _findpath(element.getpath(), lookup, missing)
    if found: template = util.read(path)
    else: template = ''
    return insertinjections(rawparse(template), lookup, missing)

def substituteHooks(tree, hook, tmplt):
    """Substitues hook with template.
    """
    new = []
    for i in tree:
        if type(i) == Hook and i.getname() == hook:
            new.extend(tmplt)
        else:
            new.append(i)
    return new

def insertinjections(tree, lookup=[], missing=False):
    """This function expands partials.

    :param tree: parse tree of Mustache nodes
    :param lookup: list of directories in which lookup for partials should be done
    :param missing: whether to allow missing partials or not
    """
    inserted = []
    for el in tree:
        if type(el) == Injection:
            injection = _resolveinjection(el, lookup, missing)
            injection = substituteHooks(injection, el.gethookname(), el._template)
            inserted.extend(injection)
        else:
            inserted.append(el)
    return inserted

def _getWrapHead(tree):
    wrapper, name = None, ''
    name = tree[0].getname()
    origin = tree.pop(0)
    wrapper = type(origin)
    return (wrapper, origin, name, tree)

def _wrap(tree, debug_prefix=''):
    wrapper, origin, name, tree = _getWrapHead(tree)
    sprefix = debug_prefix + ('^' if wrapper == Inverted else '#') + name + ':'
    if DEBUG: print('{0} started wrapping (wrapper: {1})'.format(sprefix, wrapper))
    n, wrapped = (0, [])
    closed = False
    while n < len(tree):
        el = tree[n]
        prefix = '{0} {1}:'.format(sprefix, n)
        i = 1
        if type(el) in (Section, Inverted):
            i, part = _wrap(tree[n:], debug_prefix=(prefix+' -> '))
        else:
            part = el
        wrapped.append(part)
        n += i
        last = wrapped[-1]
        if type(last) == Close and last.getname() == name:
            if DEBUG: print(prefix, 'closing after {0} elements(s)'.format(n))
            closed = True
            n += 1
            break
    if DEBUG: print('{0} finished wrapping'.format(sprefix))
    if closed:
        final = (n, wrapper(name, wrapped[:-1]))
    else:
        final = (1, origin)
    return final

def assemble(tree):
    """Returns assembled tree.
    Assembling includes, e.g. wrapping sections into single elements.
    """
    assembled = []
    i = 0
    while i < len(tree):
        el = tree[i]
        if type(el) in [Section, Inverted, Injection]:
            n, part = _wrap(tree[i:])
        else:
            part = el
            n = 1
        assembled.append(part)
        i += n
    return assembled

def _isspace(s, empty=False):
    """Returns true if string contains only space (` `) characters.
    """
    ok = (True if s else empty)
    for i in s:
        if not ok: break
        if i != ' ': ok = False
    return ok

def _hasfrontpadding(s, only=False):
    """Returns (bool, cut) tuple.
    Bool is true string has front padding and cut is the index at which padding ends.
    Padding without newline doesn't count.
    """
    n = s.find('\n')
    n = (n if n != -1 else len(s)+1)
    rn = s.find('\r\n')
    rn = (rn if rn != -1 else len(s)+1)
    has, cut = False, (n if n < rn else rn)
    if cut > 0 and _isspace(s[:cut], empty=True) or cut == 0: has = True
    if (cut == len(s)-1 and not only) or (cut > len(s)): has = False
    return has

def sreverse(s):
    """Reverses order of characters in string.
    """
    s = list(s)
    s.reverse()
    return ''.join(s)

def _hasbackpadding(s, only=False):
    """See _hasfrontpadding().
    """
    return _hasfrontpadding(s=sreverse(s), only=only)

def _isstandalone(tree, index):
    """Returns tuple containing information about whether given index in given tree is a standalone tag.
    Returned value is a 3-tuple: (standalone, where, cut)

    - standalone: actual info about whether the index is standalone or not,
    - where: where to use cut (useful only for standlone tags),
    - cut: cut to apply to a text of item (defined by `where`, useful only for standalone tags),
    """
    standalone, where, cut = False, '', 0
    if type(tree[index]) not in [Section, Close, Inverted]: return (standalone, where, cut)
    prev = (tree[index-1] if index > 0 else None)
    next = (tree[index+1] if index < len(tree)-1 else None)
    report = ''
    report += '[{0}, {1}] '.format(str(type(prev))[8:-2], str(type(next))[8:-2])
    report += 'index: {0} and object: {1} '.format(index, tree[index])
    if type(prev) is TextNode and type(next) is TextNode:
        text = next._text
        for i in range(len(text)):
            if text[i] not in [' ', '\n']:
                break
            if text[i] == '\n':
                standalone, where, cut = True, 'next', i+1
                break
        if not _hasbackpadding(prev._text) and not _hasfrontpadding(next._text):
            standalone = False
        if not _hasbackpadding(prev._text):
            standalone = False
        if not _hasfrontpadding(next._text):
            standalone = False
        if (tree[index].inline() if type(tree[index]) in [Section, Inverted] else True):
            standalone = False
        #if (prev._text[-1] != '\n' if prev._text else False) and not _hasbackpadding(prev._text): #_isspace(prev._text[prev._text.rfind('\n'):]):
        #    if QUICKTEST: print('[{0}] standalone = false; (newline not in last index of preceding text node: {1})'.format(index, repr(prev._text)))
        #    standalone = False
        if index == 1 and _isspace(prev._text) and _hasfrontpadding(next._text):
            if QUICKTEST: print('[{0}] standalone = true; (node is preceded only by indentation)'.format(index))
            standalone = True
            where = 'next,empty.prev'
        #if '\n' not in prev._text and (tree[index].inline() if type(tree[index]) in [Section, Inverted] else True):
        #    standalone = False
        if (prev._text[-1] == '\n' if prev._text else False) and (next._text[0] == '\n' if next._text else False):
            standalone = True
        if _hasbackpadding(prev._text) and _hasfrontpadding(next._text):
            standalone = True
            where = 'both'
    elif prev is None and type(next) is TextNode:
        report += '(appears to be the first element) '
        text = next._text
        for i in range(len(text)):
            if text[i] not in [' ', '\n']:
                break
            if text[i] == '\n':
                standalone, where, cut = True, 'next', i+1
                break
    elif type(prev) is TextNode and next is None:
        report += '(appears to be the last element) '
        text = prev._text
        for i in range(1, len(text)):
            i = -i
            if text[i] not in [' ', '\n']:
                break
            if text[i] == '\n':
                standalone, where, cut = True, 'prev', i
                break
    if QUICKTEST and standalone: print(report + ('standalone' if standalone else ''))
    return (standalone, where, cut)

def clean(tree):
    """Cleans tree from unneeded whitespace, newlines etc.
    Call it eye-candy for code.
    """
    cleaned = []
    i = 0
    while i < len(tree):
        item = tree[i]
        next = (tree[i+1] if i < len(tree)-1 else None)
        prev = (tree[i-1] if i > 0 else None)
        standalone, where, cut = _isstandalone(tree, i)
        if standalone:
            if where == 'prev':
                if QUICKTEST: print('prev:', repr(prev._text), end=' -> ')
                prev._text = prev._text[:cut]
                if QUICKTEST: print(repr(prev._text))
            elif where == 'next,empty.prev':
                if QUICKTEST: print('next (with emptying prev):', repr(next._text), end=' -> ')
                next._text = next._text[cut:]
                prev._text = ''
                if QUICKTEST: print(repr(next._text))
            elif where == 'empty.prev':
                prev._text = ''
            elif where == 'both':
                prev._text = prev._text.rstrip() + '\n'
                next._text = next._text.lstrip()
            else:
                if QUICKTEST: print('next:', repr(next._text), end=' -> ')
                next._text = next._text[cut:]
                if QUICKTEST: print(repr(next._text))
        cleaned.append(item)
        i += 1
    return cleaned

def parse(template, lookup=[]):
    curr = rawparse(template)
    final = []
    while True:
        next = assemble(clean(curr))
        next = insertinjections(next, lookup)
        if curr == next:
            final = next
            break
        curr = next
    return final
