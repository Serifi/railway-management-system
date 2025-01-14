import uuid
from flask import request, jsonify
from functools import wraps

tokens = {} # in-memory

def generate_token():
    """ Generate a unique token using UUID """
    return str(uuid.uuid4())

def authenticate(f):
    """ Decorator to ensure that a valid token is provided in the authorization header """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Retrieve authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"message": "Authorization header missing"}), 401

        # Extract the token from the header
        token = auth_header.split(" ")[1] if " " in auth_header else auth_header
        user = tokens.get(token)

        # Check if the token is valid
        if not user:
            return jsonify({"message": "Invalid or expired token"}), 401

        from flask import g
        g.current_user = user
        return f(*args, **kwargs)
    return decorated_function

def authorize(roles=[]):
    """ Decorator to ensure the authenticated user has the required role """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import g
            user = g.get('current_user')

            # Check the user and role
            if not user or user.role.value not in roles:
                return jsonify({"message": "Forbidden"}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def login_user(employee):
    """ Logs in a user by generating a unique token by associating it with the user and returns the generated token """
    token = generate_token()
    tokens[token] = employee
    return token

def logout_user(token):
    """ Logs out a user by removing their token """
    tokens.pop(token, None)