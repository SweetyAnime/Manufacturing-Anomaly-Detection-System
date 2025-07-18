from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return '''
    <html>
    <head>
        <title>Test Flask App</title>
    </head>
    <body>
        <h1>Flask Application is Running!</h1>
        <p>If you see this message, Flask is working correctly.</p>
        <p>The full Manufacturing Anomaly Detection System is in app.py</p>
    </body>
    </html>
    '''

if __name__ == '__main__':
    print("Starting Flask test application...")
    print("Open your browser and go to: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
