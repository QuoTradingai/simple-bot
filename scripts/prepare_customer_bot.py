"""
Prepare Customer Bot Code
==========================
Updates the customer version bot to work with GUI launcher:
1. Use customer logger (clean logs for PowerShell)
2. Call QuoTrading AI cloud API (not local RL)
3. Handle GUI launch environment
"""

from pathlib import Path
import shutil

CUSTOMER_DIR = Path("../simple-bot-customer")

def update_main_py():
    """Update main.py to use customer logger."""
    print("📝 Updating src/main.py...")
    
    main_file = CUSTOMER_DIR / "src" / "main.py"
    content = main_file.read_text(encoding='utf-8')
    
    # Add customer logger import at top
    if "from .customer_logger import" not in content:
        # Find first import from .
        import_line = "from .config import"
        if import_line in content:
            content = content.replace(
                import_line,
                f"from .customer_logger import log_status, log_trade, log_signal, log_risk, log_performance\n{import_line}"
            )
    
    # Replace verbose logging with customer helpers
    replacements = {
        'logger.info("Starting QuoTrading AI Bot")': 'log_status("QuoTrading AI Bot starting...")',
        'logger.info("Bot initialized successfully")': 'log_status("Bot initialized successfully")',
        'logger.info("Shutting down bot")': 'log_status("Shutting down bot")',
        'logger.error(': 'logging.error(',  # Keep errors as-is
        'logger.warning(': 'logging.warning(',  # Keep warnings as-is
    }
    
    for old, new in replacements.items():
        content = content.replace(old, new)
    
    main_file.write_text(content, encoding='utf-8')
    print("  ✓ main.py updated with customer logger")


def update_vwap_bounce_bot():
    """Update vwap_bounce_bot.py to use customer logger."""
    print("📝 Updating src/vwap_bounce_bot.py...")
    
    bot_file = CUSTOMER_DIR / "src" / "vwap_bounce_bot.py"
    content = bot_file.read_text(encoding='utf-8')
    
    # Add customer logger import
    if "from .customer_logger import" not in content:
        # Add after other imports
        import_section = "import logging\nimport asyncio"
        if import_section in content:
            content = content.replace(
                import_section,
                f"{import_section}\nfrom .customer_logger import log_status, log_trade, log_signal, log_risk, log_performance"
            )
    
    # Replace verbose logs with customer logger calls
    # These are the main log points customers should see
    replacements = {
        # Entry/Exit logs
        'self.logger.info(f"ENTRY': 'log_trade(f"ENTRY',
        'self.logger.info(f"EXIT': 'log_trade(f"EXIT',
        'self.logger.info(f"[TRADE]': 'log_trade(f"',
        
        # Signal logs  
        'self.logger.info(f"[SIGNAL]': 'log_signal(f"',
        'self.logger.info(f"Signal detected': 'log_signal(f"Signal detected',
        
        # Status logs
        'self.logger.info(f"[STATUS]': 'log_status(f"',
        'self.logger.info(f"Session': 'log_status(f"Session',
        'self.logger.info(f"Flattening': 'log_status(f"Flattening',
        
        # Risk logs
        'self.logger.info(f"[RISK]': 'log_risk(f"',
        'self.logger.warning(f"Daily limit': 'log_risk(f"WARNING: Daily limit',
        
        # Performance logs
        'self.logger.info(f"[PERFORMANCE]': 'log_performance(f"',
        'self.logger.info(f"Daily P&L': 'log_performance(f"Daily P&L',
    }
    
    for old, new in replacements.items():
        content = content.replace(old, new)
    
    # Remove verbose debug logs (just comment them out)
    # Keep self.logger for errors/warnings that aren't customer-facing
    
    bot_file.write_text(content, encoding='utf-8')
    print("  ✓ vwap_bounce_bot.py updated with customer logger")


def update_signal_confidence():
    """Update signal_confidence.py to use customer logger (keep local RL for now)."""
    print("📝 Updating src/signal_confidence.py...")
    
    signal_file = CUSTOMER_DIR / "src" / "signal_confidence.py"
    content = signal_file.read_text(encoding='utf-8')
    
    # Add customer logger import
    if "from .customer_logger import" not in content:
        # Add after other imports
        import_section = "import logging"
        if import_section in content and "from .customer_logger" not in content:
            content = content.replace(
                "import logging\n",
                "import logging\nfrom .customer_logger import log_signal, log_status\n"
            )
    
    # Replace verbose logs with customer logger (keep RL logic intact)
    replacements = {
        'logger.info("Signal confidence': 'log_signal("Signal confidence',
        'logger.info(f"Signal confidence': 'log_signal(f"Signal confidence',
        'self.logger.info("Confidence': 'log_signal("Confidence',
        'self.logger.info(f"Confidence': 'log_signal(f"Confidence',
    }
    
    for old, new in replacements.items():
        content = content.replace(old, new)
    
    signal_file.write_text(content, encoding='utf-8')
    print("  ✓ signal_confidence.py updated (uses customer logger, keeps local RL)")


def update_run_py():
    """Update run.py to ensure proper working directory."""
    print("📝 Updating run.py...")
    
    run_file = CUSTOMER_DIR / "run.py"
    content = '''#!/usr/bin/env python3
"""
QuoTrading AI - Launcher
========================
Main entry point for customer bot.
"""

import os
import sys
from pathlib import Path

# Ensure we're in the right directory (important for GUI launch)
os.chdir(Path(__file__).parent)

# Run the bot
from src.main import main

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\\n[STATUS] Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\\n[ERROR] Bot crashed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
'''
    
    run_file.write_text(content, encoding='utf-8')
    print("  ✓ run.py updated (ensures correct working directory)")


def main():
    """Update customer bot code."""
    print("=" * 60)
    print("Preparing Customer Bot for GUI Launcher")
    print("=" * 60)
    
    if not CUSTOMER_DIR.exists():
        print(f"❌ Error: {CUSTOMER_DIR} not found!")
        print("Run build_customer_version.py first!")
        return
    
    # Update all files
    update_run_py()
    update_main_py()
    update_vwap_bounce_bot()
    update_signal_confidence()
    
    print("\n" + "=" * 60)
    print("✅ Customer bot prepared!")
    print("=" * 60)
    print("\nUpdates made:")
    print("  ✓ run.py - Proper working directory handling")
    print("  ✓ main.py - Customer logger integration")
    print("  ✓ vwap_bounce_bot.py - Clean customer-friendly logs")
    print("  ✓ signal_confidence.py - Customer logger (keeps local RL)")
    print("\nBot ready for GUI launcher!")
    print("  - RL models stay LOCAL (until you build cloud API)")
    print("  - Logs are CLEAN (customer-friendly)")
    print("  - Works from PowerShell terminal")
    print("\nNext: Test with GUI launcher!")
    print("  cd ..\\simple-bot-customer")
    print("  python QuoTrading_Launcher.py")


if __name__ == "__main__":
    main()
