from flask import Blueprint, jsonify, request
from app.services.regions_service import RegionsService

regions_bp = Blueprint('regions', __name__, url_prefix='/api/regions')

@regions_bp.route('/', methods=['GET'])
def get_all_regions():
    try:
        service = RegionsService()
        regions_dto = service.get_all_regions_dto()
        return jsonify({"regions": regions_dto}), 200
    except Exception as e:
        service.logger.error(f"Unexpected error: {e}")
        return jsonify({
            "error": "Wystąpił nieoczekiwany błąd podczas pobierania regionów.",
            "details": str(e)
        }), 500

@regions_bp.route('/<int:region_id>', methods=['GET'])
def get_region(region_id):
    try:
        service = RegionsService()
        region_dto = service.get_region_by_id_dto(region_id)
        if not region_dto:
            return jsonify({"error": "Region not found."}), 404
        return jsonify({"region": region_dto}), 200
    except Exception as e:
        service.logger.error(f"Unexpected error: {e}")
        return jsonify({
            "error": "Wystąpił nieoczekiwany błąd podczas pobierania regionu.",
            "details": str(e)
        }), 500

@regions_bp.route('/load', methods=['POST'])
def load_regions():
    try:
        data = request.get_json()
        regions = data.get('regions')
        if not regions or not isinstance(regions, list):
            return jsonify({"error": "A list of regions is required."}), 400

        service = RegionsService()
        added_regions = []
        for region_name in regions:
            region_dto = service.add_region(region_name)
            added_regions.append(region_dto)

        return jsonify({"message": "Regions loaded successfully.", "regions": added_regions}), 200
    except Exception as e:
        service.logger.error(f"Unexpected error: {e}")
        return jsonify({
            "error": "Wystąpił nieoczekiwany błąd podczas ładowania regionów.",
            "details": str(e)
        }), 500

@regions_bp.route('/create', methods=['POST'])
def create_region():
    try:
        data = request.get_json()
        region_name = data.get('region_name')
        if not region_name:
            return jsonify({"error": "Region name is required."}), 400

        service = RegionsService()
        region_dto = service.add_region(region_name)
        return jsonify({"region": region_dto}), 201
    except Exception as e:
        service.logger.error(f"Unexpected error: {e}")
        return jsonify({
            "error": "Wystąpił nieoczekiwany błąd podczas tworzenia regionu.",
            "details": str(e)
        }), 500

@regions_bp.route('/<int:region_id>', methods=['PUT'])
def update_region(region_id):
    try:
        data = request.get_json()
        new_name = data.get('region_name')
        if not new_name:
            return jsonify({"error": "New region name is required."}), 400

        service = RegionsService()
        region_dto = service.update_region(region_id, new_name)
        if not region_dto:
            return jsonify({"error": "Region not found."}), 404
        return jsonify({"region": region_dto}), 200
    except Exception as e:
        service.logger.error(f"Unexpected error: {e}")
        return jsonify({
            "error": "Wystąpił nieoczekiwany błąd podczas aktualizacji regionu.",
            "details": str(e)
        }), 500

@regions_bp.route('/<int:region_id>', methods=['DELETE'])
def delete_region(region_id):
    try:
        service = RegionsService()
        result = service.delete_region(region_id)
        if result:
            return jsonify({"message": "Region deleted successfully."}), 200
        else:
            return jsonify({"error": "Region not found."}), 404
    except Exception as e:
        service.logger.error(f"Unexpected error: {e}")
        return jsonify({
            "error": "Wystąpił nieoczekiwany błąd podczas usuwania regionu.",
            "details": str(e)
        }), 500