import os
import shutil
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

def create_backup():
    # Files to back up
    files_to_backup = [
        'integrated_gui.py',
        'integrated_ai.py',
        'ai_code_translator/security/vulnerability_scanner.py',
        'ai_code_translator/security/vulnerability.py'
    ]
    
    # Create backups directory if it doesn't exist
    backup_dir = os.path.join(os.path.dirname(__file__), 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    
    # Create timestamp for backup folder
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_folder = os.path.join(backup_dir, f'backup_{timestamp}')
    os.makedirs(backup_folder, exist_ok=True)
    
    # Backup each file
    backed_up_files = []
    for file_path in files_to_backup:
        try:
            full_path = os.path.join(os.path.dirname(__file__), file_path)
            if os.path.exists(full_path):
                # Create subdirectories in backup if needed
                dest_dir = os.path.join(backup_folder, os.path.dirname(file_path))
                os.makedirs(dest_dir, exist_ok=True)
                
                # Copy the file
                dest_path = os.path.join(backup_folder, file_path)
                shutil.copy2(full_path, dest_path)
                backed_up_files.append(file_path)
        except Exception as e:
            print(f"Error backing up {file_path}: {str(e)}")
    
    return backup_folder, backed_up_files

def show_backup_gui():
    def perform_backup():
        backup_folder, backed_up_files = create_backup()
        if backed_up_files:
            message = f"Successfully backed up {len(backed_up_files)} files to:\n{backup_folder}"
            backup_list.config(state=tk.NORMAL)
            backup_list.delete(1.0, tk.END)
            backup_list.insert(tk.END, "Backed up files:\n")
            for file in backed_up_files:
                backup_list.insert(tk.END, f"- {file}\n")
            backup_list.config(state=tk.DISABLED)
            status_label.config(text="Backup completed successfully!", foreground="green")
        else:
            messagebox.showerror("Backup Failed", "No files were backed up. Please check if the files exist.")
    
    # Create the main window
    root = tk.Tk()
    root.title("Code Backup Utility")
    root.geometry("600x400")
    
    # Style the window
    style = ttk.Style()
    style.configure("TButton", padding=6, font=('Segoe UI', 10))
    style.configure("TLabel", font=('Segoe UI', 10))
    
    # Create widgets
    header = ttk.Label(root, text="AI Code Translator - Backup Utility", font=('Segoe UI', 12, 'bold'))
    header.pack(pady=10)
    
    info_text = "This utility will create a backup of the following files:"
    info_label = ttk.Label(root, text=info_text, wraplength=550)
    info_label.pack(pady=(0, 10))
    
    # List of files to be backed up
    files_list = ttk.Label(root, text="• integrated_gui.py\n• integrated_ai.py\n• ai_code_translator/security/vulnerability_scanner.py\n• ai_code_translator/security/vulnerability.py", 
                          justify=tk.LEFT)
    files_list.pack(pady=(0, 20))
    
    # Backup button
    backup_btn = ttk.Button(root, text="Create Backup Now", command=perform_backup)
    backup_btn.pack(pady=5)
    
    # Status label
    status_label = ttk.Label(root, text="", font=('Segoe UI', 10))
    status_label.pack(pady=5)
    
    # Backup list
    backup_list = tk.Text(root, height=10, wrap=tk.WORD, state=tk.DISABLED)
    backup_list.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
    
    # Add some padding
    ttk.Label(root, text="").pack(pady=5)
    
    # Run the application
    root.mainloop()

if __name__ == "__main__":
    show_backup_gui()
