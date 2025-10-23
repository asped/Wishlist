from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, PasswordField, EmailField, TextAreaField, SelectField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from datetime import datetime, timedelta
import os
import hashlib
import secrets
import bcrypt
from itsdangerous import URLSafeTimedSerializer
import re
import requests
from urllib.parse import urljoin, urlparse
from urllib.parse import urlparse
import mimetypes
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def validate_image_url(url):
    """
    Validate that a URL points to a legitimate image and is safe to use.
    Returns (is_valid, error_message)
    """
    if not url or not url.strip():
        return True, None  # Empty URLs are allowed
    
    url = url.strip()
    
    # Parse the URL
    try:
        parsed = urlparse(url)
    except Exception:
        return False, "Invalid URL format"
    
    # Check protocol - only allow http/https
    if parsed.scheme not in ['http', 'https']:
        return False, "Only HTTP and HTTPS URLs are allowed"
    
    # Check for suspicious patterns that might indicate XSS attempts
    suspicious_patterns = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'onload\s*=',
        r'onerror\s*=',
        r'onclick\s*=',
        r'<script',
        r'</script>',
        r'<iframe',
        r'<object',
        r'<embed',
        r'<link',
        r'<meta',
        r'<style',
        r'expression\s*\(',
        r'url\s*\(',
        r'@import',
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, url, re.IGNORECASE):
            return False, "URL contains potentially dangerous content"
    
    # Check if URL looks like an image based on extension
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp', '.ico']
    url_lower = url.lower()
    
    # Check file extension
    has_image_extension = any(url_lower.endswith(ext) for ext in image_extensions)
    
    # If it doesn't have an image extension, try to validate by making a HEAD request
    if not has_image_extension:
        try:
            # Make a HEAD request to check content type without downloading the full file
            response = requests.head(url, timeout=10, allow_redirects=True)
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '').lower()
                if not content_type.startswith('image/'):
                    return False, "URL does not point to an image file"
            else:
                return False, f"Could not verify image (HTTP {response.status_code})"
                
        except requests.exceptions.RequestException as e:
            return False, f"Could not verify image URL: {str(e)}"
    
    # Additional security checks
    # Check for localhost/internal IPs (optional - comment out if you want to allow local images)
    if parsed.hostname:
        if parsed.hostname in ['localhost', '127.0.0.1', '0.0.0.0']:
            return False, "Local URLs are not allowed for security reasons"
        
        # Check for private IP ranges
        if parsed.hostname.startswith('192.168.') or parsed.hostname.startswith('10.') or parsed.hostname.startswith('172.'):
            return False, "Private network URLs are not allowed"
    
    return True, None

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///wishlist.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Security configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')

# Email configuration (Brevo API only - no SMTP needed)

# Flask environment configuration
app.config['ENV'] = os.environ.get('FLASK_ENV', 'production')
app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'False').lower() in ['true', 'on', '1']

db = SQLAlchemy(app)
csrf = CSRFProtect(app)

# Database Models
class Family(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    children = db.relationship('Child', backref='family', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Family {self.name}>'

class SuperAdmin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<SuperAdmin {self.email}>'

class Child(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'), nullable=False)
    gifts = db.relationship('Gift', backref='child', lazy=True, cascade='all, delete-orphan')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Child {self.name}>'

class Gift(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    link = db.Column(db.String(500))
    link2 = db.Column(db.String(500))
    image_url = db.Column(db.String(500))
    price_range = db.Column(db.String(100))
    is_purchased = db.Column(db.Boolean, default=False)
    purchased_by = db.Column(db.String(100))
    child_id = db.Column(db.Integer, db.ForeignKey('child.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)  # Soft delete
    deleted_at = db.Column(db.DateTime)

    def __repr__(self):
        return f'<Gift {self.name}>'

class PasswordResetToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    token = db.Column(db.String(255), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Forms
class FamilyLoginForm(FlaskForm):
    password = PasswordField('Rodinné heslo', validators=[DataRequired()])
    submit = SubmitField('Prihlásiť sa')

class SuperAdminLoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Heslo', validators=[DataRequired()])
    submit = SubmitField('Prihlásiť sa')

class FamilyPasswordForm(FlaskForm):
    current_password = PasswordField('Súčasné rodinné heslo', validators=[DataRequired()])
    password = PasswordField('Nové rodinné heslo', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Potvrdiť heslo', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Zmeniť heslo')

class ChildForm(FlaskForm):
    name = StringField('Meno', validators=[DataRequired(), Length(max=100)])
    age = StringField('Vek')
    submit = SubmitField('Uložiť')

class GiftForm(FlaskForm):
    name = StringField('Názov darčeka', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Popis')
    link = StringField('Link 1')
    link2 = StringField('Link 2')
    image_url = StringField('URL obrázka')
    price_range = StringField('Cenové rozpätie')
    submit = SubmitField('Uložiť')

class FamilyForm(FlaskForm):
    name = StringField('Názov rodiny', validators=[DataRequired(), Length(max=100)])
    password = PasswordField('Rodinné heslo', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Potvrdiť heslo', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Vytvoriť rodinu')

# Utility functions
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, password_hash):
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def generate_reset_token():
    return secrets.token_urlsafe(32)

def send_reset_email(email, token, user_type='admin'):
    try:
        import requests
        
        reset_url = f"{request.url_root}reset-password/{token}"
        
        # Brevo API configuration
        api_key = os.environ.get('BREVO_API_KEY')
        sender_email = os.environ.get('BREVO_SENDER_EMAIL')
        sender_name = os.environ.get('BREVO_SENDER_NAME', 'Wishlist App')
        
        if not api_key or not sender_email:
            print("Brevo API not configured")
            return False
        
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
                    "email": email,
                    "name": "User"
                }
            ],
            "subject": "Reset hesla - Rodinný Zoznam Darčekov",
            "htmlContent": f"""
            <html>
            <body>
                <h2>Reset hesla</h2>
                <p>Dobrý deň,</p>
                <p>dostali ste túto správu, pretože ste požiadali o reset hesla pre váš účet v Rodinnom Zozname Darčekov.</p>
                <p>Pre nastavenie nového hesla kliknite na nasledujúci link:</p>
                <p><a href="{reset_url}" style="background-color: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Resetovať heslo</a></p>
                <p>Tento link je platný 1 hodinu.</p>
                <p>Ak ste nepožiadali o reset hesla, ignorujte túto správu.</p>
                <br>
                <p>S pozdravom,<br>Tím Rodinného Zoznamu Darčekov</p>
            </body>
            </html>
            """,
            "textContent": f"""
Dobrý deň,

dostali ste túto správu, pretože ste požiadali o reset hesla pre váš účet v Rodinnom Zozname Darčekov.

Pre nastavenie nového hesla kliknite na nasledujúci link:
{reset_url}

Tento link je platný 1 hodinu.

Ak ste nepožiadali o reset hesla, ignorujte túto správu.

S pozdravom,
Tím Rodinného Zoznamu Darčekov
            """
        }
        
        # Send request
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 201:
            return True
        else:
            print(f"Brevo API error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

# Authentication decorators
def require_family_auth(f):
    def decorated_function(*args, **kwargs):
        if not session.get('family_id'):
            return redirect(url_for('family_login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def require_superadmin_auth(f):
    def decorated_function(*args, **kwargs):
        if not session.get('superadmin_id'):
            return redirect(url_for('superadmin_login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Create tables
with app.app_context():
    db.create_all()
    
    # Create default superadmin if none exists
    if not SuperAdmin.query.first():
        superadmin = SuperAdmin(
            email='admin@wishlist.com',
            password_hash=hash_password('admin123'),
            is_active=True
        )
        db.session.add(superadmin)
        db.session.commit()
        print("Default superadmin created: admin@wishlist.com / admin123")

# Public Routes
@app.route('/')
def index():
    """Redirect to family login"""
    return redirect(url_for('family_login'))

@app.route('/family-login', methods=['GET', 'POST'])
def family_login():
    """Family password login"""
    form = FamilyLoginForm()
    if form.validate_on_submit():
        password = form.password.data.strip()
        
        # Get all active families and check passwords
        # Note: bcrypt hashes include salt, so we can't query directly by hash
        families = Family.query.filter_by(is_active=True).all()
        
        # Check each family's password
        for family in families:
            if check_password(password, family.password_hash):
                session['family_id'] = family.id
                session['family_name'] = family.name
                return redirect(url_for('family_dashboard'))
        
        # No matching password found
        flash('Nesprávne rodinné heslo', 'error')
    
    return render_template('family_login.html', form=form)

@app.route('/family-logout')
def family_logout():
    """Logout from all sessions (family and admin)"""
    # Clear all session data
    session.pop('family_id', None)
    session.pop('family_name', None)
    session.pop('admin_id', None)
    session.pop('admin_email', None)
    session.pop('superadmin_id', None)
    session.pop('superadmin_email', None)
    return redirect(url_for('family_login'))

@app.route('/family-dashboard')
@require_family_auth
def family_dashboard():
    """Main page showing all children and their gift lists"""
    family_id = session['family_id']
    children = Child.query.filter_by(family_id=family_id).order_by(Child.name).all()
    return render_template('family_dashboard.html', children=children)

@app.route('/child/<int:child_id>')
@require_family_auth
def child_gifts(child_id):
    """View gifts for a specific child"""
    family_id = session['family_id']
    child = Child.query.filter_by(id=child_id, family_id=family_id).first_or_404()
    # Sort gifts: available first, then purchased, exclude soft deleted
    sorted_gifts = sorted([g for g in child.gifts if not g.is_deleted], key=lambda g: (g.is_purchased, g.created_at))
    child.gifts = sorted_gifts
    return render_template('child_gifts.html', child=child)

@app.route('/gift/<int:gift_id>/purchase', methods=['POST'])
@require_family_auth
def purchase_gift(gift_id):
    """Mark a gift as purchased"""
    family_id = session['family_id']
    gift = Gift.query.join(Child).filter(
        Gift.id == gift_id,
        Child.family_id == family_id,
        Gift.is_deleted == False
    ).first_or_404()
    
    buyer_name = request.form.get('buyer_name', '').strip()
    
    if not buyer_name:
        return jsonify({'error': 'Please enter your name'}), 400
    
    gift.is_purchased = True
    gift.purchased_by = buyer_name
    db.session.commit()
    
    return redirect(url_for('child_gifts', child_id=gift.child_id))

@app.route('/gift/<int:gift_id>/unmark', methods=['POST'])
@require_family_auth
def unmark_gift(gift_id):
    """Unmark a gift as purchased (in case of mistake)"""
    family_id = session['family_id']
    gift = Gift.query.join(Child).filter(
        Gift.id == gift_id,
        Child.family_id == family_id,
        Gift.is_deleted == False
    ).first_or_404()
    
    gift.is_purchased = False
    gift.purchased_by = None
    db.session.commit()
    
    return redirect(url_for('child_gifts', child_id=gift.child_id))

# Admin Routes

@app.route('/admin')
@require_family_auth
def admin_dashboard():
    """Admin dashboard - accessible to all family members"""
    family_id = session['family_id']
    children = Child.query.filter_by(family_id=family_id).order_by(Child.name).all()
    return render_template('admin/dashboard.html', children=children)

@app.route('/admin/child/add', methods=['GET', 'POST'])
@require_family_auth
def admin_add_child():
    """Add a new child"""
    form = ChildForm()
    if form.validate_on_submit():
        name = form.name.data.strip()
        age = form.age.data.strip()
        
        child = Child(
            name=name,
            age=int(age) if age else None,
            family_id=session['family_id']
        )
        db.session.add(child)
        db.session.commit()
        
        flash('Člen rodiny bol úspešne pridaný', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/child_form.html', form=form)

@app.route('/admin/child/<int:child_id>/edit', methods=['GET', 'POST'])
@require_family_auth
def admin_edit_child(child_id):
    """Edit a child"""
    family_id = session['family_id']
    child = Child.query.filter_by(id=child_id, family_id=family_id).first_or_404()
    
    form = ChildForm(obj=child)
    if form.validate_on_submit():
        child.name = form.name.data.strip()
        age = form.age.data.strip()
        child.age = int(age) if age else None
        
        db.session.commit()
        flash('Člen rodiny bol úspešne upravený', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/child_form.html', form=form, child=child)

@app.route('/admin/child/<int:child_id>/delete', methods=['POST'])
@require_family_auth
def admin_delete_child(child_id):
    """Delete a child and all their gifts"""
    family_id = session['family_id']
    child = Child.query.filter_by(id=child_id, family_id=family_id).first_or_404()
    db.session.delete(child)
    db.session.commit()
    
    flash('Člen rodiny bol úspešne odstránený', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/child/<int:child_id>/gifts')
@require_family_auth
def admin_child_gifts(child_id):
    """Manage gifts for a child"""
    family_id = session['family_id']
    child = Child.query.filter_by(id=child_id, family_id=family_id).first_or_404()
    # Filter out soft deleted gifts
    child.gifts = [g for g in child.gifts if not g.is_deleted]
    return render_template('admin/gifts.html', child=child)

@app.route('/admin/child/<int:child_id>/gift/add', methods=['GET', 'POST'])
@require_family_auth
def admin_add_gift(child_id):
    """Add a gift for a child"""
    family_id = session['family_id']
    child = Child.query.filter_by(id=child_id, family_id=family_id).first_or_404()
    
    form = GiftForm()
    if form.validate_on_submit():
        # Handle file upload
        image_url = form.image_url.data.strip()
        
        # Validate image URL if provided
        if image_url:
            is_valid, error_msg = validate_image_url(image_url)
            if not is_valid:
                flash(f'Chyba v URL obrázka: {error_msg}', 'error')
                return render_template('admin/gift_form.html', form=form, child=child)
        
        if 'image_file' in request.files:
            file = request.files['image_file']
            if file and file.filename:
                # Save uploaded file
                import os
                from werkzeug.utils import secure_filename
                
                # Create uploads directory if it doesn't exist
                upload_dir = os.path.join(app.root_path, 'static', 'uploads')
                os.makedirs(upload_dir, exist_ok=True)
                
                # Generate unique filename
                filename = secure_filename(file.filename)
                name, ext = os.path.splitext(filename)
                unique_filename = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
                
                # Save file
                file_path = os.path.join(upload_dir, unique_filename)
                file.save(file_path)
                
                # Set image URL to the uploaded file
                image_url = f"/static/uploads/{unique_filename}"
        
        gift = Gift(
            name=form.name.data.strip(),
            description=form.description.data.strip(),
            link=form.link.data.strip(),
            link2=form.link2.data.strip(),
            image_url=image_url,
            price_range=form.price_range.data.strip(),
            child_id=child_id
        )
        db.session.add(gift)
        db.session.commit()
        
        flash('Darček bol úspešne pridaný', 'success')
        return redirect(url_for('admin_child_gifts', child_id=child_id))
    
    return render_template('admin/gift_form.html', form=form, child=child)

@app.route('/admin/gift/<int:gift_id>/edit', methods=['GET', 'POST'])
@require_family_auth
def admin_edit_gift(gift_id):
    """Edit a gift"""
    family_id = session['family_id']
    gift = Gift.query.join(Child).filter(
        Gift.id == gift_id,
        Child.family_id == family_id,
        Gift.is_deleted == False
    ).first_or_404()
    
    form = GiftForm(obj=gift)
    if form.validate_on_submit():
        # Handle file upload
        image_url = form.image_url.data.strip()
        
        # Validate image URL if provided
        if image_url:
            is_valid, error_msg = validate_image_url(image_url)
            if not is_valid:
                flash(f'Chyba v URL obrázka: {error_msg}', 'error')
                return render_template('admin/gift_form.html', form=form, child=gift.child, gift=gift)
        
        if 'image_file' in request.files:
            file = request.files['image_file']
            if file and file.filename:
                # Save uploaded file
                import os
                from werkzeug.utils import secure_filename
                
                # Create uploads directory if it doesn't exist
                upload_dir = os.path.join(app.root_path, 'static', 'uploads')
                os.makedirs(upload_dir, exist_ok=True)
                
                # Generate unique filename
                filename = secure_filename(file.filename)
                name, ext = os.path.splitext(filename)
                unique_filename = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
                
                # Save file
                file_path = os.path.join(upload_dir, unique_filename)
                file.save(file_path)
                
                # Set image URL to the uploaded file
                image_url = f"/static/uploads/{unique_filename}"
        
        gift.name = form.name.data.strip()
        gift.description = form.description.data.strip()
        gift.link = form.link.data.strip()
        gift.link2 = form.link2.data.strip()
        gift.image_url = image_url
        gift.price_range = form.price_range.data.strip()
        
        db.session.commit()
        flash('Darček bol úspešne upravený', 'success')
        return redirect(url_for('admin_child_gifts', child_id=gift.child_id))
    
    return render_template('admin/gift_form.html', form=form, child=gift.child, gift=gift)

@app.route('/admin/gift/<int:gift_id>/delete', methods=['POST'])
@require_family_auth
def admin_delete_gift(gift_id):
    """Soft delete a gift"""
    family_id = session['family_id']
    gift = Gift.query.join(Child).filter(
        Gift.id == gift_id,
        Child.family_id == family_id,
        Gift.is_deleted == False
    ).first_or_404()
    
    child_id = gift.child_id
    gift.is_deleted = True
    gift.deleted_at = datetime.utcnow()
    db.session.commit()
    
    flash('Darček bol úspešne odstránený', 'success')
    return redirect(url_for('admin_child_gifts', child_id=child_id))

@app.route('/admin/gift/<int:gift_id>/unmark', methods=['POST'])
@require_family_auth
def admin_unmark_gift(gift_id):
    """Mark a gift as not purchased with confirmation"""
    family_id = session['family_id']
    gift = Gift.query.join(Child).filter(
        Gift.id == gift_id,
        Child.family_id == family_id,
        Gift.is_deleted == False
    ).first_or_404()
    
    gift.is_purchased = False
    gift.purchased_by = None
    db.session.commit()
    
    flash('Darček bol označený ako nekúpený', 'success')
    return redirect(url_for('admin_child_gifts', child_id=gift.child_id))

@app.route('/admin/family-settings', methods=['GET', 'POST'])
@require_family_auth
def admin_family_settings():
    """Family can change family password"""
    family_id = session['family_id']
    family = Family.query.get(family_id)
    
    form = FamilyPasswordForm()
    if form.validate_on_submit():
        current_password = form.current_password.data
        new_password = form.password.data
        
        # Verify current password
        if not check_password(current_password, family.password_hash):
            flash('Nesprávne súčasné heslo', 'error')
            return render_template('admin/family_settings.html', form=form, family=family)
        
        # Check if new password is unique
        existing_family = Family.query.filter(
            Family.password_hash == hash_password(new_password),
            Family.id != family_id
        ).first()
        
        if existing_family:
            flash('Toto heslo už používa iná rodina', 'error')
        else:
            family.password_hash = hash_password(new_password)
            db.session.commit()
            flash('Rodinné heslo bolo úspešne zmenené', 'success')
    
    return render_template('admin/family_settings.html', form=form, family=family)

# SuperAdmin Routes
@app.route('/superadmin-login', methods=['GET', 'POST'])
def superadmin_login():
    """SuperAdmin login"""
    form = SuperAdminLoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        password = form.password.data
        
        superadmin = SuperAdmin.query.filter_by(email=email, is_active=True).first()
        
        if superadmin and check_password(password, superadmin.password_hash):
            session['superadmin_id'] = superadmin.id
            session['superadmin_email'] = superadmin.email
            
            # Update last login
            superadmin.last_login = datetime.utcnow()
            db.session.commit()
            
            return redirect(url_for('superadmin_dashboard'))
        else:
            flash('Nesprávne prihlasovacie údaje', 'error')
    
    return render_template('superadmin_login.html', form=form)

@app.route('/superadmin-logout')
def superadmin_logout():
    """Logout from superadmin session"""
    session.pop('superadmin_id', None)
    session.pop('superadmin_email', None)
    return redirect(url_for('family_login'))

@app.route('/superadmin')
@require_superadmin_auth
def superadmin_dashboard():
    """SuperAdmin dashboard with stats"""
    families = Family.query.filter_by(is_active=True).all()
    total_children = Child.query.count()
    total_gifts = Gift.query.count()
    
    return render_template('superadmin/dashboard.html', 
                         families=families,
                         total_children=total_children,
                         total_gifts=total_gifts)

@app.route('/superadmin/family/add', methods=['GET', 'POST'])
@require_superadmin_auth
def superadmin_add_family():
    """Create new family"""
    form = FamilyForm()
    if form.validate_on_submit():
        family_name = form.name.data.strip()
        family_password = form.password.data
        
        # Check if family password is unique
        existing_family = Family.query.filter_by(password_hash=hash_password(family_password)).first()
        if existing_family:
            flash('Toto rodinné heslo už používa iná rodina', 'error')
            return render_template('superadmin/family_form.html', form=form)
        
        # Create family
        family = Family(
            name=family_name,
            password_hash=hash_password(family_password)
        )
        db.session.add(family)
        db.session.commit()
        
        flash('Rodina bola úspešne vytvorená', 'success')
        return redirect(url_for('superadmin_dashboard'))
    
    return render_template('superadmin/family_form.html', form=form)

@app.route('/superadmin/family/<int:family_id>/reset-password', methods=['POST'])
@require_superadmin_auth
def superadmin_reset_family_password(family_id):
    """Reset family password"""
    family = Family.query.get_or_404(family_id)
    
    # Generate new password
    new_password = secrets.token_urlsafe(8)
    family.password_hash = hash_password(new_password)
    db.session.commit()
    
    flash(f'Nové rodinné heslo: {new_password}', 'success')
    return redirect(url_for('superadmin_dashboard'))

@app.route('/superadmin/family/<int:family_id>/delete', methods=['POST'])
@require_superadmin_auth
def superadmin_delete_family(family_id):
    """Delete family"""
    family = Family.query.get_or_404(family_id)
    family.is_active = False
    db.session.commit()
    
    flash('Rodina bola deaktivovaná', 'success')
    return redirect(url_for('superadmin_dashboard'))

@app.route('/superadmin/deleted-gifts')
@require_superadmin_auth
def superadmin_deleted_gifts():
    """View all soft deleted gifts for recovery"""
    deleted_gifts = Gift.query.filter_by(is_deleted=True).order_by(Gift.deleted_at.desc()).all()
    return render_template('superadmin/deleted_gifts.html', gifts=deleted_gifts)

@app.route('/superadmin/gift/<int:gift_id>/restore', methods=['POST'])
@require_superadmin_auth
def superadmin_restore_gift(gift_id):
    """Restore a soft deleted gift"""
    gift = Gift.query.filter_by(id=gift_id, is_deleted=True).first_or_404()
    
    gift.is_deleted = False
    gift.deleted_at = None
    db.session.commit()
    
    flash('Darček bol úspešne obnovený', 'success')
    return redirect(url_for('superadmin_deleted_gifts'))

if __name__ == '__main__':
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() in ['true', 'on', '1']
    app.run(debug=debug, host=host, port=port)
