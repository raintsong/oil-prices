import os
import logging
from flask import Flask, request
from api.routes.prices import prices_bp
from api.routes.admin import admin_bp

# Standard logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.url_map.strict_slashes = False

# Register your API logic
app.register_blueprint(prices_bp)
app.register_blueprint(admin_bp)

@app.route('/api/debug')
def debug_check():
    # Log the request details for your monitoring
    path = request.path
    logger.info(f"Debug accessed at path: {path}")
    return {"status": "alive", "handled_by": "flask"}

if __name__ == "__main__":
    app.run(debug=True, port=5000)