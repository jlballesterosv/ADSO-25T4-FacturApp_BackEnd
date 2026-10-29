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

@products_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product_by_id(product_id):
    product = Products.get_by_id(product_id)
    if product:
        return jsonify({
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'stock': product.stock,
            'category_id': product.category_id,
            'active': product.active
        })
    else:
        return jsonify({'success': False,
                         'message': 'Product not found'}), 404

@products_bp.route('/products', methods=['POST'])
def post_products():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    price = data.get('price')
    stock = data.get('stock', 0)
    category_id = data.get('category_id')
    errors = {}
    if not name:
        errors['name'] = 'name is required' 
    else:
        existing_product = Products.get_by_name(name)
        if existing_product:
            errors['name'] = 'name must be unique'
    if not price:
        errors['price'] = 'price is required'
    else:
        try:
            price = float(price)
            if price < 0:
                errors['price'] = 'price must be a non-negative number'
        except ValueError:
            errors['price'] = 'price must be a number'    
    if not category_id:
        errors['category_id'] = 'category_id is required'
    if errors:    
        return jsonify({ 'success': False,
                         'message': 'Errors in data validation',
                         'validation-errors': errors
                       }), 400    
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

@products_bp.route('/products/<int:product_id>', methods=['PUT'])
def put_products(product_id):
    product = Products.get_by_id(product_id)
    if not product:
        return jsonify({'success': False,
                         'message': 'Product not found'}), 404
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    price = data.get('price')
    stock = data.get('stock')
    category_id = data.get('category_id')
    errors = {}

    if product.name != name:
        existing_product = Products.get_by_name(name)
        if existing_product:
            errors['name'] = 'name must be unique'

    if name is not None:
        product.name = name

    

    if description is not None:
        product.description = description
    if price is not None:
        try:
            price = float(price)
            if price < 0:
                errors['price'] = 'price must be a non-negative number'
            else:
                product.price = price
        except ValueError:
            errors['price'] = 'price must be a number'
    if stock is not None:
        try:
            stock = float(stock)
            if stock < 0:
                errors['stock'] = 'stock must be a non-negative number'
            else:
                product.stock = stock
        except ValueError:
            errors['stock'] = 'stock must be a number'
    if category_id is not None:
        product.category_id = category_id
    if errors:    
        return jsonify({ 'success': False,
                         'message': 'Errors in data validation',
                         'validation-errors': errors
                       }), 400    
    Products.update(product)
    return jsonify({
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'stock': product.stock,
        'category_id': product.category_id,
        'active': product.active
    })