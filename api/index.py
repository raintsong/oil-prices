import os
from flask import Flask, send_from_directory
from api.routes.prices import prices_bp
from api.routes.admin import admin_bp

app = Flask(__name__)
app.url_map.strict_slashes = False

# Register Blueprints
app.register_blueprint(prices_bp)
app.register_blueprint(admin_bp)
# --- DYNAMIC PATH RESOLUTION (The Vercel Fix) ---
# BASE_DIR is where index.py lives (the api/ folder)
# We go up one level to get to the project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_static_file(filename):
    """
    Vercel flattens the 'public' folder into the root during deployment.
    This helper checks the root first, then the public folder.
    """
    # 1. Check project root (where Vercel puts static assets)
    root_path = os.path.join(BASE_DIR, filename)
    if os.path.exists(root_path):
        return BASE_DIR, filename
    
    # 2. Check public folder (for local development)
    public_path = os.path.join(BASE_DIR, 'public', filename)
    if os.path.exists(public_path):
        return os.path.join(BASE_DIR, 'public'), filename
        
    return BASE_DIR, filename # Fallback

@app.route('/')
def serve_index():
    directory, file = get_static_file('index.html')
    return send_from_directory(directory, file)

@app.route('/admin')
def serve_admin():
    directory, file = get_static_file('admin.html')
    return send_from_directory(directory, file)


# Local development entry
if __name__ == "__main__":
    app.run(debug=True, port=5000)