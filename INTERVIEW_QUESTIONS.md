# Python Developer Interview Questions (Junior → Senior) with example

A study guide of commonly asked Python interview questions, grouped by level and
topic. Each question has a short model answer. Use the answers to check your own
reasoning. Interviewers usually ask follow-up questions, so be ready to explain
*why*, not just *what*.

**Levels**

| Level | Typical experience | Focus |
|---|---|---|
| Junior | 0–2 years | Syntax, data types, basic OOP, errors, standard library |
| Mid-level | 2–5 years | Idioms, decorators, generators, testing, concurrency, web/DB |
| Senior | 5+ years | Internals, performance, architecture, system design, leadership |

**Contents**

1. [Junior: Python Fundamentals](#1-junior-python-fundamentals)
2. [Junior: OOP Basics](#2-junior-oop-basics)
3. [Mid-level: Functions, Iterators, and Idioms](#3-mid-level-functions-iterators-and-idioms)
4. [Mid-level: Advanced OOP and Data Modeling](#4-mid-level-advanced-oop-and-data-modeling)
5. [Mid-level: Standard Library and Typing](#5-mid-level-standard-library-and-typing)
6. [Concurrency: Threads, Processes, asyncio](#6-concurrency-threads-processes-asyncio)
7. [Senior: CPython Internals and Performance](#7-senior-cpython-internals-and-performance)
8. [Senior: Architecture, Design, and Reliability](#8-senior-architecture-design-and-reliability)
9. [Web APIs and FastAPI](#9-web-apis-and-fastapi)
10. [Databases and SQLAlchemy](#10-databases-and-sqlalchemy)
11. [Testing](#11-testing)
12. [Security](#12-security)
13. [Tooling, DevOps, and Git](#13-tooling-devops-and-git)
14. [Predict the Output (Trick Questions)](#14-predict-the-output-trick-questions)
15. [Coding Exercises](#15-coding-exercises)
16. [System Design and Scenario Questions](#16-system-design-and-scenario-questions)
17. [Behavioral Questions](#17-behavioral-questions)
18. [Questions About This Project](#18-questions-about-this-project)

---

## 1. Junior: Python Fundamentals

1. **What is Python, and what are its key characteristics?**
   A high-level, general-purpose language. It is dynamically typed (types are
   checked at runtime) but strongly typed (`"1" + 1` raises an error). It supports
   procedural, OOP, and functional styles. CPython compiles source code to
   bytecode and runs it on a virtual machine.

2. **Is Python compiled or interpreted?**
   Both. CPython compiles `.py` files to bytecode (cached as `.pyc`), and the
   CPython virtual machine interprets that bytecode.

3. **What is the difference between a list and a tuple?**
   Lists are mutable; tuples are immutable. A tuple is hashable (usable as a dict
   key) if all its elements are hashable. Tuples use slightly less memory and
   signal "fixed structure".

4. **Which built-in types are mutable and which are immutable?**
   Mutable: `list`, `dict`, `set`, `bytearray`. Immutable: `int`, `float`,
   `bool`, `str`, `tuple`, `frozenset`, `bytes`.

5. **What is the difference between `is` and `==`?**
   `==` compares values (calls `__eq__`). `is` compares identity (same object in
   memory). Use `is` only for singletons such as `None`.
   example
   ```python
    a = [1, 2]
    b = [1, 2]
    a == b  # True, same values
    ````
6. **What are `*args` and `**kwargs`?**
   `*args` collects extra positional arguments into a tuple. `**kwargs` collects
   extra keyword arguments into a dict.

7. **Why is a mutable default argument dangerous?**
   Default values are evaluated once, when the function is defined, so every call
   shares the same list or dict. Use `None` and create the object inside:
   ```python
   def add(item, items=None):
       items = [] if items is None else items
       items.append(item)
       return items
   ```

8. **What is the difference between a shallow copy and a deep copy?**
   A shallow copy (`copy.copy`, `list[:]`) creates a new container that shares
   the same nested objects. A deep copy (`copy.deepcopy`) recursively copies the
   nested objects too.

9. **What is PEP 8?**
   The official Python style guide: naming, indentation, line length, imports,
   and so on. Tools like `ruff` and `black` enforce it.

10. **List comprehension vs generator expression?**
    `[x*x for x in data]` builds the whole list in memory. `(x*x for x in data)`
    produces values lazily, one at a time. Use generators for large or infinite
    data.

11. **How does a dictionary work internally?**
    It is a hash table: a key's hash determines where its value is stored.
    Average lookup, insert, and delete are O(1). Keys must be hashable. Since
    Python 3.7, dicts preserve insertion order.

12. **What is a set, and when would you use one?**
    An unordered collection of unique, hashable items with O(1) average
    membership tests. Use sets to remove duplicates, for fast `in` checks, and
    for union/intersection/difference.

13. **What is the difference between `append` and `extend`?**
    `append(x)` adds `x` as a single element. `extend(iterable)` adds each
    element of the iterable.

14. **What do `break`, `continue`, and `pass` do?**
    `break` exits the loop. `continue` skips to the next iteration. `pass` does
    nothing; it is a placeholder where a statement is required.

15. **What are truthy and falsy values?**
    Falsy: `None`, `False`, `0`, `0.0`, `""`, `[]`, `{}`, `set()`, `()`, and
    objects whose `__bool__` returns `False` or `__len__` returns 0. Everything
    else is truthy.

16. **Why is `"".join(parts)` preferred over `+=` in a loop for strings?**
    Strings are immutable, so `+=` may create a new string each time (O(n²)
    overall). `join` builds the result in a single pass.

17. **What are f-strings?**
    Formatted string literals: `f"{name} is {age}"`. They are readable, fast, and
    support expressions and format specifiers such as `f"{price:.2f}"`.

18. **How does slicing work?**
    `seq[start:stop:step]`. `stop` is exclusive. Negative indexes count from the
    end. `seq[::-1]` returns a reversed copy.

19. **What do `enumerate` and `zip` do?**
    `enumerate(items)` yields `(index, item)` pairs. `zip(a, b)` yields tuples
    pairing elements from each iterable and stops at the shortest. Use
    `zip(..., strict=True)` (Python 3.10+) to require equal lengths.

20. **Explain `try / except / else / finally`.**
    `try` runs code that may raise an exception.
    `except` handles errors. `else` runs only if no exception occurred.
    `finally` always runs, which makes it the place for cleanup.

21. **How do you create a custom exception?**
    Subclass `Exception` (not `BaseException`):
    `class InsufficientFundsError(Exception):
        pass`

    `BaseException
        ├── SystemExit
        ├── KeyboardInterrupt
        ├── GeneratorExit
        └── Exception
            ├── ValueError
            ├── TypeError
            ├── IndexError
            ├── KeyError
            └── ...
        ```

22. **Why use `with open(...)` for files?**
    The context manager closes the file automatically, even if an exception
    occurs.

23. **What does `if __name__ == "__main__":` do?**
    The code inside runs only when the file is executed directly, not when it is
    imported as a module.

24. **What is the difference between a module and a package?**
    A module is a single `.py` file. A package is a directory of modules (usually
    with an `__init__.py`) that can be imported as a namespace.

25. **What is the LEGB rule?**
    The order Python looks up names: Local → Enclosing → Global → Built-in. Use
    `global` or `nonlocal` to assign to outer-scope variables.

26. **What is a lambda function?**
    A small anonymous function made of a single expression:
    `sorted(users, key=lambda u: u.age)`.

27. **What do `map`, `filter`, and `functools.reduce` do?**
    `map` applies a function to each item. `filter` keeps items where the
    function returns a truthy value. `reduce` folds items into a single value.
    Comprehensions are often clearer.

28. **What is the difference between `sorted()` and `list.sort()`?**
    `sorted()` returns a new list and works on any iterable. `.sort()` sorts a
    list in place and returns `None`. Both accept `key=` and `reverse=`.

29. **What do `/`, `//`, `%`, and `**` do?**
    True division (always returns a float), floor division, modulo, and power.
    Python integers have arbitrary precision.

30. **Why is `0.1 + 0.2 != 0.3`?**
    Binary floating point cannot represent these decimals exactly. Use
    `math.isclose()` for comparisons and `decimal.Decimal` for money.

31. **What is a virtual environment, and why use one?**
    An isolated Python environment with its own installed packages
    (`python -m venv .venv`). It prevents version conflicts between projects.

32. **What is `requirements.txt`?**
    A list of a project's dependencies, installed with
    `pip install -r requirements.txt`.

33. **What is the difference between `remove`, `pop`, and `del` on a list?**
    `remove(x)` deletes the first matching value. `pop(i)` removes and returns
    the item at index `i` (the last item by default). `del lst[i]` deletes by
    index or slice.

34. **Name some useful dict methods.**
    `get(key, default)`, `setdefault`, `items`, `keys`, `values`, `pop`,
    `update`. Also `collections.defaultdict` and `collections.Counter`.

35. **How do you merge two dicts?**
    `a | b` (Python 3.9+) or `{**a, **b}`. On duplicate keys, the right-hand side
    wins.

36. **How do you swap two variables?**
    `a, b = b, a` (tuple packing and unpacking).

37. **Is checking `x in my_list` fast?**
    No. It is O(n). `x in my_set` and `key in my_dict` are O(1) on average.

38. **What do `type()`, `isinstance()`, `dir()`, and `help()` do?**
    `type()` returns an object's exact type. `isinstance()` checks the type,
    including subclasses (prefer it). `dir()` lists attributes. `help()` shows
    documentation.

39. **Does Python pass arguments by value or by reference?**
    Neither, exactly. It passes object references ("pass by assignment").
    Mutating a mutable argument affects the caller; rebinding the parameter does
    not.

40. **What is the walrus operator?**
    `:=` assigns inside an expression (Python 3.8+):
    `while (line := f.readline()):`.

---

## 2. Junior: OOP Basics

41. **What is the difference between a class and an object?**
    A class is a blueprint; an object is an instance created from it.

42. **What is `self`?**
    The instance a method is called on. It is passed automatically as the first
    argument.

43. **What is the difference between `__init__` and `__new__`?**
    `__new__` creates and returns the instance; `__init__` initializes it.
    Override `__new__` mainly for immutable types or for controlling instance
    creation.

44. **Instance variables vs class variables?**
    Instance variables (set on `self`) belong to one object. Class variables are
    shared by all instances. Beware of a mutable class variable, such as a list,
    shared by every instance.

45. **What are the four pillars of OOP?**
    Encapsulation, abstraction, inheritance, and polymorphism.

46. **How does Python handle private attributes?**
    By convention: `_name` means internal. `__name` triggers name mangling to
    `_ClassName__name`, which prevents accidental override in subclasses. It is
    not true privacy.

47. **What does `super()` do?**
    It calls the next method in the MRO (method resolution order). This is
    usually the parent class, and it makes cooperative multiple inheritance work.

48. **`@staticmethod` vs `@classmethod`?**
    A `classmethod` receives the class (`cls`) and is often used for alternative
    constructors. A `staticmethod` receives neither the instance nor the class;
    it is a plain function namespaced in the class.

49. **What does `@property` do?**
    It exposes a method as an attribute, enabling computed values, validation,
    and read-only access without changing the public API.

50. **`__str__` vs `__repr__`?**
    `__str__` is a readable string for end users. `__repr__` is an unambiguous
    string for developers, ideally one that could recreate the object. `print`
    uses `__str__` and falls back to `__repr__`.

51. **What are abstract base classes?**
    Classes that inherit from `abc.ABC` and have `@abstractmethod` methods. They
    cannot be instantiated until a subclass implements every abstract method.

52. **What are dunder (magic) methods? Give examples.**
    Special methods Python calls implicitly: `__len__`, `__eq__`, `__lt__`,
    `__hash__`, `__iter__`, `__getitem__`, `__enter__`, `__call__`, `__add__`.

53. **Composition vs inheritance?**
    Inheritance models an "is-a" relationship; composition models a "has-a"
    relationship. Prefer composition: it is more flexible and less tightly
    coupled. (This project's services *have* a repository; they do not inherit
    from one.)

54. **What are dataclasses?**
    `@dataclass` generates `__init__`, `__repr__`, and `__eq__` from type-annotated
    fields. Options include `frozen=True`, `slots=True`, `order=True`, and
    `field(default_factory=list)`.

---

## 3. Mid-level: Functions, Iterators, and Idioms

55. **What is a closure?**
    An inner function that remembers variables from its enclosing scope after
    the outer function has returned.

56. **What is a decorator? Write one.**
    A callable that takes a function and returns a new function that adds
    behavior:
    ```python
    import functools, time

    def timed(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                return func(*args, **kwargs)
            finally:
                print(f"{func.__name__}: {time.perf_counter() - start:.3f}s")
        return wrapper
    ```

57. **Why use `functools.wraps`?**
    It preserves the wrapped function's `__name__`, `__doc__`, and signature
    metadata, which matters for debugging, documentation, and frameworks.

58. **How do you write a decorator that takes arguments?**
    Add another level of nesting: a factory that receives the arguments and
    returns the real decorator, for example `@retry(times=3)`.

59. **Can you decorate a class? Can a class be a decorator?**
    Yes to both. A class decorator receives and returns a class. A class with
    `__call__` can act as a decorator.

60. **What is a generator?**
    A function that uses `yield`. It returns a lazy iterator, pauses at each
    `yield`, and keeps its state between values. It is memory-efficient.

61. **What does `yield from` do?**
    It delegates to a sub-iterator: it yields all of its values and passes
    `send()` calls and exceptions through.

62. **What is the difference between an iterable and an iterator?**
    An iterable has `__iter__` and can be looped over repeatedly (for example a
    list). An iterator has `__iter__` and `__next__`, tracks its position, and is
    exhausted after one pass.

63. **How do context managers work?**
    `with` calls `__enter__` at the start and `__exit__` at the end, even if an
    exception occurs. `@contextlib.contextmanager` builds one from a generator.
    Async versions use `__aenter__`/`__aexit__`.

64. **What do `functools.lru_cache` and `functools.cache` do?**
    They memoize function results by argument (the arguments must be hashable).
    `lru_cache(maxsize=N)` evicts the least recently used entries; `cache` is
    unbounded.

65. **What does `functools.partial` do?**
    It creates a new callable with some arguments pre-filled.

66. **Name useful `itertools` functions.**
    `chain`, `islice`, `groupby` (group only consecutive equal keys, so sort
    first), `product`, `permutations`, `combinations`, `accumulate`, `cycle`,
    `batched` (Python 3.12+).

67. **What is extended unpacking?**
    `first, *middle, last = items`. It works in assignments and in function
    calls.

68. **What is structural pattern matching?**
    `match` / `case` (Python 3.10+). It matches against literals, sequences,
    mappings, class patterns, and guards. It is more than a switch statement.

69. **EAFP vs LBYL?**
    "Easier to Ask Forgiveness than Permission" (`try`/`except`) vs "Look Before
    You Leap" (`if` checks first). EAFP is idiomatic in Python and avoids race
    conditions between the check and the use.

70. **How do you chain exceptions?**
    `raise NewError(...) from original` keeps the cause in the traceback.
    `from None` suppresses the context (this project's seller route uses it).

71. **What are `ExceptionGroup` and `except*`?**
    Introduced in Python 3.11 to raise and handle several exceptions at once.
    They are used by `asyncio.TaskGroup`.

72. **What is "first-class functions"?**
    Functions are objects: they can be assigned to variables, passed as
    arguments, returned, and stored in data structures.

73. **How do you read a 10 GB file without running out of memory?**
    Iterate over the file object line by line (`for line in f`), read
    fixed-size chunks (`f.read(65536)`), or use `mmap`. Never call `f.read()` on
    the whole file.

74. **What is the time complexity of common list operations?**
    `append` and `pop()`: O(1) amortized. `insert(0, x)` and `pop(0)`: O(n).
    Indexing: O(1). `x in list`: O(n). Use `collections.deque` for O(1)
    operations at both ends.

75. **When would you use `heapq` and `bisect`?**
    `heapq` for a priority queue or top-k (`heapq.nlargest`). `bisect` for
    binary search and insertion into a sorted list.

76. **Regular expressions: greedy vs non-greedy?**
    `.*` matches as much as possible; `.*?` matches as little as possible.
    Precompile frequently used patterns with `re.compile`.

---

## 4. Mid-level: Advanced OOP and Data Modeling

77. **What is the MRO, and how is it computed?**
    The Method Resolution Order is the order in which classes are searched for
    attributes. Python computes it with the C3 linearization algorithm. View it
    with `Class.__mro__`. It resolves the diamond-inheritance problem.

78. **What are mixins?**
    Small classes that add one focused capability through multiple inheritance
    (for example `JSONSerializableMixin`). They are not meant to be instantiated
    alone.

79. **What does `__slots__` do?**
    It declares a fixed set of attributes and removes the per-instance
    `__dict__`. This saves memory and speeds up attribute access, but you cannot
    add new attributes dynamically.

80. **What is the contract between `__eq__` and `__hash__`?**
    Objects that compare equal must have equal hashes. If you define `__eq__`
    without `__hash__`, Python sets `__hash__ = None`, making instances
    unhashable.

81. **`__getattr__` vs `__getattribute__`?**
    `__getattribute__` runs on *every* attribute access. `__getattr__` runs only
    when normal lookup fails. Override `__getattr__` for proxies and fallbacks.

82. **What does `__call__` do?**
    It makes instances callable like functions. This is useful for stateful
    callables and for middleware: this project's `RequestContextMiddleware` is a
    callable class.

83. **What are `Enum` members and why use them?**
    Named constants with identity and iteration support (`class Status(Enum)`).
    `StrEnum` and `IntEnum` also behave as `str` or `int`.

84. **`NamedTuple` vs `dataclass` vs Pydantic `BaseModel`?**
    `NamedTuple` is an immutable, lightweight tuple. `dataclass` is a mutable,
    flexible plain class with no validation. Pydantic validates and converts
    data at runtime, so use it at system boundaries such as API input and
    config.

85. **What is duck typing?**
    "If it walks like a duck..." Code relies on an object's behavior (its
    methods), not its declared type. `typing.Protocol` makes this explicit for
    type checkers.

86. **How do you implement a comparable, sortable class?**
    Define `__eq__` and `__lt__`, then use `functools.total_ordering`, or use
    `@dataclass(order=True)`.

87. **What is operator overloading?**
    Defining dunder methods such as `__add__`, `__mul__`, and `__getitem__` so
    your objects work with operators.

---

## 5. Mid-level: Standard Library and Typing

88. **Do type hints affect runtime behavior?**
    No. Python does not enforce them at runtime. Static checkers (mypy, pyright)
    and libraries such as Pydantic and FastAPI read them.

89. **Explain common typing constructs.**
    `X | None` (Optional), `X | Y` (Union), `list[int]`, `dict[str, int]`,
    `Callable[[int], str]`, `TypeVar` and `Generic`, `Protocol`, `Literal`,
    `TypedDict`, `Final`, `Annotated`.

90. **What is a `Protocol`?**
    Structural typing: any class with matching methods satisfies the protocol
    without inheriting from it.

91. **What is `typing.Annotated`?**
    It attaches metadata to a type: `Annotated[int, Field(gt=0)]`. FastAPI and
    Pydantic use it heavily.

92. **`logging` vs `print`?**
    `logging` supports levels, handlers, formatters, and a logger hierarchy, and
    can be configured without code changes. Use `logging.getLogger(__name__)`.

93. **`pathlib` vs `os.path`?**
    `pathlib.Path` is object-oriented and more readable:
    `Path("data") / "file.txt"`.

94. **Why is `pickle` risky?**
    Unpickling untrusted data can execute arbitrary code. Use JSON for
    untrusted input.

95. **How do you handle time zones correctly?**
    Store and compute in UTC with timezone-aware datetimes
    (`datetime.now(timezone.utc)`), use `zoneinfo` for local zones, and avoid
    naive datetimes.

96. **How do you fix a circular import?**
    Move shared code into a third module, import inside the function that needs
    it, or restructure dependencies. Under `if TYPE_CHECKING:`, imports used
    only in type hints are skipped at runtime.

97. **Absolute vs relative imports?**
    `from app.models import Product` vs `from .models import Product`. Absolute
    imports are clearer and are the PEP 8 recommendation.

98. **What is `pyproject.toml`?**
    The standard configuration file for building and packaging projects
    (PEP 517/518/621). Many tools (ruff, pytest, mypy) also read their settings
    from it.

99. **What are wheels?**
    Prebuilt distribution packages (`.whl`) that install quickly without running
    a build step.

100. **What does `collections` provide?**
     `defaultdict`, `Counter`, `deque`, `OrderedDict`, `namedtuple`, and
     `ChainMap`.

---

## 6. Concurrency: Threads, Processes, asyncio

101. **What is the GIL?**
     The Global Interpreter Lock lets only one thread execute Python bytecode at
     a time in standard CPython. Threads still help with I/O-bound work because
     the GIL is released while waiting on I/O. CPU-bound work needs
     multiprocessing or native code. Python 3.13 added an experimental
     free-threaded (no-GIL) build (PEP 703).

102. **When do you use threading vs multiprocessing vs asyncio?**
     Threading: I/O-bound work with blocking libraries. Multiprocessing:
     CPU-bound work. asyncio: very high-concurrency I/O (thousands of sockets)
     with async-compatible libraries.

103. **What is `concurrent.futures`?**
     A high-level API with `ThreadPoolExecutor` and `ProcessPoolExecutor`. You
     submit tasks and receive `Future` objects.

104. **What is a race condition, and how do you prevent one?**
     Multiple threads accessing shared state where the result depends on
     timing. Prevent it with `threading.Lock`, queues, immutable data, or by not
     sharing state.

105. **What is a deadlock?**
     Two or more threads each waiting for a lock the other holds. Avoid it with
     a consistent lock order, timeouts, and fewer locks.

106. **What are a coroutine, an event loop, and `await`?**
     A coroutine is an `async def` function that can pause. The event loop
     schedules coroutines and resumes them when their I/O is ready. `await`
     yields control until the awaited result is available.

107. **`asyncio.gather` vs `create_task` vs `TaskGroup`?**
     `create_task` schedules a coroutine to run concurrently. `gather` runs
     several and collects their results. `TaskGroup` (Python 3.11+) provides
     structured concurrency: if one task fails, the others are cancelled and the
     errors are raised as an `ExceptionGroup`.

108. **What happens if you call blocking code inside an `async def`?**
     It blocks the entire event loop, so every other request stalls. Use async
     libraries, `await asyncio.to_thread(func)`, or `loop.run_in_executor`.

109. **How do you limit concurrency in asyncio?**
     Use `asyncio.Semaphore(n)`, worker tasks reading from an `asyncio.Queue`,
     or connection-pool limits.

110. **How does task cancellation work?**
     `task.cancel()` raises `CancelledError` at the task's current `await`. Clean
     up in `finally` and re-raise `CancelledError`; do not swallow it.

111. **How do you add timeouts in asyncio?**
     `async with asyncio.timeout(5):` (Python 3.11+) or
     `asyncio.wait_for(coro, 5)`.

112. **What are the pitfalls of multiprocessing?**
     Arguments and results must be picklable. Startup cost is high. Memory is
     not shared by default. The start method differs by platform (`spawn` is the
     default on macOS and Windows), and `spawn` needs the
     `if __name__ == "__main__"` guard.

113. **Thread-safe queues?**
     `queue.Queue` for threads, `multiprocessing.Queue` for processes, and
     `asyncio.Queue` for coroutines. `asyncio.Queue` is *not* thread-safe.

114. **Can a sync function call an async function?**
     Only through an event loop: `asyncio.run(coro())` from synchronous top-level
     code, or `asyncio.run_coroutine_threadsafe` from another thread.

---

## 7. Senior: CPython Internals and Performance

115. **How does CPython run your code?**
     Source → tokens → AST → bytecode (cached in `.pyc`) → the evaluation loop
     in the virtual machine. Inspect bytecode with the `dis` module.

116. **How does Python manage memory?**
     Primarily through reference counting: an object is freed when its count
     reaches zero. A generational cyclic garbage collector (`gc`) handles
     reference cycles. Small objects use the `pymalloc` allocator.

117. **How do memory leaks happen in Python, and how do you find them?**
     Causes: unbounded caches or globals, lingering references (closures,
     registries), and leaks in C extensions. Tools: `tracemalloc`, `objgraph`,
     `memray`, and comparing heap snapshots.

118. **What are integer caching and string interning?**
     CPython caches the integers -5 to 256 and interns some strings, so `is`
     sometimes returns `True` for equal values. This is an implementation
     detail; never rely on it.

119. **What are descriptors?**
     Objects that define `__get__`, `__set__`, or `__delete__`, which control
     attribute access on another class. `property`, methods, `classmethod`, and
     `staticmethod`, as well as ORM columns, are built on descriptors. Data
     descriptors (defining `__set__`) take precedence over instance `__dict__`
     entries.

120. **What is a metaclass?**
     The class of a class (`type` by default). It controls class creation and is
     used for registries, validation, and ORMs. Prefer `__init_subclass__` or
     class decorators for simpler cases.

121. **What is the attribute lookup order for `obj.attr`?**
     Data descriptors on the type → the instance `__dict__` → non-data
     descriptors and class attributes → `__getattr__`.

122. **What are weak references?**
     References (`weakref`) that do not increase the reference count. Use them
     for caches and observers that should not keep objects alive.

123. **What performance improvements came in recent Python versions?**
     3.11 introduced a specializing adaptive interpreter (often 10–60% faster).
     3.12 added a per-interpreter GIL (PEP 684). 3.13 added an experimental
     free-threaded build and an experimental JIT compiler.

124. **How do you profile Python code?**
     `cProfile` and `pstats` for function-level timing, `py-spy` for sampling
     production processes, `line_profiler` for line-level detail, `timeit` for
     micro-benchmarks, and `tracemalloc` or `memray` for memory.

125. **How do you speed up slow Python code?**
     Measure first. Then improve the algorithm and data structures, use
     built-ins and comprehensions, cache results, batch I/O, use NumPy
     vectorization, move hot loops to C, Cython, or Rust, use multiprocessing for
     CPU-bound work, and use async I/O for I/O-bound work.

126. **Why are local variables faster than globals?**
     Locals are accessed by array index in the frame; globals need a dict
     lookup.

127. **What is monkey patching, and what are the risks?**
     Modifying classes or modules at runtime. It is useful in tests but fragile
     in production: it hides behavior and can break on library upgrades.

128. **How does `asyncio` work under the hood?**
     The event loop uses OS selectors (epoll or kqueue) to wait on many sockets.
     Tasks wrap coroutines and are resumed when the futures they await
     complete. Everything runs in a single thread.

---

## 8. Senior: Architecture, Design, and Reliability

129. **Which design patterns do you use in Python, and how do they differ from Java?**
     Python simplifies many patterns. A singleton can be a module, a strategy
     can be a passed function, and a factory can be a dict of callables.
     Repository, adapter, observer, and dependency injection remain common.
     This project uses the repository and service layer patterns.

130. **Explain the SOLID principles with Python examples.**
     Single responsibility (routes vs services vs repositories),
     open/closed (extend through new classes or plugins), Liskov substitution
     (subclasses honor their parent's contract), interface segregation (small
     Protocols), and dependency inversion (depend on abstractions; inject
     repositories into services).

131. **Why separate routes, services, and repositories?**
     Each layer has one reason to change. Business logic becomes testable
     without HTTP or a database, persistence can be swapped, and the codebase
     scales with the team.

132. **What is dependency injection, and how does FastAPI support it?**
     Providing a component's collaborators from outside instead of creating
     them inside. FastAPI's `Depends()` resolves dependencies per request and
     allows overrides in tests.

133. **How do you manage configuration and secrets?**
     Follow the 12-factor approach: put config in environment variables,
     validate it with `pydantic-settings`, never commit secrets, and use a
     secret manager (Vault, AWS Secrets Manager) in production.

134. **What is observability?**
     Logs, metrics, and traces. Use structured logs with correlation or request
     IDs (as this project's middleware does), RED metrics (Rate, Errors,
     Duration), and distributed tracing with OpenTelemetry.

135. **How do you design reliable calls to external services?**
     Use timeouts, retries with exponential backoff and jitter, idempotency
     keys, circuit breakers, bulkheads, and fallbacks.

136. **What caching strategies do you know?**
     Cache-aside, read-through, write-through, write-behind, and TTL-based
     expiry. Cache invalidation is the hard part. Tools include Redis and
     in-process LRU caches.

137. **What rate-limiting algorithms do you know?**
     Fixed window, sliding window log, sliding window counter, token bucket, and
     leaky bucket. In distributed systems, rate limits are often stored in Redis.

138. **When do you use a message queue?**
     To decouple services, absorb traffic spikes, and run background jobs.
     Examples: Celery with RabbitMQ or Redis, and Kafka for event streams.
     Understand at-least-once vs exactly-once delivery and design idempotent
     consumers.

139. **How do you scale a Python web service?**
     Keep it stateless and scale horizontally behind a load balancer. Run
     multiple worker processes (gunicorn with uvicorn workers). Use connection
     pooling, caching, async I/O, and read replicas, and offload heavy work to
     queues.

140. **How do you handle backward compatibility and deprecation in an API or library?**
     Use semantic versioning and API versioning (`/api/v1`). Add deprecation
     warnings (`warnings.warn(..., DeprecationWarning)`), publish migration
     guides, and remove deprecated features only after a deprecation window.

141. **How do you approach technical debt?**
     Make it visible (tickets), quantify its impact, pay it down
     incrementally alongside features, and use the "boy scout rule" (leave code
     cleaner than you found it).

142. **What do you look for in a code review?**
     Correctness, edge cases, security, tests, readability, naming, and
     performance where it matters. Keep feedback specific and kind, and
     automate style checks.

143. **How do you design a plugin system in Python?**
     Use entry points (`importlib.metadata.entry_points`), a registry populated
     by `__init_subclass__` or decorators, and a stable interface defined by an
     ABC or Protocol.

144. **Monolith vs microservices?**
     Start with a well-structured monolith (a modular monolith). Split into
     services only when there is a clear need: independent scaling, separate
     teams, or different release cycles. Microservices add network and
     operational complexity.

---

## 9. Web APIs and FastAPI

145. **What is FastAPI?**
     A modern Python web framework built on Starlette (ASGI, routing,
     middleware) and Pydantic (validation). It generates OpenAPI documentation
     from type hints.

146. **WSGI vs ASGI?**
     WSGI is a synchronous interface: one request per worker thread (Flask,
     classic Django). ASGI is asynchronous and supports async I/O, WebSockets,
     and long-lived connections (FastAPI, Starlette, Django async).

147. **`def` vs `async def` endpoints in FastAPI?**
     `def` endpoints run in a threadpool, so blocking code is acceptable.
     `async def` endpoints run on the event loop and must not block; use only
     async libraries inside them.

148. **How does `Depends` work?**
     FastAPI resolves dependencies (functions, classes, or generators) per
     request, caches each one within the request by default, and runs
     `yield`-dependency cleanup after the response. This project's `get_db`
     yields an `AsyncSession` this way.

149. **What are the main Pydantic v2 features?**
     `BaseModel`, `Field` constraints, `field_validator`, `model_validator`,
     `model_dump()`, `model_validate()`, and
     `ConfigDict(from_attributes=True)` for ORM objects (this replaced v1's
     `orm_mode`).

150. **What is `response_model` for?**
     It validates and filters the response. For example, `SellerResponse` omits
     the `password` field even though the ORM object contains it.

151. **Path vs query vs body parameters?**
     Path: `/products/{product_id}`. Query: `?limit=10`. Body: JSON parsed into a
     Pydantic model. FastAPI infers the kind from the function signature.

152. **How do you handle errors in FastAPI?**
     Raise `HTTPException(status_code, detail)` and register custom exception
     handlers with `@app.exception_handler(...)`. Validation errors return 422
     automatically.

153. **Middleware vs dependency: when do you use each?**
     Middleware runs for every request and suits cross-cutting concerns:
     logging, CORS, request IDs, timing. Dependencies apply to specific routes
     and suit auth, database sessions, and pagination parameters.

154. **What is CORS?**
     A browser security mechanism. A server must explicitly allow cross-origin
     requests using `Access-Control-Allow-*` headers. Never use `*` together
     with credentials.

155. **What are lifespan events?**
     An async context manager passed as `FastAPI(lifespan=...)` that runs
     startup and shutdown logic. It replaces the deprecated `on_event` hooks.
     This project creates tables and disposes of the engine there.

156. **`BackgroundTasks` vs Celery?**
     `BackgroundTasks` runs short tasks in the same process after the response
     is sent. Celery or another queue handles durable, retryable, heavy, or
     distributed jobs.

157. **How do you implement authentication?**
     OAuth2 password flow with JWTs (`OAuth2PasswordBearer`), a dependency that
     decodes the token and loads the user, scopes or roles for authorization,
     short-lived access tokens, and refresh tokens.

158. **401 vs 403?**
     401 Unauthorized means not authenticated (missing or invalid credentials).
     403 Forbidden means authenticated but not allowed.

159. **Which HTTP status codes should you know?**
     200 OK, 201 Created, 204 No Content, 301/302 redirects, 400 Bad Request,
     401, 403, 404 Not Found, 409 Conflict, 422 Unprocessable Entity, 429 Too
     Many Requests, 500 Internal Server Error, 502/503/504 gateway or
     availability errors.

160. **PUT vs PATCH vs POST?**
     POST creates a resource (not idempotent). PUT replaces a resource
     (idempotent). PATCH partially updates a resource.

161. **Offset vs cursor pagination?**
     Offset (`LIMIT/OFFSET`) is simple but slow on deep pages and unstable when
     data changes. Cursor (keyset) pagination is fast and stable, but you cannot
     jump to an arbitrary page.

162. **How do you test FastAPI apps?**
     Use `httpx.AsyncClient` with `ASGITransport` (or `TestClient`), override
     dependencies with `app.dependency_overrides`, and run against a test
     database.

163. **Django vs Flask vs FastAPI?**
     Django is batteries-included (ORM, admin, auth). Flask is a minimal,
     flexible WSGI framework. FastAPI is async, type-hint driven, and generates
     API documentation automatically.

164. **How do you deploy a FastAPI app?**
     Run uvicorn workers, or gunicorn with `uvicorn.workers.UvicornWorker`,
     behind a reverse proxy or load balancer, inside a container, with health
     checks and settings from environment variables.

165. **Do WebSockets and streaming responses work in FastAPI?**
     Yes. Use `@app.websocket` for bidirectional communication and
     `StreamingResponse` or Server-Sent Events for large or incremental output.

---

## 10. Databases and SQLAlchemy

166. **What are the pros and cons of an ORM?**
     Pros: productivity, database portability, safety from SQL injection, and
     working with Python objects. Cons: hidden queries (N+1), performance
     overhead, and harder complex SQL. Know when to drop down to raw SQL.

167. **SQLAlchemy Core vs ORM?**
     Core is an SQL expression language working with tables and rows. The ORM
     maps classes to tables and manages object identity through a `Session`.
     SQLAlchemy 2.0 uses `select()` for both.

168. **What does a `Session` do?**
     It implements the unit-of-work pattern: it tracks object changes,
     `flush()` sends SQL, `commit()` ends the transaction, and `refresh()`
     reloads an object from the database.

169. **What is `expire_on_commit`, and why is it set to `False` in async code?**
     By default, objects expire after commit and reload on next access. In
     async code, that implicit reload would be lazy I/O, which fails. With
     `expire_on_commit=False`, attributes remain usable after commit.

170. **What is the N+1 query problem?**
     One query loads N rows, then N additional queries load each row's related
     data. Fix it with eager loading: `selectinload()` or `joinedload()`.

171. **Why does lazy loading fail with `AsyncSession`?**
     Implicit lazy loads would perform I/O outside an `await`, which raises
     `MissingGreenlet`. Use eager loading, `await session.refresh(obj, [...])`,
     or `AsyncAttrs`.

172. **What are ACID and isolation levels?**
     Atomicity, Consistency, Isolation, Durability. The isolation levels are
     Read Uncommitted, Read Committed, Repeatable Read, and Serializable; they
     trade consistency against concurrency (dirty reads, non-repeatable reads,
     phantom reads).

173. **When do indexes help, and when do they hurt?**
     They speed up `WHERE`, `JOIN`, and `ORDER BY` on selective columns. They
     slow down writes and use storage. Use `EXPLAIN` to verify a query uses
     them.

174. **Why use migrations (Alembic)?**
     To version schema changes, apply them consistently in every environment,
     and roll them back. Avoid `create_all` in production.

175. **What is connection pooling?**
     Reusing database connections instead of opening a new one per request.
     Tune `pool_size`, `max_overflow`, `pool_pre_ping`, and `pool_recycle`.

176. **Optimistic vs pessimistic locking?**
     Optimistic: use a version column and detect conflicts on write.
     Pessimistic: lock rows up front (`SELECT ... FOR UPDATE`).

177. **What is the difference between SQL join types?**
     INNER returns only matches. LEFT returns all left rows plus matches.
     RIGHT is the reverse of LEFT. FULL OUTER returns all rows from both sides.
     CROSS returns the Cartesian product.

178. **`WHERE` vs `HAVING`?**
     `WHERE` filters rows before grouping; `HAVING` filters groups after
     aggregation.

179. **What are window functions?**
     Functions that compute across related rows without collapsing them:
     `ROW_NUMBER()`, `RANK()`, `SUM() OVER (PARTITION BY ...)`.

180. **Normalization vs denormalization?**
     Normalization removes redundancy and protects integrity. Denormalization
     duplicates data to make reads faster. It is a trade-off driven by access
     patterns.

181. **SQL vs NoSQL?**
     SQL databases offer relational data, joins, and strong consistency.
     NoSQL databases (document, key-value, wide-column, graph) offer flexible
     schemas, horizontal scale, and data models matched to access patterns.

182. **How do you handle unique-constraint violations?**
     Catch `IntegrityError`, roll back the session, and return 409 Conflict.
     This project's seller route does exactly this.

183. **How do you prevent SQL injection?**
     Use parameterized queries or the ORM. Never build SQL with string
     formatting from user input.

---

## 11. Testing

184. **`unittest` vs `pytest`?**
     `unittest` is built in and class-based with xUnit-style assertions.
     `pytest` uses plain `assert`, fixtures, parametrization, and plugins, and is
     the industry default. It can also run `unittest` tests.

185. **What are pytest fixtures and scopes?**
     Reusable setup and teardown (code after `yield` runs as teardown). Scopes
     are `function`, `class`, `module`, `package`, and `session`. Shared
     fixtures live in `conftest.py`.

186. **What does `@pytest.mark.parametrize` do?**
     It runs the same test with multiple input and expected-output sets.

187. **How does mocking work, and where do you patch?**
     `unittest.mock.patch` replaces objects during a test. Patch where the
     object is *looked up*, not where it is defined. Use `AsyncMock` for
     coroutines.

188. **What is the test pyramid?**
     Many fast unit tests, fewer integration tests, and very few slow end-to-end
     tests.

189. **Is 100% coverage the goal?**
     No. Coverage shows which code is untested, not which code is correct. Focus
     on critical paths, edge cases, and meaningful assertions.

190. **What is TDD?**
     Red → Green → Refactor: write a failing test, make it pass with the
     simplest code, then improve the design.

191. **How do you test async code?**
     Use `pytest-asyncio` (this project sets `asyncio_mode = auto` in
     `pytest.ini`), async fixtures, and `AsyncMock`.

192. **How do you test database code?**
     Use an in-memory SQLite database (as this project's tests do), roll back
     transactions per test, or use real databases through Testcontainers for
     production parity.

193. **What is property-based testing?**
     Generating many random inputs that must satisfy an invariant, for example
     with the `hypothesis` library. It finds edge cases you did not think of.

194. **How do you organize tests with classes?**
     Group related tests in `Test*` classes. Set up shared objects with
     `setup_method` or an autouse fixture, as `TestProductService` and
     `TestSellerService` do in this project.

---

## 12. Security

195. **How should passwords be stored?**
     Hash them with a slow, salted algorithm (bcrypt, argon2, or scrypt). Never
     store plain text, and never use fast hashes such as MD5 or SHA-256 for
     passwords.

196. **Why are `eval`/`exec` dangerous?**
     They execute arbitrary code. Use `ast.literal_eval` to parse literals.

197. **Why is `yaml.load` unsafe?**
     It can construct arbitrary Python objects. Use `yaml.safe_load`.

198. **What are common JWT pitfalls?**
     Accepting the `none` algorithm, weak secrets, long-lived tokens without
     revocation, storing sensitive data in the payload (it is only encoded, not
     encrypted), and not validating `exp`, `aud`, or `iss`.

199. **Name items from the OWASP Top 10.**
     Broken access control, cryptographic failures, injection, insecure design,
     security misconfiguration, vulnerable components, authentication failures,
     data-integrity failures, logging and monitoring failures, and SSRF.

200. **How do you keep dependencies secure?**
     Pin versions with lock files, scan with `pip-audit` or Dependabot, update
     regularly, and minimize the number of dependencies.

201. **How do you validate input?**
     Validate at the boundary with Pydantic: types, lengths, ranges, and
     formats (for example `EmailStr`). Reject unknown input instead of trying to
     sanitize everything.

---

## 13. Tooling, DevOps, and Git

202. **Which code-quality tools do you use?**
     `ruff` (lint and format), `black`, `mypy` or `pyright` (type checking),
     and `pre-commit` hooks to run them automatically.

203. **How do you manage dependencies reproducibly?**
     Use lock files (`uv`, `poetry`, or `pip-tools`). Keep direct dependencies
     in `pyproject.toml` and the resolved, pinned versions in the lock file.

204. **What are Docker best practices for Python?**
     Use slim base images and multi-stage builds, run as a non-root user,
     install dependencies before copying code (for layer caching), add a
     `.dockerignore`, set `PYTHONUNBUFFERED=1`, and run one process per
     container.

205. **What steps belong in a CI/CD pipeline?**
     Install → lint and format check → type check → tests with coverage →
     security scan → build the image → deploy to staging → smoke tests →
     promote to production.

206. **Git merge vs rebase?**
     Merge preserves history and adds a merge commit. Rebase rewrites commits
     onto a new base for linear history. Never rebase shared branches.

207. **Why `--force-with-lease` instead of `--force`?**
     It refuses to overwrite the remote branch if someone else has pushed since
     your last fetch.

208. **What do `git cherry-pick`, `git stash`, and `git bisect` do?**
     `cherry-pick` applies a specific commit. `stash` temporarily shelves
     changes. `bisect` binary-searches history to find the commit that
     introduced a bug.

209. **How should applications log inside containers?**
     Write to stdout and stderr, preferably as structured JSON, and let the
     platform collect and ship the logs.

210. **What are health checks (liveness vs readiness)?**
     Liveness: is the process alive (restart it if not)? Readiness: can it serve
     traffic now (for example, are its dependencies available)?

---

## 14. Predict the Output (Trick Questions)

211. **Mutable default argument**
     ```python
     def f(x, acc=[]):
         acc.append(x)
         return acc
     print(f(1), f(2))
     ```
     Output: `[1, 2] [1, 2]`. Both calls share the same list, and both printed
     values are that one list.

212. **Late-binding closures**
     ```python
     funcs = [lambda: i for i in range(3)]
     print([f() for f in funcs])
     ```
     Output: `[2, 2, 2]`. Each lambda looks up `i` when called. Fix it with
     `lambda i=i: i`.

213. **Shared rows in a nested list**
     ```python
     grid = [[0] * 3] * 3
     grid[0][0] = 1
     print(grid)
     ```
     Output: `[[1, 0, 0], [1, 0, 0], [1, 0, 0]]`. All three rows are the same
     list. Use `[[0] * 3 for _ in range(3)]`.

214. **`return` in `finally`**
     ```python
     def f():
         try:
             return 1
         finally:
             return 2
     print(f())
     ```
     Output: `2`. The `finally` block's `return` overrides the first one, and
     it would also swallow any exception.

215. **Dict keys `True` and `1`**
     ```python
     print({True: "a", 1: "b"})
     ```
     Output: `{True: 'b'}`. `True == 1` and both have the same hash, so they are
     the same key. The first key object is kept; the value is overwritten.

216. **Augmented assignment on a tuple element**
     ```python
     t = ([],)
     t[0] += [1]
     ```
     This raises `TypeError`, *but* `t` becomes `([1],)`. The list is extended
     in place first, and then assigning back to the tuple item fails.

217. **Banker's rounding**
     ```python
     print(round(2.5), round(3.5))
     ```
     Output: `2 4`. Python rounds halves to the nearest even number.

218. **`+=` vs `+` on lists**
     ```python
     a = [1]; b = a; b += [2]; print(a)
     a = [1]; b = a; b = b + [2]; print(a)
     ```
     Output: `[1, 2]`, then `[1]`. `+=` mutates the list in place; `+` creates a
     new list.

219. **Tuple syntax**
     ```python
     print(type(()), type((1)), type((1,)))
     ```
     Output: `tuple`, `int`, `tuple`. The comma makes a tuple, not the
     parentheses.

220. **Truthiness of strings**
     ```python
     print(bool("False"), bool(""), bool(" "))
     ```
     Output: `True False True`. Any non-empty string is truthy.

221. **Chained comparison**
     ```python
     print(1 < 2 < 3, 3 > 2 > 1 == 1, (1 < 2) < 3)
     ```
     Output: `True True True`. `a < b < c` means `a < b and b < c`. In the last
     expression, `True < 3` is `1 < 3`.

222. **Generator exhaustion**
     ```python
     g = (x for x in range(3))
     print(list(g), list(g))
     ```
     Output: `[0, 1, 2] []`. A generator can be consumed only once.

223. **Class variable shared by instances**
     ```python
     class A:
         items = []
     a, b = A(), A()
     a.items.append(1)
     print(b.items)
     ```
     Output: `[1]`. The list is shared by every instance. Initialize it in
     `__init__` instead.

224. **Name mangling**
     ```python
     class A:
         __x = 1
     print(hasattr(A, "__x"), hasattr(A, "_A__x"))
     ```
     Output: `False True`.

---

## 15. Coding Exercises

Commonly asked exercises, grouped by difficulty. Solve each one, then discuss its
time and space complexity and the edge cases.

**Junior**

225. Reverse a string and check whether it is a palindrome (ignoring case and
     punctuation).
226. FizzBuzz.
227. Count word frequency in text (`collections.Counter`).
228. Find duplicates in a list.
229. Check whether two strings are anagrams.
230. Find the second-largest number in a list.
231. Remove duplicates from a list while preserving order (`dict.fromkeys`).
232. Fibonacci: iterative, recursive with memoization, and as a generator.
233. Transpose a matrix (`list(zip(*matrix))`).
234. Count vowels in a string.

**Mid-level**

235. Two Sum: find the indices of two numbers that add up to a target, in O(n)
     with a dict.
236. Validate balanced parentheses with a stack.
237. Find the first non-repeating character in a string.
238. Flatten an arbitrarily nested list (recursion or a generator with
     `yield from`).
239. Merge two sorted lists, then merge k sorted lists (`heapq.merge`).
240. Group anagrams (dict of sorted-key → list).
241. Find the longest substring without repeating characters (sliding window).
242. Find the top-k frequent elements (`Counter.most_common` or `heapq`).
243. Write a `@retry(times, delay, exceptions)` decorator with exponential
     backoff.
244. Write a timer context manager, both as a class and with `@contextmanager`.
245. Chunk a list or iterable into batches of size n.
246. Deep-merge two nested dicts.
247. Implement binary search.
248. Rotate an array by k positions.
249. Parse a log file and report the top 5 IP addresses by request count.

**Senior**

250. Implement an LRU cache (`OrderedDict` or a dict plus a doubly linked list)
     with O(1) operations.
251. Implement a thread-safe counter, then a thread-safe bounded queue.
252. Fetch 1,000 URLs concurrently with asyncio, at most 20 at a time
     (`Semaphore`), with timeouts and retries.
253. Implement a token-bucket rate limiter.
254. Implement a minimal dependency-injection container.
255. Implement a descriptor that validates attribute types.
256. Implement a plugin registry using `__init_subclass__`.
257. Detect a cycle in a linked list (Floyd's algorithm).
258. Implement a producer–consumer pipeline with `asyncio.Queue` and graceful
     shutdown.
259. Design and implement an in-memory key-value store with TTL expiry.
260. Stream-process a CSV that is larger than memory and compute aggregates.

---

## 16. System Design and Scenario Questions

261. **An API endpoint is slow in production. How do you investigate?**
     Reproduce it and measure. Check traces (OpenTelemetry), logs with request
     IDs, and metrics. Profile with `py-spy`. Inspect database queries
     (`EXPLAIN`, N+1, missing indexes) and external calls. Fix the biggest
     bottleneck first, then verify.

262. **Memory usage grows continuously. How do you debug it?**
     Compare `tracemalloc` snapshots, use `memray`, check unbounded caches,
     global lists, and lingering references. Reproduce under load and confirm
     the fix with metrics.

263. **Design a URL shortener.**
     Covers ID generation (base62, collision handling), storage (key-value
     store), redirect latency (caching), analytics (async event stream), rate
     limiting, and expiry.

264. **Design a notification service (email, SMS, push).**
     Covers a queue-based fan-out, provider adapters, retries with a
     dead-letter queue, user preferences, templates, idempotency, and rate
     limits per provider.

265. **Design a rate limiter for a public API.**
     Covers the algorithm choice (token bucket), distributed state (Redis with
     atomic Lua scripts), per-user and per-IP keys, 429 responses with
     `Retry-After`, and behavior when Redis is unavailable.

266. **How would you migrate a synchronous codebase to async?**
     This project went through this migration. Convert from the bottom up:
     async database driver → repositories → services → routes. Replace
     blocking libraries. Watch for lazy loading and `expire_on_commit`. Update
     the tests with `pytest-asyncio`. Migrate incrementally behind tests.

267. **How do you deploy a breaking database migration with zero downtime?**
     Use expand and contract: add new columns or tables (backward compatible),
     deploy code that writes to both, backfill, switch reads, then remove the
     old schema in a later release.

268. **How would you handle a sudden 10× traffic spike?**
     Autoscale stateless workers, add caching and CDNs, queue
     non-critical work, apply rate limiting, and protect the database with
     connection limits and read replicas. Afterwards, load test and do capacity
     planning.

269. **How do you design an idempotent payment endpoint?**
     Require an idempotency key from the client, store each key with its
     response, return the stored response on retries, and use database
     constraints and transactions to avoid double charges.

270. **How do you structure a large Python codebase for multiple teams?**
     Use a modular monolith or separate packages with clear boundaries, shared
     internal libraries, enforced dependency rules (`import-linter`),
     consistent tooling, and ownership through CODEOWNERS.

---

## 17. Behavioral Questions

Answer with the **STAR** method: Situation, Task, Action, Result.

271. Tell me about a difficult bug you fixed. How did you find the root cause?
272. Describe a time you disagreed with a teammate on a technical decision.
273. Tell me about a project you are proud of and your specific contribution.
274. How do you handle tight deadlines and changing requirements?
275. Describe a time you made a mistake in production. What did you learn?
276. How do you keep your Python skills current?
277. How have you mentored a junior developer? *(senior)*
278. How do you balance technical debt against feature delivery? *(senior)*
279. Describe a time you improved a team process or the developer experience.
     *(senior)*
280. How do you make an architectural decision and get team buy-in? *(senior)*

---

## 18. Questions About This Project

Interviewers often ask you to walk through your own code. Practice explaining
these with this repository.

281. **Walk through what happens when a client calls `POST /products`.**
     The request passes through `RequestContextMiddleware`, then
     `CORSMiddleware`, then reaches the route in `app/api/routes/products.py`.
     FastAPI validates the body as `ProductCreate` and injects an
     `AsyncSession` via `Depends(get_db)`. `ProductService.create_product()`
     builds a `Product` ORM object, and `ProductRepository.create()` adds it,
     commits, and refreshes it. FastAPI serializes the result through the
     `ProductResponse` response model and returns 201.

282. **Why do the routes return `Product` but declare `response_model=ProductResponse`?**
     The return annotation describes what the function actually returns (an ORM
     object). `response_model` tells FastAPI how to validate and serialize the
     output. `from_attributes=True` lets Pydantic read the ORM object's
     attributes.

283. **Why use classes for the repositories and services?**
     They encapsulate their responsibilities, take their dependencies through
     constructor injection (a service receives a repository), are easy to
     substitute in tests, and keep the routes thin.

284. **How is the seller's password protected?**
     `SellerService` hashes it with bcrypt via `passlib` before saving it.
     `SellerResponse` excludes the password field, so it never appears in API
     responses.

285. **Why is `bcrypt<5` pinned?**
     `passlib` 1.7.4 is incompatible with bcrypt 5, which rejects the long test
     password that passlib uses during backend detection. Pinning avoids that
     runtime error. Migrating away from passlib (for example to `pwdlib` or
     using `bcrypt` directly) is a reasonable follow-up.

286. **Why is the request-context middleware written as pure ASGI instead of `BaseHTTPMiddleware`?**
     Pure ASGI middleware has lower overhead, does not interfere with streaming
     responses or background tasks, and avoids the known issues
     `BaseHTTPMiddleware` has with context variables.

287. **What do `X-Request-ID` and `X-Process-Time` give you?**
     A correlation ID for linking client reports to server logs and traces, and
     per-request latency visible to clients and logged on the server.

288. **Why is `allow_credentials` disabled when CORS origins are `*`?**
     Browsers reject credentialed requests that are answered with a wildcard
     origin. Credentials require an explicit list of allowed origins.

289. **Why are the OpenTelemetry imports inside `configure_telemetry()`?**
     So the app starts and runs normally when telemetry is disabled, even if
     the exporter packages are not installed, and so startup does not pay the
     import cost.

290. **Why `create_async_engine` and `expire_on_commit=False`?**
     Database I/O must not block the event loop, so async drivers
     (`aiosqlite`, `aiomysql`) are used. After a commit, async sessions cannot
     lazily reload expired attributes, so objects are kept un-expired.

291. **How are the tests isolated from the development database?**
     The `db_session` fixture creates an in-memory `sqlite+aiosqlite` engine
     with `StaticPool`, creates the tables, yields a session, and then drops
     the tables and disposes of the engine.

292. **What would you add next to make this production-ready?**
     Alembic migrations instead of `create_all`, authentication (OAuth2 and
     JWT), pagination, API versioning (`/api/v1`), integration tests with
     `httpx.AsyncClient`, a Dockerfile, CI (ruff, mypy, pytest), structured JSON
     logging, rate limiting, and health and readiness endpoints.

293. **The product update route reads and then writes. What is the race condition, and how would you fix it?**
     Two concurrent updates can overwrite each other (a lost update). Fix it
     with optimistic locking (a version column) or `SELECT ... FOR UPDATE`.

294. **How would you add a `GET /products?min_price=&max_price=&limit=&offset=` filter?**
     Add query parameters with validation (`Query(ge=0)`), build a conditional
     `select()` in the repository, return a paginated response model, and add an
     index on `price` if the table is large.
