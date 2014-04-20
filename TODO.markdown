## To-do list of Muspyche

### General

- improve in-code documentation,
- add `manual/` directory, write manuals for Muspyche and place 'em there,
- add *context lookup* feature for partials (can use the same lookup paths and resolution methods as partial resolving code),


----

### Mustache features

- fix bug that causes comments containg `}}` string to be incorrectly parsed,


----

### Mustache 2.0 features

- implement access to global scope (partly finished, is supported for variables inside sections, maybe for other elements),
- implement *else* notation (section-inverted-close),


----

### Extended features

**Uber- or meta-templates**

> TODO: description

Steps:

- create a way to make writing meta-templates (or maybe *uber-*?) - which could be used as a templates for templates - possible,
- implement hook-syntax: `{{@hook}}` - this token would be substituted with *injections*,
- implement injection-syntax (a.k.a. *reverse partial* syntax): `{{<uber:hook}}` (opening), `{{~uber:hook}}`;
  this will read template `uber`, replace hook `hook` inside it with what was between injection tags, insert actual injection tokens as subtitute for tokens describing injection,

Behaviour:

template: `uber`

```
print("{{@text}}")
```

template: `main`

```
#!/usr/bin/python3

{{<uber:text}} {{string}} {{~uber:text}}
```

context for `main`: `{"string": "Hello World!"}`

Template `main` is being parsed.  
Expected outcome:

- as a dumped template, with the unnecessary whitespace not stripped):

```
#!/usr/bin/python3

print(" {{string}} ")

```

- as a rendered text:

```
#!/usr/bin/python3

print(" Hello World! ")

```


----

### Already achievable tricks that may get dedicated syntax (i.e. become features)

**Negated variables**

- implement negated variables (`{{~foo}} Some code {{/foo}}`) -- there already is a way to achieve this:
  inerts get single dict as input will parse just once with this dict as context so these two pieces of code
  yield the same result in rendered document: `{{~foo}} Some code {{/foo}}` (proposed) and `{{^foo}} Some code {{/foo}}` (implemented in Mustache 1.0).
