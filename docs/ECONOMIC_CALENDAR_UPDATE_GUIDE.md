# Economic Calendar Update Guide

## Overview
The bot uses `data/economic_calendar.json` to avoid trading during high-impact news events.

## Update Schedule
Update this file **every 6 months** (January and July).

## How to Update

### Method 1: Manual Update (Recommended)
1. Go to https://www.forexfactory.com/calendar
2. Filter for:
   - **Currency:** USD
   - **Impact:** High (red icon)
   - **Time Range:** Next 6 months
3. Add events to `data/economic_calendar.json` in this format:
   ```json
   {
     "date": "2026-06-05",
     "time": "08:30",
     "currency": "USD",
     "event": "Nonfarm Payrolls (NFP)",
     "impact": "high"
   }
   ```

### Method 2: Copy from Web Scraper (if available)
If you have access to a tool that can scrape Forex Factory:
1. Run: `python scripts/scrape_forex_calendar.py`
2. The script will attempt to fetch events automatically
3. Note: Forex Factory may block automated requests

## Key Events to Include
- **NFP (Nonfarm Payrolls)** - First Friday of every month at 8:30 AM ET
- **FOMC Meetings** - 8 times per year (check Fed calendar)
- **CPI (Consumer Price Index)** - Monthly around 13th at 8:30 AM ET
- **PPI (Producer Price Index)** - Monthly around 14th at 8:30 AM ET
- **Fed Chair Speeches** - Check Fed calendar
- **GDP Reports** - Quarterly

## File Format
```json
{
  "last_updated": "2025-11-07 00:00:00",
  "valid_through": "2026-05-07",
  "total_events": 24,
  "events": [
    {
      "date": "YYYY-MM-DD",
      "time": "HH:MM",
      "currency": "USD",
      "event": "Event Name",
      "impact": "high"
    }
  ]
}
```

## Time Format
- Use 24-hour format (military time)
- Eastern Time (ET)
- Examples:
  - 8:30 AM = "08:30"
  - 2:00 PM = "14:00"

## Validation
After updating, run the bot to ensure it loads the calendar without errors.

## Automation Note
Forex Factory has anti-scraping protection, so manual updates are currently the most reliable method.
