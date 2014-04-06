import muspyche

v = muspyche.parser.Variable(key='foo')
print(v.render({'foo': '<h2>Hello World!</h2>'}))

v = muspyche.parser.Variable(key='foo', escape=False)
print(v.render({'foo': '<h2>Hello World!</h2>'}))

v = muspyche.parser.Variable(key='')
print(v.render({'foo': 'Hello World!'}))

v = muspyche.parser.Variable(key='foo')
print(v.render({'bar': 'Hello World!'}))

v = muspyche.parser.Variable(key='foo', miss=False)
print(v.render({'bar': 'Hello World!'}))

