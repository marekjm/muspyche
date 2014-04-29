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


path = os.path.normpath(os.path.join(os.path.split(__file__)[0], '..', 'spec', 'specs', '*.json'))
tmp = os.path.normpath(os.path.join(os.path.split(__file__)[0], 'tmp'))


FAILFAST = '--failfast' in sys.argv


specs = glob.glob(path)
required, optional = [], []
for i in specs: (optional if os.path.split(i)[1].startswith('~') else required).append(i)
#print('required:', required)
#print('optional:', optional)

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


stop = False
for path, case in required:
    temp, data, got, expexted = '', {}, '', ''
    for test in case['tests']:
        partials = (test['partials'] if 'partials' in test else {})
        for key, value in partials.items(): dump(os.path.join(tmp, key), value)
        title = '{0}: {1}: "{2}"'.format(path, test['name'], test['desc'])
        print('testing: {0}'.format(title), end='')
        got = muspyche.api.make(template=test['template'], context=test['data'], lookup=[tmp], missing=True)
        n = len(title) + len('testing: ')
        print('\b'*n, end='')
        print(' ' * n, end='')
        print('\b'*n, end='')
        ok = got == test['expected']
        print('{0}: {1}'.format(('OK' if ok else 'FAIL'), title))
        for i in [x for x in os.listdir(tmp) if not x.startswith('.')]: os.remove(os.path.join(tmp, i))
        if not ok and FAILFAST:
            stop = True
            temp, data = test['template'], test['data']
            expected = test['expected']
            break
    if stop:
        print('template:', temp)
        print('context:', data)
        [print(line) for line in difflib.unified_diff(expected.splitlines(), got.splitlines(), fromfile='expected', tofile='got')]
        break
