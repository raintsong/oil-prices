import os
import logging
from flask import Flask
from api.routes.prices import prices_bp
from api.routes.admin import admin_bp

# Standard logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# We removed static_folder and static_url_path because 
# Next.js now handles the static files.

app.url_map.strict_slashes = False

# Register your Blueprints
# These provide the /api/price/<category> and admin endpoints
app.register_blueprint(prices_bp)
app.register_blueprint(admin_bp)

@app.route('/api/debug')
def debug_check():
    return {"status": "alive", "handled_by": "flask"}

if __name__ == "__main__":
    # Use port 5328 to avoid conflicts with common services 
    # and match standard Vercel Python examples.
    app.run(debug=True, port=5328)