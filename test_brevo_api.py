#!/usr/bin/env python3
"""
Test script for Brevo API email
"""

import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_brevo_api():
    """Test sending email via Brevo API"""
    
    # Get credentials from .env
    api_key = os.environ.get('BREVO_API_KEY')
    sender_email = os.environ.get('BREVO_SENDER_EMAIL')
    sender_name = os.environ.get('BREVO_SENDER_NAME', 'Wishlist App')
    
    # Check if credentials are set
    if not api_key or api_key == 'your-brevo-api-key-here':
        print("❌ Error: Please set your Brevo API key in .env file")
        print("   Update BREVO_API_KEY=your-brevo-api-key-here")
        return False
    
    if not sender_email or sender_email == 'your-brevo-email@domain.com':
        print("❌ Error: Please set your sender email in .env file")
        print("   Update BREVO_SENDER_EMAIL=your-brevo-email@domain.com")
        return False
    
    try:
        # Brevo API endpoint
        url = "https://api.brevo.com/v3/smtp/email"
        
        # Headers
        headers = {
            "accept": "application/json",
            "api-key": api_key,
            "content-type": "application/json"
        }
        
        # Email data
        data = {
            "sender": {
                "name": sender_name,
                "email": sender_email
            },
            "to": [
                {
                    "email": sender_email,  # Send to yourself
                    "name": "Test User"
                }
            ],
            "subject": "Test Email - Brevo API Setup",
            "htmlContent": """
            <html>
            <body>
                <h2>Hello!</h2>
                <p>This is a test email to verify that Brevo API is working correctly.</p>
                <p>If you receive this email, your Brevo API setup is successful! 🎉</p>
                <br>
                <p>Best regards,<br>Your Wishlist App</p>
            </body>
            </html>
            """,
            "textContent": """
            Hello!
            
            This is a test email to verify that Brevo API is working correctly.
            
            If you receive this email, your Brevo API setup is successful! 🎉
            
            Best regards,
            Your Wishlist App
            """
        }
        
        # Send request
        print("Sending email via Brevo API...")
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 201:
            print("✅ Email sent successfully!")
            print(f"   Sent to: {sender_email}")
            print("   Check your inbox for the test email")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        print("\nTroubleshooting:")
        print("1. Check your Brevo API key")
        print("2. Verify your sender email address")
        print("3. Make sure your Brevo account is verified")
        print("4. Check if API access is enabled in your Brevo account")
        return False

if __name__ == '__main__':
    print("🧪 Testing Brevo API Email Configuration...")
    print("=" * 50)
    
    # Show current configuration
    print(f"API Key: {'*' * 20 if os.environ.get('BREVO_API_KEY') else 'NOT SET'}")
    print(f"Sender Email: {os.environ.get('BREVO_SENDER_EMAIL', 'NOT SET')}")
    print(f"Sender Name: {os.environ.get('BREVO_SENDER_NAME', 'Wishlist App')}")
    print("=" * 50)
    
    # Test email
    test_brevo_api()
