"""This file contains context stack implementation for Muspyche.
"""


import html
import re
import warnings


# issue warnings?
WARN = False


def parsepath(path):
    """Parses access path and
    returns specifiers to follow.
    """
    parts = (path.split('.') if path else [])
    indexed = re.compile('([a-zA-Z-_]*)\[([0-9]*)\]')
    for i, part in enumerate(parts):
        if indexed.match(part) is None:
            parts[i] = (part, None)
        else:
            match = indexed.match(part)
            parts[i] = (match.group(1), int(match.group(2) if match.group(2) else 0))
    return parts

def dumppath(parts):
    """Dumps parsed access path.
    """
    path = ''
    for i, item in enumerate(parts):
        part, index = item
        path += part
        if index is not None: path += '[{}]'.format(index)
        if i < len(parts)-1: path += '.'
    return path


class ContextStack:
    """Object implementing context stack.
    """
    def __init__(self, context):
        self._global, self._current = {}, {}
        self._stack = {}
        self._adjusts, self._stacks = [], []
        self._index = None
        for k, v in context.items(): self._global[k] = v
        self._toglobal()

    def __iter__(self):
        """Returns iterator for current context.
        """
        if type(self._current) == list:
            l = []
            for i, item in enumerate(self._current):
                context = ContextStack(self._global)
                context._current = item
                context._index = i
                context._adjusts = self._adjusts
                l.append(context)
        else:
            l = self._current
        return iter(l)

    def _toglobal(self):
        """Makes global context become current context.
        """
        self._current = {}
        for k, v in self._global.items(): self._current[k] = v

    def _updatestack(self):
        """Inserts values from current to stack.
        """
        try:
            keys = []
            for k, v in self._current.items():
                if k not in self._stack: keys.append(k)
                self._stack[k] = v
        except AttributeError:
            keys = []
        finally:
            self._stacks.append(keys)

    def current(self, stack=False):
        if stack:
            context = self
        else:
            context = self._current
        return context

    def adjust(self, path, store=True, global_lookup=False):
        """Adjusts current context.
        """
        if path and store:
            self._adjusts.append(path)
        parts = parsepath(path)
        for part, index in parts:
            if type(self._current) == bool: break
            if part.startswith('::'):
                self._toglobal()
                part = part[2:]
                if not part: continue
            if part in self._current:
                self._current = (self._current[part] if index is None else self._current[part][index])
            elif part in self._global and global_lookup:
                self._current = self._global[part]
            elif part == '' and index is not None:
                self._current = self._current[index]
            else:
                if WARN: warnings.warn('path cannot be resolved: "{0}": invalid part: {1}'.format(path, part))
                self._current = {}
                break
        self._updatestack()
        return self

    def restore(self):
        """Restores current context to previous state.
        """
        if self._adjusts: self._adjusts.pop(-1)
        path = '::' + '.'.join(self._adjusts)
        self.adjust(path, store=False)
        if self._index is not None: self._current = self._current[self._index]

    def split(self, path):
        """Splits context access path to namespace and key.
        """
        ns, key = '', ''
        if path == '.':
            key = '.'
        else:
            parts = path.split('.')
            key = parts.pop(-1)
            ns = '.'.join(parts)
        if not ns and key.startswith('::'):
            ns = '::'
            key = key[2:]
        return (ns, key)

    def get(self, key, escape=True):
        """Returns value associated with given key.
        Key is a string that may contain dots (access specifiers) and double-colons (global context switches),
        in such case an adjustemnt of context will be performed. Adjustemnts made by .get() are atomic to single call.
        Key may be just a single dot, in which case it will yield what is currently on top of _current context.
        Non-list, non-string values are automatically coerced to empty strings before being returned.
        """
        value = ''
        path, key = self.split(key)
        key, index = parsepath(key)[0]
        if path:
            self.adjust(path)
        if key == '.':
            value = self._current
        else:
            if type(self._current) is not dict:
                value = self.current()
            else:
                value = (self._current[key] if key in self._current else '')
                value = (value if index is None else value[index])
        if type(value) in [bool, int, float]: value = str(value)
        if type(value) is str and escape: value = html.escape(str(value))
        if path: self.restore()
        return value

    def keys(self):
        """Returns current keys.
        """
        return self._current.keys()
