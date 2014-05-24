#!/usr/bin/env python3

"""Tests for context stack implementation.
"""

import unittest

import muspyche


class StandalonenessTests(unittest.TestCase):
    def testStandaloneLine(self):
        temp = '''Stuff:\n{{#stuff}}\n  * {{foo}},\n{{/stuff}}\n'''
        parsed = muspyche.parser.parse(temp)
        print(parsed)


if __name__ == '__main__':
    unittest.main()
