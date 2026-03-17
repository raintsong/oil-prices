import os
from flask import Flask, send_from_directory
from api.routes.prices import prices_bp
from api.routes.admin import admin_bp

app = Flask(__name__)
app.url_map.strict_slashes = False

# Register Blueprints
app.register_blueprint(prices_bp)
app.register_blueprint(admin_bp)

# --- DYNAMIC PATH RESOLUTION ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC_DIR = os.path.join(BASE_DIR, 'public')

@app.route('/')
def serve_index():
    if os.path.exists(os.path.join(PUBLIC_DIR, 'index.html')):
        return send_from_directory(PUBLIC_DIR, 'index.html')
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/admin')
def serve_admin():
    if os.path.exists(os.path.join(PUBLIC_DIR, 'admin.html')):
        return send_from_directory(PUBLIC_DIR, 'admin.html')
    return send_from_directory(BASE_DIR, 'admin.html')

# Local development entry
if __name__ == "__main__":
    app.run(debug=True, port=5000)