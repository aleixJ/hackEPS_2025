from flask import Flask, jsonify
from flask_cors import CORS
import json
from pathlib import Path

app = Flask(__name__)
CORS(app)

# Crear matriz 20x20 donde cada celda contiene una lista vacía
matrix_20x20 = [[[] for _ in range(20)] for _ in range(20)]

def load_crime_data():
    """
    Carga el JSON de criminalidad y llena la matriz 20x20.
    Cada celda contendrá una lista donde el índice 0 está vacío y el índice 1 
    contiene el valor de criminalidad del JSON.
    """
    json_path = Path(__file__).parent / 'city_stats' / 'jsons' / 'crime_matrix_20x20_20251122T194040Z.json'
    
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        crime_data = data[0]
        crime_matrix = crime_data['CrimeMatrix']
        
        # Verificar dimensiones y ajustar si es necesario
        rows = len(crime_matrix)
        cols = len(crime_matrix[0]) if rows > 0 else 0
        
        # Llenar la matriz 20x20
        for i in range(20):
            for j in range(20):
                # Ajustar índices si las dimensiones no coinciden
                row_idx = min(i, rows - 1) if rows > 0 else 0
                col_idx = min(j, cols - 1) if cols > 0 else 0
                
                # Índice 0: vacío, Índice 1: valor de criminalidad
                crime_value = crime_matrix[row_idx][col_idx] if rows > 0 and cols > 0 else 0.0
                matrix_20x20[i][j] = [None, crime_value]
        
        return {
            'success': True,
            'origin': {
                'north': crime_data['Norigin'],
                'west': crime_data['WOrigin']
            },
            'steps': {
                'vertical': crime_data['VerticalStep'],
                'horizontal': crime_data['HorizontalStep']
            },
            'dimensions': {
                'rows': rows,
                'cols': cols
            }
        }
    
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {json_path}")
        return {'success': False, 'error': 'Archivo no encontrado'}
    except Exception as e:
        print(f"Error al cargar datos de criminalidad: {e}")
        return {'success': False, 'error': str(e)}

# Cargar datos al iniciar el servidor
crime_info = load_crime_data()

@app.route('/api/osm-data')
def get_osm_data():
    return jsonify({
        'message': 'Hola desde el servidor!',
        'rectangle': {
            'north': 34.3344,
            'east': -118.1236,
            'south': 33.8624,
            'west': -118.6057
        },
        'matrix': matrix_20x20,
        'crime_info': crime_info
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)

