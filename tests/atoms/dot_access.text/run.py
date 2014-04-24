#!/usr/bin/env python3

import difflib
import json
import os
import sys

import muspyche

# td -- test directory
td = os.path.join(os.path.split(__file__)[0])

expected = muspyche.util.read(os.path.join(td, 'expected.txt'))

context = json.loads(muspyche.util.read(os.path.join(td, 'context.json')))
template = muspyche.util.read(os.path.join(td, 'template.mustache'))

print(muspyche.parser.parse(template))

actual = muspyche.api.make(template, context, lookup=[td])

if '--verbose' in sys.argv: print(actual, end='')

[print(line) for line in difflib.unified_diff(expected.splitlines(), actual.splitlines(), fromfile='expected', tofile='actual')]

# reverts boolean comparison: yields 1 if not equal, and 0 if equal
# used to return exit code to console
exit(not int(actual == expected))
