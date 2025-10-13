#!/usr/bin/env python3
"""
Simple test script for Brevo email
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_brevo_email():
    """Test sending email via Brevo SMTP"""
    
    # Get credentials from .env
    smtp_server = os.environ.get('MAIL_SERVER', 'smtp-relay.brevo.com')
    smtp_port = int(os.environ.get('MAIL_PORT', 587))
    username = os.environ.get('MAIL_USERNAME')
    password = os.environ.get('MAIL_PASSWORD')
    sender_email = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # Check if credentials are set
    if not username or username == 'your-brevo-email@domain.com':
        print("❌ Error: Please set your Brevo email in .env file")
        print("   Update MAIL_USERNAME=your-brevo-email@domain.com")
        return False
    
    if not password or password == 'your-brevo-password':
        print("❌ Error: Please set your Brevo password in .env file")
        print("   Update MAIL_PASSWORD=your-brevo-password")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = sender_email  # Send to yourself
        msg['Subject'] = "Test Email - Brevo Setup"
        
        body = """
Hello!

This is a test email to verify that Brevo is working correctly.

If you receive this email, your Brevo setup is successful! 🎉

Best regards,
Your Wishlist App
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Connect to server and send email
        print(f"Connecting to {smtp_server}:{smtp_port}...")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Enable TLS encryption
        server.login(username, password)
        
        text = msg.as_string()
        server.sendmail(sender_email, sender_email, text)
        server.quit()
        
        print("✅ Email sent successfully!")
        print(f"   Sent to: {sender_email}")
        print("   Check your inbox for the test email")
        return True
        
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        print("\nTroubleshooting:")
        print("1. Check your Brevo email and password")
        print("2. Make sure your Brevo account is verified")
        print("3. Check if SMTP is enabled in your Brevo account")
        return False

if __name__ == '__main__':
    print("🧪 Testing Brevo Email Configuration...")
    print("=" * 50)
    
    # Show current configuration
    print(f"SMTP Server: {os.environ.get('MAIL_SERVER', 'smtp-relay.brevo.com')}")
    print(f"SMTP Port: {os.environ.get('MAIL_PORT', 587)}")
    print(f"Username: {os.environ.get('MAIL_USERNAME', 'NOT SET')}")
    print(f"Password: {'*' * 20 if os.environ.get('MAIL_PASSWORD') else 'NOT SET'}")
    print(f"Sender: {os.environ.get('MAIL_DEFAULT_SENDER', 'NOT SET')}")
    print("=" * 50)
    
    # Test email
    test_brevo_email()
