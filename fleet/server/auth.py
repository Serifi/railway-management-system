import uuid
from flask import request, jsonify
from functools import wraps

# In-Memory-Token-Speicher (für Einfachheit; in Produktion nicht empfohlen)
tokens = {}

def generate_token():
    return str(uuid.uuid4())

def authenticate(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"message": "Authorization header missing"}), 401

        token = auth_header.split(" ")[1] if " " in auth_header else auth_header
        user = tokens.get(token)

        if not user:
            return jsonify({"message": "Invalid or expired token"}), 401

        # Füge den Benutzer zur Flask globalen `g` Variable hinzu
        from flask import g
        g.current_user = user
        return f(*args, **kwargs)
    return decorated_function

def authorize(roles=[]):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import g
            user = g.get('current_user')
            if not user or user.role.value not in roles:
                return jsonify({"message": "Forbidden"}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def login_user(employee):
    token = generate_token()
    tokens[token] = employee
    return token

def logout_user(token):
    tokens.pop(token, None)