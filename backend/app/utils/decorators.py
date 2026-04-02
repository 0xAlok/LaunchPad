from functools import wraps
from flask import jsonify
from flask_security import current_user


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({"error": "Authentication required"}), 401
            if not any(current_user.has_role(role) for role in roles):
                return jsonify({"error": "You do not have permission to access this resource"}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator
