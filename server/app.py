from flask import Flask, jsonify
from flask_cors import CORS
import json
from pathlib import Path

app = Flask(__name__)
CORS(app)

# Crear matriz 20x20 donde cada celda contiene un vector [income, crimes, connectivity, noise, walkability, accessibility, wellbeing, ...]
# Formato de cada celda: [income, crimes, connectivity, noise, walkability, accessibility, wellbeing, 0, 0, 0, community_vibe]
matrix_LA_alldata_20x20 = [[[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0] for _ in range(20)] for _ in range(20)]

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

def load_accessibility_data():
    """
    Carga el JSON de accessibility y llena el índice 5 de la matriz unificada.
    Cada celda contendrá el valor de accessibility en el índice 5 del vector.
    """
    # Buscar el archivo más reciente de accessibility
    json_dir = Path(__file__).parent / 'city_stats' / 'jsons'
    accessibility_files = list(json_dir.glob('accessibility_matrix_20x20_*.json'))
    
    if not accessibility_files:
        print("Error: No se encontró ningún archivo de accessibility")
        return {'success': False, 'error': 'Archivo no encontrado'}
    
    # Usar el archivo más reciente
    json_path = sorted(accessibility_files)[-1]
    print(f"Cargando accessibility desde: {json_path}")
    
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        accessibility_data = data[0]
        accessibility_matrix = accessibility_data['AccessibilityMatrix']
        
        # Verificar dimensiones
        rows = len(accessibility_matrix)
        cols = len(accessibility_matrix[0]) if rows > 0 else 0
        
        # Llenar la matriz unificada - índice 5 = accessibility
        for i in range(20):
            for j in range(20):
                if i < rows and j < cols:
                    matrix_LA_alldata_20x20[i][j][5] = accessibility_matrix[i][j]
        
        return {
            'success': True,
            'origin': {
                'north': accessibility_data['Norigin'],
                'west': accessibility_data['WOrigin']
            },
            'steps': {
                'vertical': accessibility_data['VerticalStep'],
                'horizontal': accessibility_data['HorizontalStep']
            },
            'dimensions': {
                'rows': rows,
                'cols': cols
            },
            'max_score': accessibility_data.get('MaxScore', 1.0)
        }
    
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {json_path}")
        return {'success': False, 'error': 'Archivo no encontrado'}
    except Exception as e:
        print(f"Error al cargar datos de accessibility: {e}")
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

def load_mobility_data():
    """
    Carga el JSON de mobility y llena el índice 7 de la matriz unificada.
    Cada celda contendrá el valor de mobility en el índice 7 del vector.
    """
    # Buscar el archivo mobility
    json_dir = Path(__file__).parent / 'city_stats' / 'jsons'
    mobility_files = list(json_dir.glob('mobility*.json'))
    
    if not mobility_files:
        return {'success': False, 'error': 'Archivo mobility no encontrado'}
    
    # Usar el archivo más reciente
    json_path = sorted(mobility_files)[-1]
    print(f"Cargando mobility desde: {json_path}")
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        mobility_matrix = data[0]['MobilityMatrix']
        vertical_step = data[0]['VerticalStep']
        horizontal_step = data[0]['HorizontalStep']
        
        # Llenar el índice 7 de la matriz unificada
        for i in range(20):
            for j in range(20):
                matrix_LA_alldata_20x20[i][j][7] = mobility_matrix[i][j]
        
        print("✓ Datos de mobility cargados correctamente en índice 7")
        return {
            'success': True,
            'origin': f"N:{data[0]['Norigin']}, W:{data[0]['WOrigin']}",
            'steps': f"Vertical:{vertical_step}, Horizontal:{horizontal_step}",
            'dimensions': '20x20',
            'max_score': data[0].get('MaxScore', 'N/A')
        }
    
    except FileNotFoundError:
        return {'success': False, 'error': 'Archivo no encontrado'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def load_education_data():
    """
    Carga el JSON de education y llena el índice 8 de la matriz unificada.
    Cada celda contendrá el valor de education en el índice 8 del vector.
    """
    # Buscar el archivo education
    json_dir = Path(__file__).parent / 'city_stats' / 'jsons'
    education_files = list(json_dir.glob('education_matrix_*.json'))
    
    if not education_files:
        return {'success': False, 'error': 'Archivo education no encontrado'}
    
    # Usar el archivo más reciente
    json_path = sorted(education_files)[-1]
    print(f"Cargando education desde: {json_path}")
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # El archivo usa 'CrimeMatrix' en lugar de 'EducationMatrix'
        education_matrix = data[0].get('EducationMatrix') or data[0].get('CrimeMatrix')
        vertical_step = data[0]['VerticalStep']
        horizontal_step = data[0]['HorizontalStep']
        
        # Llenar el índice 8 de la matriz unificada
        for i in range(20):
            for j in range(20):
                matrix_LA_alldata_20x20[i][j][8] = education_matrix[i][j]
        
        print("✓ Datos de education cargados correctamente en índice 8")
        return {
            'success': True,
            'origin': f"N:{data[0]['Norigin']}, W:{data[0]['WOrigin']}",
            'steps': f"Vertical:{vertical_step}, Horizontal:{horizontal_step}",
            'dimensions': '20x20',
            'max_score': data[0].get('MaxScore', 'N/A')
        }
    
    except FileNotFoundError:
        return {'success': False, 'error': 'Archivo no encontrado'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def load_health_data():
    """
    Carga el JSON de health y llena el índice 10 de la matriz unificada.
    Cada celda contendrá el valor de health en el índice 10 del vector.
    """
    # Buscar el archivo más reciente de health
    json_dir = Path(__file__).parent / 'city_stats' / 'jsons'
    health_files = list(json_dir.glob('health_matrix_20x20_*.json'))
    
    if not health_files:
        print("Error: No se encontró ningún archivo de health")
        return {'success': False, 'error': 'Archivo no encontrado'}
    
    # Usar el archivo más reciente
    json_path = sorted(health_files)[-1]
    print(f"Cargando health desde: {json_path}")
    
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        health_data = data[0]
        health_matrix = health_data['HealthMatrix']
        
        # Verificar dimensiones
        rows = len(health_matrix)
        cols = len(health_matrix[0]) if rows > 0 else 0
        
        # Llenar la matriz unificada - índice 10 = health
        for i in range(20):
            for j in range(20):
                if i < rows and j < cols:
                    matrix_LA_alldata_20x20[i][j][10] = health_matrix[i][j]
        
        return {
            'success': True,
            'origin': {
                'north': health_data.get('Norigin', 0),
                'west': health_data.get('WOrigin', 0)
            },
            'steps': {
                'vertical': health_data.get('VerticalStep', 0),
                'horizontal': health_data.get('HorizontalStep', 0)
            },
            'dimensions': {
                'rows': rows,
                'cols': cols
            },
            'max_score': health_data.get('MaxScore', 1.0)
        }
    
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {json_path}")
        return {'success': False, 'error': 'Archivo no encontrado'}
    except Exception as e:
        print(f"Error al cargar datos de health: {e}")
        return {'success': False, 'error': str(e)}

def load_community_vibe_data():
    """
    Carga el JSON de community vibe y llena el índice 10 de la matriz unificada.
    Cada celda contendrá el valor de community vibe en el índice 10 del vector.
    """
    # Buscar el archivo más reciente de community_vibe
    json_dir = Path(__file__).parent / 'city_stats' / 'jsons'
    community_vibe_files = list(json_dir.glob('community_vibe_matrix_20x20_*.json'))
    
    if not community_vibe_files:
        print("Error: No se encontró ningún archivo de community_vibe")
        return {'success': False, 'error': 'Archivo no encontrado'}
    
    # Usar el archivo más reciente
    json_path = sorted(community_vibe_files)[-1]
    print(f"Cargando community_vibe desde: {json_path}")
    
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        community_vibe_data = data[0]
        community_vibe_matrix = community_vibe_data['CommunityVibMatrix']
        
        # Verificar dimensiones
        rows = len(community_vibe_matrix)
        cols = len(community_vibe_matrix[0]) if rows > 0 else 0
        
        # Llenar la matriz unificada - índice 9 = community_vibe
        for i in range(20):
            for j in range(20):
                if i < rows and j < cols:
                    matrix_LA_alldata_20x20[i][j][9] = community_vibe_matrix[i][j]
        
        return {
            'success': True,
            'origin': {
                'north': community_vibe_data.get('Norigin', 0),
                'west': community_vibe_data.get('WOrigin', 0)
            },
            'steps': {
                'vertical': community_vibe_data.get('VerticalStep', 0),
                'horizontal': community_vibe_data.get('HorizontalStep', 0)
            },
            'dimensions': {
                'rows': rows,
                'cols': cols
            },
            'max_score': max(max(row) for row in community_vibe_matrix) if rows > 0 and cols > 0 else 1.0
        }
    
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {json_path}")
        return {'success': False, 'error': 'Archivo no encontrado'}
    except Exception as e:
        print(f"Error al cargar datos de community_vibe: {e}")
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
# Cargar datos en orden: income(0), crime(1), connectivity(2), noise(3), walkability(4), accessibility(5), wellbeing(6), mobility(7), education(8), community_vibe(9), health(10)
income_info = load_income_data()
crimes_info = load_crime_data()
connectivity_info = load_connectivity_data()
noise_info = load_noise_data()
walkability_info = load_walkability_data()
accessibility_info = load_accessibility_data()
wellbeing_info = load_wellbeing_data()
mobility_info = load_mobility_data()
education_info = load_education_data()
health_info = load_health_data()
community_vibe_info = load_community_vibe_data()

@app.route('/api/osm-data')
def get_osm_data():
    # Información sobre los datos cargados
    data_info = {
        'income': income_info,
        'crimes': crimes_info,
        'connectivity': connectivity_info,
        'noise': noise_info,
        'walkability': walkability_info,
        'accessibility': accessibility_info,
        'wellbeing': wellbeing_info,
        'mobility': mobility_info,
        'education': education_info,
        'health': health_info,
        'community_vibe': community_vibe_info
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
            'description': 'Cada celda es un vector [income, crimes, connectivity, noise, walkability, accessibility, wellbeing, mobility, education, community_vibe, health]',
            'indices': {
                '0': 'income (0-1)',
                '1': 'crimes (0-1)',
                '2': 'connectivity (0-1)',
                '3': 'noise (0-1)',
                '4': 'walkability (0-1)',
                '5': 'accessibility (0-1)',
                '6': 'wellbeing (0-1)',
                '7': 'mobility (0-1)',
                '8': 'education (0-1)',
                '9': 'community_vibe (0-1)',
                '10': 'health (0-1)'
            }
        }
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)

