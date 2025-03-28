import os
from flask import Flask
from flask_session import Session
from config import Config

session = Session()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize Flask extensions
    session.init_app(app)
    
    # Register blueprints
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.upload import bp as upload_bp
    app.register_blueprint(upload_bp, url_prefix='/upload')
    
    from app.visualize import bp as visualize_bp
    app.register_blueprint(visualize_bp, url_prefix='/visualize')
    
    # Register error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        # Make sure this renders the correct template
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500
    
    # Add a context processor to provide the current year for the footer
    @app.context_processor
    def inject_now():
        return {'now': datetime.datetime.now()}
    
    return app

from flask import render_template
import datetime
