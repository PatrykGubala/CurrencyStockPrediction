from flask import Blueprint, jsonify

interest_bp = Blueprint("interest", __name__)

@interest_bp.route('/interest-rate', methods=['GET'])
def get_interest_rate():
    return jsonify({"message": "Interest rate data"})
