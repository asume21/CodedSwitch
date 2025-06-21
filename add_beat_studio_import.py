"""
Script to add Beat Studio import to integrated_gui.py
"""

def add_beat_studio_import():
    """Add the Beat Studio integration import to the integrated GUI."""
    
    # Read the current integrated_gui.py
    with open('integrated_gui.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the location after the librosa import section
    import_section = """# Optional imports with fallbacks
try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    # Note: logger not available yet, will log later"""
    
    # Add Beat Studio import after librosa
    beat_studio_import = """
# Beat Studio integration
try:
    from beat_studio_integration import beat_studio_integration, BEAT_STUDIO_AVAILABLE
    print("✅ Beat Studio integration loaded successfully!")
except ImportError as e:
    print(f"⚠️ Beat Studio integration not available: {e}")
    BEAT_STUDIO_AVAILABLE = False
    beat_studio_integration = None"""
    
    # Replace the import section
    new_content = content.replace(
        import_section,
        import_section + beat_studio_import
    )
    
    # Write back to file
    with open('integrated_gui.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Beat Studio import added to integrated_gui.py")

if __name__ == "__main__":
    add_beat_studio_import()
