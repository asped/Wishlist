#!/usr/bin/env python3
"""
Command-line tool to create initial admin account and family
Usage: python setup_admin.py
"""

import os
import sys
import getpass
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Family, AdminUser, SuperAdmin
from app import hash_password, check_password

def create_superadmin():
    """Create superadmin account"""
    print("\n🔧 Creating SuperAdmin Account...")
    print("=" * 50)
    
    email = input("SuperAdmin Email: ").strip().lower()
    if not email:
        print("❌ Email is required!")
        return False
    
    password = getpass.getpass("SuperAdmin Password: ")
    if len(password) < 6:
        print("❌ Password must be at least 6 characters!")
        return False
    
    confirm_password = getpass.getpass("Confirm Password: ")
    if password != confirm_password:
        print("❌ Passwords don't match!")
        return False
    
    # Check if superadmin already exists
    existing = SuperAdmin.query.filter_by(email=email).first()
    if existing:
        print(f"❌ SuperAdmin with email {email} already exists!")
        return False
    
    # Create superadmin
    superadmin = SuperAdmin(
        email=email,
        password_hash=hash_password(password),
        is_active=True
    )
    
    db.session.add(superadmin)
    db.session.commit()
    
    print(f"✅ SuperAdmin account created: {email}")
    return True

def create_family_and_admin():
    """Create initial family and admin account"""
    print("\n👨‍👩‍👧‍👦 Creating Initial Family and Admin...")
    print("=" * 50)
    
    # Family details
    family_name = input("Family Name: ").strip()
    if not family_name:
        print("❌ Family name is required!")
        return False
    
    family_password = getpass.getpass("Family Password: ")
    if len(family_password) < 6:
        print("❌ Password must be at least 6 characters!")
        return False
    
    confirm_password = getpass.getpass("Confirm Family Password: ")
    if family_password != confirm_password:
        print("❌ Passwords don't match!")
        return False
    
    # Admin details
    admin_email = input("Admin Email: ").strip().lower()
    if not admin_email:
        print("❌ Admin email is required!")
        return False
    
    admin_password = getpass.getpass("Admin Password: ")
    if len(admin_password) < 6:
        print("❌ Password must be at least 6 characters!")
        return False
    
    confirm_password = getpass.getpass("Confirm Admin Password: ")
    if admin_password != confirm_password:
        print("❌ Passwords don't match!")
        return False
    
    # Check if family already exists
    existing_family = Family.query.filter_by(name=family_name).first()
    if existing_family:
        print(f"❌ Family '{family_name}' already exists!")
        return False
    
    # Check if admin email already exists
    existing_admin = AdminUser.query.filter_by(email=admin_email).first()
    if existing_admin:
        print(f"❌ Admin with email {admin_email} already exists!")
        return False
    
    try:
        # Create family
        family = Family(
            name=family_name,
            password_hash=hash_password(family_password),
            is_active=True
        )
        db.session.add(family)
        db.session.flush()  # Get the family ID
        
        # Create admin for this family
        admin = AdminUser(
            email=admin_email,
            password_hash=hash_password(admin_password),
            family_id=family.id,
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()
        
        print(f"✅ Family '{family_name}' created successfully!")
        print(f"✅ Admin account created: {admin_email}")
        print(f"✅ Family ID: {family.id}")
        
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creating family/admin: {e}")
        return False

def show_credentials():
    """Show created credentials"""
    print("\n📋 Created Credentials:")
    print("=" * 50)
    
    # Show families
    families = Family.query.filter_by(is_active=True).all()
    if families:
        print("👨‍👩‍👧‍👦 Families:")
        for family in families:
            print(f"  • {family.name} (ID: {family.id})")
    
    # Show admins
    admins = AdminUser.query.filter_by(is_active=True).all()
    if admins:
        print("\n👤 Admin Accounts:")
        for admin in admins:
            print(f"  • {admin.email} (Family: {admin.family.name})")
    
    # Show superadmins
    superadmins = SuperAdmin.query.filter_by(is_active=True).all()
    if superadmins:
        print("\n👑 SuperAdmin Accounts:")
        for superadmin in superadmins:
            print(f"  • {superadmin.email}")

def main():
    """Main setup function"""
    print("🎁 Wishlist App - Initial Setup")
    print("=" * 50)
    print("This tool will help you create the initial accounts for your wishlist app.")
    print()
    
    with app.app_context():
        # Create database tables
        print("🗄️ Creating database tables...")
        db.create_all()
        print("✅ Database tables created!")
        
        # Check if we already have accounts
        existing_families = Family.query.count()
        existing_admins = AdminUser.query.count()
        existing_superadmins = SuperAdmin.query.count()
        
        if existing_families > 0 or existing_admins > 0 or existing_superadmins > 0:
            print(f"\n⚠️  Found existing accounts:")
            print(f"  • Families: {existing_families}")
            print(f"  • Admins: {existing_admins}")
            print(f"  • SuperAdmins: {existing_superadmins}")
            
            choice = input("\nDo you want to add more accounts? (y/N): ").strip().lower()
            if choice != 'y':
                show_credentials()
                return
        
        # Create superadmin
        if existing_superadmins == 0:
            if not create_superadmin():
                return
        
        # Create family and admin
        if existing_families == 0:
            if not create_family_and_admin():
                return
        
        # Show all credentials
        show_credentials()
        
        print("\n🎉 Setup complete!")
        print("\nNext steps:")
        print("1. Run the app: python app.py")
        print("2. Visit: http://localhost:5000")
        print("3. Login with family password to see gift lists")
        print("4. Login as admin to manage gifts and children")
        print("5. Login as superadmin to manage families")

if __name__ == '__main__':
    main()
