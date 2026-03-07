from flask import Blueprint, jsonify
from auth import token_required

sensors_bp = Blueprint('sensors', __name__)

@sensors_bp.route('/api/sensors', methods=['GET'])
@token_required
def get_sensors(current_user):
    return jsonify([
        {"id": "SNSR-001", "name": "Main Entrance", "status": "Online", "coverage": "85%"},
        {"id": "SNSR-002", "name": "Server Room", "status": "Online", "coverage": "98%"}
    ])