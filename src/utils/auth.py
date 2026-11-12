from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import current_app, request, jsonify, g

from src.models.users import Users, Role

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

    NCFC: The authenticated user is stored in g.current_user, so the route keeps
    NCFC: its normal signature (it does not receive an extra parameter).

    NCFC: Usage (the order matters: route first, token_required below):

        from flask import g

        @products_bp.route('/products', methods=['GET'])
        @token_required
        def get_products():
            ...                      # g.current_user is available here if needed

    NCFC: Responses: 401 when the token is missing, invalid or expired, when the
    NCFC: user no longer exists or when the user is inactive (active = 0).
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # NCFC: the header must be "Authorization: Bearer <token>";
        # NCFC: "Bearer" is accepted in upper or lower case
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
        # NCFC: a user deactivated after logging in cannot keep using his token
        if current_user.active != 1:
            return jsonify({'success': False, 'message': 'User is inactive!'}), 401

        # NCFC: the user is saved in Flask's g object (it lives only during this
        # NCFC: request) instead of being passed as an argument to the route
        g.current_user = current_user
        return f(*args, **kwargs)

    return decorated


def role_required(*roles):
    """
    NCFC: Decorator that only lets in users whose role is one of `roles`.

    NCFC: It must go BELOW @token_required, because it reads the user that
    NCFC: token_required saved in g.current_user:

        @products_bp.route('/products', methods=['POST'])
        @token_required
        @role_required(Role.ADMIN)                  # only ADMIN
        def post_products():
            ...

        @products_bp.route('/products', methods=['GET'])
        @token_required
        @role_required(Role.ADMIN, Role.SELLER)     # ADMIN or SELLER
        def get_products():
            ...

    NCFC: Responses:
      - 403 when the role is not in `roles`. Users with role PENDING always get
        403, because PENDING is never passed as an allowed role.
      - 500 when it is used without @token_required above it (programming error),
        so the mistake is easy to spot while testing.
    """
    # NCFC: compare with the text values ('ADMIN', 'SELLER'), the same text the
    # NCFC: users table stores in the role column
    allowed_roles = [role.value if isinstance(role, Role) else role for role in roles]

    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # NCFC: getattr returns None when token_required did not run first
            current_user = getattr(g, 'current_user', None)
            if current_user is None:
                return jsonify({'success': False,
                                'message': 'role_required must be placed below token_required'}), 500

            if current_user.role not in allowed_roles:
                return jsonify({'success': False,
                                'message': 'You do not have permission to perform this action'}), 403

            return f(*args, **kwargs)

        return decorated

    return decorator
