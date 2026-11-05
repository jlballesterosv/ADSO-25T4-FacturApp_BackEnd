
from src.routes.v1.products_routes import products_bp


def register_routes(app):  # Register the routes with the Flask app
    app.register_blueprint(products_bp)  # Register the products blueprint