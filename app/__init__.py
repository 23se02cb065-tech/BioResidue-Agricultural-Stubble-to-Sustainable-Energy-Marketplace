import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from app.database import db
from config import Config

jwt = JWTManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Init extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.residues import residues_bp
    from app.routes.orders import orders_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.bids import bids_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(residues_bp, url_prefix="/api/residues")
    app.register_blueprint(orders_bp, url_prefix="/api/orders")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")
    app.register_blueprint(bids_bp, url_prefix="/api/bids")

    # Create all tables
    with app.app_context():
        db.create_all()

    return app
