"""
Inicialização da aplicação Flask
"""
from flask import Flask
from flask_cors import CORS
import os

def create_app():
    app = Flask(__name__)
    
    # Configurações
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///pdvmf.db')
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # CORS
    CORS(app)
    
    # Inicializar banco de dados
    from app.models import db
    db.init_app(app)
    
    # Criar tabelas
    with app.app_context():
        db.create_all()
    
    # Registrar blueprints
    from app.routes import main_bp, api_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app
