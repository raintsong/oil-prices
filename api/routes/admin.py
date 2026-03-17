from flask import Blueprint, request, jsonify
from api.utils import set_manual_prices # Your existing helper

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/api/admin/update', methods=['POST'])
def update_prices():
    data = request.get_json() # Next.js sends JSON
    
    date_str = data.get('date')
    national = data.get('national')
    ma = data.get('ma')

    # This calls your Upstash Redis logic
    success = set_manual_prices(date_str, national, ma)
    
    if success:
        return jsonify({"message": "Success"}), 200
    return jsonify({"message": "Redis Error"}), 500