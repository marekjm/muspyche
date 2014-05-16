## Uber- or meta-templates

Uber- or meta-templates (a.k.a. *injections*).

> TODO: description

**Behaviour:**

template: `uber`

```
print("{{@text}}")
```

template: `main`

```
#!/usr/bin/python3

{{<uber:text}} {{string}} {{/uber:text}}
```

context for `main`: `{"string": "Hello World!"}`

Template `main` is being parsed.  
Expected outcome:

- as a dumped template, with the unnecessary whitespace not stripped:

```
#!/usr/bin/python3

print(" {{string}} ")

```

- as a rendered text:

```
#!/usr/bin/python3

print(" Hello World! ")

```
