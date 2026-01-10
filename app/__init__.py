"""
Inicialização da aplicação Flask
"""
from flask import Flask
from flask_cors import CORS
import os
from sqlalchemy import text

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
    
    # SQLAlchemy engine options
    engine_options = {
        'pool_pre_ping': True,  # Verifica conexão antes de usar
        'pool_recycle': 3600,   # Recicla conexões a cada hora
    }
    
    # Adicionar timeout apenas para PostgreSQL
    if 'postgresql' in database_url:
        engine_options['connect_args'] = {'connect_timeout': 10}
    
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = engine_options
    
    # CORS
    CORS(app)
    
    # Inicializar banco de dados
    from app.models import db
    db.init_app(app)
    
    # Criar tabelas com retry
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            print(f"⚠️  Aviso ao criar tabelas: {e}")
            # Não falhar completamente, deixar a app rodando
    
    # Registrar blueprints
    from app.routes import main_bp, api_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Health check endpoint
    @app.route('/health')
    def health():
        """Endpoint de saúde para health checks"""
        try:
            from app.models import db
            db.session.execute(text('SELECT 1'))
            return {'status': 'ok', 'db': 'connected'}, 200
        except Exception as e:
            return {'status': 'degraded', 'db': 'disconnected', 'error': str(e)}, 503
    
    return app
