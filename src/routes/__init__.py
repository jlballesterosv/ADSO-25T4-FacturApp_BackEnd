
from src.routes.v1.products_routes import products_bp
from src.routes.v1.auth_routes import auth_bp
from src.routes.v1.users_routes import users_bp  # NCFC: users routes (assign role)


def register_routes(app):  # Register the routes with the Flask app
    app.register_blueprint(products_bp)  # Register the products blueprint
    app.register_blueprint(auth_bp)  # Register the auth blueprint
    app.register_blueprint(users_bp)  # NCFC: Register the users blueprint