# Admin Dashboard Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    ADMIN DASHBOARD (HTML/JS)                    │
│  Location: cloud-api/admin-dashboard/index.html                 │
│                                                                  │
│  Features:                                                       │
│  • Users Management Tab                                         │
│  • Activity Monitoring Tab                                      │
│  • Online Users Tab                                             │
│  • RL Brain Tab                                                 │
│  • Reports & Analytics Tab                                      │
│  • Real-time Stats Bar (incl. MRR)                             │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     │ HTTP Requests (Admin Key: ADMIN-DEV-KEY-2024)
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│               FLASK API (Python Backend)                        │
│  Location: cloud-api/flask-api/app.py                           │
│                                                                  │
│  Admin Endpoints:                                               │
│  • /api/admin/dashboard-stats    → Main stats + MRR/ARR        │
│  • /api/admin/users               → List all users              │
│  • /api/admin/user/<id>           → User details                │
│  • /api/admin/recent-activity     → API activity log            │
│  • /api/admin/online-users        → Currently active            │
│  • /api/admin/rl-experiences      → RL trade feed               │
│  • /api/admin/system-health       → DB & RL status              │
│  • /api/admin/reports/*           → Generate reports            │
│  • /api/admin/add-user            → Create new license          │
│  • /api/admin/suspend-user/<id>   → Suspend license             │
│  • /api/admin/activate-user/<id>  → Activate license            │
│  • /api/admin/extend-license/<id> → Extend expiration           │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     │ SQL Queries
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│          POSTGRESQL DATABASE (Azure)                            │
│  Location: quotrading-db.postgres.database.azure.com            │
│                                                                  │
│  Tables:                                                         │
│  ┌──────────────────────────────────────────────────┐           │
│  │ users                                             │           │
│  │  - id (PK)                                        │           │
│  │  - license_key (UNIQUE)                           │           │
│  │  - email                                          │           │
│  │  - license_type (MONTHLY/ANNUAL/TRIAL/BETA)       │           │
│  │  - license_status (ACTIVE/SUSPENDED/EXPIRED)      │           │
│  │  - license_expiration                             │           │
│  │  - stripe_customer_id (NEW)                       │           │
│  │  - notes (NEW)                                    │           │
│  │  - created_at                                     │           │
│  │  - updated_at                                     │           │
│  └──────────────────────────────────────────────────┘           │
│                                                                  │
│  ┌──────────────────────────────────────────────────┐           │
│  │ api_logs                                          │           │
│  │  - id (PK)                                        │           │
│  │  - license_key                                    │           │
│  │  - endpoint                                       │           │
│  │  - request_data (JSONB)                           │           │
│  │  - response_data (JSONB)                          │           │
│  │  - status_code                                    │           │
│  │  - created_at                                     │           │
│  └──────────────────────────────────────────────────┘           │
│                                                                  │
│  ┌──────────────────────────────────────────────────┐           │
│  │ rl_experiences                                    │           │
│  │  - id (PK)                                        │           │
│  │  - license_key                                    │           │
│  │  - symbol                                         │           │
│  │  - rsi, vwap_distance, atr, volume_ratio          │           │
│  │  - side, regime                                   │           │
│  │  - took_trade (BOOLEAN)                           │           │
│  │  - pnl                                            │           │
│  │  - duration_minutes                               │           │
│  │  - timestamp                                      │           │
│  │  - created_at                                     │           │
│  └──────────────────────────────────────────────────┘           │
│                                                                  │
│  ┌──────────────────────────────────────────────────┐           │
│  │ trade_history                                     │           │
│  │  - id (PK)                                        │           │
│  │  - license_key                                    │           │
│  │  - symbol, signal_type                            │           │
│  │  - entry_price, exit_price, pnl                   │           │
│  │  - confidence, regime                             │           │
│  │  - created_at                                     │           │
│  └──────────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────────┘
                     ▲
                     │
                     │ Webhooks (on payment events)
                     │
┌─────────────────────────────────────────────────────────────────┐
│                  STRIPE (Payment Processing)                    │
│                                                                  │
│  Integration Points:                                            │
│  • /api/stripe/create-checkout    → Start subscription          │
│  • /api/stripe/webhook            → Receive payment events      │
│  • /api/stripe/customer-portal    → Manage subscription         │
│                                                                  │
│  Events Handled:                                                │
│  • checkout.session.completed     → Create license              │
│  • invoice.payment_succeeded      → Renew license               │
│  • invoice.payment_failed         → Suspend license             │
│                                                                  │
│  ⚠️ Note: Dashboard revenue is ESTIMATED from database          │
│     For actual revenue, check Stripe Dashboard directly         │
└─────────────────────────────────────────────────────────────────┘
```

## Revenue Flow

```
User Purchase → Stripe Payment → Webhook Event → Create/Update User in DB
                                                         ↓
                                    Dashboard reads users table
                                                         ↓
                                    Calculates MRR/ARR from license_type
                                                         ↓
                                            Displays on dashboard

MONTHLY: $49.99/month
ANNUAL: $499.99/year (shown as $41.67/month MRR)
TRIAL/BETA: $0

MRR = (Monthly licenses × $49.99) + (Annual licenses × $41.67)
ARR = MRR × 12
```

## Data Flow for Dashboard Stats

```
Dashboard → API Request
              ↓
         /api/admin/dashboard-stats
              ↓
         Query users table
              ↓
    ┌─────────────────────────┐
    │ Count total users       │
    │ Count active (status)   │
    │ Count by license_type   │
    │ Calculate MRR           │
    └─────────────────────────┘
              ↓
         Query api_logs
              ↓
    ┌─────────────────────────┐
    │ Count calls (24h)       │
    │ Find online users       │
    │ (< 5 min ago)           │
    └─────────────────────────┘
              ↓
         Query rl_experiences
              ↓
    ┌─────────────────────────┐
    │ Count total trades      │
    │ Sum P&L                 │
    │ Count experiences       │
    └─────────────────────────┘
              ↓
         Return JSON
              ↓
         Dashboard displays
```

## Authentication Flow

```
User opens dashboard → JavaScript loads
                            ↓
                    const ADMIN_KEY = 'ADMIN-DEV-KEY-2024'
                            ↓
                    All API requests include:
                    ?license_key=ADMIN-DEV-KEY-2024
                    or
                    ?admin_key=ADMIN-DEV-KEY-2024
                            ↓
                    Flask validates:
                    if admin_key != ADMIN_API_KEY:
                        return 401 Unauthorized
                            ↓
                    Process request
```

## Auto-Refresh Mechanism

```
Page Load → Initialize
              ↓
         loadDashboard()
              ↓
    Load all tabs data in parallel:
    • loadStats()
    • loadUsers()
    • loadActivity()
    • loadOnlineUsers()
    • loadRLStats()
              ↓
         Display data
              ↓
    Set interval (30 seconds)
              ↓
         Repeat loadDashboard()
```

## Tab Structure

```
Header (Stats Bar)
├── Total Users
├── Active
├── Expiring Soon
├── Online Now
├── MRR ← NEW
├── API Calls (24h)
├── Total Trades
└── Total P&L

Tabs
├── Users Tab
│   ├── Search/Filter
│   ├── Users Table
│   └── Actions (Suspend/Activate/Extend/Details)
│
├── Activity Tab
│   └── Recent API Calls Table
│
├── Online Users Tab
│   └── Currently Active Users Table
│
├── RL Brain Tab
│   ├── Experience Count Card
│   ├── Trade Feed Table
│   └── Win/Loss Filters
│
└── Reports Tab
    ├── Configuration Panel
    ├── User Activity Report
    ├── Revenue Analysis Report
    ├── Trading Performance Report
    └── Retention & Churn Report
```

## File Structure

```
simple-bot/
├── cloud-api/
│   ├── admin-dashboard/
│   │   ├── index.html           ← Main dashboard (99KB)
│   │   ├── README.md            ← User guide
│   │   └── TESTING.md           ← Testing documentation
│   │
│   └── flask-api/
│       ├── app.py               ← Backend API (114KB, 44 endpoints)
│       ├── rl_decision_engine.py
│       ├── init_db.py
│       └── migrations/
│           └── add_missing_columns.sql  ← NEW columns
│
└── deployment/
    └── db_init.sql              ← Initial schema
```

## Key Fixes Made

1. ✅ JavaScript: `ADMIN_API_KEY` → `ADMIN_KEY`
2. ✅ JavaScript: `API_KEY` → `ADMIN_KEY`
3. ✅ Backend: Added `DB_PORT` configuration
4. ✅ Backend: `FROM licenses` → `FROM users` (18 instances)
5. ✅ Backend: `license_expires` → `license_expiration` (all instances)
6. ✅ Backend: Added MRR/ARR to dashboard-stats endpoint
7. ✅ Frontend: Added MRR display to stats bar
8. ✅ Database: Migration for stripe_customer_id and notes columns
9. ✅ Documentation: Complete user guide and testing docs

## Security Considerations

- Admin key is static (consider environment variable)
- No rate limiting on admin endpoints
- No audit log for admin actions
- Direct database access (no ORM)
- SQL injection protection via parameterized queries
- CORS must be configured for cross-origin access
