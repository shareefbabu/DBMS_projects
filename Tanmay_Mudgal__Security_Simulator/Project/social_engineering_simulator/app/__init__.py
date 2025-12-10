from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize extensions
db = SQLAlchemy()
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address)

def create_app(config_name='development'):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    # Initialize extensions
    # Initialize extensions
    db.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    
    # Initialize Mail
    from app.email_service import mail
    mail.init_app(app)

    # Register custom filters
    import random
    def shuffle_filter(seq):
        try:
            result = list(seq)
            random.shuffle(result)
            return result
        except:
            return seq
            
    app.jinja_env.filters['shuffle'] = shuffle_filter
    
    # Register blueprints
    with app.app_context():
        from app.routes import main_bp
        from app.learning_routes import learning_bp
        from app.micro_lesson_routes import micro_lesson_bp
        from app.notification_routes import notification_bp
        from app.admin_routes import admin_bp
        from app.payment_routes import payment_bp
        
        app.register_blueprint(main_bp)
        app.register_blueprint(learning_bp)
        app.register_blueprint(micro_lesson_bp)
        app.register_blueprint(notification_bp)
        app.register_blueprint(admin_bp)
        app.register_blueprint(payment_bp)
        
        # Create tables if they don't exist
        db.create_all()
    
    return app

