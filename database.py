import os
from flask import Flask
from models import db


def create_app():
    """إنشاء تطبيق Flask مع الداتابيز"""
    app = Flask(__name__)
    
    # ═══ SQLite Database ═══
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(basedir, 'awida.db')
    
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
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
