#!/usr/bin/env python3

"""Tests for context stack implementation.
"""

import unittest

import muspyche


class ContextStackTests(unittest.TestCase):
    def testGettingSimpleKeys(self):
        context = {'foo': 'bar'}
        stack = muspyche.context.ContextStack(context)
        self.assertEqual('bar', stack.get('foo'))

    def testGetingNonexistetKeysYieldsEmptyString(self):
        context = {}
        stack = muspyche.context.ContextStack(context)
        self.assertEqual('', stack.get('foo'))

    def testGettingValuesFromNestedDicts(self):
        context = {'a': {'b': {'c': {'d': '---'}}}}
        stack = muspyche.context.ContextStack(context)
        self.assertEqual('---', stack.get('a.b.c.d'))

    def testGettingValuesFromAdjustedContext(self):
        context = {'a': {'b': {'c': {'d': '---'}}}}
        stack = muspyche.context.ContextStack(context)
        self.assertEqual('---', stack.adjust('a.b.c').get('d'))

    def testGettingValuesFromFullyAdjustedContextUsingSingleDotKey(self):
        context = {'a': {'b': {'c': {'d': '---'}}}}
        stack = muspyche.context.ContextStack(context)
        self.assertEqual('---', stack.adjust('a.b.c.d').get('.'))

    def testRestoringSimple(self):
        context = {'c': {'three': 3}, 'a': {'one': 1}, 'd': {'four': 4}, 'b': {'two': 2}, 'e': {'five': 5}}
        stack = muspyche.context.ContextStack(context)
        stack.adjust('a')
        self.assertEqual({'one': 1}, stack.current())
        stack.restore()
        self.assertEqual(context, stack.current())

    def testRestoringNested(self):
        context = {'a': {'one': 1, 'b': {'two': 2, 'c': {'three': 3}}}}
        stack = muspyche.context.ContextStack(context)
        self.assertEqual(context, stack.current())
        stack.adjust('a') # down to 'a'
        self.assertEqual(context['a'], stack.current())
        stack.restore()   # back to global
        self.assertEqual(context, stack.current())
        stack.adjust('a') # down to 'a'
        stack.adjust('b') # down to 'b'
        stack.adjust('c') # down to 'c'
        self.assertEqual(context['a']['b']['c'], stack.current())
        stack.adjust('::a.b.c') # from top to ::a.b.c
        stack.adjust('::a.b.c') # from top to ::a.b.c
        self.assertEqual(context['a']['b']['c'], stack.current())
        stack.restore()   # will remain in the same place because there were two sequential absolute adjusts to the same path performed
        self.assertEqual(context['a']['b']['c'], stack.current())
        stack.restore()   # back to 'c'
        stack.restore()   # back to 'b'
        self.assertEqual(context['a']['b'], stack.current())
        self.assertEqual('3', stack.get('c.three'))
        self.assertEqual('3', stack.get('::a.b.c.three'))
        self.assertEqual('3', stack.get('c.three'))

    def testGettingAbsoluteKeysDoesNotInfluenceAdjustment(self):
        context = {'home': '/', 'user': {'home': '~'}}
        stack = muspyche.context.ContextStack(context)
        stack.adjust('user')
        self.assertEqual('~', stack.get('home'))
        self.assertEqual('/', stack.get('::home'))
        self.assertEqual('~', stack.get('home'))

    def testStackBuilding(self):
        context = {'c': {'three': 3}, 'a': {'one': 1}, 'd': {'four': 4}, 'b': {'two': 2}, 'e': {'five': 5}}
        stack = muspyche.context.ContextStack(context)
        self.assertEqual({}, stack._stack)
        stack.adjust('a')
        self.assertEqual({'one': 1}, stack._stack)
        stack.adjust('b')
        self.assertEqual({'one': 1, 'two': 2}, stack._stack)

    def testParsingAccessPaths(self):
        s = 'a.b[3].c.d[0].e.::.a.b[]'
        expected = [('a', None),
                    ('b', 3),
                    ('c', None),
                    ('d', 0),
                    ('e', None),
                    ('::', None),
                    ('a', None),
                    ('b', 0),
                    ]
        got = muspyche.context.parsepath(s)
        self.assertEqual(expected, got)
        self.assertEqual([], muspyche.context.parsepath(''))

    def testDumpingAccessPaths(self):
        s = 'a.b[3].c.d[0].e.::.a.b[0]'
        self.assertEqual(s, muspyche.context.dumppath(muspyche.context.parsepath(s)))

    def testUsingSpecifiersForAccessPaths(self):
        s = 'a.b[2].c.d[0].e.::.a.b[]'
        context = {'a': {'b': ['OK', None, {'c': {'d': [{'e': {}}]}}]}}
        stack = muspyche.context.ContextStack(context)
        self.assertEqual('OK', stack.get(s))

if __name__ == '__main__':
    unittest.main()
