from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Category(db.Model):
    """جدول الأقسام"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    emoji = db.Column(db.String(10), default='🍽️')
    order = db.Column(db.Integer, default=0)
    
    products = db.relationship('Product', backref='category', lazy=True)


class Product(db.Model):
    """جدول الأصناف"""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    old_price = db.Column(db.Float)
    emoji = db.Column(db.String(10), default='🍽️')
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    is_available = db.Column(db.Boolean, default=True)
    is_offer = db.Column(db.Boolean, default=False)


class Order(db.Model):
    """جدول الطلبات"""
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(200), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    customer_address = db.Column(db.Text, nullable=False)
    notes = db.Column(db.Text)
    total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=db.func.now())
    
    items = db.relationship('OrderItem', backref='order', lazy=True)


class OrderItem(db.Model):
    """جدول أصناف الطلب"""
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    product_name = db.Column(db.String(200))
    price = db.Column(db.Float)
    quantity = db.Column(db.Integer)
