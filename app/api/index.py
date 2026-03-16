from flask import Flask

app = Flask(__name__)

@app.route('/api/hello')
def hello():
    return {"message": "Hello from the Python API!"}

# Vercel needs this to handle the request
def handler(request):
    return app(request)