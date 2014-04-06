"""Module with various utility objects and functions
used across Muspyche modules.
"""

def read(path, encoding='utf-8'):
    """Reads a file and returns a string.

    By default treats file as Unicode text.
    """
    ifstream = open(path, 'rb')
    string = ifstream.read().decode(encoding)
    ifstream.close()
    return string
