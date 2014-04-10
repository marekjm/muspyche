from . import util
from . import models
from . import parser
from . import renderer


__version__ = '0.0.1'


def make(template, context, lookup=[]):
    """This function will *make the template rendered*.
    It takes two parameters:

    * `template` - a string containing Mustache template,
    * `context` - a dictionary containing context for given template,

    It returns string containg template rendered against given context.
    """
    return renderer.render(parser.parse(template, lookup), context, context)
