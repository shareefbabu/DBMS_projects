"""
Email Service for Password Reset
==================================
Sends password reset emails with secure reset links.
Supports multiple backends: SMTP, Console logging (for testing)
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from datetime import datetime
from config import Config

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending password reset emails"""
    
    def __init__(self, smtp_enabled: bool = None):
        """
        Initialize email service
        
        Args:
            smtp_enabled: Whether to use SMTP (True) or console logging (False)
                         If None, reads from Config
        """
        self.smtp_enabled = smtp_enabled if smtp_enabled is not None else Config.SMTP_ENABLED
        
        if self.smtp_enabled:
            self.smtp_host = Config.SMTP_HOST
            self.smtp_port = Config.SMTP_PORT
            self.smtp_username = Config.SMTP_USERNAME
            self.smtp_password = Config.SMTP_PASSWORD
            self.smtp_use_tls = Config.SMTP_USE_TLS
            self.email_from = Config.EMAIL_FROM
            self.email_from_name = Config.EMAIL_FROM_NAME
            logger.info("EmailService initialized with SMTP")
        else:
            logger.info("EmailService initialized with CONSOLE LOGGING mode")
    
    def send_password_reset_email(
        self, 
        recipient_email: str, 
        reset_token: str,
        reset_link: str
    ) -> bool:
        """
        Send password reset email to user
        
        Args:
            recipient_email: User's email address
            reset_token: Reset token for verification
            reset_link: Full URL for password reset page
        
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Generate email content
            subject = "Reset Your SkyBook Password"
            html_body = self._render_email_template(recipient_email, reset_link)
            text_body = self._render_text_template(recipient_email, reset_link)
            
            if self.smtp_enabled:
                # Send via SMTP
                return self._send_via_smtp(recipient_email, subject, html_body, text_body)
            else:
                # Log to console (development mode)
                return self._log_to_console(recipient_email, subject, reset_link)
                
        except Exception as e:
            logger.error(f"Error sending password reset email: {e}")
            return False
    
    def _send_via_smtp(
        self,
        recipient: str,
        subject: str,
        html_body: str,
        text_body: str
    ) -> bool:
        """Send email via SMTP server"""
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = f"{self.email_from_name} <{self.email_from}>"
            message['To'] = recipient
            
            # Attach both plain text and HTML versions
            text_part = MIMEText(text_body, 'plain')
            html_part = MIMEText(html_body, 'html')
            message.attach(text_part)
            message.attach(html_part)
            
            # Connect to SMTP server
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.smtp_use_tls:
                    server.starttls()
                
                if self.smtp_username and self.smtp_password:
                    server.login(self.smtp_username, self.smtp_password)
                
                server.send_message(message)
            
            logger.info(f"[+] Password reset email sent to {recipient}")
            return True
            
        except Exception as e:
            logger.error(f"SMTP send error: {e}")
            return False
    
    def _log_to_console(
        self,
        recipient: str,
        subject: str,
        reset_link: str
    ) -> bool:
        """Log email to console (development mode)"""
        try:
            separator = "=" * 80
            
            # Use simple text headers to avoid encoding issues
            print(f"\n{separator}")
            print("PASSWORD RESET EMAIL (DEVELOPMENT MODE)")
            print(separator)
            print(f"To: {recipient}")
            print(f"Subject: {subject}")
            print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(separator)
            print("\nPassword Reset Link:")
            print(f"   {reset_link}")
            print(f"\nThis link will expire in 1 hour")
            print(separator + "\n")
            
            logger.info(f"[+] Password reset email logged to console for {recipient}")
            return True
            
        except Exception as e:
            logger.error(f"Console logging error: {e}")
            return False
    
    def _render_email_template(self, email: str, reset_link: str) -> str:
        """Render HTML email template"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 600px;
            margin: 40px auto;
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
            font-weight: 600;
        }}
        .content {{
            padding: 40px 30px;
        }}
        .greeting {{
            font-size: 18px;
            margin-bottom: 20px;
            color: #333;
        }}
        .message {{
            color: #666;
            margin-bottom: 30px;
            font-size: 15px;
        }}
        .button-container {{
            text-align: center;
            margin: 35px 0;
        }}
        .reset-button {{
            display: inline-block;
            padding: 16px 40px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            font-size: 16px;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }}
        .security-notice {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 25px 0;
            border-radius: 4px;
        }}
        .security-notice strong {{
            color: #856404;
        }}
        .footer {{
            background: #f8f9fa;
            padding: 25px 30px;
            text-align: center;
            color: #6c757d;
            font-size: 13px;
            border-top: 1px solid #e9ecef;
        }}
        .link-text {{
            color: #667eea;
            word-break: break-all;
            font-size: 13px;
            margin-top: 15px;
        }}
        .expiry {{
            color: #dc3545;
            font-weight: 600;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 Password Reset Request</h1>
        </div>
        <div class="content">
            <p class="greeting">Hello,</p>
            
            <p class="message">
                We received a request to reset the password for your SkyBook account 
                associated with <strong>{email}</strong>.
            </p>
            
            <p class="message">
                Click the button below to create a new password:
            </p>
            
            <div class="button-container">
                <a href="{reset_link}" class="reset-button">Reset My Password</a>
            </div>
            
            <p class="message">
                Or copy and paste this link into your browser:
            </p>
            <p class="link-text">{reset_link}</p>
            
            <p class="expiry">⏰ This link will expire in 1 hour for security reasons.</p>
            
            <div class="security-notice">
                <strong>⚠️ Security Notice:</strong><br>
                If you didn't request this password reset, please ignore this email. 
                Your account is secure and no changes have been made.
            </div>
            
            <p class="message">
                For your security, this link can only be used once.
            </p>
        </div>
        <div class="footer">
            <p>This is an automated message from SkyBook Flight Booking System.</p>
            <p style="margin-top: 10px;">© 2025 SkyBook. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""
    
    def _render_text_template(self, email: str, reset_link: str) -> str:
        """Render plain text email template (fallback)"""
        return f"""
SkyBook Password Reset Request
================================

Hello,

We received a request to reset the password for your SkyBook account 
associated with {email}.

Click the link below to create a new password:

{reset_link}

This link will expire in 1 hour for security reasons.

SECURITY NOTICE:
If you didn't request this password reset, please ignore this email.
Your account is secure and no changes have been made.

For your security, this link can only be used once.

---
This is an automated message from SkyBook Flight Booking System.
© 2025 SkyBook. All rights reserved.
"""
    
    def test_connection(self) -> bool:
        """
        Test SMTP connection
        
        Returns:
            True if connection successful, False otherwise
        """
        if not self.smtp_enabled:
            logger.info("SMTP not enabled, using console logging")
            return True
        
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                if self.smtp_use_tls:
                    server.starttls()
                
                if self.smtp_username and self.smtp_password:
                    server.login(self.smtp_username, self.smtp_password)
                
                logger.info(f"[+] SMTP connection successful to {self.smtp_host}:{self.smtp_port}")
                return True
                
        except Exception as e:
            logger.error(f"SMTP connection failed: {e}")
            return False


def main():
    """Test email service"""
    import sys
    
    logging.basicConfig(level=logging.INFO, format=Config.LOG_FORMAT)
    
    try:
        print("\n" + "="*70)
        print("EMAIL SERVICE TEST")
        print("="*70)
        
        service = EmailService(smtp_enabled=False)  # Use console mode for testing
        
        # Test email sending
        print("\n1. Testing email service...")
        test_email = "test@example.com"
        test_token = "abc123def456"
        test_link = f"http://localhost:5000/reset-password.html?token={test_token}"
        
        success = service.send_password_reset_email(test_email, test_token, test_link)
        
        if success:
            print("   [+] Email service test successful!")
        else:
            print("   [-] Email service test failed")
            return 1
        
        print("\n" + "="*70)
        print("[+] Email service ready!")
        print("="*70 + "\n")
        
        return 0
        
    except Exception as e:
        print(f"\n[-] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
