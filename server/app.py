from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import time
from api import GeminiAPI

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

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
        temperature = data.get('temperature', 0.7)
        max_tokens = data.get('max_tokens', 2048)
        
        # Generate response using Gemini API
        result = gemini_api.generate_text(
            prompt=user_prompt,
            temperature=temperature,
            max_output_tokens=max_tokens
        )
        
        if not result['success']:
            return jsonify({
                'error': f"API Error: {result.get('error', 'Unknown error')}"
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
