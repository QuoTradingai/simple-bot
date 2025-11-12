"""
Alert Notifications Module
Handles email and SMS notifications for trade alerts, errors, and daily summaries.
Supports multiple email providers (Gmail, Outlook, Yahoo, custom SMTP).
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional
import json
from pathlib import Path
import pytz

logger = logging.getLogger(__name__)


class AlertNotifier:
    """Manages email and SMS alert notifications."""
    
    # Email-to-SMS gateway addresses for major carriers
    CARRIER_GATEWAYS = {
        # Major US Carriers
        'verizon': '@vtext.com',
        'att': '@txt.att.net',
        't-mobile': '@tmomail.net',
        'sprint': '@messaging.sprintpcs.com',
        
        # Popular US Carriers
        'boost': '@sms.myboostmobile.com',
        'cricket': '@mms.cricketwireless.net',
        'metro-pcs': '@mymetropcs.com',
        'us-cellular': '@email.uscc.net',
        'virgin': '@vmobl.com',
        'google-fi': '@msg.fi.google.com',
        'xfinity': '@vtext.com',
        'mint': '@tmomail.net',
        'republic': '@text.republicwireless.com',
        'ting': '@message.ting.com',
        
        # Canadian Carriers
        'rogers': '@pcs.rogers.com',
        'bell': '@txt.bell.ca',
        'telus': '@msg.telus.com'
    }
    
    # Common SMTP server configurations
    SMTP_PROVIDERS = {
        'gmail': {'server': 'smtp.gmail.com', 'port': 587, 'tls': True},
        'outlook': {'server': 'smtp-mail.outlook.com', 'port': 587, 'tls': True},
        'yahoo': {'server': 'smtp.mail.yahoo.com', 'port': 587, 'tls': True},
        'office365': {'server': 'smtp.office365.com', 'port': 587, 'tls': True},
        'custom': {'server': '', 'port': 587, 'tls': True}  # User provides server
    }
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize alert notifier with configuration.
        
        Args:
            config_path: Path to config file containing alert settings
        """
        self.config = self._load_config(config_path)
        self.enabled = self.config.get("alerts_enabled", False)
        
        # Email settings
        self.email = self.config.get("alert_email", "")
        self.email_password = self.config.get("alert_email_password", "")  # Renamed from gmail_app_password
        self.smtp_provider = self.config.get("smtp_provider", "gmail")
        self.smtp_server = self.config.get("smtp_server", "")  # For custom SMTP
        self.smtp_port = self.config.get("smtp_port", 587)
        self.smtp_tls = self.config.get("smtp_tls", True)
        
        # Additional email recipients (optional)
        self.additional_emails = self.config.get("additional_alert_emails", [])
        
        # SMS settings (optional)
        self.phone = self.config.get("alert_phone", "")
        self.carrier = self.config.get("alert_carrier", "verizon")
        
        # Validate configuration
        if self.enabled and not self._is_configured():
            logger.warning("Alerts enabled but not properly configured. Disabling alerts.")
            self.enabled = False
    
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from JSON file."""
        try:
            config_file = Path(config_path)
            if config_file.exists():
                with open(config_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
        return {}
    
    def _is_configured(self) -> bool:
        """Check if alerts are properly configured."""
        # At minimum need email and password
        return bool(self.email and self.email_password)
    
    def _get_smtp_config(self) -> dict:
        """Get SMTP configuration based on provider."""
        if self.smtp_provider == 'custom':
            return {
                'server': self.smtp_server,
                'port': self.smtp_port,
                'tls': self.smtp_tls
            }
        return self.SMTP_PROVIDERS.get(self.smtp_provider, self.SMTP_PROVIDERS['gmail'])
    
    def _send_email(self, subject: str, body: str, to_email: str) -> bool:
        """Send email via configured SMTP server.
        
        Args:
            subject: Email subject line
            body: Email body text
            to_email: Recipient email address
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self._is_configured():
            logger.warning("Cannot send email - alerts not configured")
            return False
        
        try:
            # Get SMTP configuration
            smtp_config = self._get_smtp_config()
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            # Connect to SMTP server
            server = smtplib.SMTP(smtp_config['server'], smtp_config['port'])
            if smtp_config['tls']:
                server.starttls()
            server.login(self.email, self.email_password)
            
            # Send email
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email sent to {to_email}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def _send_sms(self, message: str) -> bool:
        """Send SMS via email-to-SMS gateway.
        
        Args:
            message: SMS message text (keep short, ~160 chars)
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.phone or not self.carrier:
            logger.warning("Cannot send SMS - phone/carrier not configured")
            return False
        
        # Build SMS email address
        gateway = self.CARRIER_GATEWAYS.get(self.carrier)
        if not gateway:
            logger.error(f"Unknown carrier: {self.carrier}")
            return False
        
        sms_email = f"{self.phone}{gateway}"
        
        # Send as email (no subject for SMS)
        return self._send_email("", message, sms_email)
    
    def send_trade_alert(self, trade_type: str, symbol: str, price: float, 
                        contracts: int, side: str = "LONG") -> None:
        """Send alert for trade entry or exit.
        
        Args:
            trade_type: "ENTRY" or "EXIT"
            symbol: Trading symbol (e.g., "ES")
            price: Trade price
            contracts: Number of contracts
            side: "LONG" or "SHORT"
        """
        if not self.enabled:
            return
        
        # Format timestamp (UTC)
        timestamp = datetime.now(pytz.UTC).strftime("%I:%M:%S %p")
        
        # Create messages
        emoji = "🟢" if side == "LONG" else "🔴"
        
        # Email (detailed)
        email_subject = f"Trade Alert: {trade_type} - {symbol}"
        email_body = f"""QuoTrading AI - Trade Alert

{trade_type}: {side} {symbol}
Price: ${price:,.2f}
Contracts: {contracts}
Time: {timestamp}

This is an automated alert from your QuoTrading bot.
"""
        
        # SMS (concise)
        sms_message = f"{emoji} {trade_type}: {side} {symbol} @ {price:.2f} ({contracts}x) - {timestamp}"
        
        # Send to primary email
        self._send_email(email_subject, email_body, self.email)
        
        # Send to additional email addresses
        for additional_email in self.additional_emails:
            if additional_email:
                self._send_email(email_subject, email_body, additional_email)
        
        # Send SMS if configured
        if self.phone:
            self._send_sms(sms_message)
    
    def send_error_alert(self, error_message: str, error_type: str = "Error") -> None:
        """Send alert for bot errors.
        
        Args:
            error_message: Description of the error
            error_type: Type of error (e.g., "Connection Error", "Order Error")
        """
        if not self.enabled:
            return
        
        timestamp = datetime.now(pytz.UTC).strftime("%I:%M:%S %p")
        
        # Email
        email_subject = f"⚠️ Bot Alert: {error_type}"
        email_body = f"""QuoTrading AI - Error Alert

Error Type: {error_type}
Time: {timestamp}

Details:
{error_message}

Please check your bot and logs for more information.
"""
        
        # SMS
        sms_message = f"⚠️ Bot {error_type}: {error_message[:100]}"
        
        # Send to primary email
        self._send_email(email_subject, email_body, self.email)
        
        # Send to additional email addresses
        for additional_email in self.additional_emails:
            if additional_email:
                self._send_email(email_subject, email_body, additional_email)
        
        # Send SMS if configured
        if self.phone:
            self._send_sms(sms_message)
    
    def send_daily_summary(self, trades: int, profit_loss: float, 
                          win_rate: float, max_drawdown: float) -> None:
        """Send end-of-day performance summary.
        
        Args:
            trades: Number of trades executed
            profit_loss: Total P&L for the day
            win_rate: Win rate percentage (0-100)
            max_drawdown: Maximum drawdown for the day
        """
        if not self.enabled:
            return
        
        date = datetime.now(pytz.UTC).strftime("%B %d, %Y")
        
        # Determine emoji based on P&L
        emoji = "✅" if profit_loss >= 0 else "❌"
        
        # Email
        email_subject = f"{emoji} Daily Summary - {date}"
        email_body = f"""QuoTrading AI - Daily Performance Summary

Date: {date}

Performance Metrics:
• Total Trades: {trades}
• Profit/Loss: ${profit_loss:,.2f}
• Win Rate: {win_rate:.1f}%
• Max Drawdown: ${abs(max_drawdown):,.2f}

Keep up the great work!
"""
        
        # SMS
        sms_message = f"{emoji} Daily: {trades} trades, ${profit_loss:,.2f} P&L, {win_rate:.0f}% wins"
        
        # Send to primary email
        self._send_email(email_subject, email_body, self.email)
        
        # Send to additional email addresses
        for additional_email in self.additional_emails:
            if additional_email:
                self._send_email(email_subject, email_body, additional_email)
        
        # Send SMS if configured
        if self.phone:
            self._send_sms(sms_message)
    
    def send_daily_limit_warning(self, current_loss: float, limit: float) -> None:
        """Send warning when approaching daily loss limit.
        
        Args:
            current_loss: Current day's loss
            limit: Daily loss limit
        """
        if not self.enabled:
            return
        
        percent_used = (abs(current_loss) / limit) * 100
        
        email_subject = "⚠️ Daily Loss Limit Warning"
        email_body = f"""QuoTrading AI - Loss Limit Alert

Current Loss: ${abs(current_loss):,.2f}
Daily Limit: ${limit:,.2f}
Limit Used: {percent_used:.1f}%

You are approaching your daily loss limit. Trade carefully.
"""
        
        sms_message = f"⚠️ Loss Warning: ${abs(current_loss):,.2f} of ${limit:,.2f} limit ({percent_used:.0f}%)"
        
        # Send to primary email
        self._send_email(email_subject, email_body, self.email)
        
        # Send to additional email addresses
        for additional_email in self.additional_emails:
            if additional_email:
                self._send_email(email_subject, email_body, additional_email)
        
        # Send SMS if configured
        if self.phone:
            self._send_sms(sms_message)
    
    def send_test_alert(self) -> bool:
        """Send test alert to verify configuration.
        
        Returns:
            True if test successful, False otherwise
        """
        if not self.enabled:
            logger.warning("Cannot send test - alerts not enabled")
            return False
        
        subject = "✅ QuoTrading AI - Test Alert"
        body = f"""This is a test alert from QuoTrading AI.

Your alert notifications are working correctly!

Configuration:
• Email: {self.email}
• Phone: {self.phone if self.phone else 'Not configured'}
• Carrier: {self.carrier if self.phone else 'N/A'}

Timestamp: {datetime.now(pytz.UTC).strftime('%Y-%m-%d %I:%M:%S %p')}
"""
        
        email_success = self._send_email(subject, body, self.email)
        
        if self.phone:
            sms_success = self._send_sms("✅ QuoTrading AI test alert - Your SMS notifications are working!")
            return email_success and sms_success
        
        return email_success


# Example usage
if __name__ == "__main__":
    # Test the notification system
    notifier = AlertNotifier()
    
    if notifier.enabled:
        print("Sending test alert...")
        success = notifier.send_test_alert()
        print(f"Test alert {'sent successfully' if success else 'failed'}")
    else:
        print("Alerts not enabled or configured. Enable in launcher GUI.")


# Global notifier instance for easy import
_notifier_instance = None

def get_notifier() -> AlertNotifier:
    """Get global notifier instance (singleton pattern)."""
    global _notifier_instance
    if _notifier_instance is None:
        _notifier_instance = AlertNotifier()
    return _notifier_instance
