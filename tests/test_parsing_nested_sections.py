import muspyche

tmplt = '''{{heading}}

{{#movies}}
    {{title}}

    Characters:
    {{#chars}}
    * {{name}}
    {{/chars}}
    {{^chars}}
    There are no characters.
    {{/chars}}
{{/movies}}
{{^movies}}
There are no movies
{{/movies}}
'''

context = {'heading': 'Movies',
           'movies': [
               {'title': 'Star Wars (original trilogy)',
                'chars': [{'name': 'Yoda'},
                          {'name': 'Darth Vader'},
                          {'name': 'The Emperor'},
                          {'name': 'Obi-Wan Kenobi'},
                          {'name': 'Han Solo'},
                          {'name': 'Chewbacca'},
                          {'name': 'Luke Skywalker'},
                          {'name': 'Leia Skywalker'},
                ],
               },
               {'title': 'Star Wars (prequels)',
                'chars': [],
               },
               {'title': 'The Matrix',
               },
           ]
}


parsed = muspyche.parser.decomment(muspyche.parser.quickparse(tmplt))
#print(len(parsed), parsed)
#print(muspyche.parser.getdebugstring(parsed, indent=4))

assembled = muspyche.parser.assemble(parsed)
print(len(assembled), assembled)
print(muspyche.parser.getdebugstring(assembled[2]._template))

#print(muspyche.parser.getdebugstring(assembled, indent=4))

print('\n\n\n' + muspyche.parser.renderlist(muspyche.parser.assemble(parsed), context))
