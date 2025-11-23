from flask import Flask, jsonify
from flask_cors import CORS
import json
from pathlib import Path

app = Flask(__name__)
CORS(app)

# Crear matriz 20x20 donde cada celda contiene un vector [income, crimes, connectivity, noise, walkability, 0, wellbeing, ...]
# Formato de cada celda: [income, crimes, connectivity, noise, walkability, 0, wellbeing, 0, 0, 0]
matrix_LA_alldata_20x20 = [[[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0] for _ in range(20)] for _ in range(20)]

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
        
        # Llenar la matriz 20x20 unificada - índice 1 = crimes
        for i in range(20):
            for j in range(20):
                # Ajustar índices si las dimensiones no coinciden
                row_idx = min(i, rows - 1) if rows > 0 else 0
                col_idx = min(j, cols - 1) if cols > 0 else 0
                
                # Índice 1: valor de criminalidad
                crime_value = crime_matrix[row_idx][col_idx] if rows > 0 and cols > 0 else 0.0
                matrix_LA_alldata_20x20[i][j][1] = crime_value
        
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

def load_connectivity_data():
    """
    Carga el JSON de conectividad y llena una segunda matriz 20x20.
    Cada celda contendrá una lista donde el índice 0 está vacío y el índice 1 
    contiene el valor de conectividad del JSON.
    """
    json_path = Path(__file__).parent / 'city_stats' / 'jsons' / 'connectivity_matrix_20x20_20251122T214807Z.json'
    
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        connectivity_data = data[0]
        connectivity_matrix = connectivity_data['ConnectivityMatrix']
        
        # Verificar dimensiones
        rows = len(connectivity_matrix)
        cols = len(connectivity_matrix[0]) if rows > 0 else 0
        
        # Llenar la matriz unificada - índice 2 = connectivity
        for i in range(20):
            for j in range(20):
                row_idx = min(i, rows - 1) if rows > 0 else 0
                col_idx = min(j, cols - 1) if cols > 0 else 0
                
                # Índice 2: valor de conectividad
                connectivity_value = connectivity_matrix[row_idx][col_idx] if rows > 0 and cols > 0 else 0.0
                matrix_LA_alldata_20x20[i][j][2] = connectivity_value
        
        return {
            'success': True,
            'origin': {
                'north': connectivity_data['Norigin'],
                'west': connectivity_data['WOrigin']
            },
            'steps': {
                'vertical': connectivity_data['VerticalStep'],
                'horizontal': connectivity_data['HorizontalStep']
            },
            'dimensions': {
                'rows': rows,
                'cols': cols
            },
            'max_speed': connectivity_data.get('MaxSpeed', 1.0)
        }
    
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {json_path}")
        return {'success': False, 'error': 'Archivo no encontrado'}
    except Exception as e:
        print(f"Error al cargar datos de conectividad: {e}")
        return {'success': False, 'error': str(e)}

def load_income_data():
    """
    Carga el JSON de income y llena una tercera matriz 20x20.
    Cada celda contendrá una lista donde el índice 0 está vacío y el índice 1 
    contiene el valor de income del JSON.
    """
    json_path = Path(__file__).parent / 'city_stats' / 'jsons' / 'income_matrix_20x20.json'
    
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        income_data = data[0]
        income_matrix = income_data['matrix']
        
        # Verificar dimensiones
        rows = len(income_matrix)
        cols = len(income_matrix[0]) if rows > 0 else 0
        
        # Llenar la matriz unificada - índice 0 = income
        for i in range(20):
            for j in range(20):
                row_idx = min(i, rows - 1) if rows > 0 else 0
                col_idx = min(j, cols - 1) if cols > 0 else 0
                
                # Índice 0: valor de income
                income_value = income_matrix[row_idx][col_idx] if rows > 0 and cols > 0 else 0.0
                matrix_LA_alldata_20x20[i][j][0] = income_value
        
        return {
            'success': True,
            'origin': {
                'north': income_data['Norigin'],
                'west': income_data['WOrigin']
            },
            'steps': {
                'vertical': income_data['VerticalStep'],
                'horizontal': income_data['HorizontalStep']
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
        print(f"Error al cargar datos de income: {e}")
        return {'success': False, 'error': str(e)}

def load_noise_data():
    """
    Carga el JSON de noise y llena el índice 3 de la matriz unificada.
    Cada celda contendrá el valor de noise en el índice 3 del vector.
    """
    json_path = Path(__file__).parent / 'city_stats' / 'jsons' / 'noise_matrix_20x20_20251122T233126Z.json'
    
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        noise_data = data[0]
        noise_matrix = noise_data['NoiseMatrix']
        
        # Verificar dimensiones
        rows = len(noise_matrix)
        cols = len(noise_matrix[0]) if rows > 0 else 0
        
        # Llenar la matriz unificada - índice 3 = noise
        for i in range(20):
            for j in range(20):
                row_idx = min(i, rows - 1) if rows > 0 else 0
                col_idx = min(j, cols - 1) if cols > 0 else 0
                
                # Índice 3: valor de noise
                noise_value = noise_matrix[row_idx][col_idx] if rows > 0 and cols > 0 else 0.0
                matrix_LA_alldata_20x20[i][j][3] = noise_value
        
        return {
            'success': True,
            'origin': {
                'north': noise_data['Norigin'],
                'west': noise_data['WOrigin']
            },
            'steps': {
                'vertical': noise_data['VerticalStep'],
                'horizontal': noise_data['HorizontalStep']
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
        print(f"Error al cargar datos de noise: {e}")
        return {'success': False, 'error': str(e)}

def load_wellbeing_data():
    """
    Carga el JSON de wellbeing y llena el índice 6 de la matriz unificada.
    Cada celda contendrá el valor de wellbeing en el índice 6 del vector.
    """
    # Buscar el archivo más reciente de wellbeing
    json_dir = Path(__file__).parent / 'city_stats' / 'jsons'
    wellbeing_files = list(json_dir.glob('wellbeing_matrix_20x20_*.json'))
    
    if not wellbeing_files:
        print("Error: No se encontró ningún archivo de wellbeing")
        return {'success': False, 'error': 'Archivo no encontrado'}
    
    # Usar el archivo más reciente
    json_path = sorted(wellbeing_files)[-1]
    print(f"Cargando wellbeing desde: {json_path}")
    
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        wellbeing_data = data[0]
        wellbeing_matrix = wellbeing_data['WellbeingMatrix']
        
        # Verificar dimensiones
        rows = len(wellbeing_matrix)
        cols = len(wellbeing_matrix[0]) if rows > 0 else 0
        
        # Llenar la matriz unificada - índice 6 = wellbeing
        for i in range(20):
            for j in range(20):
                if i < rows and j < cols:
                    matrix_LA_alldata_20x20[i][j][6] = wellbeing_matrix[i][j]
        
        return {
            'success': True,
            'origin': {
                'north': wellbeing_data['Norigin'],
                'west': wellbeing_data['WOrigin']
            },
            'steps': {
                'vertical': wellbeing_data['VerticalStep'],
                'horizontal': wellbeing_data['HorizontalStep']
            },
            'dimensions': {
                'rows': rows,
                'cols': cols
            },
            'max_score': wellbeing_data.get('MaxScore', 1.0)
        }
    
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {json_path}")
        return {'success': False, 'error': 'Archivo no encontrado'}
    except Exception as e:
        print(f"Error al cargar datos de wellbeing: {e}")
        return {'success': False, 'error': str(e)}

def load_walkability_data():
    """
    Carga el JSON de walkability y llena el índice 4 de la matriz unificada.
    Cada celda contendrá el valor de walkability en el índice 4 del vector.
    """
    # Buscar el archivo más reciente de walkability
    json_dir = Path(__file__).parent / 'city_stats' / 'jsons'
    walkability_files = list(json_dir.glob('walkability_matrix_20x20_*.json'))
    
    if not walkability_files:
        print("Error: No se encontró ningún archivo de walkability")
        return {'success': False, 'error': 'Archivo no encontrado'}
    
    # Usar el archivo más reciente
    json_path = sorted(walkability_files)[-1]
    print(f"Cargando walkability desde: {json_path}")
    
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        walkability_data = data[0]
        walkability_matrix = walkability_data['WalkabilityMatrix']
        
        # Verificar dimensiones
        rows = len(walkability_matrix)
        cols = len(walkability_matrix[0]) if rows > 0 else 0
        
        # Llenar la matriz unificada - índice 4 = walkability
        for i in range(20):
            for j in range(20):
                if i < rows and j < cols:
                    matrix_LA_alldata_20x20[i][j][4] = walkability_matrix[i][j]
        
        return {
            'success': True,
            'origin': {
                'north': walkability_data['Norigin'],
                'west': walkability_data['WOrigin']
            },
            'steps': {
                'vertical': walkability_data['VerticalStep'],
                'horizontal': walkability_data['HorizontalStep']
            },
            'dimensions': {
                'rows': rows,
                'cols': cols
            },
            'max_score': walkability_data.get('MaxScore', 1.0)
        }
    
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {json_path}")
        return {'success': False, 'error': 'Archivo no encontrado'}
    except Exception as e:
        print(f"Error al cargar datos de walkability: {e}")
        return {'success': False, 'error': str(e)}

# Cargar datos al iniciar el servidor
# El orden importa: primero income (índice 0), luego crime (índice 1), luego connectivity (índice 2), luego noise (índice 3), luego walkability (índice 4), índice 5 reservado, luego wellbeing (índice 6)
income_info = load_income_data()
crime_info = load_crime_data()
connectivity_info = load_connectivity_data()
noise_info = load_noise_data()
walkability_info = load_walkability_data()
wellbeing_info = load_wellbeing_data()

@app.route('/api/osm-data')
def get_osm_data():
    # Información sobre los datos cargados
    data_info = {
        'income': income_info,
        'crime': crime_info,
        'connectivity': connectivity_info,
        'noise': noise_info,
        'walkability': walkability_info,
        'wellbeing': wellbeing_info
    }
    
    return jsonify({
        'message': 'Hola desde el servidor!',
        'rectangle': {
            'north': 34.3344,
            'east': -118.1236,
            'south': 33.8624,
            'west': -118.6057
        },
        'matrix_LA_alldata_20x20': matrix_LA_alldata_20x20,
        'data_info': data_info,
        'vector_format': {
            'description': 'Cada celda es un vector [income, crimes, connectivity, noise, walkability, 0, wellbeing]',
            'indices': {
                '0': 'income (0-1)',
                '1': 'crimes (0-1)',
                '2': 'connectivity (0-1)',
                '3': 'noise (0-1)',
                '4': 'walkability (0-1)',
                '5': 'reserved',
                '6': 'wellbeing (0-1)'
            }
        }
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)

