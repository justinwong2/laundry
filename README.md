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
                        INTERNET
                            |
            +---------------+---------------+
            |                               |
            v                               v
    +---------------+               +---------------+
    |  CloudFront   |               |     Nginx     |
    |    (CDN)      |               |   (HTTPS)     |
    +-------+-------+               +-------+-------+
            |                               |
            v                               v
    +---------------+               +---------------+
    |   S3 Bucket   |               |   Uvicorn     |
    | (React App)   |               |  (FastAPI)    |
    +---------------+               +-------+-------+
                                            |
                                            v
                                    +---------------+
                                    |    SQLite     |
                                    +---------------+
```

| Component | Service | URL |
|-----------|---------|-----|
| Frontend | S3 + CloudFront | `https://dsr52s967fixv.cloudfront.net` |
| Backend API | EC2 + Nginx | `https://sheares-laundry-api.mooo.com` |

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

## Deployment

### Frontend (S3 + CloudFront)

```bash
cd frontend
npm run build
aws s3 sync dist/ s3://sheares-laundry-bot-frontend --delete
aws cloudfront create-invalidation --distribution-id DISTRIBUTION_ID --paths "/*"
```

### Backend (EC2)

```bash
# SSH into EC2
ssh -i "laundry-bot-key.pem" ubuntu@EC2_IP

# Pull and restart
cd ~/laundry
git pull
sudo systemctl restart laundrybot
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

## Coin Economy

| Action | Coins |
|--------|-------|
| Claim machine | +1 |
| Release machine | +2 |
| Ping another user | -3 |
| Being pinged | +1 |

New users start with 10 coins.
