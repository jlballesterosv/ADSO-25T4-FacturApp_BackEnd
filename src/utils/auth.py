from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import current_app, request, jsonify, g

from src.models.users import Users

def generate_token(user, expires_in_hours=2):
    """
    Generate a JWT token for the given user.
    """
    payload = {
        'user_id': user.id,
        'exp': datetime.now(tz=timezone.utc) + timedelta(hours=expires_in_hours),
        'role': user.role,
        'email': user.email,
        'iat': datetime.now(tz=timezone.utc),  # Issued at time
    }
    token = jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')
    return token

def token_required(f):
    """
    Decorator to ensure that a valid JWT token is present in the request headers.

    The authenticated user is stored in g.current_user, so the route keeps its
    normal signature (it does not receive an extra parameter).

    Usage (the order matters: route first, token_required below):

        from flask import g

        @products_bp.route('/products', methods=['GET'])
        @token_required
        def get_products():
            user = g.current_user
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization', '')
        parts = auth_header.split()
        if len(parts) == 2 and parts[0].lower() == 'bearer':
            token = parts[1]

        if not token:
            return jsonify({'success': False, 'message': 'Token is missing!'}), 401

        try:
            payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'message': 'Invalid token!'}), 401

        current_user = Users.get_by_id(payload['user_id'])
        if not current_user:
            return jsonify({'success': False, 'message': 'User not found!'}), 401
        if current_user.active != 1:
            return jsonify({'success': False, 'message': 'User is inactive!'}), 401

        g.current_user = current_user
        return f(*args, **kwargs)

    return decorated
