from flask import Blueprint, request, jsonify
from datetime import datetime
from api.utils import redis, ADMIN_PW

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/api/admin/update', methods=['POST'])
def admin_update():
    try:
        data = request.json
        if not data or data.get('pw') != ADMIN_PW:
            return jsonify({"error": "Unauthorized"}), 401
        
        raw_date = data.get('date')
        # Format: 2026-03-16 -> Mar 16
        formatted_date = datetime.strptime(raw_date, '%Y-%m-%d').strftime('%b %d') if raw_date else datetime.now().strftime('%b %d')
        
        redis.set('manual_date', formatted_date)
        redis.set('manual_price_nat', data.get('nat_price'))
        redis.set('manual_price_ma', data.get('ma_price'))
        
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500