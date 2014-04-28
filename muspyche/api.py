"""This is high-level API for Muspyche.
Use it if you do not want to deal with separate
parsing, expanding and rendering of templates.
"""

from . import parser, renderer


def make(template, context, lookup=[], missing=False):
    """This function will *make the template rendered*.

    * `template` - a string containing Mustache template,
    * `context` - a dictionary containing context for given template,
    * `lookup` - list of diretories to look partials and injections up in,
    * `missing` - boolean, if true missing partials and injections will coerce to empty strings,

    It returns string containg template rendered against given context.
    """
    parsed = parser.parse(template, lookup, missing)
    return renderer.render(parsed, context, context, lookup, missing)
