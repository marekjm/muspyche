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

- implement access to global scope (partly finished, is supported for variables inside sections),
- implement *else* notation (section-inverted-close),
- implement negated variables (`{{~foo}} Some code {{/foo}}`) -- there already is a way to achieve this:
  inerts get single dict as input will parse just once with this dict as context so these two pieces of code
  yield the same result in rendered document: `{{~foo}} Some code {{/foo}}` (proposed) and `{{^foo}} Some code {{/foo}}` (implemented in Mustache 1.0).
