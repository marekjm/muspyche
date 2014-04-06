from . import util
from . import models
from . import parser
from . import renderer


def make(temp, ctxt):
    return renderer.render(parser.parse(temp), ctxt)
