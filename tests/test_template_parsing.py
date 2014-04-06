import muspyche


tmplt = '''{{greeting}}{{! this should be some nice greeting }}

{{{literal}}}

{{&literal}}

{{ normal }}}

{{#section}}
    {{say}}, {{name}}!
{{/section}}
{{^section}}
    Nothing.
{{/section}}

Foo!
'''

x = '''

{{#people}}
    <span> Hi, {{name}}! </span> <br>
{{/people}}
{{^people}}
    <span> Nobody's here... </span> <br>
{{/people}}

{{
'''

contxt = {'greeting': 'Hello World!',
        'groups': [
            {'group_name': 'x',
             'people': [{'name': 'You'}]
             },
            {'group_name': 'Star Wars',
             'people': [
                       {'name': 'Me'},
                       {'name': 'Yoda'},
                       {'name': 'Luke'},
                       {'name': 'Han'},
                       ]
             }
        ],
        'people': [
            {'name': 'Bob'},
            ],
        'literal': '<code>const int answer = 42;</code>',
        'normal': '<code>const int answer = 42;</code>',
        'section': [
            {'say': 'Arr', 'name': 'Jack'},
            {'say': 'Hi', 'name': 'Bob'},
            {'say': 'Hello', 'name': 'Julie'},
            {'say': 'Welcome', 'name': 'Amy'}
            ]
}

"""
print(p.parse(tmplt))
print(muspyche.parser.parse(tmplt))

for i in muspyche.parser.parse(tmplt):
    if type(i) in [muspyche.parser.Section, muspyche.parser.Inverted]:
        print(i.render(contxt[i.getname()]), end='')
    else:
        print(i.render(contxt), end='')
"""

print([str(type(i))[8:-2] for i in muspyche.parser.quickparse(tmplt)])

#print('\n')

#for el in muspyche.parser.quickparse(tmplt):
#    if type(el) in [muspyche.parser.Section, muspyche.parser.Inverted]:
#        print('{0}: {1}'.format(el, el._template))
#    else:
#        print('{0}: {1}'.format(el, repr(el.render(contxt))))


#print(muspyche.parser.render(muspyche.parser.quickparse(tmplt), contxt))
#print(muspyche.parser.render(muspyche.parser.ParsedTemplate(muspyche.parser.parse(tmplt)), contxt))
