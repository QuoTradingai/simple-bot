# GUI Navigation Flow Documentation

## Overview
The QuoTrading Launcher has a 3-screen progressive onboarding flow with proper navigation buttons on each screen.

## Screen Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     Screen 0: Login                         │
│           Username, Password & API Key Entry                │
│                                                              │
│  • Username field                                            │
│  • Password field (hidden)                                   │
│  • API Key field (hidden)                                    │
│  • [NEXT →] button                                           │
└──────────────────────────────┬──────────────────────────────┘
                               │ NEXT
                               ▼
┌─────────────────────────────────────────────────────────────┐
│               Screen 1: Broker Setup                        │
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
│             Screen 2: Trading Settings                      │
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
- Validates API key is not empty
- Makes cloud validation call with username, password, and API key
- On success, saves credentials and proceeds to broker screen
- On failure, shows error message

### Screen 1 → Screen 2
- Validates broker selection
- Validates API token is not empty
- Validates username is not empty
- Makes broker validation call
- On success, saves credentials and proceeds to trading screen
- On failure, shows error message

### Screen 2 → Start Bot
- Validates at least one trading symbol is selected
- Validates account size is a positive number
- Validates daily loss limit is a positive number
- Creates .env file with all settings
- Launches the trading bot
- Closes the launcher GUI

## Key Features

1. **Simplified Flow**: Only 3 screens for a streamlined setup process
2. **Clear Navigation**: Each screen has visible navigation buttons
3. **Data Persistence**: All entered data is saved to config.json
4. **Validation Feedback**: Clear error messages guide the user
5. **Admin Bypass**: Admin master key (QUOTRADING_ADMIN_MASTER_2025) skips validation
6. **Back Navigation**: Users can go back to correct mistakes without losing data

## Changes Made

- Simplified to 3-screen flow (from 5 screens)
- Removed separate API key screen - combined with username/password on Screen 0
- Removed QuoTrading Account screen entirely
- Screen 1 is now Broker Setup (was Screen 3)
- Screen 2 is now Trading Settings (was Screen 4)
- Updated all navigation and validation flow
- Simplified .env file generation
