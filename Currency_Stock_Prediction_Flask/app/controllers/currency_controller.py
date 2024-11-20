from flask import Blueprint, request, jsonify

currency_bp = Blueprint("currency", __name__)

@currency_bp.route('/exchange-rate', methods=['GET'])
def get_exchange_rate():
    return jsonify({"message": "Exchange rate data"})
