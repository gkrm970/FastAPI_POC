# FastAPI_POC

Framework Structure for FastAPI POC
FastAPI_POC/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Creates the FastAPI application
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Environment/database configuration
│   │   └── security.py         # Password hashing and security
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── database.py         # Engine and sessions
│   │   └── base.py             # SQLAlchemy Base and model imports
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── product.py          # Product database model
│   │   └── seller.py           # Seller database model
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── product.py          # Product request/response schemas
│   │   └── seller.py           # Seller request/response schemas
│   │
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── product.py          # Product database queries
│   │   └── seller.py           # Seller database queries
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── product.py          # Product business logic
│   │   └── seller.py           # Seller business logic
│   │
│   └── api/
│       ├── __init__.py
│       ├── dependencies.py     # Shared FastAPI dependencies
│       └── routes/
│           ├── __init__.py
│           ├── products.py     # Product endpoints
│           └── sellers.py      # Seller endpoints
│
├── tests/
│   ├── __init__.py
│   ├── test_products.py
│   └── test_sellers.py
│
├── .env                        # Local settings; do not commit
├── .env.example                # Safe configuration template
├── .gitignore
├── requirements.txt
└── README.md
