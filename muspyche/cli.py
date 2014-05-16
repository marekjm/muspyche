#!/usr/bin/env python3

"""Muspyche simple CLI interface (from Muspyche version {0}).

USAGE:

    muspyche <template>
    muspyche <template>.mustache [<context>.json]
    muspyche <template>.mustache <context>.json [<output>]

DESCRIPTION:

    In the absence of <context> it is assumed by the program that that there should
    be a file named <template>.json which will contain the context.

    Templates may be given without '.mustache' extension. Program will look first for
    the exact name, then - if not found - will append '.mustache' to the filename and search again.
    The extension will not be appended if the file already ends with '.mustache'.

    This simplest form of invocation is:    myspyche foo
    which translates to:                    myspyche foo.mustache foo.json

    If <output> is specified it is assumed to be a file into which rendered text should be written.
    If it is not specified, content is written to standard output (not print(...)'ed).

OUTPUT:

    Output is printed to standard output (woth Python print() function).

EXAMPLES:

    muspyche <template>
        
        Muspyche will assume that <template> should be used as a base for both template and context.
        Template will be <template>.mustache and context <template>.json

    muspyche <template>.mustache

        Muspyche will assume that <template> should be used as a base for both template and context.
        Context will be <template>.json

    muspyche <template>.mustache <context>.json

        No assumptions are needed, template and context are as supplied.

    muspyche <foo>.json <bar>.mustache

        Muspyche assumes that the operands ending with .json are context, and those ending with .mustache, and
        that template comes first.
        If two operandas are given and first ends with .mustache and second with .json they are switched.
"""

import json
import os
import sys

import muspyche


args = sys.argv[1:]

# If there are no operands, display help message and exit
if len(args) == 0:
    print(__doc__.format(muspyche.__version__), end='')
    exit(0)

# Check if number of operands outside of valid range
if len(args) > 3:
    print('fail: invalid number of operands: expected number between 1 and 3 but got {0}'.format(len(args)))
    exit(1)


# Extract base template and context paths
TEMPLATE = args.pop(0)
CONTEXT = (args.pop(0) if args else '')
OUTPUT = (args.pop(0) if args else '')


# If template ends with '.json' and context ends with '.mustache'
# assume they should be switched
if TEMPLATE.endswith('.json') and CONTEXT.endswith('.mustache'): CONTEXT, TEMPLATE = TEMPLATE, CONTEXT


# Check if template can be found
if not os.path.isfile(TEMPLATE) and TEMPLATE.endswith('.mustache'):
    print('fail: cannot find template: {0}'.format(TEMPLATE))
    exit(1)

# Check if template can be found while trying to adjust the path
if not os.path.isfile(TEMPLATE) and not TEMPLATE.endswith('.mustache'):
    candidate = TEMPLATE + '.mustache'
    if os.path.isfile(candidate):
        TEMPLATE = candidate[:]
    else:
        print('fail: cannot find template: {0}'.format(TEMPLATE))
        exit(1)

# Deduce context path from template path if context was not given
if not CONTEXT: CONTEXT = (os.path.splitext(TEMPLATE)[0] if TEMPLATE.endswith('.mustache') else TEMPLATE) + '.json'

# Check if context is present
if not os.path.isfile(CONTEXT):
    print('fail: cannot find context for template: {0}'.format(TEMPLATE))
    exit(1)


#print('template = "{0}"'.format(TEMPLATE))
#print('context  = "{0}"'.format(CONTEXT))

ifstream = open(TEMPLATE, 'r')
TEMPLATE = ifstream.read()
ifstream.close()


ifstream = open(CONTEXT, 'r')
try:
    CONTEXT, err = json.loads(ifstream.read()), None
except ValueError as e:
    print('fail: invalid context: {0}'.format(e))
    err = e
except (Exception) as e:
    print('fatal: unhandled exception: {0}: {1}'.format(str(type(e))[8:-1], e))
finally:
    if err is not None: exit(1)
ifstream.close()


tree = muspyche.parser.parse(TEMPLATE)
renderer = muspyche.renderer.Renderer(tree, muspyche.context.ContextStack(CONTEXT))

ostream = (sys.stdout if not OUTPUT else open(OUTPUT, 'w'))
ostream.write(renderer.render())
if OUTPUT: ostream.close()
