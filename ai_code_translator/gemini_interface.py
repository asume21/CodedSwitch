"""
Google Gemini API interface for code translation and chat.
"""

import os
import logging
from typing import Optional, List, Dict, Any, Union
import re
import json
from google.oauth2 import service_account
import google.generativeai as genai

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GeminiInterface:
    """Interface for Google's Gemini API."""
    
    def __init__(self, api_key: str = None, model_name: str = "models/gemini-1.5-pro-001"):
        """Initialize the Gemini interface.
        
        Args:
            api_key: Optional Gemini API key
            model_name: Model name (default: models/gemini-1.5-pro-001)
        """
        self.model_name = model_name
        self.api_key = api_key
        self.model = None
        self.chat = None
        
        # Configure Gemini with API key
        try:
            if api_key:
                # Ensure API key is a string
                if not isinstance(api_key, str):
                    raise ValueError("API key must be a string")
                
                genai.configure(api_key=api_key)
                logger.info(f"Configured Gemini with API key for model: {model_name}")
            else:
                raise ValueError("No valid API key provided")
                
            # Initialize the model
            self.model = genai.GenerativeModel(
                model_name=model_name,
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 2048,
                },
                safety_settings=[
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_HATE_SPEECH",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    }
                ]
            )
            
            # Initialize chat session
            self.chat = self.model.start_chat(history=[])
            logger.info(f"Successfully initialized Gemini model: {model_name}")
            
        except ValueError as ve:
            logger.error(f"Value error during initialization: {str(ve)}")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Gemini interface: {str(e)}", exc_info=True)
            raise

    async def send_message(self, message: str) -> str:
        """Send a message to the Gemini model and get a response.
        
        Args:
            message: Message to send
            
        Returns:
            Response text
        
        Raises:
            ValueError: If the message is empty or None
            Exception: If there's an error sending the message
        """
        try:
            if not message or not isinstance(message, str):
                raise ValueError("Message must be a non-empty string")
                
            logger.debug(f"Sending message to Gemini: {message[:100]}...")
            
            response = await self.chat.send_message_async(
                message,
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "max_output_tokens": 2048,
                }
            )
            
            logger.debug(f"Received response from Gemini: {response.text[:100]}...")
            return str(response)
            
        except ValueError as ve:
            logger.error(f"Value error in send_message: {str(ve)}")
            raise
        except Exception as e:
            logger.error(f"Error sending message to Gemini: {str(e)}", exc_info=True)
            raise

    async def translate_code(self, code: str, source_lang: str, target_lang: str) -> str:
        """Translate code between programming languages.
        
        Args:
            code: Code to translate
            source_lang: Source language
            target_lang: Target language
            
        Returns:
            Translated code
            
        Raises:
            ValueError: If input parameters are invalid
            Exception: If translation fails
        """
        try:
            if not code or not isinstance(code, str):
                raise ValueError("Code must be a non-empty string")
            if not source_lang or not target_lang:
                raise ValueError("Language parameters cannot be empty")
                
            logger.info(f"Translating code from {source_lang} to {target_lang}")
            
            # Create translation prompt
            prompt = f"""Translate this {source_lang} code to {target_lang}:
            Maintain the same functionality and logic.
            Add comments to explain key parts.
            
            {source_lang} code:
            ```{source_lang}
            {code}
            ```
            
            Translate to {target_lang}:
            ```{target_lang}
            """
            
            logger.debug(f"Translation prompt: {prompt[:200]}...")
            
            # Get response
            response = await self.send_message(prompt)
            
            logger.debug(f"Translation response: {response[:200]}...")
            return response
            
        except ValueError as ve:
            logger.error(f"Value error in translation: {str(ve)}")
            raise
        except Exception as e:
            logger.error(f"Translation failed: {str(e)}", exc_info=True)
            raise

    async def generate_content(self, prompt: str, generation_config: dict = None) -> str:
        """Generate content using the Gemini model.
        
        Args:
            prompt: The prompt to generate content from
            generation_config: Optional generation configuration
            
        Returns:
            Generated content
            
        Raises:
            ValueError: If the prompt is empty or None
            Exception: If content generation fails
        """
        try:
            if not prompt or not isinstance(prompt, str):
                raise ValueError("Prompt must be a non-empty string")
                
            logger.debug(f"Generating content for prompt: {prompt[:100]}...")
            
            if not generation_config:
                generation_config = {
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "max_output_tokens": 2048,
                }
            
            response = await self.model.generate_content_async(
                prompt,
                generation_config=generation_config
            )
            
            # Get the first candidate's text
            if response.candidates and response.candidates[0].content:
                text = response.candidates[0].content.parts[0].text
                logger.debug(f"Generated content: {text[:100]}...")
                return text
            else:
                raise ValueError("No valid content generated")
            
        except ValueError as ve:
            logger.error(f"Value error in generate_content: {str(ve)}")
            raise
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}", exc_info=True)
            raise

    async def analyze_code(self, code: str, lang: str) -> dict:
        """Analyze code for potential improvements and issues.
        
        Args:
            code: Code to analyze
            lang: Programming language of the code
            
        Returns:
            Dictionary with analysis results
            
        Raises:
            ValueError: If input parameters are invalid
            Exception: If analysis fails
        """
        try:
            if not code or not isinstance(code, str):
                raise ValueError("Code must be a non-empty string")
            if not lang or not isinstance(lang, str):
                raise ValueError("Language must be a non-empty string")
                
            logger.info(f"Analyzing {lang} code")
            
            prompt = f"""Analyze this {lang} code for potential issues and improvements:
            {code}
            
            Please provide:
            1. Code quality assessment
            2. Potential improvements
            3. Best practices suggestions
            4. Any potential security concerns
            """
            
            response = await self.generate_content(prompt)
            
            logger.info(f"Analysis complete for {lang} code")
            return {
                "analysis": response,
                "success": True
            }
            
        except ValueError as ve:
            logger.error(f"Value error in analysis: {str(ve)}")
            return {
                "analysis": f"Error: {str(ve)}",
                "success": False
            }
            
        except Exception as e:
            logger.error(f"Error in analysis: {str(e)}", exc_info=True)
            return {
                "analysis": f"Error: {str(e)}",
                "success": False
            }

    async def get_fix_suggestion(self, vulnerability: str, code: str, lang: str) -> str:
        """Get a fix suggestion for a vulnerability.
        
        Args:
            vulnerability: Description of the vulnerability
            code: The code containing the vulnerability
            lang: Programming language
            
        Returns:
            Fix suggestion
            
        Raises:
            ValueError: If input parameters are invalid
            Exception: If suggestion generation fails
        """
        try:
            if not vulnerability or not isinstance(vulnerability, str):
                raise ValueError("Vulnerability description must be a non-empty string")
            if not code or not isinstance(code, str):
                raise ValueError("Code must be a non-empty string")
            if not lang or not isinstance(lang, str):
                raise ValueError("Language must be a non-empty string")
                
            logger.info(f"Generating fix suggestion for {lang} code")
            
            prompt = f"""Here is a {lang} code snippet with a vulnerability:
            {code}
            
            The vulnerability is: {vulnerability}
            
            Please provide a secure fix for this vulnerability. Include:
            1. The fixed code
            2. Explanation of the changes
            3. Security best practices used
            """
            
            response = await self.generate_content(prompt)
            
            logger.info(f"Fix suggestion generated for {lang} code")
            return response
            
        except ValueError as ve:
            logger.error(f"Value error in fix suggestion: {str(ve)}")
            raise
        except Exception as e:
            logger.error(f"Error generating fix suggestion: {str(e)}", exc_info=True)
            raise

    async def chat_response(self, message: str) -> str:
        """Generate a chat response."""
        try:
            print(f"DEBUG - GeminiInterface.chat_response called with: {message}")
            response = await self.send_message(message)
            
            print(f"DEBUG - Raw response from Gemini: {response}")
            return response
            
        except Exception as e:
            print(f"DEBUG - Error in GeminiInterface.chat_response: {str(e)}")
            return f"I apologize, but I encountered an error: {str(e)}"


class IntegratedTranslatorAI:
    def __init__(self, api_key: str = None, model: str = "models/gemini-1.5-pro-001"):
        """Initialize the IntegratedTranslatorAI."""
        self.credentials_path = None
        self.model_name = model
        
        # Initialize Gemini interface
        self.gemini = GeminiInterface(api_key=api_key, model_name=model)
        self.vulnerability_scanner = VulnerabilityScanner(premium_key=None, credentials_path=None)
        
        # Initialize the chatbot
        self.chatbot = ChatbotInterface(api_key=api_key, model=model)
        
        # Initialize the translator
        self.translator = TranslatorInterface(self.gemini)
        
        # Initialize the vulnerability scanner
        self.scanner = VulnerabilityScannerInterface(self.vulnerability_scanner)
    
    def _setup_chat(self):
        """Set up the chat with initial context and personality."""
        system_prompt = f"{self.context['personality']}\n\nCapabilities:\n"
        for capability in self.context['capabilities']:
            system_prompt += f"- {capability}\n"
            
        self.chat = self.model.start_chat(history=[{
            "role": "system",
            "content": system_prompt
        }])
    
    async def chat_response(self, message: str) -> str:
        """Generate a contextual response to user message."""
        try:
            # Add message to history
            self.context["conversation_history"].append({"role": "user", "content": message})
            
            # Check for user frustration indicators
            frustration_indicators = ["god", "damn", "!!", "???", "wtf", "idk", "i dont know"]
            is_frustrated = any(indicator in message.lower() for indicator in frustration_indicators)
            
            if is_frustrated:
                # Provide a helpful, guiding response
                response = await self.gemini.send_message(
                    f"""I notice you might be feeling frustrated. Let me help guide you:

1. I can translate code between languages like Python, JavaScript, Java, etc.
2. I can explain code and suggest improvements
3. I can help debug issues
4. I can analyze code for security vulnerabilities

What would you like to start with? For example:
- "Translate some Python code to JavaScript"
- "Help me understand this code"
- "Check my code for security issues"
""",
                    safety_settings={"categories": [{"category": "DANGEROUS", "threshold": "BLOCK_NONE"}]}
                )
            else:
                # Check for code-related keywords
                code_keywords = ["translate", "code", "function", "class", "bug", "error", "fix"]
                is_code_related = any(keyword in message.lower() for keyword in code_keywords)
                
                # Generate response based on context
                if is_code_related:
                    response = await self.gemini.send_message(
                        f"As a code translation expert, help with: {message}",
                        safety_settings={"categories": [{"category": "DANGEROUS", "threshold": "BLOCK_NONE"}]}
                    )
                else:
                    # General conversation
                    context = "You are Astutely, a helpful and friendly code translation assistant. " + \
                            "If the user seems unsure, guide them with specific examples and options."
                    response = await self.gemini.send_message(
                        context + "\n\nUser message: " + message,
                        safety_settings={"categories": [{"category": "DANGEROUS", "threshold": "BLOCK_NONE"}]}
                    )
            
            # Add response to history
            self.context["conversation_history"].append({"role": "assistant", "content": str(response)})
            
            return str(response)
            
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}"
    
    async def translate_code(self, source_code: str, target_language: str, use_neural: bool = True, use_llm: bool = True) -> str:
        """Translate code between programming languages."""
        try:
            prompt = f"""Translate this code to {target_language}. 
            Maintain functionality while following {target_language} best practices.
            If you see potential improvements, mention them after the translation.
            
            Source code:
            ```
            {source_code}
            ```"""
            
            response = await self.gemini.send_message(prompt)
            
            # Extract code from response
            code_match = re.search(r"```(?:\w+)?\n(.*?)```", str(response), re.DOTALL)
            if code_match:
                return code_match.group(1).strip()
            return str(response)
            
        except Exception as e:
            return f"Translation error: {str(e)}"
