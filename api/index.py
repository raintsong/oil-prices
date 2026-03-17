import os
from flask import Flask, send_from_directory

app = Flask(__name__)

# This finds the absolute path to your project root
# (one level up from where this script lives)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC_DIR = os.path.join(BASE_DIR, 'public')

@app.route('/')
def local_index():
    # If the file doesn't exist, this will now give a clearer error in your console
    if not os.path.exists(os.path.join(PUBLIC_DIR, 'index.html')):
        return f"Error: index.html not found in {PUBLIC_DIR}", 404
    return send_from_directory(PUBLIC_DIR, 'index.html')

@app.route('/api/hello')
def hello():
    return {"message": "API is working!"}

if __name__ == "__main__":
    app.run(debug=True, port=5000)