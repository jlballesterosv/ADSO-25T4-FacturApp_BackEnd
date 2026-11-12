from flask import Blueprint, jsonify, request

from src.models.users import Users, Role  # NCFC: Role is used to create users as PENDING
from src.utils.auth import generate_token


auth_bp = Blueprint('auth_v1', __name__, url_prefix='/api/v1')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    # NCFC: the role is no longer read from the request body. Before this change
    # NCFC: anyone could register as ADMIN by sending "role": "ADMIN".

    if not email or not password or not name:
        return jsonify({'success': False, 'message': 'Email, password, and name are required'}), 400
    
    if len(password) < 6:
        return jsonify({'success': False, 'message': 'Password must be at least 6 characters long'}), 400
    
    existing_user = Users.get_by_email(email)
    if existing_user:
        return jsonify({'success': False, 'message': 'Email already registered'}), 400
    
    # NCFC: every new user starts as PENDING; an ADMIN assigns the real role later
    new_user = Users(email=email, password=password, name=name, role=Role.PENDING.value)
    new_user.save()

    return jsonify({'success': True, 'message': 'User registered successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'success': False, 'message': 'Email and password are required'}), 400
    
    user = Users.get_by_email(email)
    if not user or not user.check_password(password):
        return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
    
    return jsonify({
        'access_token': generate_token(user),
        'token_type': 'Bearer',
        'expires_in': 7200,  # 2 hours in seconds
        'user': {
            'id': user.id,
            'email': user.email,
            'name': user.name,
            'role': user.role
        }
    }), 200


