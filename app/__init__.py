"""
Flask Application Factory
Initializes the Flask app with all configurations and blueprints
"""

from flask import Flask, render_template, session
from flask_session import Session
import os

def create_app(config_name=None):
    """
    Application factory pattern for Flask
    
    Args:
        config_name: Configuration environment (development, production, testing)
        
    Returns:
        Configured Flask application instance
    """
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    from app.config import get_config
    app.config.from_object(get_config(config_name))
    
    # Initialize Flask-Session
    Session(app)
    
    # Register blueprints (routes)
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register template filters
    register_template_filters(app)
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        """Health check endpoint for load balancers"""
        return {'status': 'healthy', 'service': 'banking-analytics'}, 200
    
    return app


def register_blueprints(app):
    """
    Register all Flask blueprints (route modules)
    
    Args:
        app: Flask application instance
    """
    from app.routes.auth_routes import auth_bp
    from app.routes.account_routes import account_bp
    from app.routes.transaction_routes import transaction_bp
    from app.routes.analytics_routes import analytics_bp
    
    # Register blueprints with URL prefixes
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(account_bp, url_prefix='/account')
    app.register_blueprint(transaction_bp, url_prefix='/transactions')
    app.register_blueprint(analytics_bp, url_prefix='/analytics')
    
    # Root route
    @app.route('/')
    def index():
        """Landing page - redirect based on authentication"""
        if 'user_id' in session:
            return render_template('dashboard.html')
        return render_template('login.html')


def register_error_handlers(app):
    """
    Register custom error handlers
    
    Args:
        app: Flask application instance
    """
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 errors"""
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        # Log error for monitoring
        app.logger.error(f'Internal Server Error: {error}')
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        """Handle 403 forbidden errors"""
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(401)
    def unauthorized_error(error):
        """Handle 401 unauthorized errors"""
        return render_template('errors/401.html'), 401


def register_template_filters(app):
    """
    Register custom Jinja2 template filters
    
    Args:
        app: Flask application instance
    """
    
    @app.template_filter('currency')
    def currency_filter(value):
        """Format value as currency"""
        try:
            return f"${float(value):,.2f}"
        except (ValueError, TypeError):
            return "$0.00"
    
    @app.template_filter('datetime')
    def datetime_filter(value, format='%Y-%m-%d %H:%M:%S'):
        """Format datetime string"""
        try:
            from datetime import datetime
            if isinstance(value, str):
                dt = datetime.fromisoformat(value)
            else:
                dt = value
            return dt.strftime(format)
        except:
            return value
    
    @app.template_filter('transaction_type_badge')
    def transaction_type_badge(transaction_type):
        """Return Bootstrap badge class for transaction type"""
        badges = {
            'deposit': 'success',
            'withdrawal': 'warning',
            'transfer_in': 'info',
            'transfer_out': 'primary'
        }
        return badges.get(transaction_type.lower(), 'secondary')
