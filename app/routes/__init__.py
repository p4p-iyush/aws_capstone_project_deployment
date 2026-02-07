"""
Routes Package
Presentation Layer
"""

from app.routes.auth_routes import auth_bp, login_required
from app.routes.account_routes import account_bp
from app.routes.transaction_routes import transaction_bp
from app.routes.analytics_routes import analytics_bp

__all__ = [
    'auth_bp',
    'account_bp',
    'transaction_bp',
    'analytics_bp',
    'login_required'
]
