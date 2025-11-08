"""
Generate 6 months of major USD economic events based on predictable schedules.

Major high-impact events:
- NFP (Non-Farm Payrolls): First Friday of each month, 8:30 AM ET
- FOMC Rate Decision: 8 times per year (every ~6 weeks)
- CPI: Around 13th of each month, 8:30 AM ET  
- PPI: Around 14th of each month, 8:30 AM ET
- Unemployment Claims: Every Thursday, 8:30 AM ET (weekly, but not tracked as "high impact")
"""

from datetime import datetime, timedelta
import json
from pathlib import Path
import calendar


def get_first_friday(year, month):
    """Get the first Friday of a given month."""
    # Find the first day of the month
    first_day = datetime(year, month, 1)
    # Calculate days until Friday (4 = Friday in weekday())
    days_until_friday = (4 - first_day.weekday()) % 7
    if days_until_friday == 0 and first_day.weekday() != 4:
        days_until_friday = 7
    first_friday = first_day + timedelta(days=days_until_friday)
    return first_friday.date()


def generate_nfp_dates(start_date, months=6):
    """Generate NFP (Non-Farm Payrolls) dates for next N months."""
    events = []
    current_date = start_date
    
    for _ in range(months):
        # Move to next month
        if current_date.month == 12:
            year = current_date.year + 1
            month = 1
        else:
            year = current_date.year
            month = current_date.month + 1
        
        # Get first Friday of that month
        nfp_date = get_first_friday(year, month)
        
        events.append({
            'date': nfp_date.strftime('%Y-%m-%d'),
            'time': '8:30am',
            'currency': 'USD',
            'event': 'Non-Farm Employment Change',
            'impact': 'high'
        })
        
        current_date = datetime(year, month, 1).date()
    
    return events


def generate_cpi_dates(start_date, months=6):
    """Generate CPI dates (typically around 13th of each month)."""
    events = []
    current_date = start_date
    
    for _ in range(months):
        # Move to next month
        if current_date.month == 12:
            year = current_date.year + 1
            month = 1
        else:
            year = current_date.year
            month = current_date.month + 1
        
        # CPI is usually around the 13th, but can vary
        # We'll use 13th as default
        cpi_date = datetime(year, month, 13).date()
        
        events.append({
            'date': cpi_date.strftime('%Y-%m-%d'),
            'time': '8:30am',
            'currency': 'USD',
            'event': 'Core CPI m/m',
            'impact': 'high'
        })
        
        current_date = datetime(year, month, 1).date()
    
    return events


def generate_ppi_dates(start_date, months=6):
    """Generate PPI dates (typically around 14th of each month)."""
    events = []
    current_date = start_date
    
    for _ in range(months):
        # Move to next month
        if current_date.month == 12:
            year = current_date.year + 1
            month = 1
        else:
            year = current_date.year
            month = current_date.month + 1
        
        # PPI is usually the day after CPI
        ppi_date = datetime(year, month, 14).date()
        
        events.append({
            'date': ppi_date.strftime('%Y-%m-%d'),
            'time': '8:30am',
            'currency': 'USD',
            'event': 'Core PPI m/m',
            'impact': 'high'
        })
        
        current_date = datetime(year, month, 1).date()
    
    return events


def generate_fomc_dates():
    """
    Generate FOMC meeting dates.
    FOMC meets 8 times per year, roughly every 6 weeks.
    These dates are published in advance - using known 2025-2026 schedule.
    """
    # Known FOMC dates (these are published on federalreserve.gov)
    # Update these periodically from: https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm
    fomc_dates_2025_2026 = [
        '2025-11-06',  # November 2025
        '2025-12-17',  # December 2025
        '2026-01-28',  # January 2026
        '2026-03-17',  # March 2026
        '2026-05-05',  # May 2026
        '2026-06-16',  # June 2026
        '2026-07-28',  # July 2026
        '2026-09-15',  # September 2026
    ]
    
    events = []
    for date_str in fomc_dates_2025_2026:
        # Only include future dates
        if datetime.strptime(date_str, '%Y-%m-%d').date() >= datetime.now().date():
            events.append({
                'date': date_str,
                'time': '2:00pm',
                'currency': 'USD',
                'event': 'FOMC Statement',
                'impact': 'high'
            })
            # Also add press conference 30 min later
            events.append({
                'date': date_str,
                'time': '2:30pm',
                'currency': 'USD',
                'event': 'FOMC Press Conference',
                'impact': 'high'
            })
    
    return events


def main():
    print("="*60)
    print("Generating 6 Months of Major USD Economic Events")
    print("="*60 + "\n")
    
    start_date = datetime.now().date()
    
    # Generate all major events
    print("Generating NFP dates...")
    nfp = generate_nfp_dates(start_date, months=6)
    
    print("Generating CPI dates...")
    cpi = generate_cpi_dates(start_date, months=6)
    
    print("Generating PPI dates...")
    ppi = generate_ppi_dates(start_date, months=6)
    
    print("Adding FOMC dates...")
    fomc = generate_fomc_dates()
    
    # Combine all events
    all_events = nfp + cpi + ppi + fomc
    
    # Sort by date
    all_events.sort(key=lambda x: x['date'])
    
    # Filter out past dates
    today = datetime.now().date().strftime('%Y-%m-%d')
    future_events = [e for e in all_events if e['date'] >= today]
    
    # Save to file
    output_path = Path(__file__).parent.parent / "data" / "economic_calendar.json"
    
    calendar_data = {
        'last_updated': datetime.now().isoformat(),
        'valid_through': future_events[-1]['date'] if future_events else 'N/A',
        'total_events': len(future_events),
        'source': 'Auto-generated from predictable schedules',
        'note': 'NFP, CPI, PPI dates are based on typical schedules. FOMC dates from federalreserve.gov',
        'events': future_events
    }
    
    with open(output_path, 'w') as f:
        json.dump(calendar_data, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"✓ Generated {len(future_events)} events")
    print(f"  Valid through: {future_events[-1]['date']}")
    print(f"  Saved to: {output_path}")
    print(f"{'='*60}\n")
    
    # Print preview
    print("Next 10 events:")
    for event in future_events[:10]:
        print(f"  {event['date']} {event['time']:>8} - {event['event']}")


if __name__ == "__main__":
    main()
