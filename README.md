# Bot Battle Arena

A backend focused web platform where users upload autonomous bots that compete
against each other in turn based games like TicTacToe and SinkTheShip.
The backend acts as a referee, running each bot in an isolated Docker container, communicating via stdin/stdout.
It enforces game rules, tracks ELO ratings, and streams live match updates via WebSockets.

---

## Tech Stack

| Layer         | Technology                                      |
|---------------|-------------------------------------------------|
| Language      | Python 3.12.3                                   |
| API Framework | FastAPI                                         |
| Task Queue    | Celery                                          |
| Broker/Cache  | Redis                                           |
| Database      | PostgreSQL                                      |
| ORM           | SQLAlchemy + Alembic                            |
| Containers    | Docker + docker-py                              |
| Auth          | JWT (python-jose) + bcrypt (passlib)            |
| WebSockets    | FastAPI built-in                                |
| Frontend      | Next.js + Tailwind CSS *(UPCOMING)*          |

---

## How It Works

1. A user uploads bot code (Python or JavaScript) via the API
2. A user creates a match by selecting two bots and a game type
3. The API queues a Celery job and returns the match ID
4. A Celery worker picks up the job and runs the referee
5. The referee starts two Docker containers / one per bot
6. Each turn: the referee writes the current game state as JSON to the bot's
   stdin, reads the bot's move from stdout, validates it, applies it, stores
   the turn, and broadcasts the new state over WebSocket
7. When the game ends, the referee cleans up containers, updates ELO ratings,
   and marks the match complete
8. Viewers watching in real time receive every state update live via WebSocket
   (Redis pub/sub bridges the Celery worker and FastAPI processes)

Bots are intentionally simple to write:

Bot example:

```python
import sys, json

state = json.loads(sys.stdin.readline())
# decide your move based on state
print(json.dumps({"row": 0, "col": 0}))
```

---


## API Overview

### Auth
| Method | Endpoint          | Description              |
|--------|-------------------|--------------------------|
| POST   | `/auth/register`  | Register a new user      |
| POST   | `/auth/login`     | Login, receive JWT token |

### Bots
| Method | Endpoint         | Description                        |
|--------|------------------|------------------------------------|
| POST   | `/bots`          | Upload a new bot (auth required)   |
| GET    | `/bots`          | List all bots                      |
| GET    | `/bots/me`       | List your own bots                 |
| GET    | `/bots/{id}`     | Get a specific bot                 |
| DELETE | `/bots/{id}`     | Delete your bot(s) (auth required)    |

### Matches
| Method    | Endpoint                      | Description                    |
|-----------|-------------------------------|--------------------------------|
| POST      | `/matches`                    | Create and queue a match       |
| GET       | `/matches/{id}`               | Get match status               |
| GET       | `/matches/{id}/replay`        | Get full turn-by-turn replay   |
| GET       | `/matches`                    | List recent matches            |
| WebSocket | `/matches/{id}/live`          | Stream live match updates      |

### Leaderboard
| Method | Endpoint              | Description            |
|--------|-----------------------|------------------------|
| GET    | `/leaderboard/bots`   | Top bots by ELO        |
| GET    | `/leaderboard/users`  | Top users              |

Full interactive docs available at `/docs` (Swagger UI via FastAPI).

---

## Security Model

Bot code runs in Docker containers with the following restrictions enforced
on every execution:

- **No network access** — `network_disabled=True`
- **Read-only filesystem** — `read_only=True`
- **64MB memory cap** — `mem_limit=64m`
- **CPU quota** — limited to 25% of one core
- **Process limit** — `pids_limit=50` (prevents fork bombs)
- **No root** — containers run as a non-root user
- **No Linux capabilities** — `cap_drop=["ALL"]`
- **No privilege escalation** — `security_opt=["no-new-privileges"]`
- **Hard timeout** — bots that don't respond within the time limit forfeit the turn

---

## Running Locally

### Prerequisites
- Docker & Docker Compose
- Python 3.12+

### Setup

```bash
git clone https://github.com/ruff1e/BotArena.git
cd BotArena
cp .env.example .env
# Fill in your secrets in .env
```

Start infrastructure (Postgres + Redis):

```bash
docker compose up postgres redis -d
```

Install dependencies and run migrations:

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
```

Start the API server:

```bash
uvicorn app.main:app --reload
```

Start the Celery worker (in a separate terminal):

```bash
celery -A app.worker worker --loglevel=info
```

Visit `http://localhost:8000/docs` to explore the API.

---

## Environment Variables

```text
DATABASE_URL=postgresql://user:password@localhost:5432/botarena
REDIS_URL=redis://localhost:6379/0
JWT_SECRET=your-secret-key-here
JWT_EXPIRE_HOURS=24
```

---

## Running Tests

```bash
pytest tests/
```

---

## Roadmap

- [x] Phase 1  — Local setup & prerequisites
- [x] Phase 2  — Database schema & models
- [x] Phase 3  — Authentication API
- [x] Phase 4  — Bot management API
- [x] Phase 5  — Game engine(s)
- [x] Phase 6  — Docker sandbox
- [x] Phase 7  — Referee
- [x] Phase 8  — Celery worker
- [x] Phase 9  — Match API & WebSocket
- [x] Phase 10 — Leaderboard, pagination, polish
- [X] Phase 11 — Dockerize full application
- [ ] Phase 13 — Next.js frontend
