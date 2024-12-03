from flask import Blueprint, jsonify, request
from app.services.currencies_service import CurrenciesService

currencies_bp = Blueprint('currencies', __name__, url_prefix='/api/currencies')

@currencies_bp.route('/', methods=['GET'])
def get_all_currencies():
    try:
        service = CurrenciesService()
        currencies_dto = service.get_all_currencies_dto()
        return jsonify({"currencies": currencies_dto}), 200
    except Exception as e:
        service.logger.error(f"Unexpected error: {e}")
        return jsonify({
            "error": "Wystąpił nieoczekiwany błąd podczas pobierania walut.",
            "details": str(e)
        }), 500

@currencies_bp.route('/load', methods=['POST'])
def load_currencies():
    try:
        data = request.get_json()
        currencies = data.get('currencies')
        if not currencies or not isinstance(currencies, list):
            return jsonify({"error": "A list of currencies is required."}), 400

        service = CurrenciesService()
        added_currencies = []
        for currency in currencies:
            code = currency.get('code')
            name = currency.get('name')
            symbol = currency.get('symbol')
            if not code or not name:
                continue
            currency_dto = service.add_currency(code, name, symbol)
            added_currencies.append(currency_dto)

        return jsonify({"message": "Currencies loaded successfully.", "currencies": added_currencies}), 200
    except Exception as e:
        service.logger.error(f"Unexpected error: {e}")
        return jsonify({
            "error": "Wystąpił nieoczekiwany błąd podczas ładowania walut.",
            "details": str(e)
        }), 500

@currencies_bp.route('/create', methods=['POST'])
def create_currency():
    try:
        data = request.get_json()
        code = data.get('code')
        name = data.get('name')
        symbol = data.get('symbol')
        if not code or not name:
            return jsonify({"error": "Currency code and name are required."}), 400

        service = CurrenciesService()
        currency_dto = service.add_currency(code, name, symbol)
        return jsonify({"currency": currency_dto}), 201
    except Exception as e:
        service.logger.error(f"Unexpected error: {e}")
        return jsonify({
            "error": "Wystąpił nieoczekiwany błąd podczas tworzenia waluty.",
            "details": str(e)
        }), 500

@currencies_bp.route('/<int:currency_id>', methods=['GET'])
def get_currency(currency_id):
    try:
        service = CurrenciesService()
        currency_dto = service.get_currency_by_id_dto(currency_id)
        if not currency_dto:
            return jsonify({"error": "Currency not found."}), 404
        return jsonify({"currency": currency_dto}), 200
    except Exception as e:
        service.logger.error(f"Unexpected error: {e}")
        return jsonify({
            "error": "Wystąpił nieoczekiwany błąd podczas pobierania waluty.",
            "details": str(e)
        }), 500

@currencies_bp.route('/<int:currency_id>', methods=['PUT'])
def update_currency(currency_id):
    try:
        data = request.get_json()
        new_name = data.get('name')
        new_symbol = data.get('symbol')
        if not new_name:
            return jsonify({"error": "New currency name is required."}), 400

        service = CurrenciesService()
        currency_dto = service.update_currency(currency_id, new_name, new_symbol)
        if not currency_dto:
            return jsonify({"error": "Currency not found."}), 404
        return jsonify({"currency": currency_dto}), 200
    except Exception as e:
        service.logger.error(f"Unexpected error: {e}")
        return jsonify({
            "error": "Wystąpił nieoczekiwany błąd podczas aktualizacji waluty.",
            "details": str(e)
        }), 500

@currencies_bp.route('/<int:currency_id>', methods=['DELETE'])
def delete_currency(currency_id):
    try:
        service = CurrenciesService()
        result = service.delete_currency(currency_id)
        if result:
            return jsonify({"message": "Currency deleted successfully."}), 200
        else:
            return jsonify({"error": "Currency not found."}), 404
    except Exception as e:
        service.logger.error(f"Unexpected error: {e}")
        return jsonify({
            "error": "Wystąpił nieoczekiwany błąd podczas usuwania waluty.",
            "details": str(e)
        }), 500