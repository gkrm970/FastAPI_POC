# Senior Python Developer — Interview Q&A Bank

> **Format:** Each question is followed immediately by a detailed answer.  
> **Levels:** 🟢 Mid · 🟡 Senior · 🔴 Lead  
> **Types:** 💬 Verbal · 💻 Code

---

## 1. Core Python — Language Internals

### Verbal Questions

---

**Q1 🟡💬 What is the GIL and how does it affect multi-threaded Python programs?**

**A:** The **Global Interpreter Lock (GIL)** is a mutex in CPython that allows only one thread to execute Python bytecode at a time, even on a multi-core machine. It exists because CPython's reference-counting memory management is not thread-safe.

- **CPU-bound threads** (pure Python loops, calculations): the GIL serialises them — you get no speedup from multiple threads.
- **I/O-bound threads** (network, disk, `time.sleep`): the GIL is *released* during syscalls, so threads genuinely overlap.

**Workarounds:**
| Scenario | Tool | Reason |
|---|---|---|
| CPU-bound Python | `multiprocessing` | Each process has its own GIL |
| I/O-bound | `asyncio` or `threading` | GIL released during I/O waits |
| CPU-bound with C libs | `threading` + NumPy/OpenCV | C extensions release the GIL |
| Future | Python 3.13 no-GIL mode | PEP 703 (experimental) |

---

**Q2 🟡💬 Explain Python's memory management. How does reference counting work alongside the cyclic garbage collector?**

**A:** CPython uses two mechanisms:

1. **Reference counting** — every object has a `ob_refcnt`. When it hits 0, the object is deallocated immediately. Fast and deterministic.
2. **Cyclic GC** — reference counting cannot free *reference cycles* (e.g. `a.ref = b; b.ref = a`). The `gc` module's generational collector periodically scans for cycles and breaks them.

```python
import gc, sys

a = []
b = [a]
a.append(b)          # cycle: a → b → a
print(sys.getrefcount(a))  # > 1 even with no external references
gc.collect()         # cyclic GC frees them
```

Key points: `__del__` can delay collection; use `weakref` to avoid cycles in caches.

---

**Q3 🟡💬 What is the difference between `__new__` and `__init__`? When would you override `__new__`?**

**A:**
- `__new__(cls, ...)` — *creates* and *returns* a new instance. Called first.
- `__init__(self, ...)` — *initialises* the instance after it's created. Cannot create a different object.

Override `__new__` when:
- Implementing a **singleton** (control whether a new instance is created).
- Subclassing **immutable types** (`int`, `str`, `tuple`) — you must set the value in `__new__` because `__init__` runs after the object is already frozen.
- Metaclass-level object factories.

```python
class Singleton:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

---

**Q4 🟡💬 Explain MRO (Method Resolution Order) in Python's multiple inheritance using C3 linearisation.**

**A:** Python uses the **C3 linearisation algorithm** to determine the order in which base classes are searched when looking up a method.

```python
class A: pass
class B(A): pass
class C(A): pass
class D(B, C): pass

print(D.__mro__)
# (<class 'D'>, <class 'B'>, <class 'C'>, <class 'A'>, <class 'object'>)
```

Rule: a class always appears before its parents, and the order of parents in the class definition is respected. Use `super()` to traverse the MRO cooperatively.

---

**Q5 🟡💬 What are descriptors? How do `__get__`, `__set__`, and `__delete__` work?**

**A:** A **descriptor** is any object that defines `__get__`, `__set__`, or `__delete__`. When an attribute lookup finds a descriptor on the *class*, Python calls the descriptor protocol instead of returning the object directly.

- **Non-data descriptor** — only `__get__` (e.g. functions/methods).
- **Data descriptor** — `__get__` + `__set__`/`__delete__` (e.g. `property`, `classmethod`). These take priority over instance `__dict__`.

```python
class Celsius:
    def __set_name__(self, owner, name): self.name = name
    def __get__(self, obj, objtype=None):
        return obj.__dict__.get(self.name, 0)
    def __set__(self, obj, value):
        if value < -273.15:
            raise ValueError("Below absolute zero")
        obj.__dict__[self.name] = value

class Temperature:
    degrees = Celsius()

t = Temperature()
t.degrees = 100  # calls __set__
print(t.degrees)  # calls __get__
```

---

**Q6 🟢💬 What is the difference between `@staticmethod`, `@classmethod`, and a regular method?**

**A:**
| | Receives | Use case |
|---|---|---|
| Regular method | `self` (instance) | Access/modify instance state |
| `@classmethod` | `cls` (class) | Alternative constructors, factory methods |
| `@staticmethod` | nothing | Utility functions logically grouped in the class |

```python
class Date:
    def __init__(self, y, m, d): self.y, self.m, self.d = y, m, d

    @classmethod
    def from_string(cls, s):           # factory
        return cls(*map(int, s.split("-")))

    @staticmethod
    def is_valid(s):                   # utility — no class/instance needed
        parts = s.split("-")
        return len(parts) == 3
```

---

**Q7 🔴💬 What are metaclasses? When would you actually use one in production code?**

**A:** A **metaclass** is the class of a class — it controls how classes are *created*. `type` is the default metaclass.

```python
class Meta(type):
    def __new__(mcs, name, bases, namespace):
        # enforce: all public methods must have docstrings
        for k, v in namespace.items():
            if callable(v) and not k.startswith("_") and not v.__doc__:
                raise TypeError(f"{name}.{k} must have a docstring")
        return super().__new__(mcs, name, bases, namespace)

class MyAPI(metaclass=Meta):
    def create(self):
        """Create a resource."""
        ...
```

**Real production uses:**
- ORMs (Django models, SQLAlchemy) — register models in a registry.
- API frameworks — auto-register route handlers.
- Abstract base class enforcement.
- In modern Python, `__init_subclass__` and class decorators often replace metaclasses for simpler cases.

---

**Q8 🟢💬 What is the difference between shallow copy and deep copy? When can a shallow copy cause bugs?**

**A:**
- **Shallow copy** (`copy.copy`, `list[:]`, `dict.copy()`) — creates a new container but the *elements* are still references to the same objects.
- **Deep copy** (`copy.deepcopy`) — recursively copies every nested object.

```python
import copy

original = {"scores": [1, 2, 3]}
shallow  = copy.copy(original)
deep     = copy.deepcopy(original)

shallow["scores"].append(99)   # mutates original["scores"] too!
deep["scores"].append(99)      # original is untouched
```

Bug risk: any time nested mutable objects (lists, dicts, custom objects) are shared unintentionally.

---

**Q9 🟡💬 What is `__slots__`? What are the trade-offs?**

**A:** `__slots__` replaces the per-instance `__dict__` with a fixed set of C-level slot descriptors.

```python
class Point:
    __slots__ = ("x", "y")
    def __init__(self, x, y): self.x = x; self.y = y
```

**Benefits:** ~30-50% less memory per instance; faster attribute access.  
**Drawbacks:** Cannot add arbitrary attributes at runtime; breaks some patterns (pickle, multiple inheritance) unless carefully handled; no `__weakref__` by default.

---

**Q10 🟡💬 How does Python's `import` system work? What is `__all__`?**

**A:** When you `import foo`:
1. Python checks `sys.modules` — if already imported, returns the cached module.
2. Otherwise, finds the module via `sys.meta_path` finders (file system, zip, namespace packages).
3. Loads and executes the module code in a new module namespace.
4. Stores result in `sys.modules`.

`__all__` is a list of names exported when `from module import *` is used. It does **not** prevent direct imports — it only controls the wildcard.

---

### Code Questions

---

**Q1 💻 What is the output? Explain why.**

```python
x = [[]] * 3
x[0].append(1)
print(x)
```

**A:** Output: `[[1], [1], [1]]`

`[[]] * 3` creates a list containing **three references to the same inner list object**. Mutating through `x[0]` mutates the single shared list, so all three slots reflect the change.

**Fix:**
```python
x = [[] for _ in range(3)]  # three distinct list objects
x[0].append(1)
print(x)  # [[1], [], []]
```

---

**Q2 💻 Implement a thread-safe singleton using a metaclass.**

```python
import threading

class SingletonMeta(type):
    _instances: dict = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class Database(metaclass=SingletonMeta):
    def __init__(self, url: str):
        self.url = url

db1 = Database("postgresql://localhost/dev")
db2 = Database("ignored")
assert db1 is db2   # True
```

**Key point:** The lock ensures only one thread can run the creation branch; subsequent threads get the cached instance.

---

**Q3 💻 What is wrong with this decorator? How do you fix it?**

```python
def retry(func):
    def wrapper(*args, **kwargs):
        for _ in range(3):
            try:
                return func(*args, **kwargs)
            except Exception:
                pass
    return wrapper
```

**Problems:**
1. **Swallows all exceptions silently** — if all retries fail, `None` is returned with no error.
2. **No back-off** — hammers the failing service immediately.
3. **Catches everything** — including `KeyboardInterrupt`, `SystemExit`.
4. **Not configurable** — attempts and exception types are hard-coded.
5. **Missing `functools.wraps`** — loses `__name__`, `__doc__`.

**Fixed version:**
```python
import time, functools

def retry(max_attempts=3, delay=0.5, exceptions=(Exception,)):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    if attempt == max_attempts:
                        raise
                    time.sleep(delay * 2 ** (attempt - 1))
        return wrapper
    return decorator
```

---

**Q4 💻 Implement a context manager that measures execution time — both class-based and `@contextmanager`.**

```python
import time
from contextlib import contextmanager

# ── Class-based ───────────────────────────────────────────
class Timer:
    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, *args):
        self.elapsed = time.perf_counter() - self.start
        print(f"Elapsed: {self.elapsed:.4f}s")
        return False  # don't suppress exceptions

with Timer() as t:
    time.sleep(0.1)
print(t.elapsed)

# ── @contextmanager ───────────────────────────────────────
@contextmanager
def timer():
    start = time.perf_counter()
    try:
        yield
    finally:
        print(f"Elapsed: {time.perf_counter() - start:.4f}s")

with timer():
    time.sleep(0.1)
```

---

**Q5 💻 Explain the output and fix it.**

```python
def make_multipliers():
    return [lambda x: i * x for i in range(4)]

print([m(2) for m in make_multipliers()])
```

**A:** Output: `[6, 6, 6, 6]`

All lambdas close over the **same variable `i`** (late binding). By the time any lambda is called, the loop has finished and `i == 3`.

**Fixes:**
```python
# Fix 1 — default argument captures value at definition time
[lambda x, i=i: i * x for i in range(4)]

# Fix 2 — functools.partial
import functools
[functools.partial(lambda i, x: i * x, i) for i in range(4)]
```

---

## 2. Data Structures & Algorithms

### Verbal Questions

---

**Q1 🟢💬 Time complexity of dict lookups, list appends, and set membership?**

**A:**
| Operation | Average | Worst case | Notes |
|---|---|---|---|
| `dict[key]` | O(1) | O(n) | Hash collision (rare) |
| `list.append(x)` | O(1) amortised | O(n) | Occasional resize doubles capacity |
| `x in set` | O(1) | O(n) | Hash collision (rare) |
| `x in list` | O(n) | O(n) | Linear scan |

---

**Q2 🟢💬 When would you choose a `deque` over a `list` for a queue?**

**A:** Use `collections.deque` when you need efficient **popleft**. `list.pop(0)` is O(n) because every element shifts; `deque.popleft()` is O(1). For a FIFO queue, `deque` is always the right choice. Use `list` only when you need random access by index.

---

**Q3 🟡💬 Generator vs list comprehension — memory implications?**

**A:** A list comprehension materialises all elements into memory at once — O(n) space. A generator yields one item at a time — O(1) space regardless of the sequence length. Use generators for large or infinite sequences, pipelines, and when you only need one pass.

```python
# 1 billion items — list comprehension would exhaust RAM
total = sum(x * x for x in range(1_000_000_000))
```

---

**Q4 🟡💬 What is `functools.lru_cache`? How does it work internally?**

**A:** `lru_cache` memoises a function's return values keyed on its arguments using a **fixed-size LRU (Least Recently Used) cache**. Internally it uses an ordered dict / doubly-linked list to evict the least recently accessed entry when the `maxsize` is reached.

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def fib(n):
    return n if n < 2 else fib(n-1) + fib(n-2)
```

Arguments must be **hashable**. `cache_info()` returns hits/misses/size.

---

**Q5 🟡💬 When would you use `heapq` vs `sorted()`?**

**A:**
- `sorted()` — sort a whole collection once: O(n log n), returns a new list. Best when you need the full sorted order.
- `heapq` — when you need the **k smallest/largest items** repeatedly, or a **priority queue** with dynamic insertions. `heappush`/`heappop` are O(log n). `heapq.nlargest(k, data)` is O(n + k log n) — faster than sort when k << n.

---

### Code Questions

---

**Q1 💻 Implement an LRU Cache (`get`/`put` in O(1)) without `functools`.**

```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache: OrderedDict = OrderedDict()

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)   # mark as recently used
        return self.cache[key]

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)  # evict LRU (front)
```

---

**Q2 💻 Find all pairs that sum to a target — most efficient approach.**

```python
def two_sum(nums: list[int], target: int) -> list[tuple[int, int]]:
    seen: dict[int, int] = {}   # value → index
    pairs = []
    for i, n in enumerate(nums):
        complement = target - n
        if complement in seen:
            pairs.append((complement, n))
        seen[n] = i
    return pairs

print(two_sum([1, 2, 3, 4, 6], 7))  # [(1, 6), (3, 4)]
```

**Complexity:** O(n) time, O(n) space.

---

**Q3 💻 Flatten a nested dictionary of arbitrary depth.**

```python
def flatten(d: dict, parent_key: str = "", sep: str = ".") -> dict:
    items: dict = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(flatten(v, new_key, sep))
        else:
            items[new_key] = v
    return items

print(flatten({"a": {"b": {"c": 1}}, "d": 2}))
# {"a.b.c": 1, "d": 2}
```

---

**Q4 💻 Generator that yields Fibonacci numbers indefinitely.**

```python
from itertools import islice

def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

print(list(islice(fibonacci(), 10)))
# [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

---

## 3. Object-Oriented Design & Design Patterns

### Verbal Questions

---

**Q1 🟡💬 Explain SOLID principles with a Python example for each.**

**A:**

**S — Single Responsibility:** A class should have one reason to change.
```python
# Bad: UserService handles both DB and email
# Good: split into UserRepository + EmailService
```

**O — Open/Closed:** Open for extension, closed for modification.
```python
from abc import ABC, abstractmethod
class Discount(ABC):
    @abstractmethod
    def apply(self, price: float) -> float: ...

class VIPDiscount(Discount):
    def apply(self, price): return price * 0.8
```

**L — Liskov Substitution:** Subclasses must be usable wherever the parent is expected without breaking behaviour.

**I — Interface Segregation:** Many small interfaces > one large interface. Use `Protocol` or multiple ABCs.

**D — Dependency Inversion:** Depend on abstractions, not concretions. Inject dependencies.

```python
class OrderService:
    def __init__(self, repo: AbstractOrderRepo):  # depends on abstraction
        self.repo = repo
```

---

**Q2 🟡💬 Composition vs inheritance — when do you prefer each?**

**A:**
- **Inheritance** ("is-a"): use when there is a genuine taxonomic relationship and you want to reuse and override behaviour. Keep hierarchies shallow (max 2–3 levels).
- **Composition** ("has-a"): preferred in most cases — more flexible, avoids the fragile base class problem, easier to test. "Favour composition over inheritance" (GoF).

```python
# Inheritance: Dog IS-A Animal ✓
# Composition: Car HAS-A Engine ✓ (not Car IS-A Engine)
class Car:
    def __init__(self):
        self.engine = Engine()   # composition
```

---

**Q3 🟡💬 Describe the Repository pattern. How does it help with testability?**

**A:** The Repository pattern abstracts data access behind an interface, decoupling business logic from the storage mechanism. Your service layer talks to `AbstractProductRepo`; the real implementation queries PostgreSQL; the test implementation uses an in-memory dict.

```python
from abc import ABC, abstractmethod

class AbstractProductRepo(ABC):
    @abstractmethod
    async def get(self, id: int): ...
    @abstractmethod
    async def save(self, product): ...

class InMemoryProductRepo(AbstractProductRepo):  # for tests
    def __init__(self): self._store = {}
    async def get(self, id): return self._store.get(id)
    async def save(self, p): self._store[p.id] = p
```

---

**Q4 🟡💬 What is dependency injection? How do you implement it in Python without a DI framework?**

**A:** DI means providing a component's dependencies from the outside rather than letting it create them internally. This makes components testable and loosely coupled.

```python
# Without DI — hard to test
class OrderService:
    def __init__(self):
        self.db = PostgresDB()   # coupled to Postgres

# With DI — inject the dependency
class OrderService:
    def __init__(self, db: AbstractDB):
        self.db = db             # test can pass InMemoryDB
```

In FastAPI, `Depends()` is the DI mechanism. Without a framework, pass dependencies through `__init__` (constructor injection).

---

**Q5 🟡💬 Difference between Strategy, Template Method, and Command patterns?**

**A:**
| Pattern | Intent | Python idiom |
|---|---|---|
| **Strategy** | Swap algorithm at runtime | Inject a callable or ABC subclass |
| **Template Method** | Define skeleton in base class, subclass fills steps | Abstract base class with `@abstractmethod` hooks |
| **Command** | Encapsulate a request as an object (undo/redo, queuing) | Callable objects or dataclasses with `execute()` |

---

### Code Questions

---

**Q1 💻 Refactor `Discount` to follow the Open/Closed Principle.**

```python
from abc import ABC, abstractmethod

class DiscountStrategy(ABC):
    @abstractmethod
    def apply(self, price: float) -> float: ...

class VIPDiscount(DiscountStrategy):
    def apply(self, price): return price * 0.80

class RegularDiscount(DiscountStrategy):
    def apply(self, price): return price * 0.95

class NoDiscount(DiscountStrategy):
    def apply(self, price): return price

class Order:
    def __init__(self, price: float, discount: DiscountStrategy):
        self.final_price = discount.apply(price)

# Adding a new discount type requires NO change to existing code.
print(Order(100, VIPDiscount()).final_price)   # 80.0
```

---

**Q2 💻 Implement the Observer pattern for a simple event bus.**

```python
from collections import defaultdict
from typing import Callable

class EventBus:
    def __init__(self):
        self._handlers: dict[str, list[Callable]] = defaultdict(list)

    def subscribe(self, event: str, handler: Callable) -> None:
        self._handlers[event].append(handler)

    def unsubscribe(self, event: str, handler: Callable) -> None:
        self._handlers[event].remove(handler)

    def publish(self, event: str, payload=None) -> None:
        for handler in list(self._handlers[event]):
            handler(payload)

bus = EventBus()
bus.subscribe("order.created", lambda p: print(f"Email sent for order {p['id']}"))
bus.subscribe("order.created", lambda p: print(f"Audit log: {p['id']}"))
bus.publish("order.created", {"id": 42})
```

---

**Q3 💻 Design an extensible `PaymentProcessor` (Stripe, PayPal, new providers without modifying existing code).**

```python
from abc import ABC, abstractmethod
from typing import Protocol

class PaymentProvider(Protocol):
    def charge(self, amount: float, currency: str) -> str: ...

class StripeProvider:
    def charge(self, amount, currency):
        return f"Stripe charged {amount} {currency}"

class PayPalProvider:
    def charge(self, amount, currency):
        return f"PayPal charged {amount} {currency}"

class PaymentProcessor:
    def __init__(self, provider: PaymentProvider):
        self._provider = provider

    def process(self, amount: float, currency: str = "USD") -> str:
        if amount <= 0:
            raise ValueError("Amount must be positive")
        return self._provider.charge(amount, currency)

# Adding CryptoProvider requires ZERO changes here.
processor = PaymentProcessor(StripeProvider())
print(processor.process(99.99))
```

---

## 4. Async Python & Concurrency

### Verbal Questions

---

**Q1 🟡💬 What is the event loop in `asyncio`? How is it different from threads?**

**A:** The asyncio **event loop** is a single-threaded scheduler that runs coroutines cooperatively. When a coroutine `await`s an I/O operation, it yields control back to the loop, which runs other ready coroutines. There is no preemption — coroutines must explicitly yield.

Threads use OS-level preemption and true parallelism (subject to the GIL for CPython). asyncio uses less memory (no per-thread stack), has no race conditions on shared state within the loop, and scales to thousands of concurrent I/O operations with one thread.

---

**Q2 🟡💬 `asyncio.gather` vs `asyncio.wait` vs `asyncio.TaskGroup`?**

**A:**
| | Returns | On first error | Control |
|---|---|---|---|
| `gather` | results in order | raises immediately (default) | simple |
| `wait` | (done, pending) sets | configurable (FIRST_EXCEPTION, ALL_COMPLETED) | fine-grained |
| `TaskGroup` (3.11+) | — | cancels all siblings | structured concurrency |

`TaskGroup` is preferred in new code — it guarantees cleanup and prevents task leaks.

---

**Q3 🟡💬 When would you use `multiprocessing` vs `threading` vs `asyncio`?**

**A:**
| Workload | Best choice | Reason |
|---|---|---|
| CPU-bound (pure Python) | `multiprocessing` | Bypasses GIL, real parallelism |
| CPU-bound (NumPy/C ext) | `threading` | C extensions release the GIL |
| I/O-bound (many connections) | `asyncio` | Single thread, no context-switch overhead |
| I/O-bound (blocking libs) | `threading` | GIL released during I/O syscalls |
| Mixed CPU + I/O | `asyncio` + `run_in_executor` | Offload CPU to process pool |

---

**Q4 🟡💬 What is a coroutine? Difference between `async def` and a regular generator?**

**A:** A **coroutine** (`async def`) is a function that can suspend at `await` points, yielding control to the event loop. Unlike a generator (which uses `yield` and is pull-based), a coroutine is push-based — the event loop drives it by calling `.send()` internally. Coroutines are awaitables; generators are iterables. You cannot `await` a plain generator.

---

**Q5 🟡💬 Race conditions in async code — how do you prevent them?**

**A:** Even in single-threaded asyncio, a race condition occurs when two coroutines interleave at `await` points and both read-then-write shared state:

```python
# RACE: two coroutines both read counter=0, both write counter=1
async def increment():
    val = counter          # read
    await asyncio.sleep(0) # yield — other coroutine runs here
    counter = val + 1      # write → lost update
```

**Fixes:**
- `asyncio.Lock` — mutual exclusion across `await` points.
- `asyncio.Queue` — producer-consumer without shared mutable state.
- Avoid sharing mutable state across coroutines when possible.

---

**Q6 🟡💬 What is `asyncio.Queue`? When is it useful?**

**A:** `asyncio.Queue` is a thread-safe, async-native FIFO queue for producer-consumer patterns within the event loop. Producers call `await q.put(item)`; consumers call `await q.get()`. The queue backpressure (`maxsize`) prevents producers from outrunning consumers. Useful for rate-limited processing, batching, and work pipelines.

---

### Code Questions

---

**Q1 💻 What is wrong with this async code? How do you make it concurrent?**

```python
# WRONG — sequential, total time = 3 × sleep(1)
async def main():
    results = []
    for url in ["url1", "url2", "url3"]:
        results.append(await fetch(url))   # waits for each before starting next
```

**Problem:** `await` inside the loop means each request waits for the previous one to complete — no concurrency.

```python
# CORRECT — all three run concurrently, total time ≈ 1 × sleep(1)
import asyncio

async def main():
    results = await asyncio.gather(
        fetch("url1"), fetch("url2"), fetch("url3")
    )
    return results

# Or with TaskGroup (Python 3.11+):
async def main():
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(fetch(u)) for u in ["url1","url2","url3"]]
    return [t.result() for t in tasks]
```

---

**Q2 💻 Rate-limited async HTTP client — at most N requests per second.**

```python
import asyncio, aiohttp, time

class RateLimiter:
    def __init__(self, rate: int):
        self._sem = asyncio.Semaphore(rate)

    async def __aenter__(self):
        await self._sem.acquire()
        # Release the slot after 1 second, allowing the next request
        asyncio.get_event_loop().call_later(1.0, self._sem.release)

    async def __aexit__(self, *_):
        pass  # release is scheduled via call_later

limiter = RateLimiter(rate=5)   # 5 req/s

async def fetch(session, url):
    async with limiter:
        async with session.get(url) as resp:
            return await resp.json()
```

---

**Q3 💻 Producer-consumer pattern using `asyncio.Queue`.**

```python
import asyncio, random

async def producer(queue: asyncio.Queue, n: int):
    for i in range(n):
        item = f"task-{i}"
        await queue.put(item)
        print(f"  produced: {item}")
        await asyncio.sleep(random.uniform(0.05, 0.2))
    await queue.put(None)   # sentinel to stop consumer

async def consumer(queue: asyncio.Queue):
    while True:
        item = await queue.get()
        if item is None:
            break
        print(f"  consumed: {item}")
        await asyncio.sleep(0.1)   # simulate processing
        queue.task_done()

async def main():
    q: asyncio.Queue = asyncio.Queue(maxsize=3)
    await asyncio.gather(producer(q, 8), consumer(q))

asyncio.run(main())
```

---

## 5. FastAPI & REST API Design

### Verbal Questions

---

**Q1 🟢💬 How does FastAPI handle request validation? What library does it use?**

**A:** FastAPI uses **Pydantic** (v2 in FastAPI 0.100+) for request validation. Declare a Pydantic `BaseModel` as a parameter type and FastAPI automatically:
1. Parses the request body JSON.
2. Validates each field against the type annotation and any validators.
3. Returns HTTP **422 Unprocessable Entity** with field-level error details if validation fails.
4. Provides the validated object to the route handler.

Path/query parameters use Pydantic field validators too, declared via `Path(...)`, `Query(...)`.

---

**Q2 🟡💬 What is dependency injection in FastAPI? Give a real-world example.**

**A:** `Depends(callable)` tells FastAPI to call `callable`, inject its return value into the route, and share the instance within the request. Dependencies can be chained — a dependency can itself declare `Depends`.

```python
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session           # teardown after response

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db:    AsyncSession = Depends(get_db),
) -> User:
    ...                         # decode JWT, load user from db

@router.get("/me")
async def read_me(user: User = Depends(get_current_user)):
    return user
```

---

**Q3 🟡💬 How do you implement JWT authentication in FastAPI?**

**A:**
1. **Login endpoint** — verify credentials, sign a JWT with `python-jose`/`PyJWT`, return `{"access_token": ..., "token_type": "bearer"}`.
2. **`OAuth2PasswordBearer`** — tells FastAPI/Swagger where the token endpoint is; extracts the `Authorization: Bearer <token>` header.
3. **`get_current_user` dependency** — decodes JWT, validates expiry/signature, loads user from DB, raises HTTP 401 on failure.
4. **RBAC** — a `require_role(*roles)` factory dependency wraps `get_current_user` and raises HTTP 403 if the user's role is not in `roles`.

---

**Q4 🟡💬 `APIRouter` vs including routes directly on the `FastAPI` app?**

**A:** `APIRouter` is a mini-application with the same path operation decorators as `FastAPI`. It lets you group related routes in a separate module, apply shared `prefix`, `tags`, `dependencies`, and `responses` to the whole group, then mount it with `app.include_router(router)`. For anything beyond a toy app, use routers — one per domain (users, products, orders).

---

**Q5 🟡💬 Background tasks in FastAPI — when to use Celery instead?**

**A:**
- **`BackgroundTasks`** — built-in; runs the task in the same process after the response is sent. No persistence, no retry, no monitoring. Good for simple fire-and-forget (send a welcome email).
- **Celery + Redis/RabbitMQ** — distributed worker process; survives app restarts; supports retries with backoff, scheduling (beat), priority queues, monitoring (Flower). Use when tasks are long-running (> a few seconds), must not be lost on restart, or need to be distributed across workers.

---

**Q6 🟡💬 How does FastAPI generate OpenAPI docs? How do you customise?**

**A:** At startup FastAPI introspects every registered route's type annotations, Pydantic models, `status_code`, `response_model`, `tags`, `summary`, `description`, and security dependencies. It builds a `dict` conforming to OpenAPI 3.x and serves it at `/openapi.json`. Swagger UI (`/docs`) and ReDoc (`/redoc`) read this JSON.

Customise with:
```python
app = FastAPI(title="My API", version="2.0", docs_url="/api/docs")

@app.get("/items", summary="List items", tags=["items"],
         response_description="A paginated list")
```

---

**Q7 🟡💬 How does middleware work in FastAPI? How do you write custom middleware?**

**A:** Middleware is an ASGI wrapper around the entire app — it intercepts every request *before* routing and every response *after* the handler returns.

```python
from fastapi import FastAPI, Request
import time, uuid

app = FastAPI()

@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start = time.perf_counter()
    response = await call_next(request)             # call the rest of the stack
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = str(time.perf_counter() - start)
    return response
```

For class-based middleware, subclass `starlette.middleware.base.BaseHTTPMiddleware`.

---

### Code Questions

---

**Q1 💻 FastAPI endpoint for paginated user listing.**

```python
from fastapi import FastAPI, Depends, Query
from pydantic import BaseModel
from typing import Generic, TypeVar, List

T = TypeVar("T")

class Page(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int

class UserOut(BaseModel):
    id: int
    name: str
    email: str

def pagination(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str = Query(""),
):
    return {"skip": (page - 1) * page_size, "limit": page_size,
            "page": page, "page_size": page_size, "search": search}

app = FastAPI()

@app.get("/users", response_model=Page[UserOut])
async def list_users(p=Depends(pagination), db=Depends(get_db)):
    query = select(User)
    if p["search"]:
        query = query.where(User.name.ilike(f"%{p['search']}%"))
    total = await db.scalar(select(func.count()).select_from(query.subquery()))
    rows  = await db.scalars(query.offset(p["skip"]).limit(p["limit"]))
    return Page(items=list(rows), total=total,
                page=p["page"], page_size=p["page_size"])
```

---

**Q2 💻 Reusable dependency that validates a JWT from the `Authorization` header.**

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel

SECRET, ALGO = "secret-key", "HS256"
oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/token")

class TokenPayload(BaseModel):
    sub: str
    role: str = "user"

async def get_current_user(token: str = Depends(oauth2)) -> TokenPayload:
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGO])
        return TokenPayload(**payload)
    except (JWTError, Exception):
        raise exc
```

---

**Q3 💻 Rate-limiting middleware using a sliding window algorithm.**

```python
import time
from collections import defaultdict, deque
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()
RATE  = 10    # max requests
WINDOW = 60   # seconds
_windows: dict[str, deque] = defaultdict(deque)

@app.middleware("http")
async def rate_limit(request: Request, call_next):
    ip  = request.client.host
    now = time.time()
    q   = _windows[ip]
    # evict timestamps outside the window
    while q and q[0] < now - WINDOW:
        q.popleft()
    if len(q) >= RATE:
        return JSONResponse({"detail": "Too many requests"}, status_code=429,
                            headers={"Retry-After": str(WINDOW)})
    q.append(now)
    return await call_next(request)
```

---

**Q4 💻 What is wrong with this Pydantic model?**

```python
class CreateUserRequest(BaseModel):
    user: User
    password: str   # ← problem
```

**Problems:**
1. **`password` should never be in a nested `User` model or logged** — it sits alongside the user data, making it easy to accidentally serialise/log the password.
2. **No validation on password strength** — should use `Annotated[str, Field(min_length=8)]` or a custom validator.
3. **Should use `SecretStr`** — Pydantic's `SecretStr` prevents the password from appearing in `repr()` and JSON serialisation.

```python
from pydantic import BaseModel, SecretStr, Field, field_validator

class CreateUserRequest(BaseModel):
    name: str
    email: str
    password: SecretStr = Field(min_length=8)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if "@" not in v:
            raise ValueError("Invalid email")
        return v.lower()
```

---

## 6. Databases — SQL, ORM & NoSQL

### Verbal Questions

---

**Q1 🟡💬 N+1 query problem and how SQLAlchemy solves it.**

**A:** The N+1 problem: loading N parent rows, then issuing 1 separate query per row to load related rows = N+1 queries total.

```python
# N+1: 1 query for users + 1 per user for orders
users = session.scalars(select(User)).all()
for u in users:
    print(u.orders)   # lazy load triggers a new query each time
```

**Fixes:**
- `selectinload` — one extra `SELECT … WHERE id IN (…)` per relationship. Best for one-to-many.
- `joinedload` — SQL JOIN in the same query. Best for many-to-one / one-to-one.

```python
stmt = select(User).options(selectinload(User.orders))
users = session.scalars(stmt).all()   # 2 queries total, not N+1
```

---

**Q2 🟡💬 Database transactions and ACID properties.**

**A:**
- **Atomicity** — all operations in a transaction succeed or all are rolled back.
- **Consistency** — the DB goes from one valid state to another; constraints are enforced.
- **Isolation** — concurrent transactions don't see each other's partial changes (controlled by isolation level).
- **Durability** — committed data survives crashes (written to disk/WAL).

In SQLAlchemy async: use `async with session.begin()` or `await session.commit()` / `await session.rollback()`.

---

**Q3 🟡💬 Optimistic vs pessimistic locking.**

**A:**
- **Optimistic locking** — no lock is held; instead a `version` column is checked at UPDATE time. If it changed since your read, the update fails → application retries. Good for low-contention scenarios.
- **Pessimistic locking** — `SELECT … FOR UPDATE` locks the row at read time. Prevents concurrent writes. Good for high-contention / financial transactions.

SQLAlchemy uses **optimistic locking** by default via `version_id_col`. Pessimistic locking: `with_for_update()`.

---

**Q4 🟡💬 When would you use NoSQL (MongoDB / Redis) over PostgreSQL?**

**A:**
- **Redis** — in-memory key-value; use for caching, session storage, rate limiting, pub/sub, leaderboards. Sub-millisecond latency.
- **MongoDB** — document store; use when schema is highly variable, data is naturally hierarchical (JSON documents), or you need flexible querying without migrations.
- **PostgreSQL** — use when you need ACID transactions, complex relational queries, JOINs, foreign keys, or full-text search. Supports JSONB for semi-structured data.

---

**Q5 🟡💬 Zero-downtime database migrations.**

**A:** Use the **expand/contract** (parallel-change) pattern:

1. **Expand** — add the new column as nullable; deploy the app (reads both old and new).
2. **Backfill** — populate the new column for existing rows in small batches.
3. **Migrate** — update app to write only to new column; deploy.
4. **Contract** — make column NOT NULL, drop old column; deploy.

Never rename or drop a column in the same deployment as the code change. Run `alembic upgrade head` in a Kubernetes **init container** before pods start.

---

**Q6 🟡💬 Connection pooling in SQLAlchemy.**

**A:** SQLAlchemy maintains a pool of reusable DB connections (`pool_size`, `max_overflow`, `pool_timeout`). Instead of opening/closing a connection per request (expensive), the pool lends a connection for the duration of a session and returns it. With async SQLAlchemy: `create_async_engine(url, pool_size=10, max_overflow=5)`. If the pool is exhausted, new requests wait up to `pool_timeout` before raising `TimeoutError`.

---

### Code Questions

---

**Q1 💻 Async SQLAlchemy query — users with recent orders, no N+1.**

```python
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.orm import selectinload

async def get_users_with_recent_orders(db: AsyncSession) -> list[User]:
    cutoff = datetime.utcnow() - timedelta(days=30)
    stmt = (
        select(User)
        .options(selectinload(User.orders))
        .join(User.orders)
        .where(Order.created_at >= cutoff)
        .distinct()
    )
    result = await db.scalars(stmt)
    return list(result)
```

---

**Q2 💻 Repository pattern for a User model.**

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: int) -> User | None:
        return await self.session.get(User, user_id)

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def create(self, **kwargs) -> User:
        user = User(**kwargs)
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def delete(self, user: User) -> None:
        await self.session.delete(user)
        await self.session.flush()
```

---

**Q3 💻 Top 5 users by total order amount in the last 90 days (including zero-order users).**

```sql
SELECT
    u.id,
    u.name,
    COALESCE(SUM(o.amount), 0)   AS total_amount
FROM users u
LEFT JOIN orders o
    ON  o.user_id   = u.id
    AND o.created_at >= NOW() - INTERVAL '90 days'
GROUP BY u.id, u.name
ORDER BY total_amount DESC
LIMIT 5;
```

`LEFT JOIN` with the date filter *inside* the join condition (not in `WHERE`) ensures users with no qualifying orders are included with `COALESCE(..., 0)`.

---


## 7. Testing

### Verbal Questions

---

**Q1 🟢💬 Unit vs integration vs end-to-end tests.**

**A:**
| Type | Scope | Speed | Isolation |
|---|---|---|---|
| Unit | Single function/class | Fast (ms) | Full mocking of dependencies |
| Integration | Multiple components (service + DB) | Medium | Real or in-memory DB |
| End-to-end | Full system (HTTP → DB → response) | Slow | Real running app |

Use the **test pyramid**: many units, fewer integration, few E2E.

---

**Q2 🟡💬 What is mocking? When should you avoid it?**

**A:** Mocking replaces a real dependency with a controllable fake (`unittest.mock.MagicMock`, `pytest-mock`). Use it to isolate a unit from I/O, external services, time, or slow operations.

**Avoid mocking when:**
- You mock so much that the test no longer tests real behaviour.
- You mock internals instead of public contracts — tests break on refactoring.
- An in-memory fake (e.g. SQLite) is available and cheap — prefer it over mocking the ORM.

---

**Q3 🟡💬 pytest fixtures — `scope` levels.**

**A:**
| Scope | Lifetime | Use case |
|---|---|---|
| `function` (default) | Per test | Fresh state; DB rollback per test |
| `class` | Per test class | Shared setup across methods |
| `module` | Per file | Expensive one-time setup (e.g. compile) |
| `session` | Entire test run | Create DB engine once, shared across all tests |

---

**Q4 🟡💬 TDD — advantages and disadvantages.**

**A:**
- **Advantages:** Forces you to think about the API before implementation; catches regressions early; acts as living documentation; leads to more modular, testable code.
- **Disadvantages:** Slower initial development; hard to apply when the design is exploratory; can lead to over-engineered tests if not disciplined; UI and integration layers are awkward to TDD.

---

**Q5 🟡💬 How do you test async code in pytest?**

**A:** Use `pytest-asyncio`. Mark async tests with `@pytest.mark.asyncio` (or configure `asyncio_mode = "auto"` in `pytest.ini`). Use `httpx.AsyncClient` with `ASGITransport` for FastAPI endpoint tests.

```python
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(transport=ASGITransport(app=app),
                           base_url="http://test") as client:
        resp = await client.get("/health")
    assert resp.status_code == 200
```

---

**Q6 🟡💬 Is 100% code coverage a good goal?**

**A:** No. Coverage tells you which lines were *executed*, not whether they were tested *correctly*. Chasing 100% leads to trivial tests just to tick boxes. A better goal: **meaningful coverage** (80–90%) focused on business logic, edge cases, and error paths — not getters/setters or framework glue code.

---

### Code Questions

---

**Q1 💻 pytest test for `get_user` using mocks.**

```python
import pytest
from unittest.mock import patch, MagicMock
from myapp import get_user

def test_get_user_success():
    mock_response = MagicMock()
    mock_response.json.return_value = {"id": 1, "name": "Alice"}
    mock_response.raise_for_status = MagicMock()

    with patch("myapp.httpx.get", return_value=mock_response) as mock_get:
        result = get_user(1)

    mock_get.assert_called_once_with("https://api.example.com/users/1")
    assert result == {"id": 1, "name": "Alice"}

def test_get_user_http_error():
    import httpx
    with patch("myapp.httpx.get") as mock_get:
        mock_get.return_value.raise_for_status.side_effect = httpx.HTTPStatusError(
            "404", request=MagicMock(), response=MagicMock()
        )
        with pytest.raises(httpx.HTTPStatusError):
            get_user(999)
```

---

**Q2 💻 pytest fixture — in-memory SQLite DB with teardown.**

```python
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.db.base import Base

@pytest_asyncio.fixture(scope="session")
async def engine():
    eng = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await eng.dispose()

@pytest_asyncio.fixture
async def db_session(engine):
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        yield session
        await session.rollback()
```

---

**Q3 💻 Parametrised test for email validation.**

```python
import pytest, re

def is_valid_email(email: str) -> bool:
    return bool(re.match(r"^[\w.+-]+@[\w-]+\.[a-z]{2,}$", email, re.I))

@pytest.mark.parametrize("email,expected", [
    ("user@example.com",     True),
    ("user.name+tag@sub.io", True),
    ("missing-at-sign",      False),
    ("@nodomain.com",        False),
    ("user@domain",          False),
    ("",                     False),
])
def test_email_validation(email, expected):
    assert is_valid_email(email) == expected
```

---

## 8. Software Architecture & System Design

### Verbal Questions

---

**Q1 🟡💬 Monolithic vs microservices vs event-driven architectures.**

**A:**
| Architecture | Pros | Cons | Best for |
|---|---|---|---|
| Monolith | Simple deploy, single transaction, easy local dev | Hard to scale parts independently | Early-stage products, small teams |
| Microservices | Independent scaling, fault isolation | Network latency, distributed tracing complexity | Large orgs, independently scaling domains |
| Event-driven | Loose coupling, async, resilient | Eventual consistency, harder to debug | High throughput, audit logs, CQRS |

---

**Q2 🟡💬 How do you design an API for versioning (v1, v2)?**

**A:**
- **URL path versioning** (`/api/v1/`, `/api/v2/`) — most common; explicit; easy to document.
- **Header versioning** (`Accept: application/vnd.api.v2+json`) — cleaner URLs; harder to test in browser.
- **Query param** (`?version=2`) — discouraged; breaks caching.

For FastAPI: create separate `APIRouter` per version, mount at different prefixes. Maintain v1 until a deprecation cutoff date is communicated.

---

**Q3 🟡💬 Circuit Breaker pattern — when to implement it?**

**A:** Prevents cascading failures when a downstream service is unhealthy. States:
- **Closed** — normal operation.
- **Open** — failure threshold exceeded; requests fail fast.
- **Half-open** — probe requests sent; if they succeed, circuit closes again.

Implement when calling external APIs, databases, or microservices that can be slow or unavailable. Libraries: `pybreaker`, `tenacity`, or Istio service mesh.

---

**Q4 🔴💬 Eventual consistency in distributed systems.**

**A:**
- **Saga pattern** — sequence of local transactions with compensating transactions on failure.
- **Event sourcing** — changes are events; projections are eventually consistent views.
- **Outbox pattern** — write to DB + outbox table in one transaction; relay publishes events reliably.
- Accept stale reads where the business allows (e.g. product inventory counts).

---

**Q5 🟡💬 What is CQRS? When is it beneficial?**

**A:** **Command Query Responsibility Segregation** separates the write model (commands) from the read model (queries). The read model is a denormalised projection updated asynchronously. Beneficial when read and write patterns differ greatly, queries need heavy aggregation, or read/write scalability must be independent. Adds complexity — only justify at scale.

---

**Q6 🟡💬 Design a URL shortener at scale.**

**A:**
- **API:** `POST /shorten` → returns short code; `GET /{code}` → 301 redirect.
- **Storage:** Base62(SHA-256 prefix) → original URL in Redis (hot) + PostgreSQL (persistent).
- **Scale:** Stateless API pods. Redis cluster handles most reads (sub-ms). Distributed counter for ID generation.
- **Rate limiting:** Per IP via Redis sliding window.
- **Analytics:** Kafka → Flink/Spark → ClickHouse for click metrics.

---

**Q7 🟡💬 Message queue — Kafka vs RabbitMQ vs Redis Streams.**

**A:**
| | Kafka | RabbitMQ | Redis Streams |
|---|---|---|---|
| Persistence | Durable log (replayable) | Queue (acked = deleted) | Log (configurable) |
| Throughput | Millions/s | 100k+/s | High |
| Use case | Event sourcing, analytics | Work queues, RPC | Lightweight pubsub |
| Complexity | High | Medium | Low (if Redis already used) |

---

### System Design Challenge

---

**Design a real-time notification service (1M+ users, at-least-once delivery, email/SMS/push).**

**A:**

```
[API Service] → POST /notifications
       ↓
[Outbox Table in PostgreSQL]   ← atomic with business write
       ↓ (Transactional Outbox Relay)
[Kafka Topic: notifications]
       ↓ (Consumer Groups)
 ┌─────┼──────────┐
[Email Worker] [SMS Worker] [Push Worker]
 (SES)          (Twilio)     (FCM/APNs)
       ↓
[Dead Letter Queue] ← retries with exponential backoff
       ↓
[Alerting: Prometheus + PagerDuty]
```

**Key decisions:**
- **Outbox pattern** ensures no notification is lost even if Kafka is down at write time.
- **Idempotency key** on each notification deduplicates retries.
- **Prometheus RED metrics** per channel (rate, errors, duration).
- **OpenTelemetry** traces from API call → Kafka message → delivery confirmation.

---

## 9. DevOps — Docker & Containerisation

### Verbal Questions

---

**Q1 🟢💬 What is the difference between a Docker image and a container?**

**A:** An **image** is an immutable, layered filesystem snapshot (the blueprint). A **container** is a running instance of an image — an isolated process with its own filesystem, network, and PID namespace. Multiple containers can run from the same image simultaneously.

---

**Q2 🟡💬 What is a multi-stage Docker build and why is it important for Python?**

**A:** Multi-stage builds use multiple `FROM` instructions in a single Dockerfile. A **builder** stage installs all build tools and dependencies; the **runtime** stage copies only what's needed (the installed packages, the app code) into a minimal base image. This keeps secrets and build tools out of the final image and reduces image size significantly.

---

**Q3 🟡💬 How do you reduce Python Docker image size? Name 5 techniques.**

**A:**
1. Use `python:3.12-slim` or `python:3.12-alpine` instead of the full image.
2. Multi-stage build — copy only the installed venv, not build tools.
3. `--no-cache-dir` in `pip install` — don't store the pip cache.
4. `--no-install-recommends` for any `apt-get install`.
5. Add `.dockerignore` to exclude `.git`, `__pycache__`, tests, docs.
6. Use `PYTHONDONTWRITEBYTECODE=1` to skip `.pyc` files.
7. Merge `RUN` commands to reduce layers.

---

**Q4 🟢💬 `CMD` vs `ENTRYPOINT` in a Dockerfile?**

**A:**
- **`ENTRYPOINT`** — the fixed executable that always runs. Not easily overridden at `docker run` time.
- **`CMD`** — default arguments to `ENTRYPOINT`, or a default command if no `ENTRYPOINT` is set. Easily overridden.

Best practice: use `ENTRYPOINT ["uvicorn"]` + `CMD ["app.main:app", "--host", "0.0.0.0"]` so you can override just the arguments in Kubernetes without changing the entrypoint.

---

**Q5 🟡💬 How do you handle secrets in Docker?**

**A:**
- **Never** bake secrets into images — they persist in layer history even after `RUN rm`.
- Use **environment variables** injected at runtime (`docker run -e DB_PASSWORD=...`).
- Use **Docker secrets** (Swarm) or **Kubernetes Secrets** mounted as env vars or files.
- In CI: use `--secret id=mysecret,src=...` in `docker buildx build` for build-time secrets (not stored in layers).

---

**Q6 🟡💬 Docker layer caching — how to optimise?**

**A:** Docker caches each layer. If a layer's content changes, all subsequent layers are invalidated. For Python:

```dockerfile
# GOOD — dependency layer cached unless requirements.txt changes
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .                           # code changes don't bust dep cache

# BAD — COPY . . first busts the pip cache on every code change
COPY . .
RUN pip install -r requirements.txt
```

---

### Code Questions

---

**Q1 💻 What is wrong with this Dockerfile? Fix it.**

```dockerfile
# WRONG
FROM python:3.11
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
```

**Problems:**
1. Full image (`python:3.11`) is ~1GB — use `slim`.
2. `COPY . .` before `pip install` — busts cache on every code change.
3. No `--no-cache-dir` — pip cache bloats the image.
4. Running as root — security risk.
5. No `PYTHONUNBUFFERED` — logs may be buffered.

```dockerfile
FROM python:3.12-slim AS builder
WORKDIR /app
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /install /usr/local
COPY . .
RUN adduser --disabled-password appuser && chown -R appuser /app
USER appuser
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

**Q2 💻 Production docker-compose.yml for FastAPI + PostgreSQL + Redis.**

```yaml
version: "3.9"

services:
  api:
    build: .
    ports: ["8000:8000"]
    env_file: .env
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      timeout: 5s
      retries: 5

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: appdb
    volumes: [pgdata:/var/lib/postgresql/data]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app"]
      interval: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      retries: 5

volumes:
  pgdata:
```

---

## 10. Kubernetes — Deployment & Operations

### Verbal Questions

---

**Q1 🟢💬 Key Kubernetes objects: Pod, Deployment, Service, Ingress, ConfigMap, Secret.**

**A:**
| Object | Purpose |
|---|---|
| **Pod** | Smallest deployable unit — one or more containers sharing network/storage |
| **Deployment** | Manages a ReplicaSet; handles rolling updates and rollbacks |
| **Service** | Stable DNS name + load balancer in front of a set of Pods (ClusterIP/NodePort/LoadBalancer) |
| **Ingress** | HTTP/HTTPS routing from outside the cluster to Services (path/host-based) |
| **ConfigMap** | Non-sensitive configuration as key-value pairs or files |
| **Secret** | Base64-encoded sensitive data (passwords, tokens) — mounted as env vars or files |

---

**Q2 🟡💬 `Deployment` vs `StatefulSet`.**

**A:**
- **Deployment** — stateless; pods are interchangeable; rolling update can replace pods in any order.
- **StatefulSet** — stateful; each pod has a stable hostname (`pod-0`, `pod-1`) and a persistent volume that follows it across restarts; pods are created/deleted in order. Use for databases, Kafka, ZooKeeper.

---

**Q3 🟡💬 How does Kubernetes handle rolling updates and rollbacks?**

**A:** A rolling update creates new pods with the new image while gradually terminating old ones, controlled by `maxSurge` (extra pods above desired) and `maxUnavailable` (pods that can be offline during update). New pods must pass readiness probes before old ones are terminated. Rollback: `kubectl rollout undo deployment/myapp` reverts to the previous ReplicaSet.

---

**Q4 🟡💬 Liveness vs readiness probe — why are both important?**

**A:**
- **Readiness** — "is this pod ready to receive traffic?" Failing pods are removed from the Service endpoints. Use for: waiting for DB connection, warmup, temporary overload.
- **Liveness** — "is this pod still alive?" Failing pods are restarted. Use for: detecting deadlocks, infinite loops.
- Using only liveness risks killing pods that are temporarily busy; using only readiness means a stuck pod never restarts.

---

**Q5 🟡💬 How do you configure HPA for a FastAPI service?**

**A:**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: fastapi-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: fastapi-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 60
```

Custom metrics (Prometheus): use `prometheus-adapter` to expose `http_requests_per_second` as a custom metric and reference it in the HPA `metrics` list.

---

**Q6 🟡💬 Kubernetes namespace — isolating environments.**

**A:** Namespaces provide a logical partition within a cluster — separate resource quotas, RBAC policies, and network policies per namespace. Common patterns:
- `dev`, `staging`, `production` in the same cluster (simpler ops, risk of noisy neighbours).
- Separate clusters per environment (stronger isolation, higher cost).

Use `ResourceQuota` to prevent one namespace from consuming all cluster resources.

---

**Q7 🟡💬 Injecting secrets from Kubernetes Secrets or HashiCorp Vault.**

**A:**
- **Kubernetes Secrets** — mounted as env vars (`envFrom.secretRef`) or volume files. Base64-encoded, not encrypted at rest by default (enable encryption at rest in etcd).
- **HashiCorp Vault** — external secrets store with fine-grained access control, dynamic credentials (rotated automatically), audit logging. Use **external-secrets-operator** or **vault-agent-injector** (sidecar) to sync secrets into Kubernetes Secrets or inject them directly into the pod.

---

**Q8 🔴💬 What is a service mesh (e.g. Istio)? What problems does it solve?**

**A:** A service mesh is an infrastructure layer that handles service-to-service communication via sidecar proxies (Envoy). It solves: mTLS (zero-trust encryption between services), traffic management (canary, blue/green, retries, circuit breaking), observability (distributed traces, metrics, access logs) — without changing application code.

---

**Q9 🟡💬 Zero-downtime deployments in Kubernetes.**

**A:**
1. `strategy.type: RollingUpdate` with `maxUnavailable: 0`, `maxSurge: 1`.
2. Readiness probes — new pods only receive traffic after they pass.
3. `preStop` lifecycle hook + `terminationGracePeriodSeconds` — give old pods time to drain in-flight requests.
4. Database migrations run as init containers *before* pods start (backward-compatible migrations).
5. Feature flags for risky changes — deploy disabled, enable gradually.

---

**Q10 🟡💬 Resource requests and limits — what happens when a Pod exceeds memory limit?**

**A:**
- **Requests** — minimum guaranteed resources; used by the scheduler to place the pod on a node.
- **Limits** — maximum allowed; enforced by the kubelet.
- If a container exceeds its **memory limit**, it is **OOMKilled** (killed immediately by the kernel OOM killer) and the pod is restarted (if the restart policy allows).
- Exceeding **CPU limit** throttles (not killed); the container gets less CPU time.

---

### Code / Config Questions

---

**Q1 💻 Kubernetes Deployment manifest for a FastAPI app.**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-app
  labels:
    app: fastapi-app
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: fastapi-app
  template:
    metadata:
      labels:
        app: fastapi-app
    spec:
      containers:
      - name: fastapi
        image: ghcr.io/myorg/fastapi-app:abc1234
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: fastapi-config
        - secretRef:
            name: fastapi-secrets
        resources:
          requests:
            cpu: "250m"
            memory: "256Mi"
          limits:
            cpu: "500m"
            memory: "512Mi"
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
          failureThreshold: 3
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 15
          periodSeconds: 20
```

---

**Q2 💻 Diagnose and roll back a CrashLoopBackOff deployment.**

```bash
# 1. See which pods are crashing
kubectl get pods -n production

# 2. Describe the failing pod for events/reasons
kubectl describe pod fastapi-app-xyz -n production

# 3. Read the container logs (current and previous crash)
kubectl logs fastapi-app-xyz -n production
kubectl logs fastapi-app-xyz -n production --previous

# 4. Check recent events in the namespace
kubectl get events -n production --sort-by='.lastTimestamp'

# 5. Roll back to the previous revision
kubectl rollout undo deployment/fastapi-app -n production

# 6. Confirm rollout
kubectl rollout status deployment/fastapi-app -n production
```

---

## 11. CI/CD Pipelines

### Verbal Questions

---

**Q1 🟢💬 CI vs Continuous Delivery vs Continuous Deployment.**

**A:**
- **CI** — automatically build and test on every commit. Catch integration bugs early.
- **Continuous Delivery** — every passing build is *releasable* to production with one manual click.
- **Continuous Deployment** — every passing build is automatically deployed to production — no manual gate.

---

**Q2 🟡💬 How do you structure a CI pipeline for a Python project?**

**A:**
1. **Lint** — `ruff check .`, `mypy` (fast, fails first).
2. **Unit tests** — `pytest` with coverage threshold.
3. **Security scan** — `bandit`, `pip-audit` (CVEs in dependencies).
4. **Build** — `docker buildx build`, tag with git SHA.
5. **Integration tests** — spin up DB/Redis with Docker Compose, run integration suite.
6. **Image scan** — `trivy` for container vulnerabilities.
7. **Push** — push image to registry only on `main`/tag.
8. **Deploy** — update Helm chart / Kustomize overlay; ArgoCD syncs.

---

**Q3 🟡💬 Managing environment-specific configuration (dev/staging/prod).**

**A:**
- **Kustomize** — base manifests + per-environment overlays that patch replicas, images, env vars.
- **Helm** — single chart with `values-dev.yaml`, `values-staging.yaml`, `values-prod.yaml`.
- **Separate namespaces** — `dev`, `staging`, `prod` in one cluster.
- **Separate clusters** — stronger isolation for prod; higher cost.
- **Secrets** — never in Git; use external-secrets-operator or Vault.

---

**Q4 🟡💬 How do you implement GitOps with ArgoCD or Flux?**

**A:** Git is the single source of truth for cluster state. An in-cluster operator watches a Git repo and reconciles the cluster to match:

1. CI pipeline builds image, tags with git SHA, pushes to registry.
2. CI updates the image tag in the Kustomize overlay / Helm values file and commits to the config repo.
3. ArgoCD/Flux detects the change, syncs the cluster (applies manifests).
4. If the live cluster drifts from Git (manual `kubectl` changes), ArgoCD/Flux reverts it.

---

**Q5 🟡💬 Managing database migrations in a Kubernetes deployment pipeline.**

**A:** Run `alembic upgrade head` as a **Kubernetes init container** that executes before the app containers start. This guarantees migrations complete before new code runs. Use backward-compatible migrations (expand/contract pattern) so old pods still work while new ones are rolling out.

---

### Code / Config Questions

---

**Q1 💻 GitHub Actions workflow — lint, type-check, test, build, push Docker image.**

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: pip-${{ runner.os }}-${{ hashFiles('requirements.txt') }}
      - run: pip install -r requirements.txt
      - run: ruff check .
      - run: mypy app/
      - run: pytest --tb=short --cov=app --cov-fail-under=80

  build-push:
    needs: quality
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v5
        with:
          push: true
          cache-from: type=gha
          cache-to: type=gha,mode=max
          tags: |
            ghcr.io/${{ github.repository }}:${{ github.sha }}
            ghcr.io/${{ github.repository }}:latest
```

---

## 12. Observability — Logging, Metrics & Tracing

### Verbal Questions

---

**Q1 🟡💬 Difference between logging, metrics, and distributed tracing.**

**A:**
| Pillar | What it captures | Tool examples |
|---|---|---|
| **Logging** | Discrete events with context (errors, requests) | structlog, Loki, ELK |
| **Metrics** | Aggregated numerical measurements over time (counters, gauges, histograms) | Prometheus, Datadog |
| **Tracing** | Causal chain of a request across services (spans, trace context) | OpenTelemetry, Jaeger, Zipkin |

---

**Q2 🟡💬 Structured logging in Python.**

**A:** Use `structlog` or Python's `logging` with a JSON formatter. Every log line is a JSON object — machine-parseable by Loki/ELK, filterable by field.

```python
import structlog

logger = structlog.get_logger()

# Every log line includes request_id automatically via context variables
logger.info("order.created", order_id=42, user_id=7, amount=99.99)
# {"event": "order.created", "order_id": 42, "user_id": 7, "amount": 99.99, ...}
```

---

**Q3 🟡💬 What is OpenTelemetry? How do you instrument a FastAPI app?**

**A:** OpenTelemetry (OTel) is a vendor-neutral observability framework for traces, metrics, and logs. For FastAPI:

```python
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

provider = TracerProvider()
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
trace.set_tracer_provider(provider)

FastAPIInstrumentor.instrument_app(app)   # auto-instruments all routes
```

Every request gets a `trace_id` propagated via `traceparent` HTTP header across services.

---

**Q4 🟡💬 Exposing Prometheus metrics from FastAPI.**

**A:**
```python
from prometheus_client import Counter, Histogram, make_asgi_app

REQUEST_COUNT   = Counter("http_requests_total", "...", ["method","path","status"])
REQUEST_LATENCY = Histogram("http_request_duration_seconds", "...", ["method","path"])

@app.middleware("http")
async def metrics_middleware(request, call_next):
    import time
    start = time.perf_counter()
    response = await call_next(request)
    REQUEST_COUNT.labels(request.method, request.url.path, response.status_code).inc()
    REQUEST_LATENCY.labels(request.method, request.url.path).observe(time.perf_counter() - start)
    return response

app.mount("/metrics", make_asgi_app())
```

---

**Q5 🟡💬 Key metrics for a Python web service — RED method.**

**A:**
- **R**ate — requests per second (how much traffic).
- **E**rror rate — % of requests returning 5xx/4xx (how many are failing).
- **D**uration — latency histogram (how long requests take): p50, p95, p99.

Additional: DB connection pool saturation, queue depth, memory usage, GC pause time.

---

### Code Questions

---

**Q1 💻 Structured JSON logging with `request_id`, `user_id`, `duration` per request.**

```python
import time, uuid, structlog
from fastapi import FastAPI, Request

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ]
)

log = structlog.get_logger()
app = FastAPI()

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        request_id=request_id,
        method=request.method,
        path=request.url.path,
    )
    start = time.perf_counter()
    response = await call_next(request)
    log.info("request", status=response.status_code,
             duration_ms=round((time.perf_counter() - start) * 1000, 2))
    response.headers["X-Request-ID"] = request_id
    return response
```

---

## 13. Security

### Verbal Questions

---

**Q1 🟡💬 SQL injection — how does an ORM protect you, and when doesn't it?**

**A:** SQLAlchemy uses **parameterised queries** — user input is passed as bound parameters, never interpolated directly into the SQL string. The DB driver handles escaping.

**When ORM doesn't protect:**
- `text()` with string formatting: `text(f"SELECT * FROM users WHERE name = '{name}'")`  — **vulnerable**.
- `execute()` with raw f-strings.
- Always use bound parameters even with `text()`: `text("... WHERE name = :name").bindparams(name=name)`.

---

**Q2 🟡💬 How do you store passwords securely in Python?**

**A:** Use `bcrypt` or `argon2-cffi` (Argon2id is the current OWASP recommendation):

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
```

Never use MD5/SHA1/SHA256 directly — they are too fast for password hashing (brute-forceable).

---

**Q3 🟡💬 OWASP Top 10 — name 5 and mitigations for a Python API.**

**A:**
| # | Vulnerability | Mitigation |
|---|---|---|
| A01 | Broken Access Control | RBAC, `require_role` dependency, test all endpoints |
| A02 | Cryptographic Failures | HTTPS everywhere, `SecretStr`, Argon2 for passwords |
| A03 | Injection (SQL/NoSQL) | ORM parameterised queries, never raw f-strings in SQL |
| A05 | Security Misconfiguration | Disable debug in prod, restrict CORS origins, security headers |
| A07 | Identification & Auth Failures | Short-lived JWTs, refresh tokens, rate-limit login endpoint |
| A09 | Security Logging Failures | Log all auth events, alert on anomalies |

---

**Q4 🟢💬 Authentication vs authorisation.**

**A:**
- **Authentication** ("who are you?") — verifying identity. Mechanisms: JWT, session cookies, API keys, OAuth2.
- **Authorisation** ("what can you do?") — verifying permissions. Mechanisms: RBAC, ABAC, scopes in OAuth2.

In FastAPI: `get_current_user` = authentication; `require_role("admin")` = authorisation.

---

**Q5 🟡💬 How do you prevent secrets from leaking into logs or error messages?**

**A:**
- Use Pydantic's `SecretStr` — `repr()` shows `'**********'`, excluded from `.model_dump()` by default.
- Configure logging to scrub known secret field names (`password`, `token`, `secret`, `key`).
- Use structured logging — never log full request bodies.
- `PYTHONTRACEMALLOC` and Sentry integrations can redact fields by pattern.
- In CI: scan logs with `truffleHog` or `detect-secrets`.

---

**Q6 🟡💬 RBAC in a FastAPI application.**

**A:**

```python
from fastapi import Depends, HTTPException, status

def require_role(*roles: str):
    def dependency(current_user=Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires role: {roles}"
            )
        return current_user
    return dependency

@router.delete("/users/{id}")
async def delete_user(
    id: int,
    _=Depends(require_role("admin", "superuser")),
    db: AsyncSession = Depends(get_db),
):
    ...
```

---

### Code Questions

---

**Q1 💻 Identify the security vulnerability and fix it.**

```python
# VULNERABLE — SQL injection
def get_user(username: str):
    cursor.execute(f"SELECT * FROM users WHERE username = '{username}'")
```

**Vulnerability:** Direct string interpolation allows an attacker to inject SQL. Input `'; DROP TABLE users; --` would execute arbitrary SQL.

```python
# FIXED — parameterised query
def get_user(username: str):
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    # PostgreSQL uses %s: cursor.execute("... WHERE username = %s", (username,))
```

With SQLAlchemy ORM: `select(User).where(User.username == username)` — always parameterised.

---

## 14. Performance & Optimisation

### Verbal Questions

---

**Q1 🟡💬 How do you profile a Python application?**

**A:**
| Tool | Use case |
|---|---|
| `cProfile` | Built-in; deterministic; good for local profiling — measures cumulative time per function |
| `line_profiler` | Line-by-line timing of specific functions (decorate with `@profile`) |
| `py-spy` | Sampling profiler; attaches to a running process without stopping it — safe for production |
| `Pyroscope` | Continuous profiling in production; Grafana integration |
| `memory_profiler` | Track memory usage per line |

---

**Q2 🟡💬 `cProfile` vs `line_profiler` vs `py-spy`.**

**A:**
- **`cProfile`** — traces every function call; overhead ~10-30%; best for development.
- **`line_profiler`** — profiles specific functions line-by-line; must annotate in advance.
- **`py-spy`** — sampling (1-10ms intervals); near-zero overhead; no code changes; works on CPython in production. Run: `py-spy top --pid <PID>`.

---

**Q3 🟡💬 How do you identify and fix a memory leak in a long-running Python service?**

**A:**
1. Monitor RSS memory over time (Prometheus `process_resident_memory_bytes`).
2. Use `tracemalloc` to snapshot and compare memory allocations:
   ```python
   import tracemalloc
   tracemalloc.start()
   # ... run code ...
   snapshot = tracemalloc.take_snapshot()
   top = snapshot.statistics("lineno")[:10]
   ```
3. Check for: global dicts/lists growing unbounded, event listener accumulation, SQLAlchemy session not closed, circular references defeating GC.
4. Use `objgraph` to find what's holding references: `objgraph.show_most_common_types()`.

---

**Q4 🟡💬 NumPy/pandas vectorisation vs Python loops.**

**A:** Python loops call the interpreter overhead for each iteration — O(n) interpreter calls. NumPy/pandas operations are implemented in C and operate on contiguous memory blocks — the inner loop runs in compiled code with SIMD optimisations.

```python
import numpy as np

data = np.random.rand(1_000_000)
# Python loop: ~500ms
result = [x * 2 + 1 for x in data]
# NumPy vectorised: ~2ms — 250× faster
result = data * 2 + 1
```

Use when: processing large arrays, numerical computation, data transformation — anything that maps a function over many elements.

---

**Q5 🟡💬 How does Redis caching reduce database load?**

**A:** Cache frequently read, rarely written data in Redis (in-memory, sub-ms reads). Pattern:

```python
async def get_product(product_id: int, redis, db):
    key = f"product:{product_id}"
    cached = await redis.get(key)
    if cached:
        return json.loads(cached)          # cache hit — no DB query
    product = await db.get(Product, product_id)   # cache miss
    await redis.setex(key, 300, product.model_dump_json())  # cache for 5 min
    return product
```

**Cache invalidation strategies:** TTL (simple), write-through (update cache on write), cache-aside (above pattern), event-driven invalidation.

---

### Code Questions

---

**Q1 💻 Optimise this slow function.**

```python
# ORIGINAL — O(n²) time, O(n) space
def find_duplicates(items: list[str]) -> list[str]:
    duplicates = []
    for i, item in enumerate(items):
        for j, other in enumerate(items):
            if i != j and item == other and item not in duplicates:
                duplicates.append(item)
    return duplicates
```

**Problems:**
1. Nested loop — O(n²).
2. `item not in duplicates` — O(n) list scan inside the loop → O(n³) total.

```python
# OPTIMISED — O(n) time, O(n) space
from collections import Counter

def find_duplicates(items: list[str]) -> list[str]:
    return [item for item, count in Counter(items).items() if count > 1]

# Even simpler with a set:
def find_duplicates_v2(items: list[str]) -> list[str]:
    seen, duplicates = set(), set()
    for item in items:
        if item in seen:
            duplicates.add(item)
        seen.add(item)
    return list(duplicates)
```

---

## 15. Behavioural & Situational

### Questions with Answer Guidance

---

**Q1 💬 Describe a production incident you handled. What was your debugging process?**

**Good answer covers:**
- Immediate action: assess impact, check monitoring dashboards, roll back if safe.
- Methodical investigation: logs → metrics → traces → recent deployments.
- Communication: status updates to stakeholders.
- Resolution and post-incident review: blameless RCA, action items.
- Systemic fix: added the missing alert/test that would have caught it earlier.

---

**Q2 💬 How do you approach reviewing a large pull request?**

**Good answer covers:**
- Ask for smaller PRs as a default process improvement.
- Read the PR description and linked ticket first — understand the *why*.
- Check tests first — they document intent.
- Look for: security issues, performance regressions, missing error handling, breaking API changes.
- Distinguish between blocking concerns vs suggestions.
- Leave constructive, specific comments with suggested fixes.

---

**Q3 💬 How do you handle technical debt in a team that always prioritises features?**

**Good answer covers:**
- Make debt visible — track it in the backlog with estimated impact.
- Frame debt in business terms: "this slows down every new feature by X%".
- Negotiate a sustainable ratio (e.g. 20% of sprint capacity for quality/debt).
- Boy Scout rule: leave code a little better than you found it during feature work.
- Prevent new debt: code reviews, linting, architecture decision records (ADRs).

---

**Q4 💬 Tell me about a time you disagreed with an architectural decision. What did you do?**

**Good answer covers:**
- Raised the concern early with data (benchmarks, failure scenarios, team experience).
- Proposed a concrete alternative with trade-offs clearly stated.
- Accepted the decision if overruled — committed and helped it succeed.
- If it later proved problematic: raised it constructively, not "I told you so".

---

**Q5 💬 How do you keep up with changes in the Python ecosystem?**

**Good answer covers:** PEPs and Python release notes, PyCon talks, Real Python, Python Weekly newsletter, following core contributors on GitHub/Twitter, reading source code of popular libraries, contributing to open source, experimenting with new features in side projects.

---

**Q6 💬 How do you mentor junior developers?**

**Good answer covers:**
- Pair programming over just reviewing PRs.
- Explain the *why*, not just the what.
- Assign progressively challenging tasks with support.
- Encourage questions; never make them feel stupid.
- Regular 1:1s to understand blockers.
- Code reviews as teaching opportunities — ask questions rather than dictating.

---

**Q7 💬 Describe your ideal development workflow from ticket to production.**

**Good answer covers:** Ticket refinement → branch from `main` → TDD → PR with description + tests → code review → CI passes (lint, test, scan) → merge → CD pipeline deploys to staging → smoke test → promote to production via GitOps → monitor metrics/alerts for 30 minutes → done.

---

## Scoring Rubric (Interviewer Guide)

| Score | Description |
|-------|-------------|
| 1 | No understanding; cannot explain the concept |
| 2 | Partial — surface-level answer, major gaps |
| 3 | Solid — understands core concept, can apply it |
| 4 | Strong — deep understanding, trade-offs, real-world examples |
| 5 | Expert — nuanced, teaches interviewer something, connects to adjacent topics |

---

*Questions cover: Core Python · DSA · OOP & Design Patterns · Async/Concurrency · FastAPI · Databases · Testing · System Design · Docker · Kubernetes · CI/CD · Observability · Security · Performance · Behavioural*
