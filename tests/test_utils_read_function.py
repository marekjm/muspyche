import muspyche

try:
    muspyche.utils.read('./assets/ascii_text.txt', encoding='utf-8')
    print('ascii as utf-8: pass')
except Exception as e:
    print('ascii as utf-8: fail: {0}: {1}'.format(type(e), e))
finally:
    pass

try:
    muspyche.utils.read('./assets/ascii_text.txt', encoding='ascii')
    print('ascii as ascii: pass')
except Exception as e:
    print('ascii as ascii: fail: {0}: {1}'.format(type(e), e))
finally:
    pass

try:
    muspyche.utils.read('./assets/unicode_text.txt', encoding='ascii')
    print('utf-8 as ascii: fail: expected exception not raised')
except UnicodeDecodeError as e:
    print('utf-8 as ascii: pass (expected exception: {0})'.format(type(e)))
except Exception as e:
    print('utf-8 as ascii: fail: unexpected exception: {0}: {1}'.format(type(e), e))
finally:
    pass

try:
    muspyche.utils.read('./assets/ascii_text.txt', encoding='ascii')
    print('utf-8 as utf-8: pass')
except Exception as e:
    print('utf-8 as utf-8: fail: {0}: {1}'.format(type(e), e))
finally:
    pass
