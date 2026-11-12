# NCFC: Routes to manage users. For now it has one endpoint: an ADMIN assigns
# NCFC: a role to a user (for example, to a new user that registered as PENDING).
#
# NCFC: The FIRST administrator cannot be created through the API (nobody would
# NCFC: have permission to assign the role). Assign it directly in the database:
# NCFC:     UPDATE users SET role = 'ADMIN' WHERE email = 'admin@example.com';
from flask import Blueprint, jsonify, request, g

from src.models.users import Users, Role
from src.utils.auth import token_required, role_required

users_bp = Blueprint('users_v1', __name__, url_prefix='/api/v1')

# NCFC: roles an ADMIN can assign. PENDING is not included: it is only the
# NCFC: initial state of a new user.
ASSIGNABLE_ROLES = [Role.ADMIN.value, Role.SELLER.value]


@users_bp.route('/users/<int:user_id>/role', methods=['PUT'])
@token_required
@role_required(Role.ADMIN)
def assign_role(user_id):
    """
    NCFC: PUT /api/v1/users/<user_id>/role  (only ADMIN)

    NCFC: Request body:   { "role": "SELLER" }      (or "ADMIN")
    NCFC: Responses:
      200 -> { "id": 2, "email": "...", "name": "...", "role": "SELLER", "active": 1 }
      400 -> { "success": false, "message": "Errors in data validation",
               "validation-errors": { "role": "role must be one of: ADMIN, SELLER" } }
      400 -> { "success": false, "message": "You cannot change your own role" }
      401 -> missing, invalid or expired token (token_required)
      403 -> the user making the request is not ADMIN (role_required)
      404 -> { "success": false, "message": "User not found" }
    """
    user = Users.get_by_id(user_id)
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404

    # NCFC: an ADMIN cannot change his own role; this prevents leaving the
    # NCFC: system without administrators by mistake
    if user.id == g.current_user.id:
        return jsonify({'success': False, 'message': 'You cannot change your own role'}), 400

    # NCFC: silent=True returns None instead of failing when the body is not JSON;
    # NCFC: in that case the role is reported as required
    data = request.get_json(silent=True) or {}
    role = data.get('role')

    # NCFC: validate first and assign later, so an invalid request leaves the
    # NCFC: user untouched
    errors = {}
    if not role:
        errors['role'] = 'role is required'
    else:
        # NCFC: accept "seller" or "Seller" and store it as "SELLER"
        role = str(role).strip().upper()
        if role not in ASSIGNABLE_ROLES:
            errors['role'] = 'role must be one of: ADMIN, SELLER'
    if errors:
        return jsonify({'success': False,
                        'message': 'Errors in data validation',
                        'validation-errors': errors}), 400

    user.role = role
    user.update()
    return jsonify({
        'id': user.id,
        'email': user.email,
        'name': user.name,
        'role': user.role,
        'active': user.active
    }), 200
