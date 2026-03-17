import os
from flask import Flask
from api.routes.prices import prices_bp
from api.routes.admin import admin_bp

app = Flask(__name__)
app.url_map.strict_slashes = False

# Register Blueprints
app.register_blueprint(prices_bp)
app.register_blueprint(admin_bp)

@app.route('/api/debug')
def debug_check():
    return {
        "status": "alive"
    }

# Local development entry
if __name__ == "__main__":
    app.run(debug=True, port=5000)