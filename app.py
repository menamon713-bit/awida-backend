from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from database import create_app, init_database
from models import db, Category, Product, Order, OrderItem

app = create_app()
CORS(app)

# عشان العربي يظهر صح في JSON
app.json.ensure_ascii = False


# ═══════════════════════════════════════════
#  الصفحة الرئيسية
# ═══════════════════════════════════════════

@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to Awida Restaurant API",
        "version": "1.0",
        "endpoints": {
            "categories": "/api/categories",
            "products": "/api/products",
            "offers": "/api/offers",
            "orders": "/api/orders",
        }
    })


# ═══════════════════════════════════════════
#  APIs الأقسام
# ═══════════════════════════════════════════

@app.route('/api/categories', methods=['GET'])
def get_categories():
    categories = Category.query.order_by(Category.order).all()
    return jsonify([{
        "id": c.id,
        "name": c.name,
        "emoji": c.emoji,
    } for c in categories])


# ═══════════════════════════════════════════
#  APIs الأصناف
# ═══════════════════════════════════════════

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
        "category_id": p.category_id,
        "is_offer": p.is_offer,
    })


@app.route('/api/products/category/<int:category_id>', methods=['GET'])
def get_products_by_category(category_id):
    products = Product.query.filter_by(
        category_id=category_id,
        is_available=True
    ).all()
    return jsonify([{
        "id": p.id,
        "name": p.name,
        "description": p.description,
        "price": p.price,
        "old_price": p.old_price,
        "emoji": p.emoji,
    } for p in products])


# ═══════════════════════════════════════════
#  APIs العروض
# ═══════════════════════════════════════════

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


# ═══════════════════════════════════════════
#  APIs الطلبات
# ═══════════════════════════════════════════

@app.route('/api/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    required = ['customer_name', 'customer_phone', 'customer_address', 'items']
    for field in required:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400
    
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
            "message": "Order created successfully",
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


# ═══════════════════════════════════════════
#  تشغيل السيرفر
# ═══════════════════════════════════════════

# ═══════════════════════════════════════════
#  لوحة التحكم
# ═══════════════════════════════════════════

@app.route('/admin')
def admin_panel():
    return render_template('admin.html')

@app.route('/api/orders/<int:order_id>', methods=['PUT'])
def update_order_status(order_id):
    """تحديث حالة الطلب"""
    order = Order.query.get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    
    data = request.get_json()
    new_status = data.get('status')
    
    if new_status not in ['pending', 'confirmed', 'delivered', 'cancelled']:
        return jsonify({"error": "Invalid status"}), 400
    
    order.status = new_status
    db.session.commit()
    
    return jsonify({
        "message": "Order status updated",
        "order_id": order.id,
        "status": order.status,
    })

if __name__ == '__main__':
    init_database(app)
    app.run(host='0.0.0.0', port=5000, debug=True)
