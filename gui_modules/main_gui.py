"""
Fixed main_gui.py with proper AI interface management
This ensures all components can access the AI properly
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as ttk
from ttkbootstrap import Style
import logging


logger = logging.getLogger(__name__)

class IntegratedTranslatorGUI:
    """Main GUI class with proper AI interface management"""
    
    def __init__(self, ai_interface=None, vulnerability_scanner=None):
        """Initialize the integrated GUI with AI interface"""
        self.ai_interface = ai_interface
        self.vulnerability_scanner = vulnerability_scanner
        
        # Store reference for all components to access
        self._ai_interface = ai_interface
        
        # Initialize GUI
        self.setup_gui()
        
        logger.info("GUI initialized with AI interface")
    
    def get_ai_interface(self):
        """Provide AI interface access to other components"""
        return getattr(self, 'ai_interface', None)
    
    def setup_gui(self):
        """Set up the main GUI with proper error handling"""
        try:
           
            # Hide any default tkinter windows
            import tkinter as tk
            default_root = tk._default_root
            if default_root:
                default_root.withdraw()
            
            # Create main window
            self.root = ttk.Window(themename="superhero")
            self.root.title("CodedSwitch - AI Code Translator")
            self.root.geometry("1200x800")
            
            # Create main interface
            self.setup_main_interface()
            
            # Initialize menu handlers with AI reference
            self.menu_handlers = self._init_menu_handlers()
            
            # Setup menu bar
            self.setup_menu_bar()
            
            # Setup status bar
            self.setup_status_bar()
            
            # Handle window closing
            self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
            
            # Bind keyboard shortcuts
            self.root.bind("<Control-n>", lambda event: self.menu_handlers._new_file())
            self.root.bind("<Control-o>", lambda event: self.menu_handlers._open_file())
            self.root.bind("<Control-s>", lambda event: self.menu_handlers._save_file())
            
        except Exception as e:
            logger.error(f"Error setting up GUI: {e}")
            raise
    
    def _init_menu_handlers(self):
        """Initialize menu handlers with proper AI connection"""
        try:
            import menu_handlers
            # Pass self (the GUI instance) so menu handlers can access AI
            return menu_handlers.MenuHandlers(self)
        except ImportError:
            logger.warning("Menu handlers not available")
            return None
    
    def setup_main_interface(self):
        """Set up the main interface with tabs"""
        # Create main container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs with error handling
        self.setup_tabs()
    
    def setup_tabs(self):
        """Set up all tabs with proper AI interface passing"""
        
        # Translator Tab
        self.translator_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.translator_tab, text="🔄 Translator")
        try:
            import translator_tab
            self.translator_tab_component = translator_tab.TranslatorTab(self, self.ai_interface)
        except Exception as e:
            logger.error(f"Failed to create translator tab: {e}")
            self._create_error_tab(self.translator_tab, "Translator", str(e))
        
        # Chatbot Tab
        self.chatbot_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.chatbot_tab, text="🤖 AI Chatbot")
        try:
            import chatbot_tab
            self.chatbot_tab_component = chatbot_tab.ChatbotTab(self, self.ai_interface)
        except Exception as e:
            logger.error(f"Failed to create chatbot tab: {e}")
            self._create_error_tab(self.chatbot_tab, "Chatbot", str(e))
        
        # Security Tab
        self.security_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.security_tab, text="🔒 Security")
        try:
            import security_tab
            self.security_tab_component = security_tab.SecurityTab(self, self.vulnerability_scanner)
        except Exception as e:
            logger.error(f"Failed to create security tab: {e}")
            self._create_error_tab(self.security_tab, "Security", str(e))
        
        # Lyric Lab Tab
        self.lyric_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.lyric_tab, text="🎤 Lyric Lab")
        try:
            import lyric_lab_tab
            self.lyric_lab_tab_component = lyric_lab_tab.LyricLabTab(self, self.ai_interface)
        except Exception as e:
            logger.error(f"Failed to create lyric lab tab: {e}")
            self._create_error_tab(self.lyric_tab, "Lyric Lab", str(e))
    
    def _create_error_tab(self, tab_frame, tab_name, error_msg):
        """Create an error display tab when module fails to load"""
        error_frame = ttk.Frame(tab_frame)
        error_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(error_frame, text=f"❌ {tab_name} Error", 
                 font=('Arial', 16, 'bold')).pack(pady=10)
        
        ttk.Label(error_frame, text=f"Could not load {tab_name} module:",
                 font=('Arial', 12)).pack(pady=5)
        
        ttk.Label(error_frame, text=error_msg, 
                 font=('Arial', 10), foreground="red").pack(pady=5)
        
        ttk.Label(error_frame, text="Please check the module file and dependencies.",
                 font=('Arial', 10)).pack(pady=5)
    
    def setup_menu_bar(self):
        """Set up the menu bar"""
        if not self.menu_handlers:
            return
            
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        
        # File menu
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.menu_handlers._new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open", command=self.menu_handlers._open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.menu_handlers._save_file, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_closing)
        
        # Tools menu
        tools_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="🎵 Beat Studio", command=self.menu_handlers._show_beat_studio)
        tools_menu.add_command(label="🎧 Audio Tools", command=self.menu_handlers._show_audio_tools)
        tools_menu.add_command(label="⚙️ Preferences", command=self.menu_handlers._show_preferences)
        
        # Help menu
        help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
    
    def setup_status_bar(self):
        """Set up the status bar"""
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Status variable
        self.status_var = tk.StringVar()
        if self.ai_interface:
            self.status_var.set("✅ CodedSwitch Ready - AI Connected")
        else:
            self.status_var.set("⚠️ CodedSwitch Ready - AI Not Available")
        
        # Status label
        self.status_label = ttk.Label(self.status_frame, textvariable=self.status_var,
                                     relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2, pady=2)
    
    def _show_about(self):
        """Show about dialog"""
        ai_status = "✅ Connected" if self.ai_interface else "❌ Not Available"
        
        about_text = f"""CodedSwitch AI Code Translator
Version: 2.0.0

AI Status: {ai_status}

Features:
• Multi-language code translation
• AI-powered chatbot assistance
• Security vulnerability scanning
• Creative lyric generation lab
• Beat Studio for music production

© 2024 CodedSwitch Team"""
        
        messagebox.showinfo("About CodedSwitch", about_text)
    
    def _on_closing(self):
        """Handle application closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit CodedSwitch?"):
            try:
                # Cleanup if needed
                if hasattr(self, 'menu_handlers') and hasattr(self.menu_handlers, 'beat_studio'):
                    self.menu_handlers.beat_studio.stop_playback()
            except:
                pass
            
            self.root.quit()
            self.root.destroy()
    
    def run(self):
        """Run the GUI application"""
        try:
            logger.info("Starting CodedSwitch GUI")
            self.root.mainloop()
        except Exception as e:
            logger.error(f"Error running GUI: {e}")
            messagebox.showerror("Application Error", f"Application error: {e}")
        finally:
            logger.info("CodedSwitch GUI ended")

# For testing the module
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Test AI interface import
    ai_interface = None
    try:
        import integrated_ai
        api_key = os.getenv('GEMINI_API_KEY', 'test_key')
        if api_key and api_key != 'test_key':
            ai_interface = integrated_ai.IntegratedTranslatorAI(api_key=api_key)
            print("✅ AI interface loaded")
        else:
            print("⚠️ No API key - AI features disabled")
    except Exception as e:
        print(f"⚠️ AI interface failed: {e}")
    
    # Create and run GUI
    app = IntegratedTranslatorGUI(ai_interface=ai_interface)
    app.run()