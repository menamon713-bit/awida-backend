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


# ═══ Seed Database ═══
@app.route('/api/seed', methods=['GET'])
def seed_database():
    try:
        db.create_all()
        
        if Category.query.count() > 0:
            return jsonify({
                "message": "Database already seeded",
                "categories": Category.query.count(),
                "products": Product.query.count(),
            })
        
        cats = [
            Category(name='مشويات', emoji='🍖', order=1),
            Category(name='محمر', emoji='🍗', order=2),
            Category(name='طواجن', emoji='🍲', order=3),
            Category(name='أكل بيتي', emoji='🏠', order=4),
            Category(name='مقبلات', emoji='🥗', order=5),
            Category(name='عروض', emoji='🔥', order=6),
        ]
        for c in cats:
            db.session.add(c)
        db.session.commit()
        
        # نجيب الأقسام
        grill = Category.query.filter_by(name='مشويات').first()
        mahmar = Category.query.filter_by(name='محمر').first()
        tagen = Category.query.filter_by(name='طواجن').first()
        home_cat = Category.query.filter_by(name='أكل بيتي').first()
        side = Category.query.filter_by(name='مقبلات').first()
        offers = Category.query.filter_by(name='عروض').first()
        
        products = [
            Product(name='كباب مشوي', price=220, emoji='🍖',
                    description='كباب بلدي مشوي على الفحم، مع أرز بسمتي وسلطة',
                    category_id=grill.id),
            Product(name='كفتة مشوية', price=198, old_price=240, emoji='🍖',
                    description='كفتة لحم مفروم مشوية، مع أرز بسمتي وسلطة',
                    category_id=grill.id),
            Product(name='شيش طاووق', price=180, emoji='🍗',
                    description='شيش طاووق متبل ومشوي، مع أرز وسلطة',
                    category_id=grill.id),
            Product(name='ريش ضاني', price=320, emoji='🥩',
                    description='ريش ضاني طازجة مشوية على الفحم',
                    category_id=grill.id),
            Product(name='فراخ مشوية', price=160, emoji='🍗',
                    description='نصف فرخة مشوية على الفحم مع أرز',
                    category_id=grill.id),
            Product(name='لحمة محمرة', price=250, emoji='🥘',
                    description='لحمة محمرة بطعم أصيل مع أرز',
                    category_id=mahmar.id),
            Product(name='فراخ محمرة', price=140, emoji='🍗',
                    description='فراخ محمرة بالبهارات مع أرز',
                    category_id=mahmar.id),
            Product(name='حمام محشي', price=280, emoji='🕊️',
                    description='حمام محشي ومحمر مع أرز',
                    category_id=mahmar.id),
            Product(name='سجق بلدي', price=150, emoji='🌭',
                    description='سجق بلدي محمر بالطماطم',
                    category_id=mahmar.id),
            Product(name='طاجن بامية', price=170, emoji='🍲',
                    description='طاجن بامية باللحمة في الفرن',
                    category_id=tagen.id),
            Product(name='طاجن بطاطس', price=160, emoji='🍲',
                    description='طاجن بطاطس باللحمة في الفرن',
                    category_id=tagen.id),
            Product(name='طاجن فاصوليا', price=155, emoji='🍲',
                    description='طاجن فاصوليا بيضا باللحمة',
                    category_id=tagen.id),
            Product(name='طاجن عكاوي', price=210, emoji='🍲',
                    description='طاجن عكاوي بالبصل في الفرن',
                    category_id=tagen.id),
            Product(name='فتة باللحمة', price=190, emoji='🍛',
                    description='فتة باللحمة والخل والتوم',
                    category_id=home_cat.id),
            Product(name='محشي مشكل', price=130, emoji='🍃',
                    description='محشي كرنب وورق عنب وكوسة',
                    category_id=home_cat.id),
            Product(name='كشري', price=80, emoji='🍚',
                    description='كشري مصري أصيل',
                    category_id=home_cat.id),
            Product(name='رقاق باللحمة', price=200, emoji='🍰',
                    description='رقاق باللحمة المفرومة',
                    category_id=home_cat.id),
            Product(name='سلطة بلدي', price=30, emoji='🥗',
                    description='سلطة خضراء طازجة',
                    category_id=side.id),
            Product(name='طحينة', price=25, emoji='🥣',
                    description='طحينة بالليمون',
                    category_id=side.id),
            Product(name='بابا غنوج', price=35, emoji='🍆',
                    description='بابا غنوج بالطحينة',
                    category_id=side.id),
            Product(name='مخلل مشكل', price=20, emoji='🥒',
                    description='مخلل بلدي مشكل',
                    category_id=side.id),
            Product(name='طبق عويضة المميز', price=98, old_price=139, emoji='🍖',
                    description='تشكيلة مشويات كاملة',
                    category_id=offers.id, is_offer=True),
            Product(name='وجبة عائلية', price=280, old_price=375, emoji='🍗',
                    description='فرخة كاملة + أرز + سلطة',
                    category_id=offers.id, is_offer=True),
            Product(name='طاجن مميز', price=160, old_price=200, emoji='🍲',
                    description='طاجن لحمة بالبصل',
                    category_id=offers.id, is_offer=True),
        ]
        
        for p in products:
            db.session.add(p)
        db.session.commit()
        
        return jsonify({
            "message": "Seeded successfully",
            "categories": len(cats),
            "products": len(products),
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


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
