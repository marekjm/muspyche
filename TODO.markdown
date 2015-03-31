## To-do list of Muspyche

### General

In general, major refactoring is needed to once again achieve the simplicity the code had
before trying to pass spec tests.  
But let us put *result correctness over code correctness* and
first focus on passing the tests.

- move context-accessing code (advanced parts like `acc.ess::path[0].to..some[1].element`) to a different library,
- implement stand-aloneness detection,
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

- implement *else* notation (section-inverted-close),


----

### Extended features

#### Context grabs

Basic syntax: `@muspyche.grab(modifier=value,):path/file.json`

**Modifiers**:

- `type`*`=dict`*: *list*: defines type of element the string will be substituted with,
- `match`*`=glob`*: *regex*, *none*: defines method used to match names,
- `naming`*`=file`*: *full*, *no*: defines method used to match names,
- `append`*`=<name>`*: defines name of the element to which grabbed data should be appended,

Appending rules:

- if the *grab* is top-level, it becomes top-level element;
- if the string is in a list, it is removed from it and the resulting element is inserted in its place;
