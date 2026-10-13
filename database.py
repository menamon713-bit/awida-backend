from flask import Flask
from models import db

# ⚙️ الإعدادات
DB_USER = 'root'
DB_PASSWORD = ''
DB_HOST = '127.0.0.1'
DB_PORT = '3306'
DB_NAME = 'awida_db'


def create_app():
    """إنشاء تطبيق Flask مع الداتابيز"""
    app = Flask(__name__)
    
    # إعدادات الداتابيز
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}'
        f'@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'awida-secret-key-change-me'
    
    # ربط الداتابيز
    db.init_app(app)
    
    return app


def init_database(app):
    """إنشاء الجداول وإضافة البيانات الأولية"""
    with app.app_context():
        db.create_all()
        print("✅ Database tables created!")
