#!/usr/bin/env python3
"""
Environment Setup Script for Wishlist App
This script helps you set up environment variables for production deployment.
"""

import os
import secrets
import sys

def generate_secret_key():
    """Generate a secure secret key"""
    return secrets.token_hex(32)

def create_env_file():
    """Create a .env file from the template"""
    template_file = 'env.template'
    env_file = '.env'
    
    if os.path.exists(env_file):
        print(f"⚠️  {env_file} already exists!")
        response = input("Do you want to overwrite it? (y/N): ")
        if response.lower() != 'y':
            print("❌ Cancelled.")
            return False
    
    if not os.path.exists(template_file):
        print(f"❌ Template file {template_file} not found!")
        return False
    
    # Read template
    with open(template_file, 'r') as f:
        content = f.read()
    
    # Generate secret key
    secret_key = generate_secret_key()
    content = content.replace('your-secret-key-change-in-production', secret_key)
    
    # Write .env file
    with open(env_file, 'w') as f:
        f.write(content)
    
    print(f"✅ Created {env_file} with generated secret key")
    print(f"🔑 Secret key: {secret_key}")
    print("\n📝 Next steps:")
    print("1. Edit .env file with your Brevo API credentials")
    print("2. Set up Brevo API key for password reset emails")
    print("3. Configure other settings as needed")
    
    return True

def show_env_status():
    """Show current environment variable status"""
    print("🔍 Environment Variables Status:")
    print("-" * 40)
    
    env_vars = [
        'SECRET_KEY',
        'FLASK_ENV', 
        'FLASK_DEBUG',
        'DATABASE_URL',
        'BREVO_API_KEY',
        'BREVO_SENDER_EMAIL',
        'BREVO_SENDER_NAME',
        'HOST',
        'PORT'
    ]
    
    for var in env_vars:
        value = os.environ.get(var, 'Not set')
        if var in ['SECRET_KEY', 'BREVO_API_KEY'] and value != 'Not set':
            value = '***' + value[-4:] if len(value) > 4 else '***'
        print(f"{var:20}: {value}")

def main():
    print("🚀 Wishlist App Environment Setup")
    print("=" * 40)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'create':
            create_env_file()
        elif command == 'status':
            show_env_status()
        elif command == 'key':
            print(f"🔑 Generated secret key: {generate_secret_key()}")
        else:
            print("❌ Unknown command. Use: create, status, or key")
    else:
        print("Available commands:")
        print("  python setup_env.py create  - Create .env file from template")
        print("  python setup_env.py status   - Show environment variables status")
        print("  python setup_env.py key     - Generate a new secret key")
        print("\nExample usage:")
        print("  python setup_env.py create")

if __name__ == '__main__':
    main()
