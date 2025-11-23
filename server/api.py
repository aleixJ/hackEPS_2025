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
        
        # Initialize the model (using gemini-2.0-flash - stable, fast model)
        # Other good options: models/gemini-2.5-flash, models/gemini-flash-latest
        self.model = genai.GenerativeModel('models/gemini-2.0-flash')
    
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
                'max_output_tokens': int(kwargs.get('max_output_tokens', 2048)),
            }
            
            # Safety settings to avoid blocking content
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE"
                },
            ]
            
            # Generate content
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            # Robust text extraction
            text_content = ""
            try:
                text_content = response.text
            except ValueError:
                # Handle cases where response.text fails (multipart or other issues)
                if response.candidates and response.candidates[0].content.parts:
                    text_content = "".join(part.text for part in response.candidates[0].content.parts)
            
            # Check if text is empty and why
            if not text_content:
                finish_reason = "UNKNOWN"
                if response.candidates:
                    finish_reason = response.candidates[0].finish_reason
                    
                print(f"DEBUG: Empty text content. Finish reason: {finish_reason}")
                if response.prompt_feedback:
                    print(f"DEBUG: Prompt feedback: {response.prompt_feedback}")
                
                # If finish_reason is MAX_TOKENS (2), it means we hit the limit.
                # But if text is empty, it's strange. 
                
                if finish_reason != 1: # 1 is STOP
                     return {
                        'success': False,
                        'error': f"Generation stopped. Finish reason: {finish_reason}",
                        'text': None
                    }

            return {
                'success': True,
                'text': text_content,
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
            
            # Safety settings to avoid blocking content
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE"
                },
            ]
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings=safety_settings,
                stream=True
            )
            
            for chunk in response:
                try:
                    text_chunk = chunk.text
                    yield text_chunk
                except ValueError:
                    # Handle cases where chunk.text fails (multipart or other issues)
                    if chunk.candidates and chunk.candidates[0].content.parts:
                        for part in chunk.candidates[0].content.parts:
                            yield part.text
                    
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
            
            # Safety settings to avoid blocking content
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE"
                },
            ]
            
            response = chat.send_message(
                final_message,
                safety_settings=safety_settings
            )
            
            # Robust text extraction
            text_content = ""
            try:
                text_content = response.text
            except ValueError:
                # Handle cases where response.text fails (multipart or other issues)
                if response.candidates and response.candidates[0].content.parts:
                    text_content = "".join(part.text for part in response.candidates[0].content.parts)
            
            return {
                'success': True,
                'text': text_content,
                'history': chat.history
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'text': None
            }
