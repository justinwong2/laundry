# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/claude-code) when working with this codebase.

## Project Overview

Laundry Bot is a Telegram Mini App + Bot for shared laundry room management with gamification. It consists of:
- **Backend**: Python FastAPI REST API + Telegram Bot (python-telegram-bot)
- **Frontend**: React + TypeScript + Vite Telegram Mini App

## Key Commands

### Backend

```bash
cd backend

# Setup
uv venv && .venv\Scripts\Activate.ps1  # Windows
uv venv && source .venv/bin/activate    # Linux/Mac
uv pip install -e ".[dev]"

# Run
uvicorn laundry.main:app --reload

# Seed database
python -m laundry.db.seed

# Test
pytest

# Lint
ruff check src/
ruff format src/
```

### Frontend

```bash
cd frontend

# Setup
npm install

# Run
npm run dev

# Build
npm run build

# Lint
npm run lint
```

## Architecture

```
backend/src/laundry/
├── main.py              # FastAPI app entrypoint
├── config.py            # Settings from environment
├── api/
│   ├── routes.py        # REST endpoints
│   ├── auth.py          # Telegram WebApp auth validation
│   └── schemas.py       # Pydantic models
├── bot/
│   ├── handlers.py      # /start, /help commands
│   └── notifications.py # Send reminders, pings
├── models/              # SQLAlchemy models (User, Machine, Session, Transaction)
├── services/            # Business logic layer
└── db/
    ├── database.py      # Async SQLite setup
    └── seed.py          # Seed Block E machines

frontend/src/
├── App.tsx              # Routes + layout
├── api/client.ts        # API client with Telegram auth
├── hooks/
│   ├── useTelegram.ts   # Telegram WebApp SDK
│   └── useMachines.ts   # React Query hooks
├── components/          # MachineGrid, MachineCard, ClaimModal, PingModal
└── pages/               # Home, MyMachines, Profile
```

## Code Style

### Python
- Type hints on all functions
- Async/await for all I/O
- Ruff for linting and formatting
- Service layer handles business logic (not routes)

### TypeScript
- Strict mode enabled
- No `any` types
- React Query for server state
- Custom hooks for reusable logic

## API Authentication

All endpoints require `X-Telegram-Init-Data` header with Telegram WebApp initData. The backend validates the hash using the bot token.

## Data Models

- **User**: telegram_id, username, block (A-E), coins
- **Machine**: code (A1, B2...), type (washer/dryer), block, qr_code
- **LaundrySession**: user → machine claim with timers
- **CoinTransaction**: audit log for coin changes

## Important Rules

1. **Validate machine exists** before any operation
2. **Check coin balance** before pinging
3. **Never allow negative coins**
4. **Never allow double-claiming** a machine
5. **Soft delete only** for session history
