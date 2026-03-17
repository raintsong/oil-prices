import os
from flask import Flask, send_from_directory
from api.routes.prices import prices_bp
from api.routes.admin import admin_bp

app = Flask(__name__)
app.url_map.strict_slashes = False

# Register Blueprints
app.register_blueprint(prices_bp)
app.register_blueprint(admin_bp)


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)


@app.route('/')
def serve_index():
    # Check root first (Vercel production), then public/ (Local)
    for path in [ROOT_DIR, os.path.join(ROOT_DIR, 'public')]:
        if os.path.exists(os.path.join(path, 'index.html')):
            return send_from_directory(path, 'index.html')
    return "index.html not found", 404

@app.route('/admin')
def serve_admin():
    for path in [ROOT_DIR, os.path.join(ROOT_DIR, 'public')]:
        if os.path.exists(os.path.join(path, 'admin.html')):
            return send_from_directory(path, 'admin.html')
    return "admin.html not found", 404

@app.route('/api/debug')
def debug_check():
    return {
        "status": "alive",
        "root_dir": ROOT_DIR,
        "files_at_root": os.listdir(ROOT_DIR)
    }

# Local development entry
if __name__ == "__main__":
    app.run(debug=True, port=5000)