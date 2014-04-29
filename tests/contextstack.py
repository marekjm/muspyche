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

    def testRestoring(self):
        context = {'a': {
                         'b': {
                               'c': {
                                     'd': {
                                           'e': 'E'
                                           },
                                     'f': 'F'
                               },
                               'g': 'G',
                               'h': {
                                     'i': 'I'
                               }
                         }
                   },
                   'z': 'Z'
                  }
        stack = muspyche.context.ContextStack(context)
        stack.adjust('a.b.c')
        stack.adjust('d')
        self.assertEqual('', stack.get('f'))
        self.assertEqual('E', stack.get('e'))
        stack.restore()
        self.assertEqual('F', stack.get('f'))
        self.assertEqual('', stack.get('e'))
        stack.adjust('::a.b.h')
        self.assertEqual('', stack.get('g'))
        self.assertEqual('I', stack.get('i'))
        stack.restore()
        self.assertEqual('F', stack.get('f'))
        self.assertEqual('', stack.get('i'))

    def testGettingAbsoluteKeysDoesNotInfluenceAdjustmentWhenLocked(self):
        context = {'home': '/', 'user': {'home': '~'}}
        stack = muspyche.context.ContextStack(context)
        stack.adjust('user')
        self.assertEqual('~', stack.get('home'))
        stack.lock()
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


if __name__ == '__main__':
    unittest.main()
