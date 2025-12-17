"""
Flask application factory
"""
from flask import Flask
from app.config import config
from app.extensions import db


def create_app(config_name='development'):
    """Create and configure the Flask application"""
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.events import events_bp
    from app.routes.theaters import theaters_bp
    from app.routes.shows import shows_bp
    from app.routes.bookings import bookings_bp
    from app.routes.customers import customers_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(events_bp, url_prefix='/events')
    app.register_blueprint(theaters_bp, url_prefix='/theaters')
    app.register_blueprint(shows_bp, url_prefix='/shows')
    app.register_blueprint(bookings_bp, url_prefix='/bookings')
    app.register_blueprint(customers_bp, url_prefix='/customers')

    return app
