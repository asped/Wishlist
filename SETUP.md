# 🎁 Wishlist App - Setup Guide

## Quick Start (Empty Database)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Create Initial Accounts
```bash
python setup_admin.py
```

This interactive script will help you create:
- **SuperAdmin account** (manages families)
- **Initial family** (with family password)
- **Admin account** (manages gifts and children)

### 3. Run the Application
```bash
python app.py
```

### 4. Access the App
- **Main App**: http://localhost:5000
- **Family Login**: Use family password to see gift lists
- **Admin Login**: Use admin email/password to manage gifts
- **SuperAdmin**: Use superadmin email/password to manage families

## Account Types

### 👨‍👩‍👧‍👦 Family Account
- **Access**: View gift lists, mark gifts as purchased
- **Login**: Family password
- **Features**: See all children's gift lists

### 👤 Admin Account  
- **Access**: Everything family can do + manage gifts and children
- **Login**: Admin email + password
- **Features**: Add/edit/delete gifts, manage children, family settings

### 👑 SuperAdmin Account
- **Access**: Everything + manage families and admins
- **Login**: SuperAdmin email + password  
- **Features**: Create families, manage admin accounts, reset passwords

## Database Setup

The app uses SQLite database (`instance/wishlist.db`). The setup script will:
- Create all necessary tables
- Set up initial accounts
- Configure proper relationships

## Environment Variables

Create a `.env` file for email configuration:
```bash
# Brevo API Configuration (optional)
BREVO_API_KEY=your-brevo-api-key-here
BREVO_SENDER_EMAIL=your-email@domain.com
BREVO_SENDER_NAME=Wishlist App

# Other settings
SECRET_KEY=your-secret-key-change-in-production
DEBUG=true
```

## Troubleshooting

### Database Issues
- Delete `instance/wishlist.db` and run setup again
- Check file permissions on database directory

### Login Issues  
- Use the setup script to create new accounts
- Check email/password spelling
- Ensure accounts are active

### Email Issues
- Configure Brevo API in `.env` file
- Test email with `python test_brevo_api.py`

## Development

### Run in Debug Mode
```bash
export DEBUG=true
python app.py
```

### Reset Database
```bash
rm instance/wishlist.db
python setup_admin.py
```

### Test Email Setup
```bash
python test_brevo_api.py
```
