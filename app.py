from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
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

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wishlist.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@wishlist.com')

db = SQLAlchemy(app)
mail = Mail(app)
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
    admin_users = db.relationship('AdminUser', backref='family', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Family {self.name}>'

class AdminUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<AdminUser {self.email}>'

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

class AdminLoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Heslo', validators=[DataRequired()])
    submit = SubmitField('Prihlásiť sa')

class SuperAdminLoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Heslo', validators=[DataRequired()])
    submit = SubmitField('Prihlásiť sa')

class PasswordResetRequestForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Poslať link na reset hesla')

class PasswordResetForm(FlaskForm):
    password = PasswordField('Nové heslo', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Potvrdiť heslo', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Nastaviť nové heslo')

class FamilyPasswordForm(FlaskForm):
    password = PasswordField('Nové rodinné heslo', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Potvrdiť heslo', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Nastaviť heslo')

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
    admin_email = EmailField('Email správcu', validators=[DataRequired(), Email()])
    admin_password = PasswordField('Heslo správcu', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Vytvoriť rodinu')

class AdminUserForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Heslo', validators=[Length(min=6)])
    submit = SubmitField('Uložiť')

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

def require_admin_auth(f):
    def decorated_function(*args, **kwargs):
        if not session.get('admin_id'):
            return redirect(url_for('admin_login'))
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
    # Sort gifts: available first, then purchased
    sorted_gifts = sorted(child.gifts, key=lambda g: (g.is_purchased, g.created_at))
    child.gifts = sorted_gifts
    return render_template('child_gifts.html', child=child)

@app.route('/gift/<int:gift_id>/purchase', methods=['POST'])
@require_family_auth
def purchase_gift(gift_id):
    """Mark a gift as purchased"""
    family_id = session['family_id']
    gift = Gift.query.join(Child).filter(
        Gift.id == gift_id,
        Child.family_id == family_id
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
        Child.family_id == family_id
    ).first_or_404()
    
    gift.is_purchased = False
    gift.purchased_by = None
    db.session.commit()
    
    return redirect(url_for('child_gifts', child_id=gift.child_id))

# Admin Routes
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    """Admin email/password login"""
    form = AdminLoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        password = form.password.data
        
        admin = AdminUser.query.filter_by(email=email, is_active=True).first()
        
        if admin and check_password(password, admin.password_hash):
            session['admin_id'] = admin.id
            session['admin_email'] = admin.email
            session['family_id'] = admin.family_id
            session['family_name'] = admin.family.name
            
            # Update last login
            admin.last_login = datetime.utcnow()
            db.session.commit()
            
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Nesprávne prihlasovacie údaje', 'error')
    
    return render_template('admin_login.html', form=form)

@app.route('/admin-logout')
def admin_logout():
    """Logout from all sessions (family and admin)"""
    # Clear all session data
    session.pop('family_id', None)
    session.pop('family_name', None)
    session.pop('admin_id', None)
    session.pop('admin_email', None)
    session.pop('superadmin_id', None)
    session.pop('superadmin_email', None)
    return redirect(url_for('family_login'))

@app.route('/admin')
@require_admin_auth
def admin_dashboard():
    """Admin dashboard"""
    family_id = session['family_id']
    children = Child.query.filter_by(family_id=family_id).order_by(Child.name).all()
    return render_template('admin/dashboard.html', children=children)

@app.route('/admin/child/add', methods=['GET', 'POST'])
@require_admin_auth
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
        
        flash('Dieťa bolo úspešne pridané', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/child_form.html', form=form)

@app.route('/admin/child/<int:child_id>/edit', methods=['GET', 'POST'])
@require_admin_auth
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
        flash('Dieťa bolo úspešne upravené', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/child_form.html', form=form, child=child)

@app.route('/admin/child/<int:child_id>/delete', methods=['POST'])
@require_admin_auth
def admin_delete_child(child_id):
    """Delete a child and all their gifts"""
    family_id = session['family_id']
    child = Child.query.filter_by(id=child_id, family_id=family_id).first_or_404()
    db.session.delete(child)
    db.session.commit()
    
    flash('Dieťa bolo úspešne odstránené', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/child/<int:child_id>/gifts')
@require_admin_auth
def admin_child_gifts(child_id):
    """Manage gifts for a child"""
    family_id = session['family_id']
    child = Child.query.filter_by(id=child_id, family_id=family_id).first_or_404()
    return render_template('admin/gifts.html', child=child)

@app.route('/admin/child/<int:child_id>/gift/add', methods=['GET', 'POST'])
@require_admin_auth
def admin_add_gift(child_id):
    """Add a gift for a child"""
    family_id = session['family_id']
    child = Child.query.filter_by(id=child_id, family_id=family_id).first_or_404()
    
    form = GiftForm()
    if form.validate_on_submit():
        gift = Gift(
            name=form.name.data.strip(),
            description=form.description.data.strip(),
            link=form.link.data.strip(),
            link2=form.link2.data.strip(),
            image_url=form.image_url.data.strip(),
            price_range=form.price_range.data.strip(),
            child_id=child_id
        )
        db.session.add(gift)
        db.session.commit()
        
        flash('Darček bol úspešne pridaný', 'success')
        return redirect(url_for('admin_child_gifts', child_id=child_id))
    
    return render_template('admin/gift_form.html', form=form, child=child)

@app.route('/admin/gift/<int:gift_id>/edit', methods=['GET', 'POST'])
@require_admin_auth
def admin_edit_gift(gift_id):
    """Edit a gift"""
    family_id = session['family_id']
    gift = Gift.query.join(Child).filter(
        Gift.id == gift_id,
        Child.family_id == family_id
    ).first_or_404()
    
    form = GiftForm(obj=gift)
    if form.validate_on_submit():
        gift.name = form.name.data.strip()
        gift.description = form.description.data.strip()
        gift.link = form.link.data.strip()
        gift.link2 = form.link2.data.strip()
        gift.image_url = form.image_url.data.strip()
        gift.price_range = form.price_range.data.strip()
        
        db.session.commit()
        flash('Darček bol úspešne upravený', 'success')
        return redirect(url_for('admin_child_gifts', child_id=gift.child_id))
    
    return render_template('admin/gift_form.html', form=form, child=gift.child, gift=gift)

@app.route('/admin/gift/<int:gift_id>/delete', methods=['POST'])
@require_admin_auth
def admin_delete_gift(gift_id):
    """Delete a gift"""
    family_id = session['family_id']
    gift = Gift.query.join(Child).filter(
        Gift.id == gift_id,
        Child.family_id == family_id
    ).first_or_404()
    
    child_id = gift.child_id
    db.session.delete(gift)
    db.session.commit()
    
    flash('Darček bol úspešne odstránený', 'success')
    return redirect(url_for('admin_child_gifts', child_id=child_id))

@app.route('/admin/family-settings', methods=['GET', 'POST'])
@require_admin_auth
def admin_family_settings():
    """Admin can change family password"""
    family_id = session['family_id']
    family = Family.query.get(family_id)
    
    form = FamilyPasswordForm()
    if form.validate_on_submit():
        password = form.password.data
        
        # Check if password is unique
        existing_family = Family.query.filter(
            Family.password_hash == hash_password(password),
            Family.id != family_id
        ).first()
        
        if existing_family:
            flash('Toto heslo už používa iná rodina', 'error')
        else:
            family.password_hash = hash_password(password)
            db.session.commit()
            flash('Rodinné heslo bolo úspešne zmenené', 'success')
    
    return render_template('admin/family_settings.html', form=form, family=family)

# Password Reset Routes
@app.route('/reset-password-request', methods=['GET', 'POST'])
def reset_password_request():
    """Request password reset"""
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        
        # Check if email exists as admin
        admin = AdminUser.query.filter_by(email=email, is_active=True).first()
        if admin:
            # Generate reset token
            token = generate_reset_token()
            expires_at = datetime.utcnow() + timedelta(hours=1)
            
            # Store token
            reset_token = PasswordResetToken(
                email=email,
                token=token,
                expires_at=expires_at
            )
            db.session.add(reset_token)
            db.session.commit()
            
            # Send email
            if send_reset_email(email, token, 'admin'):
                flash('Link na reset hesla bol odoslaný na váš email', 'success')
            else:
                flash('Chyba pri odosielaní emailu', 'error')
        else:
            flash('Email sa nenašiel v systéme', 'error')
    
    return render_template('reset_password_request.html', form=form)

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset password with token"""
    reset_token = PasswordResetToken.query.filter_by(
        token=token,
        used=False
    ).first()
    
    if not reset_token or reset_token.expires_at < datetime.utcnow():
        flash('Neplatný alebo expirovaný token', 'error')
        return redirect(url_for('reset_password_request'))
    
    form = PasswordResetForm()
    if form.validate_on_submit():
        password = form.password.data
        
        # Update admin password
        admin = AdminUser.query.filter_by(email=reset_token.email).first()
        if admin:
            admin.password_hash = hash_password(password)
            reset_token.used = True
            db.session.commit()
            
            flash('Heslo bolo úspešne zmenené', 'success')
            return redirect(url_for('admin_login'))
        else:
            flash('Chyba pri zmene hesla', 'error')
    
    return render_template('reset_password.html', form=form)

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
    total_admins = AdminUser.query.filter_by(is_active=True).count()
    
    return render_template('superadmin/dashboard.html', 
                         families=families,
                         total_children=total_children,
                         total_gifts=total_gifts,
                         total_admins=total_admins)

@app.route('/superadmin/family/add', methods=['GET', 'POST'])
@require_superadmin_auth
def superadmin_add_family():
    """Create new family"""
    form = FamilyForm()
    if form.validate_on_submit():
        family_name = form.name.data.strip()
        family_password = form.password.data
        admin_email = form.admin_email.data.strip().lower()
        admin_password = form.admin_password.data
        
        # Check if family password is unique
        existing_family = Family.query.filter_by(password_hash=hash_password(family_password)).first()
        if existing_family:
            flash('Toto rodinné heslo už používa iná rodina', 'error')
            return render_template('superadmin/family_form.html', form=form)
        
        # Check if admin email is unique
        existing_admin = AdminUser.query.filter_by(email=admin_email).first()
        if existing_admin:
            flash('Tento email už používa iný správca', 'error')
            return render_template('superadmin/family_form.html', form=form)
        
        # Create family
        family = Family(
            name=family_name,
            password_hash=hash_password(family_password)
        )
        db.session.add(family)
        db.session.flush()  # Get family ID
        
        # Create admin user
        admin = AdminUser(
            email=admin_email,
            password_hash=hash_password(admin_password),
            family_id=family.id
        )
        db.session.add(admin)
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

@app.route('/superadmin/family/<int:family_id>/admins')
@require_superadmin_auth
def superadmin_family_admins(family_id):
    """View and manage family admins"""
    family = Family.query.get_or_404(family_id)
    admins = AdminUser.query.filter_by(family_id=family_id).all()
    return render_template('superadmin/family_admins.html', family=family, admins=admins)

@app.route('/superadmin/family/<int:family_id>/admin/add', methods=['GET', 'POST'])
@require_superadmin_auth
def superadmin_add_family_admin(family_id):
    """Add new admin to family"""
    family = Family.query.get_or_404(family_id)
    
    form = AdminUserForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        password = form.password.data
        
        # Check if email already exists
        existing_admin = AdminUser.query.filter_by(email=email).first()
        if existing_admin:
            flash('Tento email už používa iný správca', 'error')
            return render_template('superadmin/admin_form.html', form=form, family=family)
        
        # Create admin user
        admin = AdminUser(
            email=email,
            password_hash=hash_password(password),
            family_id=family_id
        )
        db.session.add(admin)
        db.session.commit()
        
        flash('Správca bol úspešne pridaný', 'success')
        return redirect(url_for('superadmin_family_admins', family_id=family_id))
    
    return render_template('superadmin/admin_form.html', form=form, family=family)

@app.route('/superadmin/admin/<int:admin_id>/edit', methods=['GET', 'POST'])
@require_superadmin_auth
def superadmin_edit_family_admin(admin_id):
    """Edit family admin"""
    admin = AdminUser.query.get_or_404(admin_id)
    family = admin.family
    
    form = AdminUserForm(obj=admin)
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        password = form.password.data
        
        # Check if email already exists (excluding current admin)
        existing_admin = AdminUser.query.filter(
            AdminUser.email == email,
            AdminUser.id != admin_id
        ).first()
        if existing_admin:
            flash('Tento email už používa iný správca', 'error')
            return render_template('superadmin/admin_form.html', form=form, family=family, admin=admin)
        
        # Update admin
        admin.email = email
        if password:  # Only update password if provided
            admin.password_hash = hash_password(password)
        
        db.session.commit()
        flash('Správca bol úspešne upravený', 'success')
        return redirect(url_for('superadmin_family_admins', family_id=family.id))
    
    return render_template('superadmin/admin_form.html', form=form, family=family, admin=admin)

@app.route('/superadmin/admin/<int:admin_id>/delete', methods=['POST'])
@require_superadmin_auth
def superadmin_delete_family_admin(admin_id):
    """Delete family admin"""
    admin = AdminUser.query.get_or_404(admin_id)
    family_id = admin.family_id
    
    # Don't allow deleting the last admin
    admin_count = AdminUser.query.filter_by(family_id=family_id, is_active=True).count()
    if admin_count <= 1:
        flash('Nemôžete vymazať posledného správcu rodiny', 'error')
    else:
        admin.is_active = False
        db.session.commit()
        flash('Správca bol úspešne odstránený', 'success')
    
    return redirect(url_for('superadmin_family_admins', family_id=family_id))

@app.route('/api/fetch-product-image', methods=['POST'])
@require_admin_auth
def fetch_product_image():
    """AJAX endpoint to fetch product images from URL with iframe fallback for blocked sites"""
    try:
        data = request.get_json()
        if not data or 'product_url' not in data:
            return jsonify({'error': 'Missing product_url parameter'}), 400
        
        product_url = data['product_url'].strip()
        if not product_url:
            return jsonify({'error': 'Empty product URL'}), 400
        
        # Check if this is a known blocked site that needs iframe fallback
        parsed_url = urlparse(product_url)
        domain = parsed_url.netloc.lower()
        
        # Known blocked sites that need iframe fallback
        blocked_sites = ['alza.cz', 'mall.cz', 'amazon.', 'ebay.']
        is_blocked_site = any(blocked in domain for blocked in blocked_sites)
        
        if is_blocked_site:
            # Return iframe fallback response for blocked sites
            return jsonify({
                'success': True, 
                'iframe_fallback': True,
                'product_url': product_url,
                'message': 'Stránka je chránená proti automatickému načítaniu. Zobrazujem stránku produktu pre manuálny výber obrázka.'
            })
        
        # For non-blocked sites, try simple scraping
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'cs-CZ,cs;q=0.9,en;q=0.8',
            }
            
            response = requests.get(product_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Try to find Open Graph image
                og_image = soup.find('meta', property='og:image')
                if og_image and og_image.get('content'):
                    image_url = og_image.get('content')
                    # Convert relative URLs to absolute
                    if image_url.startswith('//'):
                        image_url = parsed_url.scheme + ':' + image_url
                    elif image_url.startswith('/'):
                        image_url = urljoin(product_url, image_url)
                    return jsonify({'success': True, 'images': [image_url]})
            
            # If scraping failed, fall back to iframe
            return jsonify({
                'success': True, 
                'iframe_fallback': True,
                'product_url': product_url,
                'message': 'Automatické načítanie obrázkov zlyhalo. Zobrazujem stránku produktu pre manuálny výber obrázka.'
            })
            
        except Exception:
            # If any error occurs, fall back to iframe
            return jsonify({
                'success': True, 
                'iframe_fallback': True,
                'product_url': product_url,
                'message': 'Automatické načítanie obrázkov zlyhalo. Zobrazujem stránku produktu pre manuálny výber obrázka.'
            })
            
    except Exception as e:
        return jsonify({'success': False, 'error': 'Failed to fetch images'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
