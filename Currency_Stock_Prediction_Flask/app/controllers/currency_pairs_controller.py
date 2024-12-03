from flask import Blueprint, jsonify, request
from app.services.currency_pairs_service import CurrencyPairsService

currency_pairs_bp = Blueprint('currency_pairs', __name__, url_prefix='/api/currency-pairs')

@currency_pairs_bp.route('/', methods=['GET'])
def get_all_currency_pairs():
    try:
        service = CurrencyPairsService()
        currency_pairs_dto = service.get_all_currency_pairs_dto()
        return jsonify({"currency_pairs": currency_pairs_dto}), 200
    except Exception as e:
        service.logger.error(f"Unexpected error: {e}")
        return jsonify({
            "error": "Wystąpił nieoczekiwany błąd podczas pobierania par walutowych.",
            "details": str(e)
        }), 500

@currency_pairs_bp.route('/<int:pair_id>', methods=['GET'])
def get_currency_pair(pair_id):
    try:
        service = CurrencyPairsService()
        pair_dto = service.get_currency_pair_by_id_dto(pair_id)
        if not pair_dto:
            return jsonify({"error": "Currency pair not found."}), 404
        return jsonify({"currency_pair": pair_dto}), 200
    except Exception as e:
        service.logger.error(f"Unexpected error: {e}")
        return jsonify({
            "error": "Wystąpił nieoczekiwany błąd podczas pobierania pary walutowej.",
            "details": str(e)
        }), 500

@currency_pairs_bp.route('/create', methods=['POST'])
def create_currency_pair():
    try:
        data = request.get_json()
        base_currency_code = data.get('base_currency_code')
        target_currency_code = data.get('target_currency_code')

        if not base_currency_code or not target_currency_code:
            return jsonify({"error": "Both base_currency_code and target_currency_code are required."}), 400

        service = CurrencyPairsService()
        pair_dto = service.create_currency_pair(base_currency_code, target_currency_code)
        if not pair_dto:
            return jsonify({"error": "Failed to create currency pair. Check if currencies exist."}), 400

        return jsonify({"currency_pair": pair_dto}), 201
    except Exception as e:
        service.logger.error(f"Unexpected error: {e}")
        return jsonify({
            "error": "Wystąpił nieoczekiwany błąd podczas tworzenia pary walutowej.",
            "details": str(e)
        }), 500

@currency_pairs_bp.route('/<int:pair_id>', methods=['DELETE'])
def delete_currency_pair(pair_id):
    try:
        service = CurrencyPairsService()
        result = service.delete_currency_pair(pair_id)
        if result:
            return jsonify({"message": "Currency pair deleted successfully."}), 200
        else:
            return jsonify({"error": "Currency pair not found."}), 404
    except Exception as e:
        service.logger.error(f"Unexpected error: {e}")
        return jsonify({
            "error": "Wystąpił nieoczekiwany błąd podczas usuwania pary walutowej.",
            "details": str(e)
        }), 500