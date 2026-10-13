import os
from flask import Flask
from models import db


def create_app():
    """إنشاء تطبيق Flask مع الداتابيز"""
    app = Flask(__name__)
    
    # ═══ إعدادات الداتابيز ═══
    # على Render: DATABASE_URL بيكون موجود
    # على Termux: بيستخدم SQLite كـ fallback
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///awida.db')
    
    # Render بيستخدم postgres:// — SQLAlchemy محتاج postgresql://
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'awida-secret-key-change-me'
    
    # ربط الداتابيز
    db.init_app(app)
    
    return app


def init_database(app):
    """إنشاء الجداول"""
    with app.app_context():
        db.create_all()
        print("✅ Database tables created!")
