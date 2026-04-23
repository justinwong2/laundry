# Laundry Bot

A Telegram Mini App + Bot for shared laundry room management with gamification.

## Features

- **Machine Status**: Visual grid showing all washers and dryers with real-time status
- **Claim & Release**: Claim machines when starting laundry, release when done
- **Reminders**: Automatic notifications at T-5min and when done
- **Ping System**: Nudge others to collect their finished laundry
- **Gamification**: Earn coins for good behavior, spend to ping

## Architecture

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
```

## Project Structure

```
laundry/
├── backend/               # Python FastAPI + Bot
│   ├── src/laundry/
│   │   ├── api/          # REST API endpoints
│   │   ├── bot/          # Telegram bot handlers
│   │   ├── models/       # SQLAlchemy models
│   │   ├── services/     # Business logic
│   │   └── db/           # Database setup
│   └── tests/
└── frontend/              # React + Vite Mini App
    └── src/
        ├── api/          # API client
        ├── components/   # React components
        ├── hooks/        # Custom hooks
        └── pages/        # Page components
```

## Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- Telegram Bot Token (from @BotFather)

### Backend

```bash
cd backend

# Create virtual environment
uv venv
# Windows:
.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
uv pip install -e ".[dev]"

# Copy environment template
cp .env.example .env
# Edit .env with your bot token

# Seed database with Block E machines
python -m laundry.db.seed

# Run server
uvicorn laundry.main:app --reload
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Copy environment template
cp .env.example .env
# Edit .env with your API URL

# Run dev server
npm run dev
```

### QR Codes

Generate QR codes for machines:

```bash
cd backend
python scripts/generate_qr.py https://your-app.vercel.app
```

## Development

### Backend

```bash
# Format
ruff format src/

# Lint
ruff check src/

# Test
pytest
```

### Frontend

```bash
# Lint
npm run lint

# Build
npm run build
```

## Deployment

### Backend
- Deploy to any Python hosting (Railway, Render, etc.)
- Set environment variables
- Run `python -m laundry.db.seed` to initialize machines

### Frontend
- Deploy to Vercel/Netlify
- Set `VITE_API_URL` to your backend URL
- Configure as Telegram Web App in BotFather

## Coin Economy

| Action | Coins |
|--------|-------|
| Claim machine | +1 |
| Release machine | +2 |
| Ping another user | -3 |
| Being pinged | +1 |

New users start with 10 coins.
