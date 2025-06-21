"""
Script to fix the indentation error in integrated_gui.py
"""

def fix_indentation_error():
    """Fix the indentation error around line 6089-6090."""
    
    # Read the current integrated_gui.py
    with open('integrated_gui.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find and fix the problematic lines around line 6089
    for i, line in enumerate(lines):
        if i >= 6088 and i <= 6092:  # Lines 6089-6093 (0-indexed)
            if line.strip().startswith('def run(self):'):
                # This line should be properly indented as a method
                lines[i] = '    def run(self):\n'
            elif line.strip().startswith('"""Run the enhanced CodedSwitch application."""'):
                # This docstring should be indented
                lines[i] = '        """Run the enhanced CodedSwitch application."""\n'
            elif line.strip().startswith('try:'):
                # This should be indented
                lines[i] = '        try:\n'
            elif line.strip().startswith('logger.info("🎤 Starting CodedSwitch Enhanced Edition...")'):
                # This should be indented more
                lines[i] = '            logger.info("🎤 Starting CodedSwitch Enhanced Edition...")\n'
            elif line.strip().startswith('self.root.mainloop()'):
                # This should be indented more
                lines[i] = '            self.root.mainloop()\n'
            elif line.strip().startswith('except KeyboardInterrupt:'):
                # This should be indented
                lines[i] = '        except KeyboardInterrupt:\n'
    
    # Write back to file
    with open('integrated_gui.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("✅ Indentation error fixed in integrated_gui.py")

if __name__ == "__main__":
    fix_indentation_error()
