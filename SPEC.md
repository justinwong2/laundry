# SPEC.md

This specification defines the Laundry Bot project — a Telegram Mini App + Bot for shared laundry room management with gamification.

**Architecture:** Telegram Mini App (React) for interactive UI + Bot for push notifications.

---

## 1. Objective

**What:** A Telegram bot that helps dormitory residents manage shared laundry machines, get reminders, and see availability.

**Who:** Residents of a dormitory with 5 blocks (A, B, C, D, E), each with their own laundry room.

**Deployment Plan:** Block E first, then roll out to all blocks.

**Core Value Propositions:**
- Know when your laundry is done (automatic reminders)
- Check machine availability without walking to the laundry room
- Nudge others to pick up finished laundry
- Leave messages for help (e.g., "please move my laundry to dryer")
- Gamification (coins) incentivizes timely updates

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                      USER                               │
└─────────────────────────┬───────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
   ┌─────────────┐  ┌───────────┐  ┌─────────────┐
   │ Mini App    │  │ QR Scan   │  │ Bot Chat    │
   │ (main UI)   │  │ (claim)   │  │ (notifs)    │
   └──────┬──────┘  └─────┬─────┘  └──────┬──────┘
          │               │               │
          └───────────────┼───────────────┘
                          ▼
              ┌───────────────────────┐
              │   FastAPI Backend     │
              │   (Python + SQLite)   │
              └───────────────────────┘
                          │
              ┌───────────┴───────────┐
              ▼                       ▼
       ┌─────────────┐        ┌─────────────┐
       │ Telegram    │        │ APScheduler │
       │ Bot API     │        │ (reminders) │
       └─────────────┘        └─────────────┘
```

**Mini App (React):** Main interface for viewing machines, claiming, releasing, pinging
**Bot:** Sends push notifications (reminders, pings) — works even when app closed
**QR Codes:** Deep link to Mini App with machine pre-selected

---

## 3. Core Features

### Mini App Screens

| Screen | Description |
|--------|-------------|
| **Home / Status** | Visual grid of all machines (washers + dryers), tap to interact |
| **Claim Modal** | Select machine → optional message → confirm claim |
| **My Machines** | List of your active sessions with release buttons |
| **Ping Modal** | Tap in-use machine → ping user (costs coins) |
| **Profile** | Your block, coin balance, transaction history |

### Bot Commands (Minimal)

| Command | Description |
|---------|-------------|
| `/start` | Register, select block, opens Mini App button |
| `/help` | Quick reference, link to open Mini App |

**Note:** All main interactions happen in Mini App. Bot is primarily for notifications.

### Bot Notifications (Push)

| Event | Message |
|-------|---------|
| Reminder (T-5min) | "⏰ Your laundry in Washer A1 is almost done!" |
| Done (T-0) | "✅ Your laundry in Washer A1 is done! Please collect it." |
| Pinged | "👋 @john is waiting for Dryer B1. Please collect your laundry!" |
| Ping received | "💰 You received 1 coin from @jane's ping." |

### QR Code Flow
1. User scans QR on machine → opens Mini App with machine pre-selected
2. Mini App shows claim modal → user confirms → timer starts
3. Bot sends reminders at T-5min and T-0
4. User opens Mini App → releases machine → earns coins

### Mini App UI Mockup

```
┌─────────────────────────────────────┐
│  🧺 Block E Laundry    💰 47 coins  │
├─────────────────────────────────────┤
│                                     │
│  WASHERS                            │
│  ┌─────┬─────┬─────┬─────┐         │
│  │ A1  │ A2  │ B1  │ B2  │         │
│  │ 🟢  │ 🔴  │ 🔴  │ 🟢  │         │
│  │     │@john│@jane│     │         │
│  │     │ 23m │ 5m! │     │         │
│  └─────┴─────┴─────┴─────┘         │
│  ┌─────┬─────┬─────┬─────┐         │
│  │ C1  │ C2  │ D1  │ D2  │         │
│  │ 🟢  │ 🟢  │ ⚠️  │ 🟢  │         │
│  │     │     │@alex│     │         │
│  │     │     │DONE │     │         │
│  └─────┴─────┴─────┴─────┘         │
│                                     │
│  DRYERS                             │
│  ┌─────┬─────┬─────┬─────┐         │
│  │ A1  │ A2  │ B1  │ B2  │         │
│  │ 🟢  │ 🟢  │ 🔴  │ 🟢  │         │
│  │     │     │@john│     │         │
│  │     │     │ 45m │     │         │
│  └─────┴─────┴─────┴─────┘         │
│  ┌─────┬─────┬─────┬─────┐         │
│  │ C1  │ C2  │ D1  │ D2  │         │
│  │ 🟢  │ 🟢  │ 🟢  │ 🟢  │         │
│  └─────┴─────┴─────┴─────┘         │
│                                     │
│  📝 Messages                        │
│  • D1 Washer (@alex): "help move"   │
│                                     │
├─────────────────────────────────────┤
│  [🏠 Home]  [🧺 My Machines]  [👤]  │
└─────────────────────────────────────┘
```

Legend: 🟢 Available  🔴 In Use  ⚠️ Done (collect!)

---

## 4. Project Structure

```
laundry/
├── SPEC.md
├── CLAUDE.md
├── README.md
├── .env.example
│
├── backend/                    # Python FastAPI + Bot
│   ├── pyproject.toml
│   ├── src/
│   │   └── laundry/
│   │       ├── __init__.py
│   │       ├── main.py             # FastAPI app + bot startup
│   │       ├── config.py           # Settings from env vars
│   │       │
│   │       ├── api/
│   │       │   ├── __init__.py
│   │       │   ├── routes.py       # REST API endpoints
│   │       │   ├── auth.py         # Telegram WebApp auth validation
│   │       │   └── schemas.py      # Pydantic request/response models
│   │       │
│   │       ├── bot/
│   │       │   ├── __init__.py
│   │       │   ├── handlers.py     # /start, /help commands
│   │       │   └── notifications.py # Send reminders, pings
│   │       │
│   │       ├── models/
│   │       │   ├── __init__.py
│   │       │   ├── user.py
│   │       │   ├── machine.py
│   │       │   └── session.py
│   │       │
│   │       ├── services/
│   │       │   ├── __init__.py
│   │       │   ├── machine_service.py
│   │       │   ├── session_service.py
│   │       │   ├── coin_service.py
│   │       │   └── reminder_service.py
│   │       │
│   │       └── db/
│   │           ├── __init__.py
│   │           ├── database.py
│   │           └── seed.py         # Seed Block E machines
│   │
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_api.py
│   │   └── test_services.py
│   │
│   └── scripts/
│       └── generate_qr.py
│
└── frontend/                   # React + Vite Mini App
    ├── package.json
    ├── vite.config.ts
    ├── index.html
    ├── src/
    │   ├── main.tsx
    │   ├── App.tsx
    │   ├── api/
    │   │   └── client.ts           # API client with Telegram auth
    │   ├── components/
    │   │   ├── MachineGrid.tsx     # Visual machine grid
    │   │   ├── MachineCard.tsx     # Individual machine tile
    │   │   ├── ClaimModal.tsx      # Claim flow
    │   │   ├── PingModal.tsx       # Ping confirmation
    │   │   └── Navigation.tsx      # Bottom nav bar
    │   ├── pages/
    │   │   ├── Home.tsx            # Main status view
    │   │   ├── MyMachines.tsx      # Active sessions
    │   │   └── Profile.tsx         # Balance, history
    │   ├── hooks/
    │   │   ├── useTelegram.ts      # Telegram WebApp SDK
    │   │   └── useMachines.ts      # Machine data fetching
    │   └── styles/
    │       └── globals.css
    └── public/
```

---

## 5. API Endpoints

All endpoints require Telegram WebApp `initData` for authentication.

### Machines

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/machines` | List all machines with current status |
| GET | `/api/machines/{id}` | Get single machine details |

### Sessions

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/sessions` | Claim a machine `{machine_id, message?}` |
| DELETE | `/api/sessions/{id}` | Release a machine |
| GET | `/api/sessions/mine` | Get user's active sessions |

### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users/me` | Get current user profile + balance |
| POST | `/api/users/register` | Register new user `{block}` |
| GET | `/api/users/me/transactions` | Coin transaction history |

### Interactions

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/ping/{machine_id}` | Ping a machine's user (costs coins) |

### Auth Flow
1. Mini App sends `initData` from Telegram WebApp SDK in header
2. Backend validates `initData` hash using bot token
3. Extract `telegram_id` from validated data
4. Create or lookup user

---

## 6. Code Style

### Python (Backend)
- **Python 3.11+** required
- **Type hints** on all function signatures
- **Async/await** for all I/O (FastAPI, database, Telegram)
- **Ruff** for linting and formatting
- **Pydantic** for request/response schemas

### TypeScript (Frontend)
- **TypeScript strict mode** enabled
- **React 18** with functional components and hooks
- **ESLint + Prettier** for formatting
- No `any` types — use proper typing

### Naming Conventions
- Python: `snake_case` functions/vars, `PascalCase` classes
- TypeScript: `camelCase` functions/vars, `PascalCase` components
- `SCREAMING_SNAKE_CASE` for constants (both)

### Architecture Patterns
- **Service layer** handles business logic (not in API routes)
- **API routes** only validate input, call services, return responses
- **React Query** for server state management
- **Custom hooks** for reusable logic

---

## 7. Testing Strategy

### Backend Tests
```bash
cd backend
pytest                              # Run all tests
pytest --cov=src/laundry            # With coverage
pytest tests/test_api.py            # API tests only
pytest -k test_claim                # Tests matching pattern
```

### Frontend Tests
```bash
cd frontend
npm run test                        # Run Vitest
npm run test:coverage               # With coverage
```

### Test Types
- **Backend unit tests:** Service functions with mocked DB
- **Backend API tests:** FastAPI TestClient
- **Frontend component tests:** React Testing Library

---

## 8. Boundaries

### ALWAYS Do
- Validate machine exists before any operation
- Check user has sufficient coins before pinging
- Send confirmation after every state change
- Log all coin transactions for audit

### ASK FIRST About
- Changing coin reward/cost values
- Adding new machine types beyond washer/dryer
- Modifying reminder timing intervals
- Database schema changes

### NEVER Do
- Allow coin balance to go negative
- Allow claiming an already-claimed machine
- Delete historical session data (soft delete only)
- Send reminders more than once per minute (rate limit)

---

## 9. Data Models

### User
| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER | Primary key |
| telegram_id | INTEGER | Telegram user ID (unique) |
| username | TEXT | Telegram username (nullable) |
| block | TEXT | User's block (A, B, C, D, E) |
| coins | INTEGER | Current balance (default: 10) |
| created_at | TIMESTAMP | Registration time |

**Note:** Username is displayed publicly in `/status` so others know who is using machines.

### Machine
| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER | Primary key |
| code | TEXT | Machine code (e.g., "A1", "B2", "D1") |
| type | TEXT | "washer" or "dryer" |
| block | TEXT | Block letter (A, B, C, D, E) |
| cycle_duration_minutes | INTEGER | Default cycle time |
| qr_code | TEXT | Unique identifier for QR (e.g., "E-WASHER-A1") |

**Machine Naming Convention:**
- Each block has 8 washers: A1, A2, B1, B2, C1, C2, D1, D2
- Each block has 8 dryers: A1, A2, B1, B2, C1, C2, D1, D2
- Full identifier: `{block}-{type}-{code}` (e.g., "E-WASHER-A1", "E-DRYER-B2")

### LaundrySession
| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER | Primary key |
| user_id | INTEGER | FK to User |
| machine_id | INTEGER | FK to Machine |
| started_at | TIMESTAMP | When cycle started |
| expected_end_at | TIMESTAMP | When cycle should end |
| ended_at | TIMESTAMP | When user released (nullable) |
| message | TEXT | Optional message (e.g., "pls help move to dryer") |
| reminder_sent | BOOLEAN | Whether end reminder was sent |

### CoinTransaction
| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER | Primary key |
| user_id | INTEGER | FK to User |
| amount | INTEGER | +/- coins |
| reason | TEXT | "claim", "release", "ping_sent", "ping_received" |
| created_at | TIMESTAMP | Transaction time |

### Block
| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER | Primary key |
| code | TEXT | Block letter (A, B, C, D, E) |
| name | TEXT | Full name (e.g., "Block E") |
| is_active | BOOLEAN | Whether bot is deployed here |
| created_at | TIMESTAMP | Creation time |

**Initial Data (MVP):**
- Block E: `is_active = true`
- Blocks A, B, C, D: `is_active = false` (for future rollout)

---

## 10. Coin Economy

| Action | Coins |
|--------|-------|
| Scan QR / claim machine | +1 |
| Release machine (mark done) | +2 |
| Ping another user | -3 |
| Being pinged | +1 (compensation) |

**Rules:**
- New users start with 10 coins
- Cannot ping if balance < 3
- No negative balances allowed

---

## 11. Dependencies

### Backend (pyproject.toml)
```toml
[project]
dependencies = [
    "fastapi>=0.110.0",           # API framework
    "uvicorn>=0.29.0",            # ASGI server
    "python-telegram-bot>=21.0",  # Telegram Bot API
    "aiosqlite>=0.19.0",          # Async SQLite
    "apscheduler>=3.10.0",        # Scheduled reminders
    "python-dotenv>=1.0.0",       # Environment variables
    "qrcode>=7.4.0",              # QR code generation
    "pydantic>=2.0.0",            # Data validation
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=4.0.0",
    "httpx>=0.27.0",              # FastAPI TestClient
    "ruff>=0.3.0",
]
```

### Frontend (package.json)
```json
{
  "dependencies": {
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "react-router-dom": "^6.22.0",
    "@tanstack/react-query": "^5.28.0",
    "@telegram-apps/sdk-react": "^1.0.0"
  },
  "devDependencies": {
    "typescript": "^5.4.0",
    "vite": "^5.2.0",
    "@vitejs/plugin-react": "^4.2.0",
    "@types/react": "^18.3.0",
    "eslint": "^8.57.0",
    "vitest": "^1.4.0",
    "@testing-library/react": "^14.2.0"
  }
}
```

---

## 12. Environment Variables

```bash
# backend/.env
TELEGRAM_BOT_TOKEN=your_bot_token_here
DATABASE_URL=sqlite:///laundry.db
LOG_LEVEL=INFO
WEBAPP_URL=https://your-app.vercel.app   # Mini App URL

# Coin settings (optional, has defaults)
COINS_CLAIM=1
COINS_RELEASE=2
COINS_PING_COST=3
COINS_PING_RECEIVE=1
COINS_STARTING=10

# Reminder settings
REMINDER_BEFORE_MINUTES=5
```

```bash
# frontend/.env
VITE_API_URL=https://your-api.example.com
```

---

## Acceptance Criteria (MVP - Block E)

### Bot
- [ ] `/start` registers user, prompts block selection, shows "Open Laundry Room" button
- [ ] Bot sends reminder at T-5min: "Your laundry is almost done!"
- [ ] Bot sends notification at T-0: "Your laundry is done!"
- [ ] Bot sends ping notification to machine owner
- [ ] QR scan opens Mini App with machine pre-selected

### Mini App
- [ ] Home screen shows visual grid of 16 machines (8 washers + 8 dryers)
- [ ] Machine tiles show status (available/in-use/done), username, time remaining
- [ ] Tapping available machine opens claim modal with optional message
- [ ] Tapping in-use machine shows ping option (if not yours)
- [ ] "My Machines" tab shows active sessions with release buttons
- [ ] Profile tab shows coin balance and transaction history
- [ ] Messages displayed below grid for machines with help requests

### API
- [ ] Auth validates Telegram WebApp initData
- [ ] All CRUD operations for machines, sessions, users work
- [ ] Ping deducts coins from sender, adds to receiver
- [ ] Cannot ping without sufficient coins

### Setup
- [ ] Database seeded with Block E machines (A1-D2 washers + A1-D2 dryers)
- [ ] QR codes generated for all 16 machines
- [ ] Frontend deployed to Vercel/similar
- [ ] Backend deployed with public API URL
