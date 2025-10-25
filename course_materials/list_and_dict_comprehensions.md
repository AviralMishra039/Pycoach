# List & Dict Comprehensions

A concise guide to Python **list** and **dict** comprehensions with syntax, examples, and nested loops. This Markdown covers basics, conditional comprehensions, nested comprehensions, performance notes, common pitfalls, and useful patterns you can reuse.

---

## Table of contents

1. Syntax overview
2. Simple list comprehensions
3. Conditionals in list comprehensions
4. Multiple `for` (nested loops) in list comprehensions
5. Common list-comprehension patterns
6. Dict comprehensions
7. Nested comprehensions (practical examples)
8. Generator expressions & set comprehensions
9. Performance considerations
10. Common pitfalls & tips
11. Quick reference & cheat-sheet

---

## 1. Syntax overview

**List comprehension** general form:

```py
[ expression for item in iterable if condition ]
```

- `expression` — expression that produces an element for the new list (can use `item`).
- `for item in iterable` — loop producing items.
- `if condition` — optional filter (keeps items where condition is `True`).

**Dict comprehension** general form:

```py
{ key_expr: value_expr for item in iterable if condition }
```

---

## 2. Simple list comprehensions

### Example: squares of numbers

```py
# classic for-loop version
squares = []
for n in range(6):
    squares.append(n * n)

# list comprehension (equivalent)
squares = [n * n for n in range(6)]
# squares -> [0, 1, 4, 9, 16, 25]
```

### Example: strings processing

```py
words = ["apple", "Banana", "Cherry"]
upper = [w.upper() for w in words]
# -> ['APPLE', 'BANANA', 'CHERRY']
```

---

## 3. Conditionals in list comprehensions

You can add an `if` filter at the end to include only items meeting a condition.

```py
nums = range(10)
even = [n for n in nums if n % 2 == 0]
# -> [0, 2, 4, 6, 8]
```

You can also use a conditional expression inside the `expression` to choose values:

```py
# use a conditional expression inside the comprehension
labels = ["even" if n % 2 == 0 else "odd" for n in range(6)]
# -> ['even', 'odd', 'even', 'odd', 'even', 'odd']
```

Note: `if` at the end *filters* items, while `... if ... else ...` is part of the value expression.

---

## 4. Multiple `for` (nested loops) in list comprehensions

You can write multiple `for` clauses separated in the comprehension — they behave like nested loops.

### Example: Cartesian product

```py
pairs = [(x, y) for x in [1, 2, 3] for y in ['a', 'b']]
# Equivalent to:
# pairs = []
# for x in [1,2,3]:
#     for y in ['a','b']:
#         pairs.append((x,y))
# pairs -> [(1,'a'), (1,'b'), (2,'a'), (2,'b'), (3,'a'), (3,'b')]
```

### Example: flattening a 2D list

```py
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
flat = [val for row in matrix for val in row]
# -> [1,2,3,4,5,6,7,8,9]
```

Order of `for` clauses matters: the left-most `for` is the outer loop.

---

## 5. Common list-comprehension patterns

### Filtering & mapping in one

```py
words = ['a', 'ab', 'abc', 'abcd']
res = [w.upper() for w in words if len(w) > 2]
# -> ['ABC','ABCD']
```

### Enumerating inside comprehension

```py
items = ['a','b','c']
indexed = [(i, v) for i, v in enumerate(items)]
# -> [(0,'a'), (1,'b'), (2,'c')]
```

### Conditional mapping (ternary in expression)

```py
nums = range(5)
labels = ['pos' if n > 0 else 'zero' for n in nums]
# -> ['zero','pos','pos','pos','pos']
```

---

## 6. Dict comprehensions

Create dictionaries from iterables using the `{k: v for ...}` syntax.

### Example: map numbers to their cubes

```py
cube_map = {n: n**3 for n in range(6)}
# -> {0:0, 1:1, 2:8, 3:27, 4:64, 5:125}
```

### Example: build a dict from two lists

```py
keys = ['name', 'age', 'city']
values = ['Ada', 28, 'Pune']
mydict = {k: v for k, v in zip(keys, values)}
# -> {'name':'Ada','age':28,'city':'Pune'}
```

### Example: invert a dict (values must be unique/hashable)

```py
orig = {'a':1, 'b':2}
inv = {v: k for k, v in orig.items()}
# -> {1:'a', 2:'b'}
```

---

## 7. Nested comprehensions (practical examples)

### Matrix transpose

```py
matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]

# transpose rows <-> columns
transpose = [[row[i] for row in matrix] for i in range(len(matrix[0]))]
# -> [[1,4,7],[2,5,8],[3,6,9]]
```

### Flatten with condition (2-level nested)

```py
matrix = [[1, -2, 3], [-4, 5]]
positive_flat = [x for row in matrix for x in row if x > 0]
# -> [1, 3, 5]
```

### Nested dict comprehension (grouping example)

Suppose we want a dictionary mapping first letters to list of words starting with that letter:

```py
words = ['apple', 'ape', 'banana', 'bob', 'carrot']
from collections import defaultdict
# comprehension approach (two-step) — first collect unique keys, then build lists
letters = sorted({w[0] for w in words})
grouped = {ch: [w for w in words if w[0] == ch] for ch in letters}
# -> {'a': ['apple','ape'], 'b':['banana','bob'], 'c':['carrot']}
```

Note: for complex grouping `defaultdict(list)` in a loop is usually clearer and sometimes faster.

---

## 8. Generator expressions & set comprehensions

- **Generator expression** (lazy evaluation): use `()` instead of `[]`.

```py
gen = (n*n for n in range(5))
# iterate with next() or for-loop, values computed on demand
```

- **Set comprehension** uses `{}` but with single expressions (not key:value):

```py
unique_lengths = {len(w) for w in ['a','bb','ccc','dd']}
# -> {1, 2, 3}
```

---

## 9. Performance considerations

- Comprehensions are usually faster and more concise than equivalent `for` loops because they are implemented in C and avoid repeated `append` calls.
- Generator expressions are memory-efficient for large datasets (they yield items one-by-one).
- For heavy or very complex operations, sometimes a `for` loop is clearer and the performance difference is negligible.

Benchmark tip: use `timeit` or `%timeit` in notebooks to compare for your specific case.

---

## 10. Common pitfalls & tips

- **Don't over-nest**: Nested comprehensions are concise but can be hard to read. If you need more than 2–3 levels, prefer regular loops or helper functions.
- **Mutable default traps**: avoid using mutable objects in comprehensions without care (e.g., building lists of the same sublist reference).
- **Dictionary comprehensions and duplicate keys**: if keys repeat, later values overwrite earlier ones — be explicit if duplicates are possible.
- **Readability > cleverness**: prioritize readable code for maintainability.

---

## 11. Quick reference & cheat-sheet

### List

```py
# squares
[n*n for n in range(5)]

# filter
[n for n in range(10) if n%2==0]

# nested
[a*b for a in [1,2] for b in [3,4]]
```

### Dict

```py
# from pairs
{k: v for k, v in [('a',1),('b',2)]}

# from items
{k: v*2 for k, v in some_dict.items()}
```

### Generator

```py
(n for n in range(10))
```

---

## Closing notes

Comprehensions are a powerful and expressive feature of Python. Use them for concise transformations and filters, but prefer clarity when working with complex logic. Save nested comprehension tricks for cases where they significantly improve readability or performance.

If you'd like, I can:

- export this as a `.md` file and provide a download link,
- convert the examples into a runnable Jupyter notebook,
- or create printable PDF notes from it.

