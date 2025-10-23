# Multi-Family Wishlist System

A comprehensive wishlist management system that supports multiple families with proper authentication and data isolation.

## Features

### Multi-Family Support
- Each family has a unique password for access
- Complete data isolation between families
- Families cannot see each other's data

### Authentication System
- **Family Access**: Simple password-based login for family members
- **Admin Access**: Email/password authentication for family administrators
- **SuperAdmin Access**: System-wide administration with email/password

### Admin Management
- Family administrators can manage their family's children and gifts
- Admins can change family passwords (with uniqueness validation)
- Password reset functionality via email

### SuperAdmin Features
- Create new families with administrators
- Manage all families and admin users
- Reset family passwords
- System statistics and monitoring
- Deactivate families

### Security Features
- CSRF protection on all forms
- Secure password hashing with bcrypt
- Email-based password reset with tokens
- Session management
- Data isolation between families

## Installation

1. Install Python dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Set up email configuration via Brevo (optional, for password resets) in .env


3. Run the application:
```bash
source venv/bin/activate
python app.py
```

The application will be available at `http://localhost:5001`

## Default SuperAdmin Account

- **Email**: admin@wishlist.com
- **Password**: admin123

**Important**: Change these credentials immediately in production!

## Usage

### For Families
1. Go to the family login page
2. Enter your family password
3. Browse children's wishlists
4. Mark gifts as purchased

### For Family Administrators
1. Go to admin login (`/admin-login`)
2. Enter your email and password
3. Manage children and gifts
4. Change family password in settings

### For SuperAdmins
1. Go to superadmin login (`/superadmin-login`)
2. Enter superadmin credentials
3. Create new families
4. Manage all families and administrators

## Database Schema

The system uses the following main models:
- **Family**: Contains family information and password
- **AdminUser**: Family administrators with email/password
- **SuperAdmin**: System administrators
- **Child**: Children belonging to a family
- **Gift**: Gifts belonging to children
- **PasswordResetToken**: Tokens for password reset functionality

## Security Notes

- All passwords are hashed using bcrypt
- CSRF tokens protect all forms
- Email verification for password resets
- Session-based authentication
- Complete data isolation between families

## Email Configuration

For password reset functionality, configure email settings in environment variables. The system supports SMTP configuration for sending password reset emails.

## Production Deployment

1. Set a strong `SECRET_KEY` environment variable
2. Configure proper email settings
3. Use a production database (PostgreSQL recommended)
4. Change default superadmin credentials
5. Set up proper SSL/TLS
6. Configure proper logging and monitoring
