from flask import request, jsonify, g
import jwt
from jwt import InvalidTokenError
from cryptography.hazmat.primitives import serialization
import logging

def init_jwt(app, pem_string):
    try:
        public_key = serialization.load_pem_public_key(pem_string.encode())
    except Exception as e:
        logging.fatal(f"Failed to load public key: {e}")
        raise

    @app.before_request
    def jwt_middleware():
        # Allow unauthenticated access to the health check endpoint
        if request.path == '/health':
            return

        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({
                "success": False,
                "message": "Missing Authorization header",
                "status": 401
            }), 401

        token = auth_header[len("Bearer "):]

        try:
            decoded_token = jwt.decode(
                token,
                public_key,
                algorithms=["RS256"]
            )
        except InvalidTokenError as e:
            return jsonify({
                "success": False,
                "message": "Invalid token",
                "status": 401
            }), 401

        email = decoded_token.get("email")
        if not email:
            return jsonify({
                "success": False,
                "message": "User not found in token claims",
                "status": 401
            }), 401

        # Store userID (email) for later use in routes
        g.user_id = email