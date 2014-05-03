#!/usr/bin/env python3

"""This file runs spec tests to check
if Muspyche conforms to the specification for Mustache.
"""

import difflib
import glob
import json
import os
import shutil
import sys

import muspyche


print('using myspyche v. {0}'.format(muspyche.__version__))


path = os.path.normpath(os.path.join(os.path.split(__file__)[0], '..', 'spec', 'specs', '*.json'))
tmp = os.path.normpath(os.path.join(os.path.split(__file__)[0], 'tmp'))


# Flow flags
FAILFAST = '--failfast' in sys.argv

# Reporting flags
QUIET = '--quiet' in sys.argv
SHOW_FAILS = '--show-fails' in sys.argv
REPR = '--repr' in sys.argv
PRINT_PARSED = '--print-parsed' in sys.argv or '-P' in sys.argv

# Test coverage flags
NO_SKIP = '--no-skip' in sys.argv
NO_DROP = '--no-drop' in sys.argv
FULL_COVERAGE = '--run-all' in sys.argv


specs = glob.glob(path)
required, optional = [], []
for i in specs: (optional if os.path.split(i)[1].startswith('~') else required).append(i)

def loadjson(path):
    ifstream = open(path)
    content = json.loads(ifstream.read())
    ifstream.close()
    return content

def dump(path, string):
    ofstream = open(path, 'w')
    ofstream.write(string)
    ofstream.close()


required = [(i, loadjson(i)) for i in required if ('comments' not in i and 'delimiters' not in i)] # let's skip comments for now and we don't support delimiter changing


SKIP = [
        'Doubled',
        'Standalone Lines',

        'Indented Standalone Lines',
        'Indented Inline Sections',


        'Standalone Line Endings',
        'Standalone Indented Lines',
        'Standalone Indentation',

        'Standalone Without Newline',
        'Standalone Without Previous Line',
        ]

DROP = [
        'Deeply Nested Contexts',
        ]

if NO_SKIP or FULL_COVERAGE: SKIP = []
if NO_DROP or FULL_COVERAGE: DROP = []


def dewhitespace(s):
    """Remove all whitespace from string.
    """
    for i in [' ', '\r\n', '\n', '\t']: s = ''.join(s.split(i))
    return s


stop = False
done, passed = 0, 0
skipped, dropped = 0, 0
for path, case in required:
    temp, data, got, expexted = '', {}, '', ''
    parsed = []
    for test in case['tests']:
        partials = (test['partials'] if 'partials' in test else {})
        for key, value in partials.items(): dump(os.path.join(tmp, key), value)
        title = '{0}: {1}: "{2}"'.format(path, test['name'], test['desc'])
        if not QUIET: print('testing: {0}'.format(title), end='')
        n = len(title) + len('testing: ')
        if not QUIET: print('\b'*n, end='')
        if not QUIET: print(' ' * n, end='')
        if not QUIET: print('\b'*n, end='')
        if test['name'] in SKIP:
            if not QUIET: print('SKIPPED: {0}'.format(title))
            skipped += 1
            continue
        if test['name'] in DROP:
            if not QUIET: print('DROPPED: {0}'.format(title))
            dropped += 1
            continue
        parsed = muspyche.parser.parse(template=test['template'])
        context = muspyche.context.ContextStack(context=test['data'], global_lookup=(test['name'] == 'Deeply Nested Contexts'))
        got = muspyche.renderer.render(parsed, context, lookup=[tmp], missing=True, newline=('\r\n' if r'\r\n' in test['desc'] else '\n'))
        ok = got == test['expected']
        information = (dewhitespace(got) == dewhitespace(test['expected']))
        if not QUIET or not ok: print('{0}: {1}'.format(('OK' if ok else ('FAIL' if not information else 'FORMATTING_FAIL')), title))
        for i in [x for x in os.listdir(tmp) if not x.startswith('.')]: os.remove(os.path.join(tmp, i))
        done += 1
        passed += (1 if ok else 0)
        if not ok and FAILFAST:
            stop = True
            temp, data = test['template'], test['data']
            expected = test['expected']
            break
    if stop:
        print('template:', (repr(temp) if REPR else temp))
        if PRINT_PARSED: print('parsed:', parsed)
        print('expected:', (repr(expected) if REPR else expected))
        print('got:', (repr(got) if REPR else got))
        print('context:', data)
        diff = difflib.unified_diff(expected.splitlines(), got.splitlines(), fromfile='expected', tofile='got')
        [print(line) for line in diff]
        break


if not FAILFAST or passed == done:
    all = done + skipped + dropped
    skipped = ('+{0} skipped'.format(skipped) if SKIP else '')
    dropped = ('+{0} dropped'.format(dropped) if DROP else '')
    moar = '({0}% with {1}{2}{3})'.format(round(passed/all*100, 2), skipped, (', ' if dropped and skipped else ''), dropped)
    if all == done: moar = ''
    print('tests passed: {0}/{1}{2} ({3}%) {4}'.format(passed, done, (':{0}'.format(all) if all != done else ''), round((passed/done*100), 2), moar))
