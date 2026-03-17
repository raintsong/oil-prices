import os
import logging
from flask import Flask, send_from_directory
from api.routes.prices import prices_bp
from api.routes.admin import admin_bp

# Standard logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='../public', static_url_path='/')
app.url_map.strict_slashes = False

# Register your API logic
app.register_blueprint(prices_bp)
app.register_blueprint(admin_bp)

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/admin')
def serve_admin():
    return send_from_directory(app.static_folder, 'admin.html')

if __name__ == "__main__":
    app.run(debug=True, port=5000)