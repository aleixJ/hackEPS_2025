from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import time
from api import GeminiAPI
import json
from pathlib import Path
import numpy as np

app = Flask(__name__)

# Configuración CORS para permitir peticiones desde cualquier origen
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": False
    }
})

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# System prompt for Real Estate Recommendation Engine
SYSTEM_PROMPT_TEMPLATE = """Actua com un analista de dades expert per a una API de recomanació immobiliària. La teva tasca és analitzar una descripció en llenguatge natural d'un usuari (el "User Persona") i traduir les seves necessitats explícites i implícites en un vector numèric de preferències.

L'objectiu és generar un array de 11 valors flotants (entre 0.0 i 1.0).

### HEURÍSTIQUES D'ARQUETIPUS (ESTERIOTIPS)
Abans de puntuar, identifica si l'usuari encaixa en algun d'aquests arquetips i aplica les modificacions automàtiques:

A. "EL PERFIL LUXE / RIC":
   - Paraules clau: Inversor, exclusiu, pressupost il·limitat, acabats premium, privacitat.
   - Índex 1 (Preu): 1.0 (Busca valor alt).
   - Índex 2 (Seguretat): FORÇAR a 0.0 (Màxima seguretat/Criminalitat zero és prioritat absoluta).
   - Índex 10 (Vibra): 0.8 (Zona exclusiva).

B. "L'ESTUDIANT / PRESSUPOST AJUSTAT":
   - Paraules clau: Universitat, compartir pis, barat, estalvi, becari.
   - Índex 1 (Preu): 0.0 (Prioritat preu baix).
   - Índex 3 (Internet): 0.9 (Estudiar online).
   - Índex 8 (Mobilitat): 0.9 (Depèn del transport públic).
   - Índex 9 (Educació): 1.0.

C. "FAMÍLIA AMB NENS":
   - Paraules clau: Fills, col·legis, parc, tranquil·litat, seguretat.
   - Índex 2 (Seguretat): FORÇAR a 0.1 o 0.0 (Prioritat molt alta).
   - Índex 4 (Soroll): 0.9 (Volen silenci/zona residencial).
   - Índex 9 (Educació): 1.0.

D. "NÒMADA DIGITAL / TECHIE":
   - Paraules clau: WFH, remot, programador, fibra òptica, coworking.
   - Índex 3 (Connectivitat): 1.0 (No negociable).
   - Índex 5 (15 minuts): 0.8 (Cafeteries i serveis a prop).

E. "AMANT DE LA NATURA / MASCOTES":
   - Paraules clau: Gos, gat, muntanya, senderisme, aire lliure.
   - Índex 7 (Pet/Verd): 1.0.
   - Índex 4 (Soroll): 0.8 (Sol preferir tranquil·litat).

F. "GENT GRAN / JUBILATS":
   - Paraules clau: Jubilació, accessible, metges, pau.
   - Índex 6 (Accessibilitat): 1.0 (Ascensors, sense barreres).
   - Índex 11 (Salut): 1.0 (Hospitals a prop).
   - Índex 4 (Soroll): 1.0 (Màxima tranquil·litat).

### DEFINICIÓ DELS 11 ÍNDEXS I REGLES DE PONDERACIÓ

1. Viabilitat econòmica (Nivell de Preu): 
   - 0.0 = Busca el més barat possible (estudiants, precaris).
   - 1.0 = Busca luxe, preu alt no és problema (rics, inversors).
   - Valor Base: 0.2

2. Seguretat física i privacitat (ESCALA INVERSA):
   - Mesura la tolerància a la inseguretat/criminalitat.
   - 0.0 = NO TOLERA CRIMINALITAT (Requereix màxima seguretat: Rics, Famílies, Persones vulnerables).
   - 1.0 = Li és igual la seguretat (o busca risc).
   - Valor Base: 0.5

3. Connectivitat digital i WFH:
   - 1.0 = Imprescindible (Nòmades, Gamers).
   - Valor Base: 0.3

4. Absència de Soroll (Contaminació acústica):
   - 1.0 = Busca silenci total (Estudiosos, Gent Gran, Famílies).
   - 0.0 = Busca festa, centre ciutat sorollós.
   - Valor Base: 0.5

5. Ubicació de “15 minuts” (Serveis a peu):
   - 1.0 = Vol tot a peu (Urbanites sense cotxe).
   - Valor Base: 0.4

6. Accessibilitat (Mobilitat reduïda):
   - 1.0 = Cadira de rodes, mobilitat reduïda, edat molt avançada.
   - Valor Base: 0.0

7. Pet-friendly i Espais Verds:
   - 1.0 = Té gos o necessita bosc/parc.
   - Valor Base: 0.1

8. Mobilitat (Transport públic/Sostenible):
   - 1.0 = Depèn totalment del transport públic/bici (Estudiants, Ecologistes).
   - 0.0 = Utilitza cotxe privat exclusivament.
   - Valor Base: 0.3

9. Centres educatius:
   - 1.0 = Té fills en edat escolar o és estudiant universitari.
   - Valor Base: 0.0

10. “Vibra” Comunitària i Oci:
    - 1.0 = Busca ambient jove, bars, vida social intensa.
    - 0.0 = Indiferent.
    - Valor Base: 0.3

11. Centres mèdics i salut:
    - 1.0 = Malalties cròniques o edat avançada.
    - Valor Base: 0.1

INSTRUCCIONS FINALS:
- NO escriguis cap explicació.
- NO utilitzis blocs de codi markdown (```json).
- NO escriguis text introductori.
- Exemple de sortida vàlida: [0.9, 0.5, 0.8, 0.2, 0.4, 0.1, 0.05, 0.6, 0.3, 0.7, 0.4]

PERFIL DE L'USUARI A ANALITZAR:
"{TEXT_INPUT_USUARI}"

OUTPUT:"""

# Initialize Gemini API
try:
    gemini_api = GeminiAPI()
    print("✓ Gemini API initialized successfully")
except Exception as e:
    print(f"✗ Error initializing Gemini API: {e}")
    gemini_api = None

# Variable global para almacenar el vector de preferencias generado por la LLM
user_preference_vector = []

@app.route('/api/generate', methods=['POST'])
def generate():
    """
    Endpoint to process user prompts and return AI-generated output using Google's Gemini API.
    """
    global user_preference_vector
    
    try:
        # Check if API is initialized
        if gemini_api is None:
            return jsonify({
                'error': 'Gemini API not initialized. Please check your GOOGLE_API_KEY in .env file.'
            }), 500
        
        data = request.get_json()
        
        if not data or 'prompt' not in data:
            return jsonify({'error': 'No prompt provided'}), 400
        
        user_prompt = data['prompt']
        
        if not user_prompt.strip():
            return jsonify({'error': 'Prompt cannot be empty'}), 400
        
        # Get optional parameters
        temperature = data.get('temperature', 0.1)  # Lower temperature for more deterministic output
        max_tokens = data.get('max_tokens', 2048)
        
        # Construct the full prompt with the system instructions
        full_prompt = SYSTEM_PROMPT_TEMPLATE.replace("{TEXT_INPUT_USUARI}", user_prompt)
        
        # Generate response using Gemini API
        result = gemini_api.generate_text(
            prompt=full_prompt,
            temperature=temperature,
            max_output_tokens=max_tokens
        )
        
        if not result['success']:
            error_msg = result.get('error', 'Unknown error')
            print(f"✗ API Error: {error_msg}")
            return jsonify({
                'error': f"API Error: {error_msg}"
            }), 500
        
        # Parsear el vector de salida
        try:
            llm_output = result['text'].strip()
            # Intentar parsear como JSON array
            user_preference_vector = json.loads(llm_output)
            print(f"✓ Vector de preferencias guardado: {user_preference_vector}")
        except json.JSONDecodeError as e:
            print(f"⚠ Error parseando vector JSON: {e}")
            print(f"⚠ Output recibido: {llm_output}")
            user_preference_vector = []
        
        return jsonify({
            'output': result['text'],
            'vector': user_preference_vector,
            'timestamp': time.time(),
            'model': 'gemini-2.5-flash'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate/stream', methods=['POST'])
def generate_stream():
    """
    Endpoint for streaming AI-generated output (Server-Sent Events).
    """
    try:
        if gemini_api is None:
            return jsonify({
                'error': 'Gemini API not initialized. Please check your GOOGLE_API_KEY in .env file.'
            }), 500
        
        data = request.get_json()
        
        if not data or 'prompt' not in data:
            return jsonify({'error': 'No prompt provided'}), 400
        
        user_prompt = data['prompt']
        
        if not user_prompt.strip():
            return jsonify({'error': 'Prompt cannot be empty'}), 400
        
        def generate_response():
            for chunk in gemini_api.generate_text_stream(prompt=user_prompt):
                yield f"data: {chunk}\n\n"
        
        return Response(
            stream_with_context(generate_response()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Endpoint for chat-based interactions with conversation history.
    """
    try:
        if gemini_api is None:
            return jsonify({
                'error': 'Gemini API not initialized. Please check your GOOGLE_API_KEY in .env file.'
            }), 500
        
        data = request.get_json()
        
        if not data or 'messages' not in data:
            return jsonify({'error': 'No messages provided'}), 400
        
        messages = data['messages']
        
        if not isinstance(messages, list) or len(messages) == 0:
            return jsonify({'error': 'Messages must be a non-empty array'}), 400
        
        # Generate chat response
        result = gemini_api.chat(messages=messages)
        
        if not result['success']:
            return jsonify({
                'error': f"API Error: {result.get('error', 'Unknown error')}"
            }), 500
        
        return jsonify({
            'output': result['text'],
            'timestamp': time.time(),
            'model': 'gemini-1.5-flash'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

@app.route('/api/models', methods=['GET'])
def list_models():
    """List available Gemini models"""
    try:
        from api import GeminiAPI
        models = GeminiAPI.list_available_models()
        return jsonify({'models': models}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


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

def calculate_similarity(vector1, vector2, method='cosine'):
    """
    Calcula la similitud entre dos vectores usando diferentes métodos.
    
    Args:
        vector1: Vector de preferencias del usuario
        vector2: Vector de características de la celda
        method: 'cosine' para similitud coseno o 'ml' para Maximum Likelihood
    
    Retorna un valor entre 0 (totalmente diferentes) y 1 (idénticos).
    """
    try:
        v1 = np.array(vector1, dtype=float)
        v2 = np.array(vector2, dtype=float)
        
        if method == 'cosine':
            # Similitud coseno
            dot_product = np.dot(v1, v2)
            norm_v1 = np.linalg.norm(v1)
            norm_v2 = np.linalg.norm(v2)
            
            if norm_v1 == 0 or norm_v2 == 0:
                return 0.0
            
            similarity = dot_product / (norm_v1 * norm_v2)
            similarity = max(0.0, min(1.0, similarity))
            
        elif method == 'ml':
            # Maximum Likelihood - usando distribución gaussiana
            # Calculamos la probabilidad de que v2 sea generado por una distribución
            # centrada en v1
            
            # Diferencia entre vectores
            diff = v1 - v2
            
            # Distancia euclidiana
            euclidean_distance = np.linalg.norm(diff)
            
            # La distancia máxima posible entre dos vectores [0,1]^11 es sqrt(11)
            max_distance = np.sqrt(11)
            
            # Convertir distancia a similitud (1 - distancia_normalizada)
            # Cuando distancia = 0, similitud = 1
            # Cuando distancia = max_distance, similitud = 0
            similarity = 1.0 - (euclidean_distance / max_distance)
            
            # Aplicar una transformación gaussiana para suavizar
            # Esto da más peso a las similitudes altas
            sigma = 0.3  # Controla la "suavidad" de la curva
            similarity = np.exp(-((1 - similarity) ** 2) / (2 * sigma ** 2))
            
            # Asegurar que está en el rango [0, 1]
            similarity = max(0.0, min(1.0, similarity))
            
        elif method == 'manhattan':
            # Manhattan Distance (L1)
            # Suma de diferencias absolutas
            manhattan_distance = np.sum(np.abs(v1 - v2))
            
            # La distancia máxima posible es 11 (cada componente puede diferir en 1)
            max_distance = 11.0
            
            # Convertir a similitud
            similarity = 1.0 - (manhattan_distance / max_distance)
            similarity = max(0.0, min(1.0, similarity))
            
        elif method == 'weighted':
            # Weighted Euclidean Distance
            # Pesos para cada dimensión (ajustables según importancia)
            weights = np.array([
                1.2,  # 0: income (más peso)
                1.5,  # 1: crimes (MUY importante - más peso)
                1.0,  # 2: connectivity
                1.0,  # 3: noise
                0.8,  # 4: walkability
                1.3,  # 5: accessibility (importante)
                0.9,  # 6: wellbeing
                0.9,  # 7: mobility
                1.1,  # 8: education
                0.8,  # 9: community_vibe
                1.2   # 10: health (importante)
            ])
            
            # Calcular distancia ponderada
            diff = v1 - v2
            weighted_distance = np.sqrt(np.sum(weights * (diff ** 2)))
            
            # Normalizar por la máxima distancia ponderada posible
            max_distance = np.sqrt(np.sum(weights))
            
            # Convertir a similitud
            similarity = 1.0 - (weighted_distance / max_distance)
            
            # Aplicar transformación suave
            similarity = np.exp(-((1 - similarity) ** 2) / 0.2)
            similarity = max(0.0, min(1.0, similarity))
            
        elif method == 'pearson':
            # Pearson Correlation Coefficient
            # Mide correlación lineal entre vectores
            
            # Evitar división por cero
            if np.std(v1) == 0 or np.std(v2) == 0:
                return 0.0
            
            # Calcular correlación de Pearson
            correlation = np.corrcoef(v1, v2)[0, 1]
            
            # Manejar NaN (puede ocurrir con vectores constantes)
            if np.isnan(correlation):
                return 0.0
            
            # Convertir de [-1, 1] a [0, 1]
            # correlation = -1 (totalmente opuestos) -> similarity = 0
            # correlation = 0 (sin correlación) -> similarity = 0.5
            # correlation = 1 (idénticos) -> similarity = 1
            similarity = (correlation + 1) / 2
            similarity = max(0.0, min(1.0, similarity))
            
        else:
            # Método por defecto: coseno
            return calculate_similarity(vector1, vector2, 'cosine')
        
        return float(similarity)
        
    except Exception as e:
        print(f"Error calculando similitud: {e}")
        return 0.0

def generate_heatmap(method='cosine'):
    """
    Genera un mapa de calor comparando user_preference_vector con cada celda de la matriz.
    
    Args:
        method: 'cosine' para similitud coseno o 'ml' para Maximum Likelihood
    
    Retorna una matriz 20x20 con valores de similitud entre 0 y 1.
    """
    global user_preference_vector
    
    if not user_preference_vector or len(user_preference_vector) != 11:
        return None
    
    heatmap = [[0.0 for _ in range(20)] for _ in range(20)]
    
    for i in range(20):
        for j in range(20):
            cell_vector = matrix_LA_alldata_20x20[i][j]
            similarity = calculate_similarity(user_preference_vector, cell_vector, method)
            heatmap[i][j] = similarity
    
    return heatmap

@app.route('/api/heatmap', methods=['GET'])
def get_heatmap():
    """
    Endpoint que retorna el mapa de calor basado en las preferencias del usuario.
    
    Query params:
        method: 'cosine' (default), 'ml', 'manhattan', 'weighted', o 'pearson'
    """
    global user_preference_vector
    
    if not user_preference_vector or len(user_preference_vector) != 11:
        return jsonify({
            'error': 'No hay vector de preferencias válido. Primero genera un vector usando /api/generate'
        }), 400
    
    # Obtener método desde query params
    method = request.args.get('method', 'cosine')
    if method not in ['cosine', 'ml', 'manhattan', 'weighted', 'pearson']:
        method = 'cosine'
    
    heatmap = generate_heatmap(method)
    
    if heatmap is None:
        return jsonify({
            'error': 'Error generando mapa de calor'
        }), 500
    
    # Encontrar el valor máximo y mínimo para normalización si es necesario
    flat_values = [val for row in heatmap for val in row]
    max_similarity = max(flat_values) if flat_values else 1.0
    min_similarity = min(flat_values) if flat_values else 0.0
    
    return jsonify({
        'heatmap': heatmap,
        'user_vector': user_preference_vector,
        'method': method,
        'stats': {
            'max_similarity': max_similarity,
            'min_similarity': min_similarity,
            'mean_similarity': sum(flat_values) / len(flat_values) if flat_values else 0.0
        },
        'rectangle': {
            'north': 34.3344,
            'east': -118.1236,
            'south': 33.8624,
            'west': -118.6057
        }
    })

@app.route('/api/update-vector', methods=['POST'])
def update_vector():
    """
    Endpoint para actualizar el vector de preferencias del usuario.
    """
    global user_preference_vector
    
    try:
        data = request.get_json()
        
        if not data or 'vector' not in data:
            return jsonify({'error': 'No vector provided'}), 400
        
        new_vector = data['vector']
        
        # Validar que sea un array de 11 elementos
        if not isinstance(new_vector, list) or len(new_vector) != 11:
            return jsonify({'error': 'Vector must have exactly 11 elements'}), 400
        
        # Validar que todos los valores estén entre 0 y 1
        for val in new_vector:
            if not isinstance(val, (int, float)) or val < 0 or val > 1:
                return jsonify({'error': 'All vector values must be between 0 and 1'}), 400
        
        # Actualizar el vector global
        user_preference_vector = new_vector
        print(f"✓ Vector actualizado manualmente: {user_preference_vector}")
        
        return jsonify({
            'success': True,
            'vector': user_preference_vector
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
    # Para producción en EC2 - escuchar en todas las interfaces
    app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)
