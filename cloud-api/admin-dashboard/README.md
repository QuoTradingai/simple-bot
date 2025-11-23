# Admin Dashboard - User Guide

## Overview
The QuoTrading Admin Dashboard provides a comprehensive view of all users, trading activity, revenue metrics, and system health.

## Features

### 1. Dashboard Stats (Top Bar)
- **Total Users**: Total number of registered users
- **Active Users**: Users with active licenses
- **Expiring Soon**: Users whose licenses expire within 7 days
- **Online Now**: Users active in the last 5 minutes
- **MRR (Monthly Recurring Revenue)**: Current monthly revenue from active subscriptions
- **API Calls (24h)**: Total API calls in the last 24 hours
- **Total Trades**: All-time total trades executed
- **Total P&L**: Cumulative profit/loss across all users

### 2. Users Tab
View and manage all registered users:
- **Search**: Filter users by account ID or email
- **Status Filters**: View Active users or all users
- **Actions**:
  - **Suspend**: Temporarily disable a user's license
  - **Activate**: Re-enable a suspended license
  - **Extend**: Add days to a license expiration
  - **Details**: View detailed user information, activity logs, and trading stats

**Color Coding**:
- Red background: License expired or expires in 0-3 days
- Orange background: License expires in 4-7 days
- Yellow background: License expires in 8-14 days

### 3. Activity Tab
Real-time API activity feed showing:
- Timestamp of each request
- User account ID
- API endpoint accessed
- HTTP method and status code
- Response time
- IP address

### 4. Online Users Tab
Shows users currently active (within last 5 minutes):
- Account ID
- Email
- License type
- Last active timestamp
- Time ago

### 5. RL Brain Tab
Monitor the collective reinforcement learning system:
- **Total Experiences**: Cumulative trading experiences across all users
- **Real-time Feed**: Live stream of trade decisions and outcomes
- **Filters**: View winning trades, losing trades, or all
- **Metrics Displayed**:
  - Symbol, side (long/short)
  - Technical indicators (RSI, VWAP distance, ATR, volume ratio)
  - Trade outcome (reward/P&L)
  - Duration

### 6. Reports Tab
Generate detailed analytics reports:

#### User Activity Report
- Filter by date range, license type, and status
- View signup dates, last active times, API usage
- Track trades and P&L per user

#### Revenue Analysis Report
- View by month/year
- **Metrics**:
  - New subscriptions and revenue
  - Monthly Recurring Revenue (MRR)
  - Average Revenue Per User (ARPU)
  - Cancellations and lost revenue
  - Churn rate

#### Trading Performance Report
- Filter by date range and symbol
- **Metrics**:
  - Total trades and win rate
  - Total P&L
  - Average trade duration
  - Best and worst performing days

#### Retention & Churn Report
- Active users vs. expired
- Retention and churn rates
- Average subscription length
- Lifetime value (LTV)
- Cohort analysis by signup month

## Revenue Tracking

### How Revenue is Calculated

1. **Monthly Recurring Revenue (MRR)**:
   - Monthly licenses: $49.99/month each
   - Annual licenses: $499.99/year (counted as $41.67/month)
   - Trial/Beta: $0
   - Formula: `MRR = (Monthly licenses × $49.99) + (Annual licenses × $41.67)`

2. **Annual Recurring Revenue (ARR)**:
   - Formula: `ARR = MRR × 12`

3. **Data Source**:
   - Revenue is calculated from the `users` table in PostgreSQL
   - Based on `license_type` and `license_status = 'ACTIVE'`
   - **No direct Stripe integration for dashboard stats**

### Stripe Integration

The system has Stripe payment integration for:
- **Checkout**: Users purchase subscriptions via Stripe
- **Webhooks**: Stripe sends events for successful payments, renewals, and failures
- **License Creation**: When payment succeeds, a license is automatically created
- **Customer Portal**: Users can manage subscriptions through Stripe

**Important**: The dashboard shows revenue **based on active licenses in the database**, not real-time Stripe transactions. To see actual payment data:
1. Log into your Stripe Dashboard at https://dashboard.stripe.com
2. View "Payments" for transaction history
3. View "Subscriptions" for recurring revenue
4. View "Revenue" for detailed financial reports

The admin dashboard MRR is an **estimate** based on license types. For accurate financial reporting, always refer to your Stripe dashboard.

### Stripe Environment Variables

Make sure these are configured in your Azure App Settings or environment:
```
STRIPE_API_KEY=sk_live_... or sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

## System Health Indicators

Top-right corner shows:
- **DB**: Database response time (should be < 100ms)
- **RL**: RL engine status and experience count

**Status Colors**:
- Green (healthy): System operating normally
- Yellow (degraded): Performance issues detected
- Red (unhealthy): System errors or offline

## Adding Users Manually

Click "+ Add User" button:
1. Enter Account ID (unique identifier)
2. Enter Email address
3. Select License Type:
   - Trial: 7 days
   - Beta: 90 days
   - Monthly: 30 days
   - Annual: 365 days
4. Optionally modify days valid
5. Add notes if needed

A license key is automatically generated and displayed after creation.

## Export Data

Click "📥 Export" to download:
- Users tab: CSV with all user data
- Reports: CSV of the current report (click "Export to CSV" after generating)

## Auto-Refresh

The dashboard automatically refreshes every 30 seconds to show real-time data.

## Access Control

The dashboard requires the admin key: `ADMIN-DEV-KEY-2024`

This is hardcoded in:
- HTML: `const ADMIN_KEY = 'ADMIN-DEV-KEY-2024';`
- Backend: `ADMIN_API_KEY` environment variable

Change this in production for security.

## Troubleshooting

**Issue**: "Database connection failed"
- Check PostgreSQL is running
- Verify DB credentials in Azure App Settings

**Issue**: "No data showing"
- Verify API endpoints are accessible
- Check browser console for errors
- Ensure CORS is configured if hosting separately

**Issue**: "Revenue shows $0"
- Check that users have `license_status = 'ACTIVE'`
- Verify `license_type` is set correctly
- Confirm database connection is working

**Issue**: "Stripe payments not creating licenses"
- Check webhook endpoint is configured in Stripe
- Verify `STRIPE_WEBHOOK_SECRET` is correct
- Check Flask API logs for webhook errors

## Technical Details

**Frontend**: Pure HTML/CSS/JavaScript
- No build process required
- Chart.js for future visualizations
- Google Sheets-inspired design

**Backend**: Flask API (Python)
- PostgreSQL database
- Endpoints: `/api/admin/*`
- Authentication: `license_key` or `admin_key` parameter

**Database Tables**:
- `users`: License and subscription data
- `api_logs`: API usage tracking
- `rl_experiences`: Trading decisions and outcomes
- `trade_history`: Historical trade data

## Future Enhancements

Planned features:
- Interactive charts for revenue trends
- Email notifications for expiring licenses
- Bulk user management
- Advanced filtering and search
- Dashboard customization
- Real-time Stripe sync
