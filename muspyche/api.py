"""This is high-level API for Muspyche.
Use it if you do not want to deal with separate
parsing, expanding and rendering of templates.
"""

from . import parser, renderer


def make(template, context, lookup=[]):
    """This function will *make the template rendered*.
    It takes two parameters:

    * `template` - a string containing Mustache template,
    * `context` - a dictionary containing context for given template,

    It returns string containg template rendered against given context.
    """
    parsed = parser.parse(template, lookup)
    #print(parsed)
    #print(parsed[0].getname())
    #print(context)
    return renderer.render(parsed, context, context)
