"""
Senior Python Developer Interview Script
=========================================
Covers: Core Python, OOP, Async, APIs (FastAPI), Testing,
        Databases, Docker, Kubernetes, Cloud Deployment, System Design,
        Security, Performance/Observability.

Run:  python3 interview_questions.py
      python3 interview_questions.py --category fastapi_rest
      python3 interview_questions.py --list-categories
      python3 interview_questions.py --random 10
      python3 interview_questions.py --dump --category cicd_cloud
"""

from __future__ import annotations

import argparse
import random
import textwrap
from dataclasses import dataclass
from typing import Optional


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Question:
    category: str
    kind: str          # "verbal" | "code"
    difficulty: str    # "mid" | "senior" | "lead"
    question: str
    hint: Optional[str] = None
    code_snippet: Optional[str] = None
    expected_answer: Optional[str] = None


# ---------------------------------------------------------------------------
# Question bank
# ---------------------------------------------------------------------------

QUESTIONS: list[Question] = [

    # ── 1. CORE PYTHON ──────────────────────────────────────────────────────

    Question(
        category="core_python",
        kind="verbal",
        difficulty="senior",
        question="Explain Python's GIL. When does it hurt performance and how do you work around it?",
        expected_answer=(
            "The Global Interpreter Lock serialises CPython bytecode execution. "
            "CPU-bound code suffers; use multiprocessing or C extensions. "
            "I/O-bound code is fine because the GIL is released during I/O waits. "
            "asyncio and threads still benefit for I/O. Jython/PyPy have no GIL."
        ),
    ),
    Question(
        category="core_python",
        kind="verbal",
        difficulty="senior",
        question="What is the difference between `__new__` and `__init__`? Give a use case for overriding `__new__`.",
        expected_answer=(
            "`__new__` creates and returns the instance; `__init__` initialises it. "
            "Override `__new__` for singletons, immutable subclasses (e.g. subclassing `int` or `str`), "
            "or metaclass-level object creation."
        ),
    ),
    Question(
        category="core_python",
        kind="verbal",
        difficulty="senior",
        question="How do Python descriptors work? Name three built-in uses.",
        expected_answer=(
            "A descriptor defines `__get__`, `__set__`, and/or `__delete__`. "
            "Used by: `property`, `classmethod`, `staticmethod`."
        ),
    ),
    Question(
        category="core_python",
        kind="verbal",
        difficulty="senior",
        question="Explain weak references and when you would use `weakref.WeakValueDictionary`.",
        hint="Think caches that should not prevent garbage collection.",
        expected_answer=(
            "A weak reference does not increment the object's reference count, so the GC can "
            "collect it even while the reference exists. "
            "`weakref.WeakValueDictionary` stores values as weak references — entries are "
            "automatically removed when the referenced object is garbage-collected. "
            "Use case: an in-process cache (e.g. caching ORM instances by PK) where you want "
            "cached objects to be freed when nothing else holds them, rather than pinning them "
            "in memory forever."
        ),
    ),
    Question(
        category="core_python",
        kind="code",
        difficulty="senior",
        question="Implement a thread-safe singleton using a metaclass.",
        code_snippet=textwrap.dedent("""\
            import threading

            class SingletonMeta(type):
                _instances = {}
                _lock = threading.Lock()

                def __call__(cls, *args, **kwargs):
                    with cls._lock:
                        if cls not in cls._instances:
                            instance = super().__call__(*args, **kwargs)
                            cls._instances[cls] = instance
                    return cls._instances[cls]

            class Database(metaclass=SingletonMeta):
                def __init__(self, url: str):
                    self.url = url

            db1 = Database("postgresql://localhost/dev")
            db2 = Database("ignored")
            assert db1 is db2
        """),
        expected_answer=(
            "SingletonMeta.__call__ acquires a class-level lock before checking _instances. "
            "Only the first thread creates the instance; all subsequent callers — including "
            "concurrent ones — return the cached object. "
            "The double-check is not needed here because the lock is held for the entire block, "
            "but the pattern scales to double-checked locking when needed."
        ),
    ),
    Question(
        category="core_python",
        kind="code",
        difficulty="senior",
        question="Write a `retry` decorator with exponential back-off.",
        code_snippet=textwrap.dedent("""\
            import time, functools, random

            def retry(max_attempts=3, base_delay=0.5, exceptions=(Exception,)):
                def decorator(func):
                    @functools.wraps(func)
                    def wrapper(*args, **kwargs):
                        for attempt in range(1, max_attempts + 1):
                            try:
                                return func(*args, **kwargs)
                            except exceptions as exc:
                                if attempt == max_attempts:
                                    raise
                                delay = base_delay * (2 ** (attempt - 1)) + random.uniform(0, 0.1)
                                time.sleep(delay)
                    return wrapper
                return decorator
        """),
        expected_answer=(
            "The decorator wraps the function, retries up to max_attempts times, and re-raises "
            "on the final attempt. `functools.wraps` preserves the original function's metadata. "
            "Exponential back-off (base * 2^attempt) avoids hammering a struggling service. "
            "Specifying `exceptions` prevents catching non-retriable errors like KeyboardInterrupt."
        ),
    ),
    Question(
        category="core_python",
        kind="code",
        difficulty="senior",
        question="Use generators and itertools to yield all pairs (a,b) where a+b is prime.",
        code_snippet=textwrap.dedent("""\
            from itertools import combinations

            def is_prime(n):
                if n < 2: return False
                return all(n % i != 0 for i in range(2, int(n**0.5) + 1))

            def prime_pairs(nums):
                return ((a, b) for a, b in combinations(nums, 2) if is_prime(a + b))

            print(list(prime_pairs([1, 2, 3, 4, 6, 8])))
        """),
        expected_answer=(
            "`combinations(nums, 2)` generates all unique pairs lazily — no list is built. "
            "The generator expression `(a, b) for ... if is_prime(a+b)` is also lazy, so pairs "
            "are produced on demand with O(1) memory. "
            "`is_prime` checks divisibility only up to √n, making it O(√n) per call."
        ),
    ),

    # ── 2. OOP & DESIGN PATTERNS ────────────────────────────────────────────

    Question(
        category="oop_design_patterns",
        kind="verbal",
        difficulty="senior",
        question="Compare composition over inheritance. When would you still prefer inheritance?",
        expected_answer=(
            "Composition ('has-a'): a class holds a reference to another object and delegates to it. "
            "Prefer composition because it is more flexible, avoids the fragile base-class problem, "
            "and makes dependencies explicit and swappable — ideal for testing. "
            "Prefer inheritance when there is a true taxonomic 'is-a' relationship (Dog IS-A Animal), "
            "when polymorphism across a clean type hierarchy is needed, "
            "or when subclassing an immutable built-in (int, str) for type safety. "
            "Rule: keep hierarchies shallow (≤ 2–3 levels); beyond that, composition is safer."
        ),
    ),
    Question(
        category="oop_design_patterns",
        kind="verbal",
        difficulty="senior",
        question="Explain SOLID principles. Give a Python example of the Open/Closed principle.",
        expected_answer=(
            "S — Single Responsibility: one class, one reason to change. "
            "O — Open/Closed: open for extension, closed for modification — new behaviour "
            "via subclasses or composition, never by editing existing code. "
            "L — Liskov Substitution: subclasses must be drop-in replacements for their parent. "
            "I — Interface Segregation: many small specific interfaces over one large one. "
            "D — Dependency Inversion: depend on abstractions (ABCs/Protocols), not concretions. "
            "Open/Closed example: replace `if order_type == 'vip':` branches with a "
            "`DiscountStrategy` ABC — each new discount type is a new subclass, "
            "no existing code is touched."
        ),
    ),
    Question(
        category="oop_design_patterns",
        kind="code",
        difficulty="senior",
        question="Implement the Strategy pattern for a payment processor (Credit Card, PayPal, Crypto).",
        code_snippet=textwrap.dedent("""\
            from abc import ABC, abstractmethod

            class PaymentStrategy(ABC):
                @abstractmethod
                def pay(self, amount: float) -> str: ...

            class CreditCard(PaymentStrategy):
                def pay(self, amount): return f"Charged ${amount:.2f} to credit card."

            class PayPal(PaymentStrategy):
                def pay(self, amount): return f"Sent ${amount:.2f} via PayPal."

            class Crypto(PaymentStrategy):
                def pay(self, amount): return f"Transferred ${amount:.2f} in BTC."

            class Checkout:
                def __init__(self, strategy: PaymentStrategy):
                    self._strategy = strategy
                def complete(self, amount): return self._strategy.pay(amount)

            print(Checkout(CreditCard()).complete(99.99))
        """),
        expected_answer=(
            "The Strategy pattern defines a family of algorithms behind a common interface "
            "(PaymentStrategy ABC). The Checkout class is closed for modification — it calls "
            "`strategy.pay()` regardless of the concrete type. Adding CryptoV2 or BankTransfer "
            "requires only a new subclass, never touching Checkout. "
            "This satisfies Open/Closed and Dependency Inversion."
        ),
    ),
    Question(
        category="oop_design_patterns",
        kind="code",
        difficulty="lead",
        question="Implement a simple event bus (Observer pattern).",
        code_snippet=textwrap.dedent("""\
            from collections import defaultdict
            from typing import Callable

            class EventBus:
                def __init__(self):
                    self._handlers: dict[str, list[Callable]] = defaultdict(list)

                def subscribe(self, event: str, handler: Callable) -> None:
                    self._handlers[event].append(handler)

                def publish(self, event: str, payload=None) -> None:
                    for handler in self._handlers[event]:
                        handler(payload)

            bus = EventBus()
            bus.subscribe("user.created", lambda p: print(f"Welcome {p['email']}"))
            bus.publish("user.created", {"email": "alice@example.com"})
        """),
        expected_answer=(
            "EventBus uses a defaultdict(list) to map event names to handler lists. "
            "`subscribe` appends; `publish` iterates and calls each handler with the payload. "
            "Publishers and subscribers are fully decoupled — the publisher does not import subscribers. "
            "Extend for production: add async dispatch (`await handler(payload)`), "
            "error isolation (try/except per handler), wildcard events, or priority ordering."
        ),
    ),

    # ── 3. ASYNC / CONCURRENCY ───────────────────────────────────────────────

    Question(
        category="async_concurrency",
        kind="verbal",
        difficulty="senior",
        question="What is the difference between `asyncio.gather`, `asyncio.wait`, and `asyncio.TaskGroup`?",
        expected_answer=(
            "`gather` runs coroutines concurrently and returns results in order. "
            "`wait` gives finer control (FIRST_COMPLETED etc.). "
            "`TaskGroup` (3.11+) is structured concurrency — cancels siblings on any failure."
        ),
    ),
    Question(
        category="async_concurrency",
        kind="verbal",
        difficulty="senior",
        question="How do you run a blocking function inside an async FastAPI endpoint without blocking the event loop?",
        expected_answer=(
            "Use `await asyncio.get_event_loop().run_in_executor(None, blocking_fn)` "
            "or `await anyio.to_thread.run_sync(blocking_fn)` (preferred in FastAPI)."
        ),
    ),
    Question(
        category="async_concurrency",
        kind="code",
        difficulty="senior",
        question="Fetch multiple URLs concurrently with aiohttp, return results as they complete.",
        code_snippet=textwrap.dedent("""\
            import asyncio, aiohttp

            async def fetch(session, url):
                async with session.get(url) as resp:
                    return {"url": url, "status": resp.status}

            async def fetch_all(urls):
                async with aiohttp.ClientSession() as session:
                    tasks = [asyncio.create_task(fetch(session, u)) for u in urls]
                    return [await t for t in asyncio.as_completed(tasks)]

            asyncio.run(fetch_all(["https://httpbin.org/get", "https://httpbin.org/status/404"]))
        """),
        expected_answer=(
            "`asyncio.create_task` schedules all fetches concurrently. "
            "`asyncio.as_completed` yields futures in completion order (not submission order), "
            "so the first response back is processed first — important for latency-sensitive pipelines. "
            "The ClientSession is shared across all tasks to reuse the underlying TCP connection pool."
        ),
    ),
    Question(
        category="async_concurrency",
        kind="code",
        difficulty="senior",
        question="Implement an async rate-limiter (max N calls/second) using a semaphore.",
        code_snippet=textwrap.dedent("""\
            import asyncio, time

            class RateLimiter:
                def __init__(self, rate: int):
                    self._sem = asyncio.Semaphore(rate)

                async def __aenter__(self):
                    await self._sem.acquire()
                    asyncio.get_event_loop().call_later(1.0, self._sem.release)

                async def __aexit__(self, *_): ...
        """),
        expected_answer=(
            "A Semaphore(N) allows at most N concurrent holders. "
            "On `__aenter__` we acquire one slot then schedule its release via `call_later(1.0, ...)` "
            "— exactly one second later — freeing the slot for the next caller. "
            "This creates a token-bucket: burst of N is allowed, then rate is capped at N/second "
            "as tokens are returned after 1 s."
        ),
    ),

    # ── 4. FASTAPI — THEORY ─────────────────────────────────────────────────

    Question(
        category="fastapi_rest",
        kind="verbal",
        difficulty="mid",
        question="What is FastAPI and what are its key advantages over Flask and Django REST Framework?",
        expected_answer=(
            "FastAPI is an async-first Python web framework built on Starlette and Pydantic. "
            "Key advantages: automatic OpenAPI/Swagger docs from type hints, native async/await support, "
            "Pydantic validation with clear error messages, dependency injection built-in, "
            "significantly faster than Flask (comparable to NodeJS/Go in benchmarks). "
            "vs Django REST: lighter, no ORM bundled, better async story, faster to scaffold."
        ),
    ),
    Question(
        category="fastapi_rest",
        kind="verbal",
        difficulty="mid",
        question="How does FastAPI generate OpenAPI documentation automatically?",
        expected_answer=(
            "FastAPI inspects Python type annotations and Pydantic models on path functions at startup. "
            "It builds an OpenAPI 3.x schema and serves it at `/openapi.json`. "
            "Swagger UI is served at `/docs`, ReDoc at `/redoc`. "
            "You can enrich docs with `summary`, `description`, `response_description`, `tags`, and `deprecated` params."
        ),
    ),
    Question(
        category="fastapi_rest",
        kind="verbal",
        difficulty="mid",
        question="What is Pydantic and what role does it play in FastAPI?",
        expected_answer=(
            "Pydantic is a data validation library using Python type hints. "
            "In FastAPI: request bodies are declared as Pydantic BaseModel subclasses — FastAPI automatically "
            "parses, validates, and serialises JSON. "
            "Validation errors return HTTP 422 with field-level detail. "
            "Pydantic v2 (used in FastAPI 0.100+) is ~5-50x faster than v1 due to a Rust core."
        ),
    ),
    Question(
        category="fastapi_rest",
        kind="verbal",
        difficulty="mid",
        question="Explain the request lifecycle in FastAPI — from HTTP request to response.",
        expected_answer=(
            "1. Uvicorn/ASGI server receives the HTTP request and calls the ASGI app. "
            "2. Middleware stack processes the request (logging, CORS, auth headers). "
            "3. Router matches the path and method to a path operation function. "
            "4. Dependency injection resolves all `Depends()` in order. "
            "5. Request body is parsed and validated by Pydantic. "
            "6. Path operation function executes (sync runs in threadpool, async runs on event loop). "
            "7. Return value is serialised (via `response_model` if set) and sent as HTTP response. "
            "8. Middleware stack processes the response on the way out."
        ),
    ),
    Question(
        category="fastapi_rest",
        kind="verbal",
        difficulty="mid",
        question="What is the difference between `async def` and `def` route handlers in FastAPI?",
        expected_answer=(
            "`async def`: runs directly on the asyncio event loop — must only call awaitable or non-blocking code. "
            "`def`: FastAPI automatically runs it in a thread pool executor (via `anyio.to_thread`) "
            "so it doesn't block the event loop. "
            "Rule of thumb: use `async def` when calling async libraries (aiohttp, asyncpg, SQLAlchemy async). "
            "Use plain `def` when using blocking libraries (requests, psycopg2) — FastAPI handles the thread offload."
        ),
    ),
    Question(
        category="fastapi_rest",
        kind="verbal",
        difficulty="senior",
        question="How does FastAPI's dependency injection system work? Explain `Depends` and sub-dependencies.",
        expected_answer=(
            "`Depends(callable)` declares a dependency that FastAPI resolves before calling the route. "
            "Dependencies can be functions, classes, or generators. "
            "Sub-dependencies: a dependency can itself declare `Depends` — FastAPI builds a DAG and resolves depth-first. "
            "Caching: within a single request, the same dependency instance is reused (override with `use_cache=False`). "
            "Dependencies declared at router or app level apply to all routes underneath."
        ),
    ),
    Question(
        category="fastapi_rest",
        kind="verbal",
        difficulty="senior",
        question="What is a FastAPI `APIRouter`? How do you structure a large application with multiple routers?",
        expected_answer=(
            "APIRouter is a mini-app for grouping related routes — same API as FastAPI but mounted with a prefix. "
            "Structure: one router per domain (users, products, orders) in separate modules. "
            "Mount with `app.include_router(users_router, prefix='/users', tags=['users'])`. "
            "Routers can have their own dependencies, middleware, and response models."
        ),
    ),
    Question(
        category="fastapi_rest",
        kind="verbal",
        difficulty="senior",
        question="Explain the difference between `response_model`, `response_class`, and `JSONResponse` in FastAPI.",
        expected_answer=(
            "`response_model`: a Pydantic model FastAPI uses to filter/serialise the return value — "
            "strips fields not in the model, triggers OpenAPI schema generation. "
            "`response_class`: the raw ASGI Response subclass (JSONResponse, HTMLResponse, StreamingResponse). "
            "Use `JSONResponse` directly when you need to set custom headers/cookies or return pre-serialised data, "
            "but it bypasses `response_model` filtering."
        ),
    ),
    Question(
        category="fastapi_rest",
        kind="verbal",
        difficulty="senior",
        question="How do you implement JWT authentication in FastAPI with role-based access control (RBAC)?",
        expected_answer=(
            "1. POST /auth/token: verify credentials, sign JWT with `python-jose` or `PyJWT`, return access token. "
            "2. Create a `get_current_user` dependency that reads `Authorization: Bearer <token>`, "
            "decodes and validates JWT, returns user from DB. "
            "3. For RBAC: add a `require_role('admin')` dependency factory that calls `get_current_user` "
            "and checks the role claim — raise HTTP 403 if insufficient. "
            "4. Use OAuth2PasswordBearer as the security scheme for Swagger UI integration."
        ),
    ),
    Question(
        category="fastapi_rest",
        kind="verbal",
        difficulty="senior",
        question="What is middleware in FastAPI/Starlette? How does it differ from a dependency?",
        expected_answer=(
            "Middleware wraps the entire ASGI app — it runs for every request/response regardless of route. "
            "Used for: CORS, request timing, adding headers, logging, rate limiting globally. "
            "Dependency: scoped to specific routes or routers, participates in DI graph, can yield (teardown). "
            "Rule: use middleware for cross-cutting concerns that apply to all routes; "
            "use dependencies for route-specific logic that needs DI or cleanup."
        ),
    ),
    Question(
        category="fastapi_rest",
        kind="verbal",
        difficulty="senior",
        question="How does FastAPI handle HTTP exceptions? What is `HTTPException` vs a custom exception handler?",
        expected_answer=(
            "`raise HTTPException(status_code=404, detail='Not found')` is the standard way — "
            "FastAPI catches it and returns a JSON error response. "
            "Custom exception handler: `@app.exception_handler(MyError)` lets you intercept any exception type "
            "and return a custom `JSONResponse`. "
            "Use `RequestValidationError` handler to customise 422 validation error format."
        ),
    ),
    Question(
        category="fastapi_rest",
        kind="verbal",
        difficulty="senior",
        question="How do you handle background tasks in FastAPI? Compare `BackgroundTasks` vs Celery.",
        expected_answer=(
            "`BackgroundTasks`: built-in, runs after response is sent, in the same process/event loop. "
            "Good for fire-and-forget tasks like sending emails. "
            "Celery: distributed task queue with a separate worker process — "
            "survives app restarts, supports retries, scheduling, priority queues, monitoring. "
            "Use BackgroundTasks for simple lightweight tasks; Celery for long-running, distributed, or retryable work."
        ),
    ),
    Question(
        category="fastapi_rest",
        kind="verbal",
        difficulty="senior",
        question="Explain CORS in FastAPI. What does `CORSMiddleware` do and when is it needed?",
        expected_answer=(
            "CORS (Cross-Origin Resource Sharing) controls which browser origins can call your API. "
            "Needed when your frontend (e.g. React on localhost:3000) calls your API (localhost:8000). "
            "`CORSMiddleware` adds `Access-Control-Allow-Origin` and other headers. "
            "Key params: `allow_origins` (list of allowed origins or ['*']), "
            "`allow_credentials`, `allow_methods`, `allow_headers`. "
            "Never use `allow_origins=['*']` with `allow_credentials=True` — browsers reject it."
        ),
    ),
    Question(
        category="fastapi_rest",
        kind="verbal",
        difficulty="senior",
        question="What are Pydantic validators (`field_validator`, `model_validator`) and when do you use each?",
        expected_answer=(
            "`field_validator`: validates or transforms a single field — use for format checks, "
            "normalisation (e.g. strip whitespace, lowercase email). "
            "`model_validator(mode='after')`: runs after all fields are validated — use for cross-field rules "
            "(e.g. end_date > start_date). "
            "`model_validator(mode='before')`: runs on raw input before field parsing — use to reshape incoming data."
        ),
    ),
    Question(
        category="fastapi_rest",
        kind="verbal",
        difficulty="senior",
        question="How do you version a FastAPI API? Describe two common strategies.",
        expected_answer=(
            "1. URL path versioning: `/api/v1/users`, `/api/v2/users` — "
            "separate APIRouter per version, mount at different prefixes. Simple, explicit. "
            "2. Header versioning: `Accept: application/vnd.myapi.v2+json` — "
            "a single URL, middleware or dependency reads the header and routes to versioned logic. "
            "More RESTful but harder to document in Swagger. "
            "URL versioning is the most common in practice."
        ),
    ),
    Question(
        category="fastapi_rest",
        kind="verbal",
        difficulty="senior",
        question="How do you test FastAPI endpoints? What tools do you use and how do you override dependencies?",
        expected_answer=(
            "Use `httpx.AsyncClient` with `ASGITransport(app=app)` and `pytest-asyncio`. "
            "Override DI: `app.dependency_overrides[get_db] = lambda: fake_db` — "
            "set before test, clean up after. "
            "Use an in-memory SQLite or test Postgres for DB tests. "
            "TestClient (sync) for simpler cases. "
            "Test auth by overriding `get_current_user` to return a fixture user."
        ),
    ),
    Question(
        category="fastapi_rest",
        kind="verbal",
        difficulty="senior",
        question="What is the lifespan event in FastAPI? How does it replace the deprecated `on_event` startup/shutdown?",
        expected_answer=(
            "The `lifespan` context manager (FastAPI 0.93+) wraps startup and shutdown in a single async generator. "
            "Code before `yield` runs at startup, code after `yield` runs at shutdown. "
            "Use it to: open DB connection pools, load ML models, initialise caches, close resources cleanly. "
            "`@app.on_event('startup')` is deprecated in favour of the lifespan pattern."
        ),
        code_snippet=textwrap.dedent("""\
            from contextlib import asynccontextmanager
            from fastapi import FastAPI

            @asynccontextmanager
            async def lifespan(app: FastAPI):
                # startup
                await db_pool.connect()
                yield
                # shutdown
                await db_pool.disconnect()

            app = FastAPI(lifespan=lifespan)
        """),
    ),
    Question(
        category="fastapi_rest",
        kind="verbal",
        difficulty="senior",
        question="How does FastAPI handle file uploads? How do you accept both a file and JSON body in the same endpoint?",
        expected_answer=(
            "Files use `UploadFile` with `File(...)` — sent as multipart/form-data. "
            "You cannot mix JSON body + file upload in the same request (HTTP limitation). "
            "Workaround: send JSON fields as form fields (`Form(...)`) alongside `File(...)`. "
            "For complex nested JSON + file, accept a JSON string as a form field and parse it with `json.loads`."
        ),
    ),
    Question(
        category="fastapi_rest",
        kind="verbal",
        difficulty="senior",
        question="Explain WebSockets in FastAPI. How do you broadcast a message to multiple connected clients?",
        expected_answer=(
            "Declare a route with `async def endpoint(websocket: WebSocket)`, call `await websocket.accept()`. "
            "For broadcasting: maintain a `ConnectionManager` with a list of active WebSocket connections; "
            "iterate and `await ws.send_text(msg)` for each. "
            "For multi-instance deployments: use a pub/sub backend (Redis) — "
            "each instance subscribes to a channel and forwards messages to its local connections."
        ),
    ),
    Question(
        category="fastapi_rest",
        kind="verbal",
        difficulty="senior",
        question="What is Server-Sent Events (SSE) and how do you implement it in FastAPI?",
        expected_answer=(
            "SSE is a one-way HTTP stream from server to browser over a persistent HTTP connection. "
            "Simpler than WebSocket when you only need server→client push (live dashboards, progress bars). "
            "In FastAPI: return a `StreamingResponse` with `media_type='text/event-stream'` "
            "and an async generator that yields `data: <payload>\\n\\n` formatted strings."
        ),
    ),
    Question(
        category="fastapi_rest",
        kind="verbal",
        difficulty="lead",
        question="How would you design a FastAPI service for high availability with 10k+ concurrent users?",
        expected_answer=(
            "Multiple uvicorn workers behind a load balancer (Kubernetes HPA). "
            "Async DB driver (asyncpg/SQLAlchemy async) with connection pool tuned to worker count. "
            "Redis for session/cache — avoid in-process state. "
            "CDN for static assets. Rate limiting via middleware (slowapi). "
            "Circuit breaker for downstream services. Prometheus + Grafana for observability. "
            "Profile with py-spy; identify and offload CPU-bound work to Celery workers."
        ),
    ),
    Question(
        category="fastapi_rest",
        kind="verbal",
        difficulty="lead",
        question="What are the trade-offs between a monolithic FastAPI app and a microservices architecture?",
        expected_answer=(
            "Monolith: simpler deploy, single DB transaction, easier local dev, lower latency. "
            "Microservices: independent scaling per service, polyglot persistence, fault isolation, "
            "but adds network latency, distributed tracing overhead, and complex deployments. "
            "FastAPI suits both: a monolith with APIRouters per domain can be split into microservices later "
            "by extracting routers into separate services with minimal change."
        ),
    ),

    # ── 4b. FASTAPI — CODE TASKS ─────────────────────────────────────────────

    Question(
        category="fastapi_rest",
        kind="code",
        difficulty="mid",
        question="Write a basic FastAPI CRUD for a `Product` resource using Pydantic models.",
        code_snippet=textwrap.dedent("""\
            from fastapi import FastAPI, HTTPException
            from pydantic import BaseModel
            from typing import Optional

            app = FastAPI()

            class ProductIn(BaseModel):
                name: str
                price: float
                stock: int = 0

            class ProductOut(ProductIn):
                id: int

            DB: dict[int, ProductOut] = {}
            _next_id = 1

            @app.post("/products", response_model=ProductOut, status_code=201)
            def create_product(data: ProductIn):
                global _next_id
                product = ProductOut(id=_next_id, **data.model_dump())
                DB[_next_id] = product
                _next_id += 1
                return product

            @app.get("/products/{product_id}", response_model=ProductOut)
            def get_product(product_id: int):
                if product_id not in DB:
                    raise HTTPException(status_code=404, detail="Product not found")
                return DB[product_id]

            @app.put("/products/{product_id}", response_model=ProductOut)
            def update_product(product_id: int, data: ProductIn):
                if product_id not in DB:
                    raise HTTPException(status_code=404, detail="Product not found")
                DB[product_id] = ProductOut(id=product_id, **data.model_dump())
                return DB[product_id]

            @app.delete("/products/{product_id}", status_code=204)
            def delete_product(product_id: int):
                if product_id not in DB:
                    raise HTTPException(status_code=404, detail="Product not found")
                del DB[product_id]
        """),
        expected_answer=(
            "ProductIn defines writable fields; ProductOut extends it with `id` (read-only)"
            "`response_model=ProductOut` makes FastAPI strip extra fields and generate the correct schema"
            "HTTP 404 is raised when a product is not found"
            "`status_code=204` on DELETE means no body"
            "In production replace the in-memory dict with an async SQLAlchemy repository."
        ),
    ),
    Question(
        category="fastapi_rest",
        kind="code",
        difficulty="senior",
        question="Implement a `Depends`-based database session dependency for SQLAlchemy async.",
        code_snippet=textwrap.dedent("""\
            from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
            from fastapi import Depends

            DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/db"

            engine = create_async_engine(DATABASE_URL, pool_size=10, max_overflow=20)
            AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

            async def get_db() -> AsyncSession:
                async with AsyncSessionLocal() as session:
                    try:
                        yield session
                        await session.commit()
                    except Exception:
                        await session.rollback()
                        raise

            # Usage in a route:
            from fastapi import APIRouter
            router = APIRouter()

            @router.get("/items/{id}")
            async def get_item(id: int, db: AsyncSession = Depends(get_db)):
                result = await db.get(Item, id)
                if not result:
                    raise HTTPException(404, "Not found")
                return result
        """),
        expected_answer=(
            "`get_db` is an async generator: it yields a session (used by the route), then commits on success or rolls back on any exception, then the context manager closes the session"
            "Using `yield` makes it a FastAPI 'dependency with cleanup' — teardown runs after the response"
            "`async_sessionmaker` with `expire_on_commit=False` prevents lazy-load errors after commit."
        ),
    ),
    Question(
        category="fastapi_rest",
        kind="code",
        difficulty="senior",
        question="Implement JWT authentication: login endpoint + `get_current_user` dependency.",
        code_snippet=textwrap.dedent("""\
            from datetime import datetime, timedelta
            from fastapi import FastAPI, Depends, HTTPException, status
            from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
            from jose import JWTError, jwt
            from pydantic import BaseModel

            SECRET_KEY = "change-me"
            ALGORITHM = "HS256"
            ACCESS_TOKEN_EXPIRE_MINUTES = 30

            oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
            app = FastAPI()

            class TokenData(BaseModel):
                username: str

            def create_access_token(data: dict) -> str:
                payload = data.copy()
                payload["exp"] = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

            async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
                try:
                    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                    username = payload.get("sub")
                    if username is None:
                        raise ValueError
                    return TokenData(username=username)
                except (JWTError, ValueError):
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                        detail="Invalid credentials",
                                        headers={"WWW-Authenticate": "Bearer"})

            @app.post("/auth/token")
            async def login(form: OAuth2PasswordRequestForm = Depends()):
                # replace with real DB lookup + password hash check
                if form.username != "admin" or form.password != "secret":
                    raise HTTPException(400, "Incorrect username or password")
                token = create_access_token({"sub": form.username})
                return {"access_token": token, "token_type": "bearer"}

            @app.get("/me")
            async def read_me(user: TokenData = Depends(get_current_user)):
                return {"username": user.username}
        """),
        expected_answer=(
            "Login: verify credentials, encode a JWT with an `exp` claim, return as Bearer token"
            "`OAuth2PasswordBearer` extracts the token from the `Authorization: Bearer` header and documents the token URL in Swagger UI"
            "`get_current_user` decodes the JWT, validates the signature and expiry via `jose.jwt.decode`, and raises HTTP 401 on any failure"
            "Routes declare `Depends(get_current_user)` for protection."
        ),
    ),
    Question(
        category="fastapi_rest",
        kind="code",
        difficulty="senior",
        question="Write a FastAPI endpoint that streams a large CSV file to the client without loading it into memory.",
        code_snippet=textwrap.dedent("""\
            from fastapi import FastAPI
            from fastapi.responses import StreamingResponse
            import csv, io

            app = FastAPI()

            def generate_csv(rows: int):
                output = io.StringIO()
                writer = csv.writer(output)
                writer.writerow(["id", "name", "score"])
                for i in range(rows):
                    writer.writerow([i, f"user_{i}", i * 1.5])
                    output.seek(0)
                    yield output.read()
                    output.seek(0)
                    output.truncate(0)

            @app.get("/export")
            def export():
                return StreamingResponse(
                    generate_csv(10_000),
                    media_type="text/csv",
                    headers={"Content-Disposition": "attachment; filename=data.csv"},
                )
        """),
        expected_answer=(
            "`StreamingResponse` accepts a generator — it writes each chunk to the client as it is yielded without buffering the whole file in memory"
            "`io.StringIO` is reused as a single-line buffer: write → seek(0) → read → truncate"
            "The `Content-Disposition` header triggers a file download in browsers."
        ),
    ),
    Question(
        category="fastapi_rest",
        kind="code",
        difficulty="senior",
        question="Implement a reusable pagination dependency and a paginated response model.",
        code_snippet=textwrap.dedent("""\
            from fastapi import FastAPI, Depends, Query
            from pydantic import BaseModel
            from typing import Generic, TypeVar, List

            T = TypeVar("T")

            class Page(BaseModel, Generic[T]):
                items: List[T]
                total: int
                page: int
                size: int

            def paginate(page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100)):
                return {"skip": (page - 1) * size, "limit": size, "page": page, "size": size}

            app = FastAPI()
            ITEMS = list(range(200))

            @app.get("/items", response_model=Page[int])
            def list_items(p=Depends(paginate)):
                chunk = ITEMS[p["skip"]: p["skip"] + p["limit"]]
                return Page(items=chunk, total=len(ITEMS), page=p["page"], size=p["size"])
        """),
        expected_answer=(
            "`paginate` is a pure function dependency — FastAPI resolves it from query params"
            "`Page[T]` is a generic Pydantic model, so `Page[int]`, `Page[UserOut]` etc"
            "all work"
            "`response_model=Page[int]` generates the correct OpenAPI schema with typed `items`"
            "The `skip/limit` pattern maps directly to SQL `OFFSET/LIMIT`."
        ),
    ),
    Question(
        category="fastapi_rest",
        kind="code",
        difficulty="senior",
        question="Add Prometheus metrics middleware to a FastAPI app tracking request count and latency.",
        code_snippet=textwrap.dedent("""\
            from fastapi import FastAPI, Request
            from prometheus_client import Counter, Histogram, make_asgi_app
            import time

            app = FastAPI()

            REQUEST_COUNT = Counter(
                "http_requests_total", "Total HTTP requests", ["method", "path", "status"]
            )
            REQUEST_LATENCY = Histogram(
                "http_request_duration_seconds", "Request latency", ["method", "path"]
            )

            @app.middleware("http")
            async def metrics_middleware(request: Request, call_next):
                start = time.perf_counter()
                response = await call_next(request)
                duration = time.perf_counter() - start
                REQUEST_COUNT.labels(
                    method=request.method, path=request.url.path, status=response.status_code
                ).inc()
                REQUEST_LATENCY.labels(
                    method=request.method, path=request.url.path
                ).observe(duration)
                return response

            app.mount("/metrics", make_asgi_app())
        """),
        expected_answer=(
            "`Counter` increments on every request, labelled by method, path and status code"
            "`Histogram` records duration in seconds; Prometheus scrapes it as a bucketed histogram for p50/p95/p99 calculation"
            "`make_asgi_app()` mounts a standard `/metrics` endpoint compatible with Prometheus scrape config"
            "The middleware wraps `call_next` so timing includes handler execution time."
        ),
    ),
    Question(
        category="fastapi_rest",
        kind="code",
        difficulty="senior",
        question="Write a custom exception handler that returns a consistent error envelope for all HTTPExceptions.",
        code_snippet=textwrap.dedent("""\
            from fastapi import FastAPI, HTTPException, Request
            from fastapi.responses import JSONResponse
            from fastapi.exceptions import RequestValidationError

            app = FastAPI()

            @app.exception_handler(HTTPException)
            async def http_exception_handler(request: Request, exc: HTTPException):
                return JSONResponse(
                    status_code=exc.status_code,
                    content={
                        "error": {
                            "code": exc.status_code,
                            "message": exc.detail,
                            "path": str(request.url),
                        }
                    },
                )

            @app.exception_handler(RequestValidationError)
            async def validation_exception_handler(request: Request, exc: RequestValidationError):
                return JSONResponse(
                    status_code=422,
                    content={
                        "error": {
                            "code": 422,
                            "message": "Validation error",
                            "detail": exc.errors(),
                            "path": str(request.url),
                        }
                    },
                )
        """),
        expected_answer=(
            "Registering `@app.exception_handler(HTTPException)` overrides FastAPI's default JSON error"
            "The envelope `{error: {code, message, path}}` gives clients a predictable structure"
            "A separate handler for `RequestValidationError` reformats 422 errors with field-level detail"
            "Both handlers return `JSONResponse` so status code, headers and body are fully controlled."
        ),
    ),
    Question(
        category="fastapi_rest",
        kind="code",
        difficulty="senior",
        question="Implement a WebSocket connection manager that broadcasts messages to all connected clients.",
        code_snippet=textwrap.dedent("""\
            from fastapi import FastAPI, WebSocket, WebSocketDisconnect

            app = FastAPI()

            class ConnectionManager:
                def __init__(self):
                    self.active: list[WebSocket] = []

                async def connect(self, ws: WebSocket):
                    await ws.accept()
                    self.active.append(ws)

                def disconnect(self, ws: WebSocket):
                    self.active.remove(ws)

                async def broadcast(self, message: str):
                    for ws in self.active:
                        await ws.send_text(message)

            manager = ConnectionManager()

            @app.websocket("/ws")
            async def websocket_endpoint(ws: WebSocket):
                await manager.connect(ws)
                try:
                    while True:
                        data = await ws.receive_text()
                        await manager.broadcast(f"Client says: {data}")
                except WebSocketDisconnect:
                    manager.disconnect(ws)
                    await manager.broadcast("A client disconnected")
        """),
        expected_answer=(
            "`ConnectionManager` holds a list of active WebSocket objects"
            "`connect` calls `ws.accept()` before appending — the handshake must complete first"
            "`broadcast` iterates and sends to every active connection; `disconnect` removes on close"
            "For multi-instance deployments, replace the in-process list with a Redis pub/sub channel so instances share the subscriber set."
        ),
    ),
    Question(
        category="fastapi_rest",
        kind="code",
        difficulty="senior",
        question="Write a FastAPI middleware that adds a unique `X-Request-ID` header to every request and response.",
        code_snippet=textwrap.dedent("""\
            import uuid
            from fastapi import FastAPI, Request

            app = FastAPI()

            @app.middleware("http")
            async def request_id_middleware(request: Request, call_next):
                request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
                response = await call_next(request)
                response.headers["X-Request-ID"] = request_id
                return response
        """),
        expected_answer=(
            "The middleware reads an existing `X-Request-ID` from the incoming request (useful when a load balancer injects one) or generates a fresh UUID4"
            "It attaches the same ID to the response header so clients can correlate logs"
            "Pair this with `structlog.contextvars.bind_contextvars(request_id=...)` so all log lines within that request automatically include the ID."
        ),
    ),
    Question(
        category="fastapi_rest",
        kind="code",
        difficulty="senior",
        question="Write a role-based access control dependency that restricts an endpoint to admin users only.",
        code_snippet=textwrap.dedent("""\
            from fastapi import Depends, HTTPException, status
            from typing import Callable

            # Assume get_current_user returns a User with a .role attribute
            def require_role(*roles: str) -> Callable:
                def dependency(user=Depends(get_current_user)):
                    if user.role not in roles:
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Required role: {roles}. Your role: {user.role}"
                        )
                    return user
                return dependency

            # Usage:
            @router.delete("/users/{id}")
            async def delete_user(
                id: int,
                admin=Depends(require_role("admin", "superuser")),
                db: AsyncSession = Depends(get_db),
            ):
                ...
        """),
        expected_answer=(
            "`require_role` is a dependency factory — it returns a new dependency closure each time"
            "The inner dependency calls `get_current_user` (auth) then checks the role (authz)"
            "HTTP 403 Forbidden (not 401) is correct: the user is authenticated but not authorised"
            "Multiple roles can be passed: `require_role('admin', 'superuser')` — use a set/tuple check."
        ),
    ),
    Question(
        category="fastapi_rest",
        kind="code",
        difficulty="senior",
        question="Implement rate limiting on a FastAPI endpoint using `slowapi`.",
        code_snippet=textwrap.dedent("""\
            from fastapi import FastAPI, Request
            from slowapi import Limiter, _rate_limit_exceeded_handler
            from slowapi.util import get_remote_address
            from slowapi.errors import RateLimitExceeded

            limiter = Limiter(key_func=get_remote_address)
            app = FastAPI()
            app.state.limiter = limiter
            app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

            @app.get("/items")
            @limiter.limit("10/minute")
            async def list_items(request: Request):
                return {"items": []}
        """),
        expected_answer=(
            "`slowapi` is a port of Flask-Limiter for Starlette/FastAPI"
            "`Limiter(key_func=get_remote_address)` buckets requests by client IP"
            "`@limiter.limit('10/minute')` is the per-endpoint limit string"
            "`app.state.limiter` registers it with the app; the exception handler converts `RateLimitExceeded` into an HTTP 429 response with a `Retry-After` header."
        ),
    ),
    Question(
        category="fastapi_rest",
        kind="code",
        difficulty="senior",
        question="Write pytest tests for a FastAPI endpoint using `httpx.AsyncClient` and dependency overrides.",
        code_snippet=textwrap.dedent("""\
            import pytest
            import pytest_asyncio
            from httpx import AsyncClient, ASGITransport
            from app.main import app
            from app.dependencies import get_current_user
            from app.schemas import User

            fake_user = User(id=1, username="testuser", role="user")

            @pytest_asyncio.fixture
            async def client():
                app.dependency_overrides[get_current_user] = lambda: fake_user
                async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                    yield ac
                app.dependency_overrides.clear()

            @pytest.mark.asyncio
            async def test_get_me(client):
                response = await client.get("/me")
                assert response.status_code == 200
                assert response.json()["username"] == "testuser"

            @pytest.mark.asyncio
            async def test_create_product(client):
                payload = {"name": "Widget", "price": 9.99, "stock": 100}
                response = await client.post("/products", json=payload)
                assert response.status_code == 201
                assert response.json()["name"] == "Widget"
        """),
        expected_answer=(
            "`ASGITransport(app=app)` drives the ASGI app in-process — no real HTTP server needed"
            "`dependency_overrides[get_current_user] = lambda: fake_user` replaces the real auth dependency with a fixture user for the duration of the test"
            "`app.dependency_overrides.clear()` in teardown prevents state leaking between tests"
            "`@pytest.mark.asyncio` (or `asyncio_mode = auto`) is required for async test functions."
        ),
    ),

    # ── 5. DATABASES & ORM ──────────────────────────────────────────────────

    Question(
        category="databases_orm",
        kind="verbal",
        difficulty="senior",
        question="Explain N+1 query problem and how SQLAlchemy's `selectinload` / `joinedload` solve it.",
        expected_answer=(
            "N+1: loading N rows then issuing 1 extra query per row to fetch a relationship = N+1 queries"
            "`selectinload` issues ONE extra `SELECT … WHERE id IN (…)` query to load all related rows at once"
            "Best for one-to-many (user → orders)"
            "`joinedload` uses a SQL JOIN in the original query, loading parent+children in one round-trip"
            "Best for many-to-one / one-to-one (order → user)"
            "Use `contains_eager` when you write the JOIN yourself and want SQLAlchemy to populate the relationship."
        ),
    ),
    Question(
        category="databases_orm",
        kind="verbal",
        difficulty="senior",
        question="When would you use a database index, and what are the downsides of over-indexing?",
        expected_answer=(
            "Add an index when a column appears in WHERE, JOIN ON, or ORDER BY clauses on large tables"
            "Types: B-tree (default, equality/range), Hash (equality only), GIN (JSONB/arrays), GiST (geometry/full-text)"
            "Downsides of over-indexing: each index slows INSERT/UPDATE/DELETE (the index must also be updated); indexes consume disk space; the query planner may choose a sub-optimal index; maintenance overhead increases (VACUUM, REINDEX)"
            "Rule: index based on real query patterns from EXPLAIN ANALYZE, not speculatively."
        ),
    ),
    Question(
        category="databases_orm",
        kind="verbal",
        difficulty="senior",
        question="Describe optimistic vs pessimistic locking. Which does SQLAlchemy use by default?",
        expected_answer=(
            "Optimistic locking: no DB lock held at read time"
            "A `version` column is checked at UPDATE — if it changed since your read, raise a StaleDataError and retry"
            "Good for low-contention reads with rare conflicts"
            "Pessimistic locking: `SELECT … FOR UPDATE` locks the row at read time, blocking concurrent writers until the transaction commits"
            "Good for financial transactions with high contention"
            "SQLAlchemy uses optimistic locking via `version_id_col` on mapped classes"
            "Pessimistic: add `.with_for_update()` to a select statement."
        ),
    ),
    Question(
        category="databases_orm",
        kind="code",
        difficulty="senior",
        question="Write an async SQLAlchemy 2.0 repository with get/list/create/update/delete.",
        code_snippet=textwrap.dedent("""\
            from sqlalchemy.ext.asyncio import AsyncSession
            from sqlalchemy import select

            class ProductRepository:
                def __init__(self, session: AsyncSession):
                    self.session = session

                async def get(self, id: int):
                    return await self.session.get(Product, id)

                async def list(self, skip=0, limit=20):
                    result = await self.session.execute(select(Product).offset(skip).limit(limit))
                    return list(result.scalars())

                async def create(self, data: dict):
                    obj = Product(**data)
                    self.session.add(obj)
                    await self.session.flush()
                    return obj

                async def update(self, id: int, data: dict):
                    obj = await self.get(id)
                    if obj:
                        for k, v in data.items():
                            setattr(obj, k, v)
                        await self.session.flush()
                    return obj

                async def delete(self, id: int) -> bool:
                    obj = await self.get(id)
                    if obj:
                        await self.session.delete(obj)
                        await self.session.flush()
                        return True
                    return False
        """),
        expected_answer=(
            "The repository pattern wraps all DB access behind a clean interface, decoupling the service layer from SQLAlchemy"
            "Each method uses `session.get` (PK lookup), `session.execute(select(...))`, `session.add` + `flush` (write without commit), and `session.delete` + `flush`"
            "`flush` sends SQL to the DB within the transaction without committing — the caller commits at a higher level (e.g"
            "the `get_db` dependency commits on success)."
        ),
    ),

    # ── 6. TESTING ──────────────────────────────────────────────────────────

    Question(
        category="testing",
        kind="verbal",
        difficulty="senior",
        question="What is the difference between a mock, a stub, a fake, and a spy?",
        expected_answer=(
            "Stub: returns canned data. Mock: records calls + has assertions. "
            "Fake: real working implementation (e.g. in-memory DB). Spy: wraps real object and records interactions."
        ),
    ),
    Question(
        category="testing",
        kind="verbal",
        difficulty="senior",
        question="How do you test async FastAPI endpoints? Describe the tools and setup.",
        expected_answer=(
            "Use `httpx.AsyncClient` with `ASGITransport` and `pytest-asyncio`. "
            "Override FastAPI dependencies with `app.dependency_overrides`. "
            "Use an in-memory SQLite or `pytest-postgresql` for DB tests."
        ),
    ),
    Question(
        category="testing",
        kind="code",
        difficulty="senior",
        question="Write a pytest fixture that creates a test DB, applies migrations, and tears down after session.",
        code_snippet=textwrap.dedent("""\
            import pytest_asyncio
            from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
            from sqlalchemy.orm import sessionmaker
            from app.db.base import Base

            TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

            @pytest_asyncio.fixture(scope="session")
            async def engine():
                eng = create_async_engine(TEST_DB_URL)
                async with eng.begin() as conn:
                    await conn.run_sync(Base.metadata.create_all)
                yield eng
                async with eng.begin() as conn:
                    await conn.run_sync(Base.metadata.drop_all)
                await eng.dispose()

            @pytest_asyncio.fixture
            async def session(engine):
                factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
                async with factory() as sess:
                    yield sess
                    await sess.rollback()
        """),
        expected_answer=(
            "A session-scoped `engine` fixture creates the in-memory SQLite DB once for the entire test run, applying all table definitions via `Base.metadata.create_all`"
            "A function-scoped `session` fixture gives each test a fresh transaction that is rolled back after the test, leaving the schema intact for the next test"
            "Using `aiosqlite` driver enables async SQLAlchemy with SQLite for lightweight CI tests."
        ),
    ),
    Question(
        category="testing",
        kind="code",
        difficulty="senior",
        question="Write parametrised pytest tests for a `fizzbuzz(n)` function covering edge cases.",
        code_snippet=textwrap.dedent("""\
            import pytest

            def fizzbuzz(n: int) -> str:
                if n % 15 == 0: return "FizzBuzz"
                if n % 3 == 0: return "Fizz"
                if n % 5 == 0: return "Buzz"
                return str(n)

            @pytest.mark.parametrize("n,expected", [
                (1, "1"), (3, "Fizz"), (5, "Buzz"),
                (15, "FizzBuzz"), (30, "FizzBuzz"), (0, "FizzBuzz"),
            ])
            def test_fizzbuzz(n, expected):
                assert fizzbuzz(n) == expected
        """),
        expected_answer=(
            "`@pytest.mark.parametrize` runs the same test body with multiple inputs, reducing boilerplate"
            "Edge cases covered: 1 (plain int), 3 (Fizz), 5 (Buzz), 15 (FizzBuzz), 30 (FizzBuzz, multiple), 0 (divisible by 15 — FizzBuzz, often missed)"
            "The `% 15 == 0` check must come before `% 3` and `% 5` to avoid shadowing."
        ),
    ),

    # ── 7. DOCKER ───────────────────────────────────────────────────────────

    Question(
        category="docker",
        kind="verbal",
        difficulty="senior",
        question="Explain Docker layer caching. How do you structure a Python Dockerfile to maximise cache hits?",
        expected_answer=(
            "Copy requirements files first, install dependencies, THEN copy source code. "
            "Code changes don't invalidate the dependency layer."
        ),
    ),
    Question(
        category="docker",
        kind="verbal",
        difficulty="senior",
        question="What is a multi-stage Docker build and why is it useful for Python?",
        expected_answer=(
            "Builder stage compiles/installs; final stage copies only the venv/wheel into a slim image. "
            "Reduces image size; keeps build tools out of production."
        ),
    ),
    Question(
        category="docker",
        kind="code",
        difficulty="senior",
        question="Write a production-ready multi-stage Dockerfile for a FastAPI app.",
        code_snippet=textwrap.dedent("""\
            FROM python:3.12-slim AS builder
            WORKDIR /app
            RUN pip install --upgrade pip
            COPY requirements.txt .
            RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

            FROM python:3.12-slim AS runtime
            WORKDIR /app
            COPY --from=builder /install /usr/local
            COPY app/ ./app/
            ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
            EXPOSE 8000
            CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
        """),
        expected_answer=(
            "Stage 1 (builder): install dependencies into `/install` prefix"
            "Stage 2 (runtime): copy only the installed packages from builder — no pip, no build tools"
            "`python:3.12-slim` reduces the final image to ~150 MB vs ~1 GB for the full image"
            "`--no-cache-dir` prevents pip from storing the download cache in the layer"
            "`PYTHONDONTWRITEBYTECODE=1` and `PYTHONUNBUFFERED=1` are best practice for containers."
        ),
    ),

    # ── 8. KUBERNETES ───────────────────────────────────────────────────────

    Question(
        category="kubernetes",
        kind="verbal",
        difficulty="senior",
        question="What is the difference between a Deployment, StatefulSet, and DaemonSet?",
        expected_answer=(
            "Deployment: stateless replicas, rolling update. "
            "StatefulSet: ordered, stable identity + persistent volumes (DBs, Kafka). "
            "DaemonSet: one pod per node (log collectors, monitoring agents)."
        ),
    ),
    Question(
        category="kubernetes",
        kind="verbal",
        difficulty="senior",
        question="Explain liveness vs readiness vs startup probes. What happens when each fails?",
        expected_answer=(
            "Liveness failure → pod restarted. "
            "Readiness failure → pod removed from Service endpoints. "
            "Startup probe → gives slow-starting containers time before liveness kicks in."
        ),
    ),
    Question(
        category="kubernetes",
        kind="verbal",
        difficulty="senior",
        question="How does Kubernetes HPA work, and what custom metrics can you use?",
        expected_answer=(
            "HPA (HorizontalPodAutoscaler) watches a metrics source and adjusts `replicas` on a Deployment"
            "Default metrics: CPU and memory utilisation (from metrics-server)"
            "Custom metrics: install `prometheus-adapter` to expose any Prometheus metric (e.g"
            "`http_requests_per_second`, queue depth) as a Kubernetes custom/external metric"
            "The HPA then scales on `type: Object` or `type: External` metric targets"
            "Scale-down is intentionally slow (stabilisation window, default 5 min) to avoid flapping."
        ),
    ),
    Question(
        category="kubernetes",
        kind="verbal",
        difficulty="senior",
        question="What is a ConfigMap vs Secret, and how do you avoid storing secrets in Git?",
        hint="Mention external-secrets-operator, Vault, or sealed-secrets.",
        expected_answer=(
            "ConfigMap: non-sensitive key-value config (feature flags, log levels) mounted as env vars or files"
            "Secret: base64-encoded sensitive data (passwords, tokens) — same mounting options but treated with additional controls (RBAC, encryption at rest in etcd)"
            "Never commit secrets to Git"
            "Alternatives: 1"
            "`external-secrets-operator` — syncs secrets from AWS Secrets Manager / GCP Secret Manager / Vault"
            "2"
            "Sealed Secrets — encrypts secrets in Git with a cluster-specific key"
            "3"
            "HashiCorp Vault + vault-agent sidecar — injects secrets directly into the pod at runtime."
        ),
    ),
    Question(
        category="kubernetes",
        kind="code",
        difficulty="senior",
        question="Write a Kubernetes Deployment + Service YAML for a FastAPI app with resource limits and probes.",
        code_snippet=textwrap.dedent("""\
            apiVersion: apps/v1
            kind: Deployment
            metadata:
              name: fastapi-app
            spec:
              replicas: 3
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
                    image: myregistry/fastapi-app:latest
                    ports:
                    - containerPort: 8000
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
                    livenessProbe:
                      httpGet:
                        path: /health
                        port: 8000
                      initialDelaySeconds: 15
                      periodSeconds: 20
            ---
            apiVersion: v1
            kind: Service
            metadata:
              name: fastapi-svc
            spec:
              selector:
                app: fastapi-app
              ports:
              - port: 80
                targetPort: 8000
              type: ClusterIP
        """),
        expected_answer=(
            "Readiness probe on `/health`: pod removed from Service endpoints while it is not ready (e.g"
            "warming up, DB migration)"
            "Liveness probe on `/health`: pod restarted when it is stuck (deadlock, OOM)"
            "`initialDelaySeconds` gives the app time to start before probes fire"
            "Resource `requests` are used by the scheduler for placement; `limits` cap actual consumption"
            "ClusterIP Service provides a stable DNS name and load-balances within the cluster."
        ),
    ),
    Question(
        category="kubernetes",
        kind="verbal",
        difficulty="senior",
        question="Walk me through a zero-downtime rolling deployment strategy in Kubernetes.",
        expected_answer=(
            "Set `strategy.type: RollingUpdate` with `maxSurge` and `maxUnavailable`. "
            "New pods must pass readiness probes before old ones are terminated. "
            "Use `minReadySeconds` and `progressDeadlineSeconds` for safety."
        ),
    ),

    # ── 9. CI/CD & CLOUD ────────────────────────────────────────────────────

    Question(
        category="cicd_cloud",
        kind="verbal",
        difficulty="senior",
        question="What is the difference between Continuous Integration, Continuous Delivery, and Continuous Deployment?",
        expected_answer=(
            "CI: automatically build and test on every commit. "
            "Continuous Delivery: every passing build is releasable with one manual click. "
            "Continuous Deployment: every passing build auto-deploys to production."
        ),
    ),
    Question(
        category="cicd_cloud",
        kind="verbal",
        difficulty="senior",
        question="Describe a complete CI/CD pipeline for a Python microservice from commit to production on Kubernetes.",
        expected_answer=(
            "1. Lint + test on PR. 2. Build Docker image, tag with git SHA. "
            "3. Push to registry. 4. Update Helm chart / Kustomize overlay. "
            "5. GitOps tool (ArgoCD / Flux) syncs to cluster. "
            "6. Readiness probes gate the rollout."
        ),
    ),
    Question(
        category="cicd_cloud",
        kind="verbal",
        difficulty="senior",
        question="What is GitOps? Compare ArgoCD and Flux.",
        expected_answer=(
            "GitOps: Git is the single source of truth for cluster state. "
            "ArgoCD: pull-based, web UI, multi-cluster, app-of-apps pattern. "
            "Flux: Kubernetes-native CRDs, tighter GitHub integration, OCI registry sources."
        ),
    ),
    Question(
        category="cicd_cloud",
        kind="verbal",
        difficulty="senior",
        question="How would you manage environment-specific configuration (dev/staging/prod) in Kubernetes?",
        hint="Kustomize overlays, Helm values files, or environment-specific namespaces.",
        expected_answer=(
            "Kustomize: a `base/` directory holds common manifests; per-environment `overlays/` patch replicas, image tags, resource limits, and env vars — no templating language needed"
            "Helm: a single chart + `values-dev.yaml`, `values-staging.yaml`, `values-prod.yaml`"
            "Namespace per environment (`dev`, `staging`, `prod`) within one cluster for simplicity; separate clusters for stronger prod isolation"
            "Secrets: never in Git — use `external-secrets-operator` or Vault per environment."
        ),
    ),
    Question(
        category="cicd_cloud",
        kind="code",
        difficulty="senior",
        question="Write a GitHub Actions workflow: lint, test, build Docker image, push to registry.",
        code_snippet=textwrap.dedent("""\
            name: CI
            on:
              push:
                branches: [main]
              pull_request:

            jobs:
              test:
                runs-on: ubuntu-latest
                steps:
                  - uses: actions/checkout@v4
                  - uses: actions/setup-python@v5
                    with:
                      python-version: "3.12"
                  - run: pip install -r requirements.txt
                  - run: ruff check .
                  - run: pytest --tb=short

              build-push:
                needs: test
                runs-on: ubuntu-latest
                if: github.ref == 'refs/heads/main'
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
                      tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
        """),
        expected_answer=(
            "The `test` job runs on every push and PR: checkout → setup Python → install deps → lint → pytest"
            "The `build-push` job depends on `test` and only runs on `main` (not PRs)"
            "`docker/build-push-action` builds a multi-platform image; `ghcr.io` is the GitHub Container Registry"
            "The image is tagged with `github.sha` (immutable, traceable) rather than `latest` (mutable)."
        ),
    ),
    Question(
        category="cicd_cloud",
        kind="verbal",
        difficulty="senior",
        question="How do you cache pip/Poetry dependencies in GitHub Actions?",
        expected_answer=(
            "Use `actions/cache` keyed on hash of `requirements.txt` or `poetry.lock`. "
            "Restore-keys allow partial cache hits on lock file changes."
        ),
        code_snippet=textwrap.dedent("""\
            - uses: actions/cache@v4
              with:
                path: ~/.cache/pip
                key: pip-${{ runner.os }}-${{ hashFiles('requirements.txt') }}
                restore-keys: pip-${{ runner.os }}-
        """),
    ),
    Question(
        category="cicd_cloud",
        kind="verbal",
        difficulty="senior",
        question="Explain GitHub Actions reusable workflows vs composite actions. When do you choose each?",
        expected_answer=(
            "Reusable workflow: full `.yml` called with `uses:` — its own job context, supports secrets. "
            "Composite action: steps bundled as a single action, runs inside caller's job — lighter, "
            "good for shared setup steps."
        ),
    ),
    Question(
        category="cicd_cloud",
        kind="verbal",
        difficulty="senior",
        question="How do you handle secrets in GitHub Actions? What are the risks of printing env vars in logs?",
        expected_answer=(
            "Store in GitHub Secrets; reference as `${{ secrets.MY_SECRET }}`. "
            "GitHub masks known values but concatenated/encoded values may leak. "
            "Prefer OIDC federation (no stored credentials) with AWS/GCP/Azure."
        ),
    ),
    Question(
        category="cicd_cloud",
        kind="code",
        difficulty="senior",
        question="Write a GitHub Actions workflow using OIDC to authenticate to AWS and push to ECR.",
        code_snippet=textwrap.dedent("""\
            name: Deploy to ECR
            on:
              push:
                branches: [main]

            permissions:
              id-token: write
              contents: read

            jobs:
              deploy:
                runs-on: ubuntu-latest
                steps:
                  - uses: actions/checkout@v4
                  - uses: aws-actions/configure-aws-credentials@v4
                    with:
                      role-to-assume: arn:aws:iam::123456789012:role/github-actions-role
                      aws-region: us-east-1
                  - uses: aws-actions/amazon-ecr-login@v2
                  - uses: docker/build-push-action@v5
                    with:
                      push: true
                      tags: 123456789012.dkr.ecr.us-east-1.amazonaws.com/myapp:${{ github.sha }}
        """),
        expected_answer=(
            "OIDC (OpenID Connect) lets GitHub Actions federate identity with AWS without storing long-lived access keys in GitHub Secrets"
            "`permissions: id-token: write` enables the OIDC token request"
            "`configure-aws-credentials` exchanges the token for temporary STS credentials for the given role"
            "The IAM role's trust policy must allow `token.actions.githubusercontent.com` as the OIDC provider with conditions matching the repo and branch."
        ),
    ),
    Question(
        category="cicd_cloud",
        kind="verbal",
        difficulty="senior",
        question="Compare trunk-based development with Gitflow. Which suits CI/CD better and why?",
        expected_answer=(
            "Trunk-based: all devs commit to `main` (or short-lived branches < 2 days) — enables true CI. "
            "Gitflow: longer-lived branches conflict with CI goals. "
            "Trunk-based + feature flags is the preferred model for high-velocity teams."
        ),
    ),
    Question(
        category="cicd_cloud",
        kind="verbal",
        difficulty="senior",
        question="What is a feature flag (feature toggle) and how does it complement CI/CD?",
        expected_answer=(
            "Decouples deployment from release. Code ships disabled; flag is flipped per user/cohort. "
            "Enables trunk-based development and instant rollback without a redeploy."
        ),
    ),
    Question(
        category="cicd_cloud",
        kind="verbal",
        difficulty="senior",
        question="What is a canary deployment? How would you implement it in Kubernetes?",
        expected_answer=(
            "Route a small % of traffic to the new version. "
            "In k8s: second Deployment with fewer replicas on same Service selector. "
            "With Istio: VirtualService weight-based routing. Argo Rollouts: dedicated CRD."
        ),
    ),
    Question(
        category="cicd_cloud",
        kind="verbal",
        difficulty="senior",
        question="Explain blue/green deployment vs rolling update — advantages and cost trade-offs.",
        expected_answer=(
            "Blue/green: atomic traffic switch, instant rollback, 2× infra cost. "
            "Rolling: uses only surge capacity, mixed-version traffic briefly."
        ),
    ),
    Question(
        category="cicd_cloud",
        kind="verbal",
        difficulty="senior",
        question="What is the test pyramid? How does it guide automation at each pipeline stage?",
        expected_answer=(
            "Base: many fast unit tests (every commit). "
            "Middle: fewer integration tests (PR merge). "
            "Top: few slow E2E tests (post-deploy staging). "
            "Inverted pyramid → slow, flaky pipelines."
        ),
    ),
    Question(
        category="cicd_cloud",
        kind="verbal",
        difficulty="senior",
        question="How do you run database migrations safely in a CI/CD pipeline with zero downtime?",
        expected_answer=(
            "Expand/contract pattern: add column nullable → backfill → make NOT NULL. "
            "Never rename/drop in the same release as the code change. "
            "Run `alembic upgrade head` as a Kubernetes init container."
        ),
    ),
    Question(
        category="cicd_cloud",
        kind="verbal",
        difficulty="senior",
        question="What is shift-left security? Name concrete tools for a Python CI pipeline.",
        expected_answer=(
            "Move security checks into CI. "
            "Tools: Bandit (SAST), pip-audit (CVEs), Trivy (container), "
            "Checkov (IaC), Semgrep (custom rules), OWASP ZAP (DAST in staging)."
        ),
    ),
    Question(
        category="cicd_cloud",
        kind="verbal",
        difficulty="senior",
        question="How do you version Docker images in CI/CD? What are the problems with using `latest`?",
        expected_answer=(
            "Tag with git commit SHA (immutable + traceable). "
            "`latest` is mutable — different images at different times, rollbacks ambiguous."
        ),
    ),
    Question(
        category="cicd_cloud",
        kind="verbal",
        difficulty="senior",
        question="What is SemVer? How do you automate version bumping in a Python project?",
        expected_answer=(
            "MAJOR.MINOR.PATCH. Tools: commitizen (Conventional Commits), "
            "python-semantic-release (auto-tag + changelog), bump2version."
        ),
    ),
    Question(
        category="cicd_cloud",
        kind="verbal",
        difficulty="senior",
        question="How do you detect a bad deployment automatically and trigger rollback?",
        expected_answer=(
            "Prometheus/Datadog alerts on error rate / latency. "
            "Argo Rollouts AnalysisTemplate aborts rollout if SLO breached. "
            "`kubectl rollout undo deployment/myapp` for manual rollback."
        ),
    ),
    Question(
        category="cicd_cloud",
        kind="verbal",
        difficulty="lead",
        question="Your team ships 20 times a day. A bad deploy causes a P1 incident. Walk through response and process changes.",
        expected_answer=(
            "Immediate: rollback / flip feature flag. "
            "Response: page on-call, incident channel, incident commander. "
            "Post-incident: blameless RCA, add missing test, improve staging parity, "
            "add SLO quality gate, consider progressive delivery."
        ),
    ),
    # Theory
    Question(
        category="cicd_cloud",
        kind="verbal",
        difficulty="mid",
        question="What are the four key stages of a typical CI/CD pipeline?",
        expected_answer=(
            "1. Source — commit triggers pipeline. 2. Build — package app. "
            "3. Test — unit/integration/security. 4. Deploy — push to environment. "
            "(5. Monitor — observe post-release.)"
        ),
    ),
    Question(
        category="cicd_cloud",
        kind="verbal",
        difficulty="mid",
        question="What is a build artifact? Give examples for a Python project.",
        expected_answer=(
            "Immutable output of a build step. Python examples: Docker image, .whl, Lambda zip, PyInstaller binary. "
            "Must be versioned and stored (GHCR, ECR, PyPI, S3)."
        ),
    ),
    Question(
        category="cicd_cloud",
        kind="verbal",
        difficulty="mid",
        question="What does 'pipeline as code' mean and why is it important?",
        expected_answer=(
            "Pipeline definition lives in version control (`.github/workflows/`, `Jenkinsfile`). "
            "Pipelines are reviewable, auditable, versioned, and reproducible."
        ),
    ),
    Question(
        category="cicd_cloud",
        kind="verbal",
        difficulty="mid",
        question="What is idempotency in CI/CD deployments and why does it matter?",
        expected_answer=(
            "A deployment re-run always produces the same result. "
            "`kubectl apply` is idempotent; `kubectl create` is not. `helm upgrade --atomic` is idempotent."
        ),
    ),
    Question(
        category="cicd_cloud",
        kind="verbal",
        difficulty="mid",
        question="What is immutable infrastructure and how does it change deploy/rollback?",
        expected_answer=(
            "Never patch servers in place — swap a new image. Rollback = re-deploy previous image. "
            "Eliminates config drift, guarantees env parity."
        ),
    ),
    Question(
        category="cicd_cloud",
        kind="verbal",
        difficulty="mid",
        question="Define the four DORA metrics and the elite team benchmarks.",
        expected_answer=(
            "Deployment Frequency, Lead Time for Changes, MTTR, Change Failure Rate. "
            "Elite: deploy multiple times/day, lead time < 1h, MTTR < 1h, CFR < 5%."
        ),
    ),
    Question(
        category="cicd_cloud",
        kind="verbal",
        difficulty="senior",
        question="What is a quality gate in CI/CD? Give five concrete examples.",
        expected_answer=(
            "Automated check that must pass before pipeline progresses. "
            "1. Coverage >= 80%. 2. Zero high CVEs (trivy). 3. Lint passes. "
            "4. No Bandit MEDIUM+ findings. 5. Load test p99 < 500ms."
        ),
    ),
    Question(
        category="cicd_cloud",
        kind="verbal",
        difficulty="senior",
        question="Explain environment promotion. How does an artifact flow from dev to staging to production?",
        expected_answer=(
            "Same immutable Docker SHA built once in CI, promoted through environments by updating manifests. "
            "Guarantees what was tested in staging is exactly what ships to prod."
        ),
    ),
    Question(
        category="cicd_cloud",
        kind="verbal",
        difficulty="senior",
        question="What is a release train vs continuous deployment? When would you choose a release train?",
        expected_answer=(
            "Release train: fixed cadence with code freeze. CD: every passing commit auto-deploys. "
            "Release trains suit regulated industries (finance, healthcare)."
        ),
    ),
    Question(
        category="cicd_cloud",
        kind="verbal",
        difficulty="senior",
        question="What is pipeline parallelism and how do you implement it for pytest?",
        expected_answer=(
            "Run independent jobs/tests concurrently. GitHub Actions matrix strategy. "
            "`pytest-xdist` (`-n auto`) for in-process parallel test execution. "
            "Trade-off: more runners = higher cost."
        ),
        code_snippet=textwrap.dedent("""\
            jobs:
              test:
                strategy:
                  matrix:
                    shard: [1, 2, 3, 4]
                steps:
                  - run: pytest --shard=${{ matrix.shard }}/4
        """),
    ),
    Question(
        category="cicd_cloud",
        kind="verbal",
        difficulty="senior",
        question="What is a flaky test and how do you handle it in CI?",
        expected_answer=(
            "Passes/fails non-deterministically. Causes: race conditions, external deps, time-based logic. "
            "Handle: quarantine in non-blocking job, `pytest-rerunfailures`, fix root cause."
        ),
    ),
    Question(
        category="cicd_cloud",
        kind="verbal",
        difficulty="senior",
        question="Explain 'fail fast' as a CI/CD principle. How do you design a pipeline for it?",
        expected_answer=(
            "Put cheap checks first: lint → unit tests → build → integration → E2E. "
            "Lint failure aborts in seconds, not after a 10-min Docker build."
        ),
    ),
    Question(
        category="cicd_cloud",
        kind="verbal",
        difficulty="senior",
        question="What is dependency pinning? Why pin, and how do you keep pins up to date?",
        expected_answer=(
            "Lock exact versions for reproducible builds. "
            "Use Dependabot / Renovate Bot to auto-raise PRs for updates and CVEs. "
            "Never use floating `>=` versions in production builds."
        ),
    ),
    Question(
        category="cicd_cloud",
        kind="verbal",
        difficulty="senior",
        question="What is an SLO/error budget and how does it connect to CI/CD release decisions?",
        expected_answer=(
            "SLO = target reliability (e.g. 99.9%). Error budget = allowed failures before breach. "
            "Freeze deployments when budget nearly exhausted. "
            "Argo Rollouts can query Prometheus SLO metrics as analysis gates."
        ),
    ),
    Question(
        category="cicd_cloud",
        kind="verbal",
        difficulty="senior",
        question="Compare push-based vs pull-based deployment models. Which does Kubernetes GitOps use and why?",
        expected_answer=(
            "Push-based: pipeline calls `kubectl apply` — needs cluster creds in CI. "
            "Pull-based (GitOps): in-cluster operator watches Git — no external creds, drift detection, audit in Git."
        ),
    ),
    Question(
        category="cicd_cloud",
        kind="verbal",
        difficulty="lead",
        question="Design a CI/CD platform for 50 microservices owned by 10 teams. Address reuse, ownership, speed, governance.",
        expected_answer=(
            "Reuse: shared reusable workflows in central repo. Ownership: teams own service pipelines. "
            "Speed: shared caches, parallel sharding, self-hosted runners. "
            "Governance: required status checks (coverage, CVE), golden path scaffolding CLI, "
            "unified dashboard (Backstage/Port)."
        ),
    ),

    # ── 10. SYSTEM DESIGN ───────────────────────────────────────────────────

    Question(
        category="system_design",
        kind="verbal",
        difficulty="lead",
        question="Design a URL shortener. Cover: API design, DB choice, caching, rate limiting, scale to 10k req/s.",
        expected_answer=(
            "API: POST /shorten {url} → {short_code}; GET /{code} → 301 redirect"
            "ID generation: Base62-encode an auto-increment counter (Redis INCR or DB sequence) for short, collision-free codes"
            "Storage: PostgreSQL for persistence (code → original_url, created_at, click_count); Redis as read-through cache for hot redirects (sub-millisecond, 99%+ of traffic)"
            "Rate limiting: Redis sliding window per IP on the shorten endpoint"
            "Scale to 10k req/s: stateless API pods behind load balancer; Redis cluster handles redirects; DB only for cache misses and writes; CDN for repeated popular redirects."
        ),
    ),
    Question(
        category="system_design",
        kind="verbal",
        difficulty="lead",
        question="A FastAPI endpoint takes 3–5s (ML inference). How do you redesign for high throughput?",
        expected_answer=(
            "Move to async task queue (Celery + Redis). Return 202 with task ID. "
            "Client polls `/tasks/{id}` or uses WebSocket. Scale workers independently."
        ),
    ),
    Question(
        category="system_design",
        kind="verbal",
        difficulty="senior",
        question="Explain the CAP theorem and give a real-world example of CP vs AP.",
        expected_answer=(
            "CAP: a distributed system can guarantee at most two of: Consistency, Availability, Partition tolerance"
            "Since network partitions are inevitable, real systems choose CP or AP"
            "CP (Consistent + Partition-tolerant): HBase, Zookeeper — on partition, refuse requests rather than return stale data"
            "Use for: financial ledgers, distributed locks"
            "AP (Available + Partition-tolerant): Cassandra, DynamoDB (with eventual consistency) — on partition, return possibly stale data rather than block"
            "Use for: user timelines, product catalogs, DNS."
        ),
    ),
    Question(
        category="system_design",
        kind="verbal",
        difficulty="senior",
        question="How would you implement distributed tracing across multiple Python microservices?",
        hint="OpenTelemetry, Jaeger/Zipkin, trace context propagation via HTTP headers.",
        expected_answer=(
            "Use OpenTelemetry (OTel) — the vendor-neutral standard for traces, metrics, and logs"
            "Each service: `pip install opentelemetry-sdk opentelemetry-instrumentation-fastapi`"
            "`FastAPIInstrumentor.instrument_app(app)` auto-creates spans for every request"
            "Propagation: OTel injects a `traceparent` HTTP header; outgoing `httpx`/`aiohttp` calls propagate it automatically with the `opentelemetry-instrumentation-httpx` package"
            "Export: send spans to Jaeger (self-hosted) or an OTLP collector → Grafana Tempo / Datadog."
        ),
    ),

    # ── 11. SECURITY ────────────────────────────────────────────────────────

    Question(
        category="security",
        kind="verbal",
        difficulty="senior",
        question="What is SQL injection and how does SQLAlchemy's ORM protect against it?",
        expected_answer="Parameterised queries — user data is never interpolated directly into SQL.",
    ),
    Question(
        category="security",
        kind="verbal",
        difficulty="senior",
        question="How do you securely store and rotate secrets for a Kubernetes-deployed Python service?",
        hint="Vault + external-secrets-operator. No secrets in code or ConfigMaps.",
        expected_answer=(
            "Never store secrets in code, Docker images, or ConfigMaps"
            "Preferred pattern: HashiCorp Vault as the secrets store with dynamic credentials (Vault generates short-lived DB passwords automatically rotated on expiry)"
            "Integration: `vault-agent-injector` sidecar writes secrets to a shared tmpfs volume; or `external-secrets-operator` syncs Vault/AWS/GCP secrets into Kubernetes Secrets"
            "In Python: read from env vars or mounted files — never hard-code"
            "Rotation: update the secret in Vault → operator syncs to k8s Secret → rolling restart picks it up."
        ),
    ),
    Question(
        category="security",
        kind="verbal",
        difficulty="senior",
        question="Explain OWASP Top-10. Which items are most relevant to a FastAPI + Postgres backend?",
        expected_answer=(
            "Most relevant: A01 Broken Access Control — always enforce RBAC with `require_role` on every protected endpoint"
            "A02 Cryptographic Failures — use HTTPS everywhere, `SecretStr` for passwords, Argon2 hashing"
            "A03 Injection — SQLAlchemy ORM uses parameterised queries; never use raw f-strings in SQL"
            "A05 Security Misconfiguration — disable debug in prod, restrict CORS origins, set security headers"
            "A07 Identification & Auth Failures — short-lived JWTs, refresh tokens, rate-limit `/auth/token`"
            "A09 Security Logging Failures — log all auth events, alert on anomalies via Prometheus/Grafana."
        ),
    ),

    # ── 12. PERFORMANCE & OBSERVABILITY ─────────────────────────────────────

    Question(
        category="performance_observability",
        kind="verbal",
        difficulty="senior",
        question="How would you profile a slow Python endpoint in production without significant overhead?",
        hint="py-spy, Pyroscope, OpenTelemetry spans, structured logging with timing.",
        expected_answer=(
            "1"
            "`py-spy top --pid <PID>` — sampling profiler, near-zero overhead, no code changes, safe in prod"
            "2"
            "OpenTelemetry custom spans: wrap suspect code with `tracer.start_as_current_span('slow_op')`    to measure specific sections without profiling the whole process"
            "3"
            "Structured logging with `time.perf_counter()` around suspect calls — zero profiler overhead"
            "4"
            "Pyroscope — continuous profiling agent; sends flame graphs to a server for time-series analysis"
            "Avoid cProfile in production — its deterministic tracing adds 10–30% overhead."
        ),
    ),
    Question(
        category="performance_observability",
        kind="verbal",
        difficulty="senior",
        question="What is a connection pool? What happens if your async FastAPI app runs out of DB connections?",
        expected_answer=(
            "A connection pool maintains a set of open DB connections reused across requests, avoiding the cost of TCP handshake + authentication on every query"
            "SQLAlchemy async engine: `pool_size` (persistent connections) + `max_overflow` (burst connections)"
            "If all connections are checked out and the pool is full: new requests wait up to `pool_timeout` (default 30s), then raise `sqlalchemy.exc.TimeoutError`"
            "In a FastAPI app this manifests as slow responses and eventually 500 errors under load"
            "Fix: tune pool_size to match worker count × avg concurrency; add connection pool metrics to Prometheus."
        ),
    ),
    Question(
        category="performance_observability",
        kind="code",
        difficulty="senior",
        question="Add Prometheus metrics middleware to FastAPI tracking request count and latency.",
        code_snippet=textwrap.dedent("""\
            from fastapi import FastAPI, Request
            from prometheus_client import Counter, Histogram, make_asgi_app
            import time

            app = FastAPI()
            REQUEST_COUNT = Counter("http_requests_total", "Total HTTP requests", ["method","path","status"])
            REQUEST_LATENCY = Histogram("http_request_duration_seconds", "Request latency", ["method","path"])

            @app.middleware("http")
            async def metrics_middleware(request: Request, call_next):
                start = time.perf_counter()
                response = await call_next(request)
                duration = time.perf_counter() - start
                REQUEST_COUNT.labels(request.method, request.url.path, response.status_code).inc()
                REQUEST_LATENCY.labels(request.method, request.url.path).observe(duration)
                return response

            app.mount("/metrics", make_asgi_app())
        """),
        expected_answer=(
            "`Counter` with labels (method, path, status) lets you compute error rate per endpoint"
            "`Histogram` records duration in seconds; Prometheus derives p50/p95/p99 from the bucket counts"
            "The middleware wraps `call_next` so the timer spans the full handler including DB calls"
            "`make_asgi_app()` mounts a `/metrics` endpoint; Prometheus scrapes it on a configurable interval"
            "Add a Grafana dashboard with RED metrics (Rate, Errors, Duration) for production observability."
        ),
    ),
]


# ---------------------------------------------------------------------------
# Terminal colour helpers (gracefully degrade on dumb terminals)
# ---------------------------------------------------------------------------

import os
import sys

_USE_COLOUR = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None

class C:
    """ANSI colour codes."""
    RESET   = "\033[0m"   if _USE_COLOUR else ""
    BOLD    = "\033[1m"   if _USE_COLOUR else ""
    DIM     = "\033[2m"   if _USE_COLOUR else ""
    CYAN    = "\033[96m"  if _USE_COLOUR else ""
    YELLOW  = "\033[93m"  if _USE_COLOUR else ""
    GREEN   = "\033[92m"  if _USE_COLOUR else ""
    BLUE    = "\033[94m"  if _USE_COLOUR else ""
    MAGENTA = "\033[95m"  if _USE_COLOUR else ""
    RED     = "\033[91m"  if _USE_COLOUR else ""
    WHITE   = "\033[97m"  if _USE_COLOUR else ""


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

WIDTH      = 72
CATEGORIES = sorted({q.category for q in QUESTIONS})

# Difficulty badge colours
DIFF_COLOUR = {
    "mid":    C.GREEN,
    "senior": C.YELLOW,
    "lead":   C.RED,
}

# Kind badge colours
KIND_COLOUR = {
    "verbal": C.CYAN,
    "code":   C.MAGENTA,
}

DIFF_LABEL = {"mid": "MID", "senior": "SENIOR", "lead": "LEAD"}
KIND_LABEL = {"verbal": "VERBAL", "code": "CODE"}

CATEGORY_DISPLAY = {
    "core_python":              "Core Python",
    "oop_design_patterns":      "OOP & Design Patterns",
    "async_concurrency":        "Async / Concurrency",
    "fastapi_rest":             "FastAPI & REST APIs",
    "databases_orm":            "Databases & ORM",
    "testing":                  "Testing",
    "docker":                   "Docker",
    "kubernetes":               "Kubernetes",
    "cicd_cloud":               "CI/CD & Cloud",
    "system_design":            "System Design",
    "security":                 "Security",
    "performance_observability": "Performance & Observability",
}


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def _line(char: str = "─") -> str:
    return char * WIDTH


def _box_top(title: str) -> str:
    inner = f" {title} "
    pad   = WIDTH - 2 - len(inner)
    left  = pad // 2
    right = pad - left
    return f"╔{'═' * (WIDTH - 2)}╗\n║{'─' * left}{inner}{'─' * right}║\n╚{'═' * (WIDTH - 2)}╝"


def _wrap_text(text: str, indent: int = 3, width: int = WIDTH) -> str:
    """Wrap a string to terminal width, preserving numbered list items."""
    lines = []
    prefix = " " * indent
    for sentence in text.split(". "):
        sentence = sentence.strip()
        if not sentence:
            continue
        wrapped = textwrap.fill(sentence, width=width - indent,
                                initial_indent=prefix,
                                subsequent_indent=prefix + "  ")
        lines.append(wrapped)
    return "\n".join(lines)


def _format_answer(text: str) -> str:
    """
    Render expected_answer text as a readable bulleted list.
    Splits on sentence boundaries that start new numbered points.
    """
    # If the text contains numbered items like "1. … 2. …", bullet them
    import re
    numbered = re.split(r"(?<=[.!?])\s+(?=\d+\.)", text)
    if len(numbered) > 1:
        return "\n".join(f"   {C.GREEN}{'●' if i else '→'}{C.RESET}  {item.strip()}"
                         for i, item in enumerate(numbered))
    # Otherwise wrap normally
    return _wrap_text(text)


def _render_badge(label: str, colour: str) -> str:
    return f"{colour}{C.BOLD}[{label}]{C.RESET}"


def _progress_bar(current: int, total: int, width: int = 30) -> str:
    filled = int(width * current / total)
    bar    = "█" * filled + "░" * (width - filled)
    pct    = int(100 * current / total)
    return f"{C.DIM}  {bar} {pct:3d}%  ({current}/{total}){C.RESET}"


# ---------------------------------------------------------------------------
# Single-question renderer
# ---------------------------------------------------------------------------

def display(q: Question, index: int, total: int) -> None:
    cat_label  = CATEGORY_DISPLAY.get(q.category, q.category)
    diff_badge = _render_badge(DIFF_LABEL[q.difficulty], DIFF_COLOUR[q.difficulty])
    kind_badge = _render_badge(KIND_LABEL[q.kind],       KIND_COLOUR[q.kind])

    # ── Header bar ──────────────────────────────────────────────────────────
    print()
    print(f"{C.BLUE}{_line('═')}{C.RESET}")
    print(f"  {C.BOLD}{C.WHITE}Q {index:02d} / {total:02d}{C.RESET}"
          f"   {C.CYAN}{cat_label}{C.RESET}"
          f"   {diff_badge}  {kind_badge}")
    print(f"{C.BLUE}{_line('─')}{C.RESET}")

    # ── Question ────────────────────────────────────────────────────────────
    print()
    print(f"  {C.BOLD}{C.YELLOW}❓  QUESTION{C.RESET}")
    print()
    for line in textwrap.wrap(q.question, width=WIDTH - 4,
                              initial_indent="    ",
                              subsequent_indent="    "):
        print(line)
    print()

    # ── Hint ────────────────────────────────────────────────────────────────
    if q.hint:
        print(f"  {C.MAGENTA}💡  HINT{C.RESET}")
        for line in textwrap.wrap(q.hint, width=WIDTH - 6,
                                  initial_indent="      ",
                                  subsequent_indent="      "):
            print(line)
        print()

    # ── Code snippet ────────────────────────────────────────────────────────
    if q.code_snippet:
        kind_tag = "python" if q.category != "cicd_cloud" or "def " in q.code_snippet else "yaml"
        print(f"  {C.MAGENTA}📝  CODE  {C.DIM}({kind_tag}){C.RESET}")
        print(f"  {C.DIM}{_line('·')}{C.RESET}")
        for line in q.code_snippet.splitlines():
            print(f"    {C.DIM}{line}{C.RESET}")
        print(f"  {C.DIM}{_line('·')}{C.RESET}")
        print()

    # ── Expected answer ─────────────────────────────────────────────────────
    if q.expected_answer:
        print(f"  {C.GREEN}✅  EXPECTED ANSWER{C.RESET}")
        print()
        print(_format_answer(q.expected_answer))
        print()

    print(f"{C.BLUE}{_line('═')}{C.RESET}")


# ---------------------------------------------------------------------------
# Interactive session
# ---------------------------------------------------------------------------

_CONTROLS = (
    f"  {C.DIM}Controls:{C.RESET}  "
    f"{C.BOLD}[Enter]{C.RESET} show answer   "
    f"{C.BOLD}[s]{C.RESET} skip   "
    f"{C.BOLD}[q]{C.RESET} quit"
)


def _banner(total: int) -> None:
    print()
    print(f"{C.BLUE}{'╔' + '═' * (WIDTH - 2) + '╗'}{C.RESET}")
    title = "SENIOR PYTHON DEVELOPER  ·  INTERVIEW SESSION"
    pad = WIDTH - 2 - len(title)
    print(f"{C.BLUE}║{C.RESET}{C.BOLD}{C.WHITE}{' ' * (pad // 2)}{title}{' ' * (pad - pad // 2)}{C.RESET}{C.BLUE}║{C.RESET}")
    sub = f"{total} questions loaded"
    pad2 = WIDTH - 2 - len(sub)
    print(f"{C.BLUE}║{C.RESET}{C.DIM}{' ' * (pad2 // 2)}{sub}{' ' * (pad2 - pad2 // 2)}{C.RESET}{C.BLUE}║{C.RESET}")
    print(f"{C.BLUE}{'╚' + '═' * (WIDTH - 2) + '╝'}{C.RESET}")


def run_session(questions: list[Question]) -> None:
    total    = len(questions)
    skipped  = 0
    answered = 0

    _banner(total)
    print(_CONTROLS)

    for i, q in enumerate(questions, start=1):
        cat_label  = CATEGORY_DISPLAY.get(q.category, q.category)
        diff_badge = _render_badge(DIFF_LABEL[q.difficulty], DIFF_COLOUR[q.difficulty])
        kind_badge = _render_badge(KIND_LABEL[q.kind],       KIND_COLOUR[q.kind])

        # ── Question card ────────────────────────────────────────────────────
        print()
        print(f"{C.BLUE}{_line('═')}{C.RESET}")
        print(f"  {C.BOLD}{C.WHITE}Q {i:02d} / {total:02d}{C.RESET}"
              f"   {C.CYAN}{cat_label}{C.RESET}"
              f"   {diff_badge}  {kind_badge}")
        print(_progress_bar(i - 1, total))
        print(f"{C.BLUE}{_line('─')}{C.RESET}")
        print()
        print(f"  {C.BOLD}{C.YELLOW}❓  QUESTION{C.RESET}")
        print()
        for line in textwrap.wrap(q.question, width=WIDTH - 4,
                                  initial_indent="    ",
                                  subsequent_indent="    "):
            print(line)
        print()

        if q.hint:
            print(f"  {C.MAGENTA}💡  HINT{C.RESET}")
            for line in textwrap.wrap(q.hint, width=WIDTH - 6,
                                      initial_indent="      ",
                                      subsequent_indent="      "):
                print(line)
            print()

        if q.code_snippet:
            kind_tag = "python" if "def " in q.code_snippet or "import " in q.code_snippet else "yaml/shell"
            print(f"  {C.MAGENTA}📝  CODE  {C.DIM}({kind_tag}){C.RESET}")
            print(f"  {C.DIM}{_line('·')}{C.RESET}")
            for line in q.code_snippet.splitlines():
                print(f"    {C.DIM}{line}{C.RESET}")
            print(f"  {C.DIM}{_line('·')}{C.RESET}")
            print()

        # ── Prompt ───────────────────────────────────────────────────────────
        try:
            cmd = input(f"  {C.BOLD}>{C.RESET} ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print(f"\n\n  {C.YELLOW}Session interrupted.{C.RESET}")
            break

        if cmd == "q":
            print(f"\n  {C.YELLOW}Interview ended.  Good luck! 🚀{C.RESET}")
            break

        if cmd == "s":
            skipped += 1
            print(f"  {C.DIM}— skipped —{C.RESET}")
            continue

        answered += 1

        # ── Answer reveal ────────────────────────────────────────────────────
        print()
        print(f"{C.BLUE}{_line('─')}{C.RESET}")
        if q.expected_answer:
            print(f"  {C.GREEN}✅  EXPECTED ANSWER{C.RESET}")
            print()
            print(_format_answer(q.expected_answer))
        elif q.code_snippet:
            print(f"  {C.GREEN}✅  ANSWER{C.RESET}  {C.DIM}Review the code snippet above.{C.RESET}")
        else:
            print(f"  {C.GREEN}✅  OPEN-ENDED{C.RESET}  {C.DIM}Evaluate based on depth and examples.{C.RESET}")
        print(f"{C.BLUE}{_line('─')}{C.RESET}")

    else:
        # completed all
        print()
        print(f"{C.GREEN}{_line('═')}{C.RESET}")
        print(f"  {C.BOLD}{C.GREEN}🎉  All {total} questions completed!{C.RESET}")

    # ── Session summary ───────────────────────────────────────────────────
    print()
    print(f"{C.BLUE}{_line('─')}{C.RESET}")
    print(f"  {C.BOLD}Session Summary{C.RESET}")
    print(f"  {C.DIM}{'─' * 30}{C.RESET}")
    print(f"  Answered  : {C.GREEN}{answered}{C.RESET}")
    print(f"  Skipped   : {C.YELLOW}{skipped}{C.RESET}")
    remaining = total - answered - skipped
    if remaining > 0:
        print(f"  Remaining : {C.DIM}{remaining}{C.RESET}")
    print(f"{C.BLUE}{_line('─')}{C.RESET}")
    print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Senior Python Developer Interview Question Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              python3 interview_questions.py
              python3 interview_questions.py --category fastapi_rest
              python3 interview_questions.py --category fastapi_rest --kind code
              python3 interview_questions.py --difficulty senior --kind verbal
              python3 interview_questions.py --random 10
              python3 interview_questions.py --dump --category cicd_cloud
              python3 interview_questions.py --list-categories
        """),
    )
    p.add_argument("--category",  "-c", metavar="SLUG",
                   help="Filter by category slug (see --list-categories)")
    p.add_argument("--kind",      "-k", choices=["verbal", "code"],
                   help="Filter by question kind")
    p.add_argument("--difficulty","-d", choices=["mid", "senior", "lead"],
                   help="Filter by difficulty level")
    p.add_argument("--random",    "-r", type=int, metavar="N",
                   help="Pick N random questions from the filtered pool")
    p.add_argument("--list-categories", action="store_true",
                   help="Print all category slugs with question counts and exit")
    p.add_argument("--dump",      action="store_true",
                   help="Print all matching questions without interactive mode")
    p.add_argument("--no-color",  action="store_true",
                   help="Disable ANSI colour output")
    return p


def main() -> None:
    parser = build_parser()
    args   = parser.parse_args()

    if args.no_color:
        # Blank out all colour codes at runtime
        for attr in vars(C):
            if not attr.startswith("_"):
                setattr(C, attr, "")

    if args.list_categories:
        print()
        print(f"  {C.BOLD}{'CATEGORY':<38} {'SLUG':<30} {'Qs':>4}{C.RESET}")
        print(f"  {C.DIM}{'─' * 38} {'─' * 30} {'─' * 4}{C.RESET}")
        for slug in CATEGORIES:
            label = CATEGORY_DISPLAY.get(slug, slug)
            count = sum(1 for q in QUESTIONS if q.category == slug)
            print(f"  {C.CYAN}{label:<38}{C.RESET} {C.DIM}{slug:<30}{C.RESET} {C.YELLOW}{count:>4}{C.RESET}")
        total = len(QUESTIONS)
        print(f"  {C.DIM}{'─' * 74}{C.RESET}")
        print(f"  {'Total':<38} {'':30} {C.BOLD}{total:>4}{C.RESET}")
        print()
        return

    pool = list(QUESTIONS)

    if args.category:
        pool = [q for q in pool if q.category == args.category]
        if not pool:
            print(f"\n  {C.RED}No questions found for category '{args.category}'.{C.RESET}")
            print(f"  Available: {', '.join(CATEGORIES)}\n")
            return

    if args.kind:
        pool = [q for q in pool if q.kind == args.kind]

    if args.difficulty:
        pool = [q for q in pool if q.difficulty == args.difficulty]

    if args.random:
        pool = random.sample(pool, min(args.random, len(pool)))

    if not pool:
        print(f"\n  {C.RED}No questions match the given filters.{C.RESET}\n")
        return

    if args.dump:
        for i, q in enumerate(pool, 1):
            display(q, i, len(pool))
        print(f"\n  {C.DIM}Total: {len(pool)} questions{C.RESET}\n")
        return

    run_session(pool)


if __name__ == "__main__":
    main()
