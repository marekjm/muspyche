## To-do list of Muspyche

### General

- improve in-code documentation,
- add `manual/` directory and write manuals for Muspyche there,

----

### Mustache features

- fix bug that causes comments containg `}}` string to be incorrectly parsed,

----

### Mustache 2.0 features

- implement access to global scope (partly finished, is supported for variables inside sections),
- implement *else* notation (section-inverted-close),
- implement negated variables (`{{~foo}} Some code {{/foo}}`),
