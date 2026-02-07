"""
Application Entry Point
Runs the Flask development server
"""

import os
from app import create_app

# Create Flask application
app = create_app()

if __name__ == '__main__':
    # Get configuration from environment
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    print(f"""
    ╔════════════════════════════════════════════════════════════╗
    ║   Banking Data Analytics & Reporting System                ║
    ║   Running on: http://{host}:{port}                        ║
    ║   Environment: {os.environ.get('FLASK_ENV', 'development')}
    ║   Debug Mode: {debug}                                      ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    
    # Run the application
    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=True  # Enable multi-threading for better performance
    )
