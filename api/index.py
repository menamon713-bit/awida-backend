from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
import os

# نضيف المسار الرئيسي عشان نقدر نستورد من models
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import db, Category, Product, Order, OrderItem

app = Flask(__name__)
CORS(app)

# ═══ إعداد الداتابيز ═══
turso_url = os.environ.get('TURSO_DATABASE_URL', '')
turso_token = os.environ.get('TURSO_AUTH_TOKEN', '')

if turso_url and turso_token:
    # Turso (SQLite سحابي)
    clean_url = turso_url.replace('libsql://', '')
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"sqlite+libsql://{clean_url}?authToken={turso_token}"
    )
else:
    # SQLite محلي (fallback)
    basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(basedir, 'awida.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'awida-secret-key-change-me'

db.init_app(app)


# ═══ الصفحة الرئيسية ═══
@app.route('/')
def home():
    turso_url = os.environ.get('TURSO_DATABASE_URL', '')
    turso_token = os.environ.get('TURSO_AUTH_TOKEN', '')
    
    return jsonify({
        "message": "Welcome to Awida Restaurant API",
        "version": "1.0",
        "debug": {
            "turso_url_set": bool(turso_url),
            "turso_token_set": bool(turso_token),
            "turso_url_prefix": turso_url[:30] if turso_url else "NOT SET",
            "db_uri_prefix": app.config['SQLALCHEMY_DATABASE_URI'][:50],
        }
    })


# ═══ الأقسام ═══
@app.route('/api/categories', methods=['GET'])
def get_categories():
    categories = Category.query.order_by(Category.order).all()
    return jsonify([{
        "id": c.id,
        "name": c.name,
        "emoji": c.emoji,
    } for c in categories])


# ═══ الأصناف ═══
@app.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.filter_by(is_available=True).all()
    return jsonify([{
        "id": p.id,
        "name": p.name,
        "description": p.description,
        "price": p.price,
        "old_price": p.old_price,
        "emoji": p.emoji,
        "category_id": p.category_id,
        "is_offer": p.is_offer,
    } for p in products])


@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    p = Product.query.get(product_id)
    if not p:
        return jsonify({"error": "Product not found"}), 404
    return jsonify({
        "id": p.id,
        "name": p.name,
        "description": p.description,
        "price": p.price,
        "old_price": p.old_price,
        "emoji": p.emoji,
    })


# ═══ العروض ═══
@app.route('/api/offers', methods=['GET'])
def get_offers():
    offers = Product.query.filter_by(is_offer=True, is_available=True).all()
    return jsonify([{
        "id": p.id,
        "name": p.name,
        "description": p.description,
        "price": p.price,
        "old_price": p.old_price,
        "emoji": p.emoji,
    } for p in offers])


# ═══ الطلبات ═══
@app.route('/api/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    try:
        total = 0
        order_items = []
        
        for item in data['items']:
            product = Product.query.get(item['product_id'])
            if product:
                total += product.price * item['quantity']
                order_items.append({
                    'product': product,
                    'quantity': item['quantity'],
                })
        
        order = Order(
            customer_name=data['customer_name'],
            customer_phone=data['customer_phone'],
            customer_address=data['customer_address'],
            notes=data.get('notes', ''),
            total=total,
        )
        
        db.session.add(order)
        db.session.flush()
        
        for item in order_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item['product'].id,
                product_name=item['product'].name,
                price=item['product'].price,
                quantity=item['quantity'],
            )
            db.session.add(order_item)
        
        db.session.commit()
        
        return jsonify({
            "message": "Order created",
            "order_id": order.id,
            "total": total,
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route('/api/orders', methods=['GET'])
def get_orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return jsonify([{
        "id": o.id,
        "customer_name": o.customer_name,
        "customer_phone": o.customer_phone,
        "customer_address": o.customer_address,
        "total": o.total,
        "status": o.status,
        "created_at": o.created_at.isoformat(),
    } for o in orders])


# ═══ Handler لـ Vercel ═══
def handler(request):
    return app(request.environ, lambda *args: None)
