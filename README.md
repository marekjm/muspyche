## Muspyche

> *Yet another Mustache library*

Muspyche is a Mustache templating framework library for Python 3.
It was forked from [Pystache](https://github.com/defunkt/pystache) library.


----


### Features

Here is a quick overview of Muspyche features.

### Vanilla

Muspyche supports great majority of vanilla Mustache features.
The only missing one is setting non-standard delimiters and
there are currently no plans to implement it.

### Extensions

Muspyche supports few extensions of Mustache (which are features of Mustache 2.0).

**Access to fields in context using dot-notation**

With Muspyche it is possible to use nested dictionaries in context and
access their values using familiar dot-notation.

Consider this context:

```
{
    "foo": {
        "bar": "Hello World!"
    }
}
```

Using this context, the following template...

```
{{foo.bar}}
```

... would render as `Hello World!`.

----

**Global context access**

This extension lets template writers access global context from whatever place in their templates they want.
Using global context for variable resolution is indicated by placing to colons - `::` - before the variable key.

Global context extension can be combined with dot-notation extension; however, only the first key can be preceded by
global-context indicator.


---


**Written for Python 3**

Muspche was started after the release of Python 3.4 (in April, 2014).
This means that by default the language grants it two things that are
extremely important for templating framework:

- full Unicode support,
- clear distinction of bytes and text.

At the moment, Muspyche does not aim to be compatible with programs written
in Python 2.x.


----

### License

Muspyche is licensed under GNU GPL v3 or GNU LGPL v3.

The choice of the license under which to use the library
is left to the User.

Full text of the GNU GPL v3 license: https://gnu.org/licenses/gpl.txt
