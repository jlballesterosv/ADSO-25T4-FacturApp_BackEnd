from flask import Flask
from src.models import Base, engine
from src.models.categories import Categories
from src.models.products import Products

from src.routes import register_routes


app = Flask(__name__)

register_routes(app)  # Register the routes with the Flask app

Base.metadata.create_all(engine)

@app.route('/')
def health():
    return {
        'success': True,
        'message': 'API is running'
    }


if __name__ == '__main__':
    app.run(debug=True)
