"""
Integrated AI for code translation and chat.
"""

import os
import logging
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from ai_code_translator.inference import translate_code as rule_based_translate
from ai_code_translator.gemini_interface import GeminiInterface
from ai_code_translator.chatbot_interface import ChatbotInterface
from ai_code_translator.translator_interface import TranslatorInterface
from ai_code_translator.security.vulnerability_scanner import VulnerabilityScanner
from ai_code_translator.security.vulnerability_scanner_interface import VulnerabilityScannerInterface
from ai_code_translator.security.vulnerability import Vulnerability, Severity, Confidence
import json
import datetime
import sys
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PremiumManager:
    """Manages premium features and licensing."""
    
    def __init__(self):
        """Initialize the premium manager."""
        self.premium_status = False
        self.license_info = None
        self.license_key = None
        self._load_license()
    
    def is_premium(self) -> bool:
        """Check if premium features are enabled."""
        return self.premium_status and self.license_key is not None
    
    def get_license_info(self) -> dict:
        """Get license information."""
        return self.license_info or {}
    
    def get_license_key(self) -> str:
        """Get the current license key."""
        return self.license_key or ""
    
    def _load_license(self):
        """Load license information from file."""
        try:
            license_file = os.path.join(os.path.dirname(__file__), "license.json")
            if os.path.exists(license_file):
                with open(license_file, "r") as f:
                    data = json.load(f)
                    self.license_info = data
                    self.license_key = data.get("key")
                    self.premium_status = data.get("status", False)
            else:
                logger.warning("No license file found. Running in basic mode.")
        except Exception as e:
            logger.error(f"Error loading license: {str(e)}")
    
    def show_upgrade_dialog(self):
        """Show the upgrade dialog."""
        # Implementation for showing upgrade dialog
        pass
    
    def _activate_premium(self, dialog):
        """Activate premium features."""
        try:
            # Validate and activate license
            if dialog and hasattr(dialog, "license_key"):
                self.license_key = dialog.license_key.get()
                # Save license info
                license_data = {
                    "key": self.license_key,
                    "status": True,
                    "activation_date": datetime.datetime.now().isoformat()
                }
                with open(os.path.join(os.path.dirname(__file__), "license.json"), "w") as f:
                    json.dump(license_data, f)
                self.premium_status = True
                self.license_info = license_data
                logger.info("Premium features activated successfully")
                return True
        except Exception as e:
            logger.error(f"Error activating premium features: {str(e)}")
        return False

class IntegratedTranslatorAI:
    def __init__(self, api_key: str = None, model_name: str = "models/gemini-1.5-pro-001"):
        """Initialize the IntegratedTranslatorAI."""
        self.model_name = model_name
        self.gemini = None
        self.chatbot = None
        self.translator = None
        self.scanner = None
        self.premium_manager = None
        
        # Initialize Gemini interface
        try:
            if api_key is None:
                api_key = os.environ.get("GEMINI_API_KEY")
                if api_key is None:
                    raise Exception("API key not provided")
            self.gemini = GeminiInterface(
                api_key=api_key,
                model_name=model_name
            )
            logger.info(f"Successfully initialized Gemini interface with model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini interface: {str(e)}")
            raise

        # Initialize components
        self.rule_based_translator = None
        self.neural_translator = None
        self.llm_interface = None
        
        # Initialize premium manager
        self.premium_manager = PremiumManager()
        
        # Initialize vulnerability scanner
        self.vulnerability_scanner = VulnerabilityScanner()
        self.scanner = self.vulnerability_scanner
        
        # Initialize the chatbot with API key and model
        self.chatbot = ChatbotInterface(api_key=api_key, model=model_name)
        
        # Initialize the translator with Gemini interface
        self.translator = TranslatorInterface(self.gemini)
        
    async def scan_code(self, code: str, language: str) -> List[Dict[str, Any]]:
        """
        Scan code for vulnerabilities.
        
        Args:
            code: Source code to scan
            language: Programming language of the code
            
        Returns:
            List of detected vulnerabilities
            
        Raises:
            ValueError: If input parameters are invalid
            Exception: If scanning fails
        """
        try:
            if not code or not isinstance(code, str):
                raise ValueError("Code must be a non-empty string")
            if not language or not isinstance(language, str):
                raise ValueError("Language must be a non-empty string")
                
            logger.info(f"Starting vulnerability scan for {language} code")
            logger.debug(f"Code length: {len(code)} characters")
            
            if not self.vulnerability_scanner:
                logger.warning("Vulnerability scanner not initialized")
                return []
                
            # First do pattern-based scanning
            vulnerabilities = await self.vulnerability_scanner.scan_code(code, language)
            
            # Then get Gemini-enhanced analysis
            try:
                analysis = await self.gemini.analyze_code(code, language)
                if analysis.get("success"):
                    # Add Gemini's findings to the vulnerabilities list
                    gemini_vulns = self._parse_gemini_analysis(analysis["analysis"])
                    vulnerabilities.extend(gemini_vulns)
            except Exception as e:
                logger.warning(f"Gemini analysis failed: {str(e)}")
            
            logger.info(f"Scan complete. Found {len(vulnerabilities)} vulnerabilities")
            
            return [
                {
                    "line": vuln.line_number,
                    "category": vuln.category,
                    "severity": vuln.severity.value,
                    "description": vuln.description,
                    "code": vuln.code_snippet,
                    "fix": await self._get_fix_suggestion(vuln, code, language),
                    "confidence": vuln.confidence
                }
                for vuln in vulnerabilities
            ]
            
        except ValueError as ve:
            logger.error(f"Value error in scan: {str(ve)}")
            return []
            
        except Exception as e:
            logger.error(f"Error scanning code: {str(e)}", exc_info=True)
            return []

    def scan_vulnerabilities(self, code: str, language: str):
        """
        Synchronous wrapper for vulnerability scanning.
        This method wraps the async scan_code method for GUI compatibility.
        
        Args:
            code: Source code to scan
            language: Programming language
            
        Returns:
            List of vulnerability objects with severity, line_number, category, description
        """
        try:
            import asyncio
            
            # Run the async scan_code method synchronously
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If loop is already running, create a new one
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, self.scanner.scan_code(code, language.lower()))
                        vulnerabilities = future.result()
                else:
                    vulnerabilities = loop.run_until_complete(self.scanner.scan_code(code, language.lower()))
            except RuntimeError:
                # No event loop running, create a new one
                vulnerabilities = asyncio.run(self.scanner.scan_code(code, language.lower()))
            
            # The vulnerabilities are already in the correct dictionary format
            # from the scan_code method, so we can return them directly
            logger.info(f"Found {len(vulnerabilities)} vulnerabilities")
            return vulnerabilities
            
        except Exception as e:
            logger.error(f"Error in vulnerability scanning: {str(e)}", exc_info=True)
            # Return empty list on error to prevent GUI crashes
            return []

    async def _get_fix_suggestion(self, vulnerability: Vulnerability, code: str, language: str) -> str:
        """Get a fix suggestion for a vulnerability."""
        try:
            return await self.gemini.get_fix_suggestion(
                vulnerability.description,
                code,
                language
            )
        except Exception as e:
            logger.warning(f"Failed to get fix suggestion: {str(e)}")
            return "Fix the vulnerability according to security best practices"

    def _parse_gemini_analysis(self, analysis: str) -> List[Vulnerability]:
        """Parse Gemini's analysis and convert it to Vulnerability objects."""
        try:
            # This is a simplified parser - in a real implementation you might want
            # to use a more sophisticated parsing approach
            vulnerabilities = []
            
            # Split the analysis into sections
            sections = analysis.split("\n\n")
            
            for section in sections:
                if "vulnerability" in section.lower():
                    # Try to extract relevant information
                    vuln = Vulnerability()
                    vuln.description = section
                    vuln.severity = Severity.MEDIUM
                    vuln.confidence = Confidence.MEDIUM
                    vulnerabilities.append(vuln)
            
            return vulnerabilities
            
        except Exception as e:
            logger.warning(f"Failed to parse Gemini analysis: {str(e)}")
            return []

    def use_gemini_model(self, model_name: str = "models/gemini-1.5-pro-001") -> bool:
        """
        Switch to using Gemini model for LLM capabilities.
        
        Args:
            model_name: Name of the Gemini model to use
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Update the existing Gemini interface
            self.gemini.model_name = model_name
            
            # Reinitialize the model with new settings
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 2048,
            }
            
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM",
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM",
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM",
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM",
                },
            ]
            
            # Reinitialize the Gemini model
            self.gemini.model = genai.GenerativeModel(
                model=model_name,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            # Restart the chat session
            self.gemini.chat = self.gemini.model.start_chat(history=[])
            
            # Update the chatbot with the new model
            self.chatbot = ChatbotInterface(self.gemini)
            
            logger.info(f"Successfully switched to model: {model_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to switch model: {str(e)}")
            return False

    def test_api_connection(self):
        """Test the Gemini API connection."""
        try:
            # Test the model by sending a simple request
            test_prompt = "Hello, how are you?"
            response = self.gemini.generate(test_prompt)
            
            if response:
                logger.info("API connection test successful")
                return True
            else:
                raise Exception("No response from API")
                
        except Exception as e:
            logger.error(f"API test failed: {str(e)}")
            return False

    def _initialize_chatbot(self):
        """Initialize or update the chatbot with the current LLM interface."""
        from ai_code_translator.chatbot import Chatbot
        
        # Determine which LLM interface to use
        llm_interface = self.gemini_interface
            
        # Initialize or update the chatbot
        if not hasattr(self, 'chatbot') or self.chatbot is None:
            self.chatbot = Chatbot(
                model_path=None,
                llm_interface=llm_interface
            )
        else:
            # Update the existing chatbot with the new LLM interface
            self.chatbot.llm_interface = llm_interface
    
    def get_current_provider(self) -> str:
        """
        Get the current LLM provider.
        
        Returns:
            "gemini" or "none"
        """
        if self.llm_interface == self.gemini_interface:
            return "gemini"
        else:
            return "none"
    
    def translate_code(self, source_code: str, target_language: str = "javascript", use_neural: bool = False, use_llm: bool = True) -> str:
        """
        Synchronous wrapper for code translation.
        Translates source code to target language using Gemini LLM.
        
        Args:
            source_code: Source code to translate
            target_language: Target language (default: javascript)
            use_neural: Whether to use neural translation model (deprecated)
            use_llm: Whether to use LLM for translation (default: True)
            
        Returns:
            Translated code as string
        """
        try:
            if not source_code or not isinstance(source_code, str):
                raise ValueError("Source code must be a non-empty string")
            if not target_language or not isinstance(target_language, str):
                raise ValueError("Target language must be a non-empty string")
                
            logger.info(f"Starting translation to {target_language}")
            
            # Use Gemini for translation
            if use_llm and self.gemini:
                prompt = f"""
                Translate this code to {target_language}:
                
                {source_code}
                
                Ensure the translation:
                1. Maintains the same functionality
                2. Follows {target_language} best practices
                3. Includes proper error handling
                4. Uses idiomatic {target_language} constructs
                5. Includes appropriate comments and documentation
                
                Return only the translated code without explanations.
                """
                
                response = self.gemini.model.generate_content(prompt)
                translated_code = response.text
                
                # Clean up the response to extract just the code
                if "```" in translated_code:
                    # Extract code from markdown code blocks
                    import re
                    code_blocks = re.findall(r'```(?:\w+)?\n(.*?)```', translated_code, re.DOTALL)
                    if code_blocks:
                        translated_code = code_blocks[-1].strip()
                
                logger.info(f"Translation completed successfully to {target_language}")
                return translated_code
            
            # Fallback to rule-based translation if LLM is not used
            return rule_based_translate(source_code, target_language)
            
        except Exception as e:
            logger.error(f"Error in translation: {str(e)}")
            return f"// Translation error: {str(e)}\n{source_code}"

    async def get_translation_feedback(self, source_code: str, translated_code: str, source_lang: str = "python", target_lang: str = "javascript") -> str:
        """
        Get feedback on a code translation.
        
        Args:
            source_code: Original source code
            translated_code: Translated code
            source_lang: Source language
            target_lang: Target language
            
        Returns:
            Feedback on the translation
        """
        try:
            if not source_code or not translated_code:
                return "No translation to analyze"
                
            prompt = f"""
            Analyze this translation from {source_lang} to {target_lang}:
            
            Original:
            {source_code}
            
            Translated:
            {translated_code}
            
            Please provide feedback on:
            1. Code quality and readability
            2. Functionality preservation
            3. Language-specific idioms
            4. Error handling
            5. Performance considerations
            """
            
            feedback = await self.gemini.generate_content(prompt)
            return feedback
            
        except Exception as e:
            logger.error(f"Error getting translation feedback: {str(e)}")
            return "Error generating feedback"
    
    def _validate_translation(
        self,
        source_code: str,
        translated_code: str,
        source_lang: str,
        target_lang: str
    ) -> None:
        """
        Validate the translation result.
        
        Args:
            source_code: Original source code
            translated_code: Translated code
            source_lang: Source language
            target_lang: Target language
        """
        # TO DO: Implement validation logic
        pass
    
    def _code_sanity_check(self, code: str, lang: str) -> bool:
        """
        Perform a basic sanity check on the code.
        
        Args:
            code: Code to check
            lang: Language of the code
            
        Returns:
            True if the code passes the sanity check, False otherwise
        """
        # TO DO: Implement sanity check logic
        return True
    
    def chat(self, message: str) -> str:
        """
        Chat with the AI assistant.
        
        Args:
            message: User message
            
        Returns:
            Assistant's response
        """
        print(f"DEBUG - IntegratedTranslatorAI.chat called with message: {message}")
        
        # Add message to conversation history
        if not hasattr(self, 'conversation_history') or self.conversation_history is None:
            self.conversation_history = []
        self.conversation_history.append({"role": "user", "content": message})
        
        # Simple direct approach to ensure functionality
        try:
            # Use the chat session directly if available
            if hasattr(self, 'chat_session') and self.chat_session:
                print("DEBUG - Using self.chat_session directly")
                response = self.chat_session.send_message(message)
                response_text = response.text
                print(f"DEBUG - Chat session response: {response_text[:100]}...")
            # Fallback to direct model if chat session not available
            elif hasattr(self, 'model') and self.model:
                print("DEBUG - Using self.model directly")
                response = self.model.generate_content(
                    f"""You are Astutely, a helpful and friendly AI code translation assistant.
                    
                    User message: {message}
                    """,
                    generation_config={
                        "temperature": 0.7,
                        "top_p": 0.95,
                        "top_k": 40,
                        "max_output_tokens": 2048,
                    }
                )
                response_text = response.text
                print(f"DEBUG - Direct model response: {response_text[:100]}...")
            else:
                print("DEBUG - No model available")
                response_text = "I'm sorry, I don't have a language model available to chat with you."
        except Exception as e:
            print(f"DEBUG - Error in chat: {str(e)}")
            response_text = f"I apologize, but I encountered an error: {str(e)}"
        
        # Add response to conversation history
        self.conversation_history.append({"role": "assistant", "content": response_text})
        
        return response_text
    
    def chat_response(self, message: str) -> str:
        """Generate a response to a chat message."""
        try:
            if self.gemini.model:
                response = self.gemini.model.generate_content(
                    f"""You are Astutely, a helpful and friendly AI code translation assistant.
                    
                    User message: {message}
                    """,
                    generation_config={
                        "temperature": 0.7,
                        "top_p": 0.95,
                        "top_k": 40,
                        "max_output_tokens": 2048,
                    }
                )
                response_text = response.text
                print(f"DEBUG - Direct model response: {response_text[:100]}...")
            else:
                print("DEBUG - No model available")
                response_text = "I'm sorry, I don't have a language model available to chat with you."
        except Exception as e:
            print(f"DEBUG - Error in chat: {str(e)}")
            response_text = f"I apologize, but I encountered an error: {str(e)}"
        
        return response_text
    
    def clear_conversation_history(self):
        """Clear conversation history."""
        if hasattr(self, 'conversation_history'):
            self.conversation_history = []
        return "Conversation history cleared."


if __name__ == "__main__":
    # Example usage
    api_key = os.environ.get("GEMINI_API_KEY")
    model_name = "models/gemini-1.5-pro-001"
    
    try:
        ai = IntegratedTranslatorAI(api_key=api_key, model_name=model_name)
        
        # Example chat
        response = ai.chatbot.chat_response("Translate this Python code to JavaScript:\n\nprint('Hello, World!')")
        print(f"Response: {response}")
        
    except Exception as e:
        logger.error(f"Error running example: {str(e)}")
