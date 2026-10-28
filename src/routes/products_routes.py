from flask import Blueprint, jsonify, request
from src.models.products import Products
products_bp = Blueprint('products', __name__)

@products_bp.route('/products', methods=['GET'])
def get_products():    
    products = Products.get()
    return jsonify([{
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'stock': product.stock,
        'category_id': product.category_id,
        'active': product.active
    } for product in products])

@products_bp.route('/products', methods=['POST'])
def post_products():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    price = data.get('price')
    stock = data.get('stock', 0)
    category_id = data.get('category_id')

    if not name or not price or not category_id:
        return jsonify({'error': 'Missing required fields'}), 400

    new_product = Products(name=name, description=description, price=price, stock=stock, category_id=category_id)
    
    Products.save(new_product)

    return jsonify({
        'id': new_product.id,
        'name': new_product.name,
        'description': new_product.description,
        'price': new_product.price,
        'stock': new_product.stock,
        'category_id': new_product.category_id,
        'active': new_product.active
    }), 201