# GUI Navigation Flow Documentation

## Overview
The QuoTrading Launcher now has a 5-screen progressive onboarding flow with proper navigation buttons on each screen.

## Screen Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     Screen 0: Login                         │
│                 Username & Password Entry                    │
│                                                              │
│  • Username field                                            │
│  • Password field (hidden)                                   │
│  • [NEXT →] button                                           │
└──────────────────────────────┬──────────────────────────────┘
                               │ NEXT
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   Screen 1: API Key                         │
│                    API Key Entry                             │
│                                                              │
│  • API Key field (hidden)                                    │
│  • [← BACK] button                                           │
│  • [NEXT →] button                                           │
└──────────────────────────────┬──────────────────────────────┘
                               │ NEXT
                               ▼
┌─────────────────────────────────────────────────────────────┐
│              Screen 2: QuoTrading Account                   │
│             Email + API Key Validation                       │
│                                                              │
│  • Email field                                               │
│  • QuoTrading API Key field (hidden)                         │
│  • [← BACK] button                                           │
│  • [NEXT →] button                                           │
└──────────────────────────────┬──────────────────────────────┘
                               │ NEXT
                               ▼
┌─────────────────────────────────────────────────────────────┐
│               Screen 3: Broker Setup                        │
│          Prop Firm / Live Broker Selection                   │
│                                                              │
│  • Account Type selection (Prop Firm / Live Broker)          │
│  • Broker dropdown                                           │
│  • API Token field (hidden)                                  │
│  • Username/Email field                                      │
│  • [← BACK] button                                           │
│  • [NEXT →] button                                           │
└──────────────────────────────┬──────────────────────────────┘
                               │ NEXT
                               ▼
┌─────────────────────────────────────────────────────────────┐
│             Screen 4: Trading Settings                      │
│          Symbol Selection & Risk Parameters                  │
│                                                              │
│  • Trading symbols (checkboxes)                              │
│  • Account size                                              │
│  • Risk per trade (%)                                        │
│  • Daily loss limit                                          │
│  • Max contracts                                             │
│  • Max trades per day                                        │
│  • [← BACK] button                                           │
│  • [START BOT →] button                                      │
└─────────────────────────────────────────────────────────────┘
```

## Navigation Rules

### Forward Navigation
- Each screen has a "NEXT" button (except the last screen which has "START BOT")
- Clicking "NEXT" validates the current screen's inputs
- If validation passes, the user proceeds to the next screen
- If validation fails, an error message is shown

### Backward Navigation
- All screens except Screen 0 have a "BACK" button
- Clicking "BACK" returns to the previous screen
- No validation is performed when going back
- Previously entered data is preserved

## Validation Flow

### Screen 0 → Screen 1
- Validates username is not empty
- Validates password is not empty
- Saves username and password to config

### Screen 1 → Screen 2
- Validates API key is not empty
- Makes cloud validation call with username, password, and API key
- On success, saves credentials and proceeds
- On failure, shows error message

### Screen 2 → Screen 3
- Validates email format
- Validates QuoTrading API key length
- Makes API validation call
- On success, saves credentials and proceeds
- On failure, shows error message

### Screen 3 → Screen 4
- Validates broker selection
- Validates API token is not empty
- Validates username is not empty
- Makes broker validation call
- On success, saves credentials and proceeds
- On failure, shows error message

### Screen 4 → Start Bot
- Validates at least one trading symbol is selected
- Validates account size is a positive number
- Validates daily loss limit is a positive number
- Creates .env file with all settings
- Launches the trading bot
- Closes the launcher GUI

## Key Features

1. **Progressive Disclosure**: Information is collected across multiple screens, reducing cognitive load
2. **Clear Navigation**: Each screen has visible navigation buttons
3. **Data Persistence**: All entered data is saved to config.json
4. **Validation Feedback**: Clear error messages guide the user
5. **Admin Bypass**: Admin master key (QUOTRADING_ADMIN_MASTER_2025) skips validation
6. **Back Navigation**: Users can go back to correct mistakes without losing data

## Changes Made

- Split the original Screen 0 (username/password/API key) into two screens:
  - New Screen 0: Username & Password only
  - New Screen 1: API Key only
- Updated all screen numbers:
  - Screen 1 (QuoTrading) → Screen 2
  - Screen 2 (Broker) → Screen 3
  - Screen 3 (Trading) → Screen 4
- Added back button to Screen 1 (API Key)
- Updated back button on Screen 2 to go to Screen 1 instead of Screen 0
- Added validation flow between Screen 0 and Screen 1
- Updated documentation to reflect new flow
