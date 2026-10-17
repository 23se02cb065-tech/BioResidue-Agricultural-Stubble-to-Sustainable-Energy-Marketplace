from datetime import datetime
import bcrypt
from app.database import db

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False) # 'farmer' or 'company'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    residues = db.relationship('Residue', backref='farmer', lazy=True)
    orders = db.relationship('Order', backref='company', lazy=True)

    def set_password(self, password):
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat()
        }

class Residue(db.Model):
    __tablename__ = 'residues'
    
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    crop_type = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, nullable=False) # in metric tons
    price_per_unit = db.Column(db.Float, nullable=False) # per metric ton
    description = db.Column(db.Text, nullable=True)
    location_name = db.Column(db.String(200), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='available', nullable=False) # 'available', 'sold'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    orders = db.relationship('Order', backref='residue', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'farmer_id': self.farmer_id,
            'crop_type': self.crop_type,
            'quantity': self.quantity,
            'price_per_unit': self.price_per_unit,
            'description': self.description,
            'location_name': self.location_name,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    residue_id = db.Column(db.Integer, db.ForeignKey('residues.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending', nullable=False) # 'pending', 'paid', 'cancelled'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    transactions = db.relationship('Transaction', backref='order', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'residue_id': self.residue_id,
            'company_id': self.company_id,
            'quantity': self.quantity,
            'total_price': self.total_price,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'crop_type': self.residue.crop_type if self.residue else None,
            'location_name': self.residue.location_name if self.residue else None,
            'farmer_username': self.residue.farmer.username if self.residue and self.residue.farmer else None
        }

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending', nullable=False) # 'pending', 'success', 'failed'
    reference = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'amount': self.amount,
            'status': self.status,
            'reference': self.reference,
            'created_at': self.created_at.isoformat()
        }

class Bid(db.Model):
    __tablename__ = 'bids'
    
    id = db.Column(db.Integer, primary_key=True)
    residue_id = db.Column(db.Integer, db.ForeignKey('residues.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    bid_price_per_unit = db.Column(db.Float, nullable=False) # price per ton in INR (Rupees)
    quantity = db.Column(db.Float, nullable=False) # in tons
    status = db.Column(db.String(20), default='pending', nullable=False) # 'pending', 'accepted', 'rejected'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    residue = db.relationship('Residue', backref='bids', lazy=True)
    company = db.relationship('User', backref='bids', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'residue_id': self.residue_id,
            'company_id': self.company_id,
            'bid_price_per_unit': self.bid_price_per_unit,
            'quantity': self.quantity,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'crop_type': self.residue.crop_type if self.residue else None,
            'location_name': self.residue.location_name if self.residue else None,
            'company_username': self.company.username if self.company else None,
            'farmer_id': self.residue.farmer_id if self.residue else None,
            'farmer_username': self.residue.farmer.username if self.residue and self.residue.farmer else None
        }
