"""This file contains context stack implementation for Muspyche.
"""


import html


class ContextStack:
    """Object implementing context stack.
    """
    def __init__(self, context):
        self._global, self._current = {}, {}
        self._stack = {}
        self._adjusts = []
        self._locked = False
        for k, v in context.items(): self._global[k] = v
        self._toglobal()

    def __iter__(self):
        """Returns iterator for current context.
        """
        if type(self._current) == list:
            l = []
            for i in self._current:
                context = ContextStack(self._global)
                context._current = i
                context.lock()
                l.append(context)
        else:
            l = self._current
        return iter(l)

    def _toglobal(self):
        """Makes global context become current context.
        """
        self._current = {}
        for k, v in self._global.items(): self._current[k] = v
        for k, v in self._current.items():
            self._stack[k] = v

    def current(self):
        return self._current

    def adjust(self, path, store=True):
        """Adjusts current context.
        """
        if path and store:
            self._adjusts.append(path)
        if path.startswith('::'):
            path = path[2:]
            self._toglobal()
        parts = (path.split('.') if path else [])
        for part in parts:
            if type(self._current) == bool: break
            if part in self._current:
                self._current = self._current[part]
            else:
                self._current = {}
                break
        try:
            for k, v in self._current.items():
                self._stack[k] = v
        except AttributeError:
            pass
        finally:
            pass
        return self

    def restore(self):
        """Restores current context to previous state.
        """
        if self._adjusts: self._adjusts.pop(-1)
        path = '::' + '.'.join(self._adjusts)
        self.adjust(path, store=False)

    def lock(self):
        """When context is locked it will stay in the same context and
        any adjustments made by .get() will be atomic to single calls.
        """
        self._locked = True

    def unlock(self):
        """Unlock context.
        """
        self._locked = False

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
        Key is a string that may contain dots (access specifiers) and double-colons (global context switches).
        Key may be just a single dot, in which case it will yield what is currently on top of _current context.
        Non-list, non-string values are automatically coerced to empty strings before being returned.
        """
        value = ''
        path, key = self.split(key)
        #print('path:', repr(path))
        #print('key:', repr(key))
        if path: self.adjust(path)
        if key == '.':
            value = self._current
        else:
            value = (self._stack[key] if key in self._stack else '')
        if type(value) is not str: value = str(value)
        if escape: value = html.escape(str(value))
        if path and self._locked: self.restore()
        return value

    def keys(self):
        """Returns keys on the stack.
        """
        return self._stack.keys()
