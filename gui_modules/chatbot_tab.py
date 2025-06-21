"""
Chatbot Tab Functionality for CodedSwitch Application - Fixed Version
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledText as TtkScrolledText
import logging
import threading
from datetime import datetime

logger = logging.getLogger(__name__)

# Safe imports
try:
    from .utils import ErrorHandler
except ImportError:
    try:
        from utils import ErrorHandler
    except ImportError:
        class ErrorHandler:
            @staticmethod
            def handle_error(operation_name: str):
                def decorator(func):
                    def wrapper(*args, **kwargs):
                        try:
                            return func(*args, **kwargs)
                        except Exception as e:
                            logger.error(f"Error in {operation_name}: {e}")
                            messagebox.showerror(f"{operation_name} Error", f"An error occurred: {e}")
                            return None
                    return wrapper
                return decorator

class ChatbotTab:
    """Handles all chatbot tab functionality."""
    
    def __init__(self, parent, ai_interface):
        self.parent = parent
        self.ai = ai_interface
        self.conversation_history = []
        self.setup_chatbot_tab()
        self._add_welcome_message()
    
    def setup_chatbot_tab(self):
        """Set up the chatbot tab with enhanced UI."""
        
        # Main frame
        main_frame = ttk.Frame(self.parent.chatbot_tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Chat display frame
        chat_frame = ttk.LabelFrame(main_frame, text="💬 Astutely Assistant", padding=10)
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.parent.chat_display = TtkScrolledText(chat_frame, height=20, wrap=tk.WORD,
                                                  font=('Arial', 10), state='disabled')
        self.parent.chat_display.pack(fill=tk.BOTH, expand=True)
        # Expose yview/xview on the ScrolledText wrapper so callbacks work correctly
        if not hasattr(self.parent.chat_display, "yview"):
            self.parent.chat_display.yview = self.parent.chat_display.text.yview  # type: ignore
        if not hasattr(self.parent.chat_display, "xview"):
            self.parent.chat_display.xview = self.parent.chat_display.text.xview  # type: ignore
        
        # Input frame
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Message input
        ttk.Label(input_frame, text="Message:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        
        self.parent.chat_input = TtkScrolledText(input_frame, height=4, wrap=tk.WORD,
                                                font=('Arial', 10))
        self.parent.chat_input.pack(fill=tk.X, pady=(5, 10))
        # Likewise expose yview/xview for the input widget to satisfy any callbacks
        if not hasattr(self.parent.chat_input, "yview"):
            self.parent.chat_input.yview = self.parent.chat_input.text.yview  # type: ignore
        if not hasattr(self.parent.chat_input, "xview"):
            self.parent.chat_input.xview = self.parent.chat_input.text.xview  # type: ignore
        self.parent.chat_input.bind('<Control-Return>', self.send_message)
        
        # Button frame
        btn_frame = ttk.Frame(input_frame)
        btn_frame.pack(fill=tk.X)
        
        # Send button
        self.send_btn = ttk.Button(btn_frame, text="📤 Send (Ctrl+Enter)", 
                             command=self.send_message,
                             bootstyle="success", width=20)
        self.send_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Clear chat button
        clear_btn = ttk.Button(btn_frame, text="🗑️ Clear Chat", 
                              command=self._clear_chat,
                              bootstyle="danger-outline", width=15)
        clear_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Export chat button
        export_btn = ttk.Button(btn_frame, text="💾 Export Chat", 
                               command=self._export_chat_history,
                               bootstyle="info-outline", width=15)
        export_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Examples button
        examples_btn = ttk.Button(btn_frame, text="💡 Examples", 
                                 command=self._show_chat_examples,
                                 bootstyle="info-outline", width=15)
        examples_btn.pack(side=tk.LEFT)
    
    def _add_welcome_message(self):
        """Add welcome message to chat."""
        welcome_msg = """🎤 Welcome to Astutely, your CodedSwitch AI assistant! 🎤

I'm here to help you with:
• Code translation between programming languages
• Programming questions and explanations
• Code debugging and optimization
• General tech discussions

Feel free to ask me anything or try these examples:
• "Translate this Python code to JavaScript: [your code]"
• "What's the difference between Python and Java?"
• "How do I optimize this algorithm?"

Let's code together! 🚀"""
        
        self._add_message_to_display("Astutely", welcome_msg, "assistant")
    
    @ErrorHandler.handle_error("Send Message")
    def send_message(self, event=None):
        """Send message to AI chatbot."""
        if not self.parent.ai_interface:
            messagebox.showwarning("AI Not Available", 
                                 "AI interface not initialized. Please check your API key.")
            return
        
        # Retrieve text from the internal Text widget of the ScrolledText component
        message = self.parent.chat_input.text.get("1.0", tk.END).strip()
        if not message:
            return
        
        # Clear input
        self.parent.chat_input.text.delete("1.0", tk.END)
        
        # Add user message to display
        self._add_message_to_display("You", message, "user")
        
        # Update status
        if hasattr(self.parent, 'status_var'):
            self.parent.status_var.set("🤖 AI is thinking...")
        
        # Disable send button during processing
        self.send_btn.config(state='disabled')
        
        def chat_worker():
            try:
                # Get AI response
                response = self.parent.ai_interface.chat_response(message)
                
                # Update UI on main thread
                self.parent.root.after(0, lambda: self._add_message_to_display("Assistant", response, "assistant"))
                
                if hasattr(self.parent, 'status_var'):
                    self.parent.root.after(0, lambda: self.parent.status_var.set("Ready"))
                
            except Exception as e:
                error_msg = f"Chat error: {str(e)}"
                self.parent.root.after(0, lambda: self._add_message_to_display("System", error_msg, "error"))
                
                if hasattr(self.parent, 'status_var'):
                    self.parent.root.after(0, lambda: self.parent.status_var.set("Ready"))
                
                logger.error(f"Chat error: {e}", exc_info=True)
            finally:
                # Re-enable send button
                self.parent.root.after(0, lambda: self.send_btn.config(state='normal'))
        
        # Run chat in background thread
        thread = threading.Thread(target=chat_worker)
        thread.daemon = True
        thread.start()
    
    def _is_translation_request(self, message: str) -> bool:
        """Check if message is a code translation request."""
        translation_keywords = ['translate', 'convert', 'change to', 'from', 'to']
        code_indicators = ['def ', 'function ', 'class ', '{', '}', '()', 'import ', 'using ', '#include']
        
        message_lower = message.lower()
        has_translation_keyword = any(keyword in message_lower for keyword in translation_keywords)
        has_code = any(indicator in message for indicator in code_indicators)
        
        return has_translation_keyword and has_code
    
    def _add_message_to_display(self, sender: str, message: str, msg_type: str = "user"):
        """Add message to chat display with formatting."""
        timestamp = datetime.now().strftime("%H:%M")
        
        self.parent.chat_display.text.config(state=tk.NORMAL)
        
        # Format based on message type
        if msg_type == "user":
            prefix = f"[{timestamp}] 👤 {sender}: "
            self.parent.chat_display.text.insert(tk.END, prefix, "user_header")
        elif msg_type == "assistant":
            prefix = f"[{timestamp}] 🤖 Assistant: "
            self.parent.chat_display.text.insert(tk.END, prefix, "assistant_header")
        elif msg_type == "error":
            prefix = f"[{timestamp}] ❌ Error: "
            self.parent.chat_display.text.insert(tk.END, prefix, "error_header")
        else:
            prefix = f"[{timestamp}] {sender}: "
            self.parent.chat_display.text.insert(tk.END, prefix)
        
        # Add message content
        self.parent.chat_display.text.insert(tk.END, f"{message}\n\n")
        
        # Configure text tags for formatting
        self.parent.chat_display.text.tag_config("user_header", foreground="#4CAF50", font=('Arial', 10, 'bold'))
        self.parent.chat_display.text.tag_config("assistant_header", foreground="#2196F3", font=('Arial', 10, 'bold'))
        self.parent.chat_display.text.tag_config("error_header", foreground="#FF6B6B", font=('Arial', 10, 'bold'))
        
        self.parent.chat_display.text.config(state=tk.DISABLED)
        self.parent.chat_display.text.see(tk.END)
        
        # Add to conversation history
        self.conversation_history.append({
            "sender": sender,
            "message": message,
            "timestamp": timestamp,
            "type": msg_type
        })
    
    @ErrorHandler.handle_error("Clear Chat")
    def _clear_chat(self, event=None):
        """Clear the chat display and conversation history."""
        self.parent.chat_display.text.config(state=tk.NORMAL)
        self.parent.chat_display.text.delete("1.0", tk.END)
        self.parent.chat_display.text.config(state=tk.DISABLED)
        
        self.conversation_history.clear()
        self._add_welcome_message()
        
        if hasattr(self.parent, 'status_var'):
            self.parent.status_var.set("🗑️ Chat cleared")
        
        logger.info("Chat cleared")
    
    @ErrorHandler.handle_error("Export Chat")
    def _export_chat_history(self):
        """Export chat history to a file."""
        if not self.conversation_history:
            messagebox.showinfo("No Chat", "No chat history to export.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export Chat History",
            defaultextension=".txt",
            filetypes=[
                ("Text files", "*.txt"),
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                if file_path.endswith('.json'):
                    import json
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(self.conversation_history, f, indent=2)
                else:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write("CodedSwitch Chat History\n")
                        f.write("=" * 50 + "\n\n")
                        
                        for msg in self.conversation_history:
                            f.write(f"[{msg['timestamp']}] {msg['sender']}: {msg['message']}\n\n")
                
                messagebox.showinfo("Export Complete", f"Chat history exported to: {file_path}")
                
                if hasattr(self.parent, 'status_var'):
                    self.parent.status_var.set(f"💾 Chat exported: {file_path}")
                
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export chat: {str(e)}")
    
    def _show_chat_examples(self):
        """Show example chat prompts."""
        examples = """💡 Try these example prompts:

🔄 Translation Examples:
• "Translate this Python function to JavaScript: def hello(): print('Hello')"
• "Convert this Java loop to Python: for(int i=0; i<10; i++)"
• "Change this C++ code to Rust: [your code]"

❓ Programming Questions:
• "What's the difference between Python lists and tuples?"
• "How do I handle exceptions in JavaScript?"
• "Explain object-oriented programming concepts"

🔧 Code Help:
• "How can I optimize this algorithm?"
• "What's wrong with this code?"
• "Best practices for [programming concept]"

🎤 Fun CodedSwitch Style:
• "Explain Python in rap lyrics"
• "Write a tech poem about debugging"
• "Create a programming joke"

Just type your question and I'll help you out! 🚀"""
        
        messagebox.showinfo("Chat Examples", examples)