"""
Patch script to integrate Lyric Lab functionality into integrated_gui.py
Run this to add the missing Lyric Lab implementation
"""
import os
import shutil
from datetime import datetime

def apply_lyric_lab_patch():
    """Apply the Lyric Lab patch to integrated_gui.py"""
    
    # Backup the current file
    backup_name = f"integrated_gui_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    shutil.copy("integrated_gui.py", backup_name)
    print(f"✅ Created backup: {backup_name}")
    
    # Read the current integrated_gui.py
    with open("integrated_gui.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Add the import at the top
    import_line = "from lyric_lab_integration import LyricLabIntegration\n"
    
    if import_line.strip() not in content:
        # Find the imports section and add our import
        lines = content.split('\n')
        import_index = -1
        
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                import_index = i
        
        if import_index != -1:
            lines.insert(import_index + 1, import_line.strip())
            print("✅ Added import statement")
        
        # Add initialization in __init__ method
        init_code = """        
        # Initialize Lyric Lab integration
        self.lyric_lab_integration = LyricLabIntegration(self)"""
        
        # Find the __init__ method and add our initialization
        for i, line in enumerate(lines):
            if "def __init__(self" in line and "IntegratedTranslatorGUI" in lines[max(0, i-5):i+1]:
                # Find where to insert (after other initializations)
                for j in range(i, min(len(lines), i + 100)):
                    if "self._setup_lyric_lab_tab()" in lines[j]:
                        lines.insert(j, init_code)
                        print("✅ Added Lyric Lab integration initialization")
                        break
                break
        
        # Replace the _setup_lyric_lab_tab method
        setup_method = """    def _setup_lyric_lab_tab(self):
        \"\"\"Set up the Lyric Lab tab with full functionality\"\"\"
        if hasattr(self, 'lyric_lab_integration'):
            self.lyric_lab_integration.setup_lyric_lab_tab(self.lyric_tab)
        else:
            # Fallback placeholder
            ttk.Label(self.lyric_tab, text="🎤 Lyric Lab - Loading...", 
                     font=('Arial', 14)).pack(expand=True)"""
        
        # Find and replace the existing _setup_lyric_lab_tab method
        in_method = False
        method_start = -1
        method_end = -1
        
        for i, line in enumerate(lines):
            if "def _setup_lyric_lab_tab(self)" in line:
                method_start = i
                in_method = True
            elif in_method and line.strip() and not line.startswith('    ') and not line.startswith('\t'):
                method_end = i
                break
        
        if method_start != -1:
            if method_end == -1:
                method_end = len(lines)
            
            # Replace the method
            lines[method_start:method_end] = setup_method.split('\n')
            print("✅ Replaced _setup_lyric_lab_tab method")
        
        # Write the modified content back
        content = '\n'.join(lines)
        
        with open("integrated_gui.py", "w", encoding="utf-8") as f:
            f.write(content)
        
        print("✅ Lyric Lab patch applied successfully!")
        print("🎵 Your integrated GUI now has complete Lyric Lab and Beat Studio functionality!")
        print("\nFeatures added:")
        print("• 🎵 Generate Beat from Lyrics")
        print("• ✨ AI-powered Lyric Generation") 
        print("• 🎛️ Full Beat Studio with Pattern Editor")
        print("• 🔍 Lyric Analysis Tools")
        print("• 🎼 Rhyme Scheme Analysis")
        print("• ⚡ Flow Analysis")
        print("• 💾 Save/Load Lyrics")
        print("• 🎯 Multiple Music Styles")
        
    else:
        print("⚠️ Lyric Lab integration already present")

if __name__ == "__main__":
    apply_lyric_lab_patch()
