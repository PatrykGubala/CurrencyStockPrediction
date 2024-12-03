from app import create_app
import os

app = create_app()

@app.route('/')
def index():
    return 'Hello from Flask with HTTPS and ngrok!'

if __name__ == '__main__':
    cert_file = os.path.join(os.path.dirname(__file__), 'cert.pem')
    key_file = os.path.join(os.path.dirname(__file__), 'key.pem')
    app.run(host='0.0.0.0', port=5000, debug=True, ssl_context=(cert_file, key_file))