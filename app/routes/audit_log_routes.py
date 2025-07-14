from flask import Blueprint, request, jsonify
from app.services import audit_log_service

audit_log_bp = Blueprint('audit_log_bp', __name__)

@audit_log_bp.route('/auditlog', methods=['POST'])
def insert_audit_log():
    return audit_log_service.insert_audit_log()

@audit_log_bp.route('/auditlog', methods=['GET'])
def get_audit_logs():
    return audit_log_service.get_audit_logs()