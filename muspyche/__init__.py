from . import util
from . import models
from . import parser
from . import renderer


def make(temp, ctxt):
    return renderer.renderlist(parser.assemble(parser.decomment(parser.quickparse(temp))), ctxt)
