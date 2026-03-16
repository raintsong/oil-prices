from flask import Flask

app = Flask(__name__) # This MUST be at the top level, not indented

@app.route('/')
def home():
    return "Hello World"

# REMOVE or move the 'if __name__ == "__main__":' block
# Vercel handles the "running" for you.
