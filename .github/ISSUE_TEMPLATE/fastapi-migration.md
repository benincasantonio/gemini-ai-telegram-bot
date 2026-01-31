## Overview

This issue tracks the migration from Flask to FastAPI, including the database layer upgrade. The current Flask implementation has async compatibility issues in serverless (Vercel) environments, causing `Event loop is closed` errors.

## Motivation

1. **Async Issues**: Flask's async support is bolted-on via werkzeug wrapper, causing event loop problems in Vercel
2. **Native ASGI**: FastAPI is built on Starlette/ASGI with native async support
3. **Better Performance**: FastAPI performs better for async I/O workloads
4. **Modern Stack**: FastAPI + SQLAlchemy 2.0 + Alembic is the modern Python async stack

---

## Migration Scope

### Phase 1: FastAPI Migration

#### 1.1 Dependencies Update (`requirements.txt`)

| Remove                    | Add                          |
| ------------------------- | ---------------------------- |
| `flask[async]~=3.1.0`     | `fastapi~=0.115.0`           |
| `Flask-SQLAlchemy~=3.1.1` | `sqlalchemy[asyncio]~=2.0.0` |
| `Flask-Migrate~=4.0.7`    | `alembic~=1.14.0`            |
| `psycopg2-binary~=2.9.10` | `asyncpg~=0.30.0`            |
| -                         | `uvicorn[standard]~=0.34.0`  |

#### 1.2 Application Entry Point

**Current** (`src/telegram_bot_api.py`):

- Flask app with async routes
- Uses `@app.post('/webhook')`
- Global singleton pattern for Gemini client

**New** (`src/main.py`):

- FastAPI app with native async
- Uses `@app.post('/webhook')`
- Lifespan context manager for startup/shutdown
- Dependency injection for services

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize resources
    yield
    # Shutdown: cleanup resources

app = FastAPI(lifespan=lifespan)
```

---

### Phase 2: Database Layer Migration

#### 2.1 Models (`src/models/`)

**Current** (`src/flask_app.py`):

```python
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat_session.id'))
    text = db.Column(db.Text)
    date = db.Column(db.DateTime)
    role = db.Column(db.String(20))
```

**New** (`src/models/chat.py`):

```python
from sqlalchemy import Column, Integer, Text, DateTime, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship

class Base(DeclarativeBase):
    pass

class ChatMessage(Base):
    __tablename__ = 'chat_message'
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey('chat_session.id'), nullable=False)
    text = Column(Text)
    date = Column(DateTime)
    role = Column(String(20))
```

#### 2.2 Database Session Management

**New** (`src/database.py`):

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

DATABASE_URL = "postgresql+asyncpg://..."

engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

#### 2.3 Postgres Driver

| Current                         | New                                     |
| ------------------------------- | --------------------------------------- |
| `psycopg2-binary` (sync)        | `asyncpg` (native async)                |
| Connection URL: `postgresql://` | Connection URL: `postgresql+asyncpg://` |

---

### Phase 3: Migration Tool (Alembic)

**Current**: Flask-Migrate (wrapper around Alembic that depends on Flask app context)

**New**: Native Alembic (no Flask dependency)

#### 3.1 Changes to `migrations/env.py`

Remove Flask dependencies:

```python
# Remove these
from flask import current_app
current_app.extensions['migrate']

# Replace with
from src.database import DATABASE_URL
from src.models.chat import Base
```

#### 3.2 Existing Migrations

Existing migration files in `migrations/versions/` can remain unchanged - they are database DDL scripts that work independently of Flask.

---

### Phase 4: Service Layer Updates

#### 4.1 ChatService (`src/chat_service.py`)

**Current**: Synchronous SQLAlchemy queries

```python
messages = self._db.session.query(ChatMessage).filter_by(...).all()
```

**New**: Async SQLAlchemy 2.0 queries

```python
async def get_chat_history(self, db: AsyncSession, session_id: int):
    result = await db.execute(
        select(ChatMessage).where(ChatMessage.chat_id == session_id)
    )
    return result.scalars().all()
```

---

### Phase 5: Vercel Configuration

**Current** (`vercel.json`):

```json
{
  "builds": [{ "src": "src/telegram_bot_api.py", "use": "@vercel/python" }]
}
```

**New**:

```json
{
  "builds": [{ "src": "src/main.py", "use": "@vercel/python" }]
}
```

---

### Phase 6: Test Updates

Update `tests/integration/test_chat_service.py`:

- Use async test fixtures with `pytest-asyncio`
- Use async session management
- SQLite async driver: `aiosqlite`

---

## Files Affected

| File                      | Action                           |
| ------------------------- | -------------------------------- |
| `requirements.txt`        | Modify dependencies              |
| `src/flask_app.py`        | Delete (replaced by new modules) |
| `src/main.py`             | **New** - FastAPI app            |
| `src/database.py`         | **New** - Async SQLAlchemy setup |
| `src/models/chat.py`      | **New** - SQLAlchemy 2.0 models  |
| `src/telegram_bot_api.py` | Migrate to FastAPI format        |
| `src/chat_service.py`     | Convert to async                 |
| `src/gemini.py`           | Remove event loop workaround     |
| `migrations/env.py`       | Remove Flask dependencies        |
| `vercel.json`             | Update entry point               |
| `run.py`                  | Update for uvicorn               |
| `tests/integration/*.py`  | Async test fixtures              |

---

## Acceptance Criteria

- [ ] FastAPI app runs successfully on Vercel
- [ ] Webhook endpoint handles Telegram messages correctly
- [ ] Chat history persisted to PostgreSQL via asyncpg
- [ ] Database migrations work via Alembic CLI
- [ ] All existing tests pass (updated for async)
- [ ] No `Event loop is closed` errors in serverless environment
- [ ] Local development works with `uvicorn`

---

## Additional Notes

- **Backwards Compatibility**: No breaking changes to the external Telegram webhook API
- **Database Schema**: No changes to table structure - existing data preserved
- **Environment Variables**: Same env vars (`DATABASE_URL`, `GEMINI_API_KEY`, etc.)
