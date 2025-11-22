from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/osm-data')
def get_osm_data():
    return jsonify({
        'message': 'Hola desde el servidor!',
        'rectangle': {
            'north': 34.3344,
            'west': -118.1236,
            'south': 33.8624,
            'east': -118.6057
        }
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)

