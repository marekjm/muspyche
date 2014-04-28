## To-do list of Muspyche

### General

In general, major refactoring is needed to once again achieve the simplicity the code had
before trying to pass spec tests.  
But let us put *result correctness over code correctness* and
first focus on passing the tests.

- improve in-code documentation,
- add `manual/` directory, write manuals for Muspyche and place 'em there,
- add *context lookup* feature for partials (can use the same lookup paths and resolution methods as partial resolving code),
- refactor comments section in rawparse,
- improve support for comments,
- improve `parser.parse()` function (maybe refactor to `parser.assemble()`?),
- fully refactor resolving of partials to rendered,
- refactor models,
- refactor rendering engines so they once more have a unified API,


----

### Mustache features

- fix bug that causes comments containg `}}` string to be incorrectly parsed,


----

### Mustache 2.0 features

- implement access to global scope (partly finished, is supported for variables inside sections, maybe for other elements),
- implement *else* notation (section-inverted-close),


----

### Extended features


----

### Already achievable tricks that may get dedicated syntax (i.e. become features)

**Negated variables**

- implement negated variables (`{{~foo}} Some code {{/foo}}`) -- there already is a way to achieve this:
  inerts get single dict as input will parse just once with this dict as context so these two pieces of code
  yield the same result in rendered document: `{{~foo}} Some code {{/foo}}` (proposed) and `{{^foo}} Some code {{/foo}}` (implemented in Mustache 1.0).
