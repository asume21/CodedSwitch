import logging
from google.generativeai import ChatSession

logger = logging.getLogger(__name__)

class ChatbotInterface:
    def __init__(self, api_key: str, model: str = "models/gemini-1.5-pro-001"):
        """Initialize the chatbot interface.
        
        Args:
            api_key: Gemini API key
            model: Model name
        """
        if not isinstance(api_key, str):
            raise ValueError("API key must be a string")
            
        self.api_key = api_key
        self.model = model
        self.chat = None
        self._initialize_chat()
        logger.info(f"Successfully initialized ChatbotInterface with model: {model}")

    def _initialize_chat(self):
        try:
            from google.generativeai import configure, GenerativeModel
            configure(api_key=self.api_key)
            self.chat = GenerativeModel(model_name=self.model).start_chat(history=[])
            logger.info("Chat session initialized")
        except Exception as e:
            logger.error(f"Failed to initialize chat session: {str(e)}")
            raise

    def send_message(self, message: str) -> str:
        """Send a message to the chatbot.
        
        Args:
            message: Message to send
            
        Returns:
            Response text
        """
        try:
            response = self.chat.send_message(
                message,
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "max_output_tokens": 2048,
                }
            )
            return str(response)
            
        except Exception as e:
            logger.error(f"Failed to send message: {str(e)}")
            raise
