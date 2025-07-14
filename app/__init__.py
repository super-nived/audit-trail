from flask import Flask, jsonify
from flask_cors import CORS
from datetime import datetime
from app.routes.audit_log_routes import audit_log_bp
from app.database import get_db_connection

def create_app():
    app = Flask(__name__)
    CORS(app)

    app.register_blueprint(audit_log_bp)

    @app.route('/test-connection')
    def test_connection():
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT @@VERSION")
            version = cursor.fetchone()[0]
            return jsonify({"message": "Connection successful", "version": version}), 200
        except Exception as e:
            return jsonify({"error": f"Connection failed: {str(e)}"}), 500
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @app.route('/health')
    def health_check():
        return jsonify({"status": "healthy", "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')}), 200

    return app