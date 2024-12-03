from flask import Blueprint, jsonify
from app.services.countries_service import CountriesService

countries_bp = Blueprint('countries', __name__, url_prefix='/api/countries')

@countries_bp.route('/load', methods=['POST'])
def load_only_countries():
    try:
        service = CountriesService()
        countries_data = service.fetch_countries_data()
        service.load_only_countries(countries_data)
        return jsonify({"message": "Tylko kraje zostały załadowane pomyślnie."}), 200
    except Exception as e:
        service.logger.error(f"Nieoczekiwany błąd: {e}")
        return jsonify({
            "error": "Wystąpił nieoczekiwany błąd.",
            "details": str(e)
        }), 500

@countries_bp.route('/load-all', methods=['POST'])
def load_countries_with_details():
    try:
        service = CountriesService()
        service.load_all_data()
        return jsonify({"message": "Kraje wraz z regionami i walutami zostały załadowane pomyślnie."}), 200
    except Exception as e:
        service.logger.error(f"Nieoczekiwany błąd: {e}")
        return jsonify({
            "error": "Wystąpił nieoczekiwany błąd.",
            "details": str(e)
        }), 500

@countries_bp.route('/', methods=['GET'])
def get_all_countries():
    try:
        service = CountriesService()
        countries_dto = service.get_all_countries_dto()
        return jsonify({"countries": countries_dto}), 200
    except Exception as e:
        service.logger.error(f"Nieoczekiwany błąd: {e}")
        return jsonify({
            "error": "Wystąpił nieoczekiwany błąd podczas pobierania krajów.",
            "details": str(e)
        }), 500

@countries_bp.route('/<country_code>', methods=['GET'])
def get_country(country_code):
    try:
        service = CountriesService()
        country_dto = service.get_country_by_code_dto(country_code.upper())
        if not country_dto:
            return jsonify({"error": "Kraj nie został znaleziony."}), 404
        return jsonify({"country": country_dto}), 200
    except Exception as e:
        service.logger.error(f"Nieoczekiwany błąd: {e}")
        return jsonify({
            "error": "Wystąpił nieoczekiwany błąd podczas pobierania kraju.",
            "details": str(e)
        }), 500