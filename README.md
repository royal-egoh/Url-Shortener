# URL Shortener API

A RESTful URL shortening service built with **FastAPI**, **SQLAlchemy**, and **SQLite**. Create short links, manage them, follow them, and track how often each one is used.

Interactive API docs are available at `/docs` (Swagger UI) once the server is running.

## Features

- Create, retrieve, update, and delete short URLs
- Randomly generated, unique short codes
- Access statistics for every link
- Public redirects from short code to original URL
- Per-user ownership through API keys (no passwords or sign-up)
- Input validation with Pydantic

## Tech Stack

| Layer | Choice |
|---|---|
| Framework | FastAPI |
| ORM | SQLAlchemy |
| Database | SQLite |
| Validation | Pydantic |
| Server | Uvicorn |

## Getting Started

### Prerequisites

- Python 3.10+

### Installation

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root:

```env
DATABASE_URL=sqlite:///./app.db
```

Tables are created automatically on first run.

### Run

```bash
uvicorn app.main:app --reload
```

The API is now available at `http://localhost:8000`, with Swagger docs at `http://localhost:8000/docs`.

## Authentication

There are no accounts or passwords. Access works with **API keys**:

1. Call `POST /shorten/keys` to get a key. It is shown **once** and cannot be recovered, because only a hash of it is stored.
2. Send it on every protected request in the `X-API-Key` header. The server also sets it as a cookie, so a browser can use it without extra code.

Each key owns its own links. You can only view, update, delete, and see stats for links created with your key.

The redirect endpoint (`GET /{shortCode}`) is public, so anyone can follow a short link.

## API Reference

All protected endpoints require the `X-API-Key` header.

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/shorten/keys` | No | Create an API key |
| POST | `/shorten/` | Yes | Create a short URL |
| GET | `/shorten/{shortCode}` | Yes | Retrieve a short URL's details |
| PUT | `/shorten/{shortCode}` | Yes | Update the original URL |
| DELETE | `/shorten/{shortCode}` | Yes | Delete a short URL |
| GET | `/shorten/{shortCode}/stats` | Yes | Get access statistics |
| GET | `/{shortCode}` | No | Redirect to the original URL |

### Create an API key

```bash
curl -X POST http://localhost:8000/shorten/keys
```

```json
{ "api_key": "sk_..." }
```

### Create a short URL

```bash
curl -X POST http://localhost:8000/shorten/ \
  -H "X-API-Key: sk_..." \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.example.com/some/long/url"}'
```

**201 Created**

```json
{
  "id": 1,
  "url": "https://www.example.com/some/long/url",
  "shortCode": "abc1234",
  "createdAt": "2026-10-12T12:00:00Z",
  "updatedAt": "2026-10-12T12:00:00Z"
}
```

### Retrieve a short URL

```bash
curl http://localhost:8000/shorten/abc1234 -H "X-API-Key: sk_..."
```

Returns **200 OK** with the same object as above, or **404** if the code does not exist or belongs to another key.

### Update a short URL

```bash
curl -X PUT http://localhost:8000/shorten/abc1234 \
  -H "X-API-Key: sk_..." \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.example.com/some/updated/url"}'
```

Returns **200 OK** with the updated object, or **404** if not found.

### Delete a short URL

```bash
curl -X DELETE http://localhost:8000/shorten/abc1234 -H "X-API-Key: sk_..."
```

Returns **204 No Content**, or **404** if not found.

### Get statistics

```bash
curl http://localhost:8000/shorten/abc1234/stats -H "X-API-Key: sk_..."
```

```json
{
  "id": 1,
  "url": "https://www.example.com/some/long/url",
  "shortCode": "abc1234",
  "createdAt": "2026-10-12T12:00:00Z",
  "updatedAt": "2026-10-12T12:00:00Z",
  "accessCount": 10
}
```

### Follow a short link

```
GET http://localhost:8000/abc1234
```

Redirects (`307`) to the original URL and increments the access count. No API key needed.

### Status codes

| Code | Meaning |
|---|---|
| 200 | Success |
| 201 | Short URL created |
| 204 | Short URL deleted |
| 307 | Redirect to original URL |
| 401 | Missing or invalid API key |
| 404 | Short URL not found |
| 422 | Request body failed validation |

## Design Decisions

**SQLite.** A shortener is overwhelmingly read-heavy (redirects), which SQLite handles well, and it needs no separate database server. Database access goes through SQLAlchemy, so moving to PostgreSQL later would be a connection-string and configuration change rather than a rewrite.

**Short codes.** Codes are 7 characters from a base62 alphabet (`a-z`, `A-Z`, `0-9`), generated with Python's `secrets` module, giving roughly 3.5 trillion combinations. Random codes are not guessable the way sequential IDs are. The database enforces uniqueness with a `UNIQUE` constraint, and creation retries on the rare collision rather than checking first, which avoids a race between concurrent requests.

**API keys instead of accounts.** Keys are generated with `secrets.token_urlsafe(32)` and stored as SHA-256 hashes, so a leaked database does not expose usable keys. Ownership is enforced in every query by filtering on the key's user ID. Links that belong to someone else return `404` rather than `403`, so the API does not reveal which codes exist.

**Redirect status.** Redirects use `307` instead of `301`. A `301` is cached by browsers, so repeat visits would skip the server and stop counting toward `accessCount`.

**Access counting.** The counter is incremented with a single `UPDATE ... SET accessCount = accessCount + 1`, so simultaneous clicks do not overwrite each other.

## Project Structure

```
app/
├── main.py            # App entry point, router registration
├── database.py        # Engine, session, Base
├── models/            # SQLAlchemy models (Users, Links)
├── schemas/           # Pydantic request/response models
├── services/          # Business logic (keys, link CRUD)
└── routers/           # API endpoints
```

## Limitations

- API keys are anonymous and not recoverable. Lose the key and you lose access to its links. A password or email-based account system would be needed for recovery.
- No rate limiting yet, so the key-creation endpoint could be abused.
- SQLite allows one writer at a time, which is fine at this scale but would be the first thing to change under heavy write load.

## Possible Improvements

- Rate limiting per key and per IP
- Custom aliases and link expiry dates
- Click analytics beyond a total count (timestamps, referrers)
- Automated tests with `pytest`
- Docker setup for deployment