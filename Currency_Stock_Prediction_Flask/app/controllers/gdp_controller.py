from flask import Blueprint, jsonify

gdp_bp = Blueprint("gdp", __name__)

@gdp_bp.route('/gdp-data', methods=['GET'])
def get_gdp_data():
    return jsonify({"message": "GDP data"})