from database import create_app
from models import db, Category, Product

app = create_app()


def seed():
    """إضافة البيانات الأولية"""
    with app.app_context():
        # نتأكد إن الجداول موجودة
        db.create_all()
        
        # لو فيه أقسام بالفعل، منضيفش تاني
        if Category.query.count() > 0:
            print("⚠️  Data already exists. Skipping...")
            return
        
        print("🌱 Adding data...")
        
        # ═══ الأقسام ═══
        categories = [
            Category(name='مشويات', emoji='🍖', order=1),
            Category(name='محمر', emoji='🍗', order=2),
            Category(name='طواجن', emoji='🍲', order=3),
            Category(name='أكل بيتي', emoji='🏠', order=4),
            Category(name='مقبلات', emoji='🥗', order=5),
            Category(name='عروض', emoji='🔥', order=6),
        ]
        
        for cat in categories:
            db.session.add(cat)
        
        db.session.commit()
        print(f"✅ Added {len(categories)} categories")
        
        # ═══ الأصناف ═══
        grill = Category.query.filter_by(name='مشويات').first()
        mahmar = Category.query.filter_by(name='محمر').first()
        tagen = Category.query.filter_by(name='طواجن').first()
        home = Category.query.filter_by(name='أكل بيتي').first()
        side = Category.query.filter_by(name='مقبلات').first()
        offers = Category.query.filter_by(name='عروض').first()
        
        products = [
            # مشويات
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
            
            # محمر
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
            
            # طواجن
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
            
            # أكل بيتي
            Product(name='فتة باللحمة', price=190, emoji='🍛',
                    description='فتة باللحمة والخل والتوم',
                    category_id=home.id),
            Product(name='محشي مشكل', price=130, emoji='🍃',
                    description='محشي كرنب وورق عنب وكوسة',
                    category_id=home.id),
            Product(name='كشري', price=80, emoji='🍚',
                    description='كشري مصري أصيل',
                    category_id=home.id),
            Product(name='رقاق باللحمة', price=200, emoji='🍰',
                    description='رقاق باللحمة المفرومة',
                    category_id=home.id),
            
            # مقبلات
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
            
            # عروض
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
        
        for prod in products:
            db.session.add(prod)
        
        db.session.commit()
        print(f"✅ Added {len(products)} products")
        print("🎉 Data seeding complete!")


if __name__ == '__main__':
    seed()
