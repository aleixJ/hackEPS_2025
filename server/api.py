"""
Google AI Studio (Gemini) API Integration
"""
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GeminiAPI:
    """
    Wrapper class for Google's Gemini API (Google AI Studio)
    """
    
    def __init__(self):
        """Initialize the Gemini API with the API key from environment variables"""
        self.api_key = os.getenv('GOOGLE_API_KEY')
        
        if not self.api_key or self.api_key == 'your_api_key_here':
            raise ValueError(
                "Google API key not found. Please set GOOGLE_API_KEY in your .env file. "
                "Get your key from: https://aistudio.google.com/app/apikey"
            )
        
        # Configure the API
        genai.configure(api_key=self.api_key)
        
        # Initialize the model (using gemini-2.5-flash - stable, fast model)
        # Other good options: models/gemini-2.5-pro, models/gemini-2.0-flash
        self.model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    def generate_text(self, prompt: str, **kwargs) -> dict:
        """
        Generate text using the Gemini API
        
        Args:
            prompt (str): The input prompt for text generation
            **kwargs: Additional parameters for generation (temperature, max_tokens, etc.)
            
        Returns:
            dict: Response containing the generated text and metadata
        """
        try:
            # Set default generation config
            generation_config = {
                'temperature': kwargs.get('temperature', 0.7),
                'top_p': kwargs.get('top_p', 0.95),
                'top_k': kwargs.get('top_k', 40),
                'max_output_tokens': kwargs.get('max_output_tokens', 2048),
            }
            
            # Generate content
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            return {
                'success': True,
                'text': response.text,
                'candidates': len(response.candidates) if hasattr(response, 'candidates') else 1,
                'prompt_feedback': response.prompt_feedback if hasattr(response, 'prompt_feedback') else None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'text': None
            }
    
    def generate_text_stream(self, prompt: str, **kwargs):
        """
        Generate text using streaming for real-time responses
        
        Args:
            prompt (str): The input prompt for text generation
            **kwargs: Additional parameters for generation
            
        Yields:
            str: Chunks of generated text
        """
        try:
            generation_config = {
                'temperature': kwargs.get('temperature', 0.7),
                'top_p': kwargs.get('top_p', 0.95),
                'top_k': kwargs.get('top_k', 40),
                'max_output_tokens': kwargs.get('max_output_tokens', 2048),
            }
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
                stream=True
            )
            
            for chunk in response:
                if hasattr(chunk, 'text'):
                    yield chunk.text
                    
        except Exception as e:
            yield f"Error: {str(e)}"
    
    def chat(self, messages: list, **kwargs) -> dict:
        """
        Create a chat conversation with the model
        
        Args:
            messages (list): List of message dictionaries with 'role' and 'content'
            **kwargs: Additional parameters for generation
            
        Returns:
            dict: Response containing the chat reply
        """
        try:
            # Start a chat session
            chat = self.model.start_chat(history=[])
            
            # Process messages
            for message in messages[:-1]:  # All but the last message
                if message['role'] == 'user':
                    chat.send_message(message['content'])
            
            # Send the final message and get response
            final_message = messages[-1]['content'] if messages else ""
            response = chat.send_message(final_message)
            
            return {
                'success': True,
                'text': response.text,
                'history': chat.history
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'text': None
            }
