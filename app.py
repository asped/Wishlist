from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wishlist.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'

db = SQLAlchemy(app)

# Database Models
class Child(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    gifts = db.relationship('Gift', backref='child', lazy=True, cascade='all, delete-orphan')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Child {self.name}>'

class Gift(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    link = db.Column(db.String(500))
    is_purchased = db.Column(db.Boolean, default=False)
    purchased_by = db.Column(db.String(100))
    child_id = db.Column(db.Integer, db.ForeignKey('child.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Gift {self.name}>'

# Create tables
with app.app_context():
    db.create_all()

# Public Routes
@app.route('/')
def index():
    """Main page showing all children and their gift lists"""
    children = Child.query.order_by(Child.name).all()
    return render_template('index.html', children=children)

@app.route('/child/<int:child_id>')
def child_gifts(child_id):
    """View gifts for a specific child"""
    child = Child.query.get_or_404(child_id)
    return render_template('child_gifts.html', child=child)

@app.route('/gift/<int:gift_id>/purchase', methods=['POST'])
def purchase_gift(gift_id):
    """Mark a gift as purchased"""
    gift = Gift.query.get_or_404(gift_id)
    buyer_name = request.form.get('buyer_name', '').strip()
    
    if not buyer_name:
        return jsonify({'error': 'Please enter your name'}), 400
    
    gift.is_purchased = True
    gift.purchased_by = buyer_name
    db.session.commit()
    
    return redirect(url_for('child_gifts', child_id=gift.child_id))

@app.route('/gift/<int:gift_id>/unmark', methods=['POST'])
def unmark_gift(gift_id):
    """Unmark a gift as purchased (in case of mistake)"""
    gift = Gift.query.get_or_404(gift_id)
    gift.is_purchased = False
    gift.purchased_by = None
    db.session.commit()
    
    return redirect(url_for('child_gifts', child_id=gift.child_id))

# Admin Routes
@app.route('/admin')
def admin():
    """Admin dashboard"""
    children = Child.query.order_by(Child.name).all()
    return render_template('admin/dashboard.html', children=children)

@app.route('/admin/child/add', methods=['GET', 'POST'])
def admin_add_child():
    """Add a new child"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        age = request.form.get('age', '').strip()
        
        if not name:
            return render_template('admin/child_form.html', error='Name is required')
        
        child = Child(name=name, age=int(age) if age else None)
        db.session.add(child)
        db.session.commit()
        
        return redirect(url_for('admin'))
    
    return render_template('admin/child_form.html')

@app.route('/admin/child/<int:child_id>/edit', methods=['GET', 'POST'])
def admin_edit_child(child_id):
    """Edit a child"""
    child = Child.query.get_or_404(child_id)
    
    if request.method == 'POST':
        child.name = request.form.get('name', '').strip()
        age = request.form.get('age', '').strip()
        child.age = int(age) if age else None
        
        db.session.commit()
        return redirect(url_for('admin'))
    
    return render_template('admin/child_form.html', child=child)

@app.route('/admin/child/<int:child_id>/delete', methods=['POST'])
def admin_delete_child(child_id):
    """Delete a child and all their gifts"""
    child = Child.query.get_or_404(child_id)
    db.session.delete(child)
    db.session.commit()
    
    return redirect(url_for('admin'))

@app.route('/admin/child/<int:child_id>/gifts')
def admin_child_gifts(child_id):
    """Manage gifts for a child"""
    child = Child.query.get_or_404(child_id)
    return render_template('admin/gifts.html', child=child)

@app.route('/admin/child/<int:child_id>/gift/add', methods=['GET', 'POST'])
def admin_add_gift(child_id):
    """Add a gift for a child"""
    child = Child.query.get_or_404(child_id)
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        link = request.form.get('link', '').strip()
        
        if not name:
            return render_template('admin/gift_form.html', child=child, error='Gift name is required')
        
        gift = Gift(
            name=name,
            description=description,
            link=link,
            child_id=child_id
        )
        db.session.add(gift)
        db.session.commit()
        
        return redirect(url_for('admin_child_gifts', child_id=child_id))
    
    return render_template('admin/gift_form.html', child=child)

@app.route('/admin/gift/<int:gift_id>/edit', methods=['GET', 'POST'])
def admin_edit_gift(gift_id):
    """Edit a gift"""
    gift = Gift.query.get_or_404(gift_id)
    
    if request.method == 'POST':
        gift.name = request.form.get('name', '').strip()
        gift.description = request.form.get('description', '').strip()
        gift.link = request.form.get('link', '').strip()
        
        db.session.commit()
        return redirect(url_for('admin_child_gifts', child_id=gift.child_id))
    
    return render_template('admin/gift_form.html', child=gift.child, gift=gift)

@app.route('/admin/gift/<int:gift_id>/delete', methods=['POST'])
def admin_delete_gift(gift_id):
    """Delete a gift"""
    gift = Gift.query.get_or_404(gift_id)
    child_id = gift.child_id
    db.session.delete(gift)
    db.session.commit()
    
    return redirect(url_for('admin_child_gifts', child_id=child_id))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
