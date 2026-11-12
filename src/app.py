from flask import Flask
from src.models import Base, engine
from src.models.categories import Categories
from src.models.products import Products

from src.routes import register_routes


app = Flask(__name__)

register_routes(app)  # Register the routes with the Flask app

# NCFC: HS256 needs a key of at least 32 characters (PyJWT warns with shorter keys).
# Change this to a secure key in production
app.config['JWT_SECRET_KEY'] = 'facturapp-adso-25t4-dev-secret-key-change-me'

Base.metadata.create_all(engine)

@app.route('/')
def health():
    return {
        'success': True,
        'message': 'API is running'
    }


if __name__ == '__main__':
    app.run(debug=True)
