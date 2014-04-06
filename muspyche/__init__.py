from . import util
from . import parser


def make(temp, ctxt):
    return parser.renderlist(parser.assemble(parser.decomment(parser.quickparse(temp))), ctxt)
