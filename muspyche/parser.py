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


class ParsedTemplate:
    """
    Represents a parsed or compiled template.

    An instance wraps a list of node objects. A node
    object must have a `render(context)` method that accepts a
    context dictionary and returns a string.
    """
    def __init__(self, elems=[]):
        self._parse_tree = elems

    def __len__(self):
        return len(self._parse_tree)

    def __iter__(self):
        return iter(self._parse_tree)

    def __repr__(self):
        return repr(self._parse_tree)

    def cut(self, a, b=-1):
        return self._parse_tree[a:b]

    def add(self, node):
        """
        Arguments:

          node: a unicode string or node object instance.  See the class
            docstring for information.

        """
        self._parse_tree.append(node)

    def render(self, context):
        """
        Returns: a string of type unicode.

        """
        parts = map(lambda node: (node if type(node) is str else node.render(context)), self._parse_tree)
        s = ''.join([p for p in parts if p is not None])
        return str(s)


EOL_CHARACTERS = ['\r', '\n']
NON_BLANK_RE = re.compile(r'^(.)', re.M)


def _compile_template_re(delimiters):
    """
    Return a regular expresssion object (re.RegexObject) instance.

    """
    # The possible tag type characters following the opening tag,
    # excluding "=" and "{".
    tag_types = "!>&/#^"

    # TODO: are we following this in the spec?
    #
    #   The tag's content MUST be a non-whitespace character sequence
    #   NOT containing the current closing delimiter.
    #
    tag = r"""
        (?P<whitespace>[\ \t]*)
        %(otag)s \s*
        (?:
          (?P<change>=) \s* (?P<delims>.+?)   \s* = |
          (?P<raw>{)    \s* (?P<raw_name>.+?) \s* } |
          (?P<tag>[%(tag_types)s]?)  \s* (?P<tag_key>[\s\S]+?)
        )
        \s* %(ctag)s
    """ % {'tag_types': tag_types, 'otag': re.escape(delimiters[0]), 'ctag': re.escape(delimiters[1])}

    return re.compile(tag, re.VERBOSE)

class Parser:
    _delimiters = None
    _template_re = None

    def __init__(self, delimiters=('{{', '}}')):
        self._delimiters = delimiters

    def _compile_delimiters(self):
        self._template_re = _compile_template_re(self._delimiters)

    def _change_delimiters(self, delimiters):
        self._delimiters = delimiters
        self._compile_delimiters()

    def parse(self, template):
        """
        Parse a template string starting at some index.

        This method uses the current tag delimiter.

        Arguments:

          template: a unicode string that is the template to parse.

          index: the index at which to start parsing.

        Returns:

          a ParsedTemplate instance.

        """
        self._compile_delimiters()

        start_index = 0
        content_end_index, parsed_section, section_key = None, None, None
        parsed_template = ParsedTemplate()

        states = []

        while True:
            match = self._template_re.search(template, start_index)

            if match is None: break

            match_index = match.start()
            end_index = match.end()

            matches = match.groupdict()

            # Normalize the matches dictionary.
            if matches['change'] is not None:
                matches.update(tag='=', tag_key=matches['delims'])
            elif matches['raw'] is not None:
                matches.update(tag='&', tag_key=matches['raw_name'])

            tag_type = matches['tag']
            tag_key = matches['tag_key']
            leading_whitespace = matches['whitespace']

            # Standalone (non-interpolation) tags consume the entire line,
            # both leading whitespace and trailing newline.
            did_tag_begin_line = match_index == 0 or template[match_index - 1] in EOL_CHARACTERS
            did_tag_end_line = end_index == len(template) or template[end_index] in EOL_CHARACTERS
            is_tag_interpolating = tag_type in ['', '&']

            if did_tag_begin_line and did_tag_end_line and not is_tag_interpolating:
                if end_index < len(template):
                    end_index += template[end_index] == '\r' and 1 or 0
                if end_index < len(template):
                    end_index += template[end_index] == '\n' and 1 or 0
            elif leading_whitespace:
                match_index += len(leading_whitespace)
                leading_whitespace = ''

            # Avoid adding spurious empty strings to the parse tree.
            if start_index != match_index:
                parsed_template.add(template[start_index:match_index])

            start_index = end_index

            if tag_type in ('#', '^'):
                # Cache current state.
                state = (tag_type, end_index, section_key, parsed_template)
                states.append(state)

                # Initialize new state
                section_key, parsed_template = tag_key, ParsedTemplate()
                continue

            if tag_type == '/':
                if tag_key != section_key:
                    raise ParsingError("Section end tag mismatch: %s != %s" % (tag_key, section_key))

                # Restore previous state with newly found section data.
                parsed_section = parsed_template

                (tag_type, section_start_index, section_key, parsed_template) = states.pop()
                node = self._make_section_node(template, tag_type, tag_key, parsed_section,
                                               section_start_index, match_index)

            else:
                node = self._make_interpolation_node(tag_type, tag_key, leading_whitespace)

            parsed_template.add(node)

        # Avoid adding spurious empty strings to the parse tree.
        if start_index != len(template):
            parsed_template.add(template[start_index:])

        return parsed_template

    def _make_interpolation_node(self, tag_type, tag_key, leading_whitespace):
        """
        Create and return a non-section node for the parse tree.

        """
        # TODO: switch to using a dictionary instead of a bunch of ifs and elifs.
        if tag_type == '!':
            return Comment()

        if tag_type == '=':
            delimiters = tag_key.split()
            self._change_delimiters(delimiters)
            return _ChangeNode(delimiters)

        if tag_type == '':
            return Variable(tag_key)

        if tag_type == '&':
            return Literal(tag_key)

        if tag_type == '>':
            return Partial(tag_key, leading_whitespace)

        raise Exception("Invalid symbol for interpolation tag: %s" % repr(tag_type))

    def _make_section_node(self, template, tag_type, tag_key, parsed_section,
                           section_start_index, section_end_index):
        """
        Create and return a section node for the parse tree.

        """
        if tag_type == '#':
            return Section(tag_key, parsed_section, self._delimiters, template, section_start_index, section_end_index)
        if tag_type == '^':
            return Inverted(tag_key, parsed_section)
        raise Exception("Invalid symbol for section tag: %s" % repr(tag_type))


def parsex(template, delimiters=('{{', '}}')):
    """
    Parse a unicode template string and return a ParsedTemplate instance.

    Arguments:

      template: a unicode template string.

      delimiters: a 2-tuple of delimiters.  Defaults to the package default.

    Examples:

    >>> parsed = parse(u"Hey {{#who}}{{name}}!{{/who}}")
    >>> print(str(parsed).replace('u', ''))  # This is a hack to get the test to pass both in Python 2 and 3.
    ['Hey ', _SectionNode(key='who', index_begin=12, index_end=21, parsed=[_EscapeNode(key='name'), '!'])]

    """
    if type(template) is not str: raise Exception("Template is not unicode: %s" % type(template))
    parser = Parser(delimiters)
    parsed = parser.parse(template)
    finalized = []
    for i in parsed:
        if type(i) == str: finalized.append( TextNode(i) )
        else: finalized.append(i)
    return finalized

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
