# Laundry Bot - Task List

## Phase 0: Developer Setup

- [x] **0.1** Add dev auth bypass for Postman/curl testing
  - Add `debug: bool = False` to `config.py`
  - Add dev bypass in `auth.py` (format: `dev:{user_id}`)
  - Update `.env.example` with `DEBUG=false`
  - Files: `config.py`, `api/auth.py`, `.env.example`
  - **Security**: Bypass only works when `DEBUG=true`

## Phase 1: Backend Core Fixes

- [x] **1.1** Fix done notification spam
  - Add `done_notification_sent` flag to LaundrySession model
  - Update `check_done_notifications()` to filter and set flag
  - Files: `models/session.py`, `services/reminder_service.py`

- [x] **1.2** Add username to machine status responses
  - Join User table when fetching machine status
  - Include username in session schema
  - Files: `services/machine_service.py`, `api/schemas.py`

## Phase 2: Bot Integration

- [ ] **2.1** Integrate bot + scheduler into FastAPI lifespan
  - Start bot polling in lifespan startup
  - Start APScheduler in lifespan startup
  - Graceful shutdown on app stop
  - Files: `main.py`

---
**CHECKPOINT 1**: Backend complete - test bot commands and API

---

## Phase 3: Frontend Polish

- [ ] **3.1** Handle QR deep link parameter
  - Parse `?machine=X` from URL
  - Auto-select machine and open ClaimModal
  - Files: `App.tsx` or `Home.tsx`

- [ ] **3.2** Dynamic block display in header
  - Replace hardcoded "Block E" with user's block
  - Files: `pages/Home.tsx`

---
**CHECKPOINT 2**: Frontend complete - test full user flow

---

## Phase 4: Testing

- [ ] **4.1** Backend API tests
  - Test all CRUD endpoints
  - Test authentication
  - Test error cases
  - Files: `tests/test_api.py` (created - has auth bypass tests)

- [ ] **4.2** Backend service tests
  - Test business logic
  - Test coin operations
  - Test validation rules
  - Files: `tests/test_services.py` (created - has notification tests)

## Phase 5: Deployment Prep

- [ ] **5.1** Generate QR codes for Block E
  - Run `scripts/generate_qr.py`
  - Verify 16 codes generated

- [ ] **5.2** Verify database seeding
  - Run `python -m laundry.db.seed`
  - Confirm 16 machines created

---
**CHECKPOINT 3**: Launch ready - all tests passing, QR codes ready
