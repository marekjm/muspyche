import muspyche

tags = ['{{tag}}',
        '{{~negated}}', # negated tag (non-standard, Mustache 2.0)
        '{{#section}}',
        '{{^inverted}}',
        '{{/closing}}',
        '{{&literal}}',
        '{{{literal}}}',
        '{{! comment}}',
        '{{!}}',    # empty comment
        '{{! this\nis\n\n a comment  \n}}',    # multiline comment
        '{{}}',     # empty
        '{{ }}',    # empty (with whitespace)
        ]


for t in tags:
    print(muspyche.parser.gettag(t[2:]))
