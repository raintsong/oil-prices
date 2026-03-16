import os
from flask import Flask, send_from_directory

app = Flask(__name__) # This MUST be at the top level, not indented

@app.route('/')
def serve_index():
    # This looks into the 'public' folder and sends the index.html
    # '..' is used because index.py is inside the /api folder
    root_dir = os.path.join(os.getcwd(), 'public')
    return send_from_directory(root_dir, 'index.html')

@app.route('/api/prices')
def get_prices():
    return {"brent_crude": 82.50}
# REMOVE or move the 'if __name__ == "__main__":' block
# Vercel handles the "running" for you.
