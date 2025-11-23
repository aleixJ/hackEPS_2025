from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import time
from api import GeminiAPI

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# System prompt for Real Estate Recommendation Engine
SYSTEM_PROMPT_TEMPLATE = """Actua com un analista de dades expert per a una API de recomanació immobiliària (Real Estate Recommendation Engine). La teva tasca és analitzar una descripció en llenguatge natural d'un usuari (el "User Persona") i traduir les seves necessitats explícites i implícites en un vector numèric de preferències.

L'objectiu és generar un array de 11 valors flotants (entre 0.0 i 1.0). Cada valor representa la importància d'un aspecte concret per a aquest usuari.

Aquests són els 11 aspectes (índexs 0-10) i les seves regles de ponderació:

1. Viabilitat econòmica total (Preu alt): 
   - Si l'usuari té pressupost ajustat = 0.1. Si és ric = 1.0.
   - Valor Base (Mínim): 0

2. Seguretat física i privacitat:
   - Important per a famílies, famosos o persones vulnerables.
   - Valor Base (Mínim): 0.2

3. Connectivitat digital i entorn WFH (Teletreball):
   - Crucial per a "Nòmades digitals" o treballs tecnològics.
   - Valor Base (Mínim): 0.1

4. Aïllament acústic (Silenci):
   - Important per a gent gran, estudiants o gent sensible al soroll.
   - Valor Base (Mínim): 0.1

5. Ubicació de “15 minuts” i caminabilitat:
   - Importància de tenir serveis a prop sense agafar cotxe.
   - Valor Base (Mínim): 0.1

6. Accessibilitat i disseny universal:
   - IMPRESCINDIBLE (1.0) si s'esmenta cadira de rodes o mobilitat reduïda.
   - Valor Base (Mínim): 0.1

7. Política pet-friendly i espais verds:
   - Si té gos/gat = 0.9 o 1.0. Si vol naturesa = 0.9 o 1.0.
   - Valor Base (Mínim): 0

8. Mobilitat híbrida (Transport públic/Bici/Cotxe elèctric):
   - Important si no vol conduir o és ecologista.
   - Valor Base (Mínim): 0.1

9. Espai exterior privat (Terrassa/Jardí):
   - Valor Base (Mínim): 0.1

10. “Vibra” de la comunitat i comoditats funcionals (Ambient jove, famílies, luxe, etc.):
    - Valor Base (Mínim): 0.1

11. Centres mèdics i salut:
    - Proximitat a hospitals.
    - Aquest valor és globalment important per a tothom.
    - Valor Base (Mínim): 0.2

INSTRUCCIONS DE CÀLCUL:
1. Comença amb el "Valor Base" per a cada aspecte.
2. Analitza el text de l'usuari. Si l'usuari menciona explícitament una necessitat, augmenta significativament el valor (fins a 0.9 o 1.0).
3. Si la necessitat és implícita pel seu perfil (ex: "sóc estudiant" implica necessitat de preu baix i bon internet), augmenta moderadament el valor (+0.3 a +0.5).
4. Mai baixis del Valor Base.
5. El valor màxim és 1.0.

INSTRUCCIONS DE FORMAT DE SORTIDA (STRICT):
- La teva resposta ha de contenir ÚNICAMENT l'array JSON.
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

@app.route('/api/generate', methods=['POST'])
def generate():
    """
    Endpoint to process user prompts and return AI-generated output using Google's Gemini API.
    """
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
        
        return jsonify({
            'output': result['text'],
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
