import os
import shutil
from datetime import datetime

def create_backup():
    # Source directory to backup
    src = r'd:\Projects\AI_Projects\AI_Code_Translator_Advanced_Final'
    
    # Destination directory for backups
    backup_dir = os.path.join(os.path.expanduser('~'), 'CodedSwitch_Backups')
    
    # Create backup directory if it doesn't exist
    os.makedirs(backup_dir, exist_ok=True)
    
    # Create timestamped backup folder
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(backup_dir, f'CodedSwitch_Backup_{timestamp}')
    
    try:
        # Copy all files and directories
        shutil.copytree(src, os.path.join(backup_path, os.path.basename(src)))
        print(f'✅ Backup created successfully at:\n{backup_path}')
        return True
    except Exception as e:
        print(f'❌ Backup failed: {str(e)}')
        return False

if __name__ == "__main__":
    create_backup()
