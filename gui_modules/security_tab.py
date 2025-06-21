"""
Security Tab Functionality for CodedSwitch Application
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
try:
    from utils import ErrorHandler
except ImportError:
    try:
        from .utils import ErrorHandler
    except ImportError:
        # Fallback ErrorHandler class
        class ErrorHandler:
            @staticmethod
            def handle_error(operation_name: str):
                def decorator(func):
                    def wrapper(*args, **kwargs):
                        try:
                            return func(*args, **kwargs)
                        except Exception as e:
                            print(f"Error in {operation_name}: {e}")
                            return None
                    return wrapper
                return decorator

logger = logging.getLogger(__name__)

class SecurityTab:
    """Handles all security scanner tab functionality."""
    
    def __init__(self, parent, vulnerability_scanner=None):
        self.parent = parent
        self.scanner = vulnerability_scanner
        self.scan_results = []
        self.setup_security_tab()
    
    def setup_security_tab(self):
        """Set up the security scanner tab."""
        
        # Main frame
        main_frame = ttk.Frame(self.parent.security_tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(header_frame, text="🔒 Security Scanner", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(side=tk.LEFT)
        
        # Scan options frame
        options_frame = ttk.LabelFrame(main_frame, text="🔧 Scan Options", padding=10)
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Language selection
        ttk.Label(options_frame, text="Language:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        self.parent.scan_language = ttk.Combobox(options_frame, 
                                                values=["Python", "JavaScript", "Java", "C++", "C#", "PHP"],
                                                state="readonly", width=15)
        self.parent.scan_language.set("Python")
        self.parent.scan_language.pack(side=tk.LEFT, padx=(5, 20))
        
        # Scan type options
        self.parent.scan_sql_injection = tk.BooleanVar(value=True)
        self.parent.scan_xss = tk.BooleanVar(value=True)
        self.parent.scan_hardcoded_secrets = tk.BooleanVar(value=True)
        self.parent.scan_unsafe_functions = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(options_frame, text="SQL Injection", 
                       variable=self.parent.scan_sql_injection).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(options_frame, text="XSS", 
                       variable=self.parent.scan_xss).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(options_frame, text="Hardcoded Secrets", 
                       variable=self.parent.scan_hardcoded_secrets).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(options_frame, text="Unsafe Functions", 
                       variable=self.parent.scan_unsafe_functions).pack(side=tk.LEFT, padx=5)
        
        # Code input frame
        input_frame = ttk.LabelFrame(main_frame, text="📝 Code to Scan", padding=10)
        input_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Code input area
        code_input_frame = ttk.Frame(input_frame)
        code_input_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.parent.security_code_input = TtkScrolledText(code_input_frame, height=10, wrap=tk.WORD,
                                                         font=('Consolas', 11))
        self.parent.security_code_input.pack(fill=tk.BOTH, expand=True)
        
        # Button frame
        input_btn_frame = ttk.Frame(input_frame)
        input_btn_frame.pack(fill=tk.X)
        
        scan_btn = ttk.Button(input_btn_frame, text="🔍 Scan Code", 
                             command=self._scan_code,
                             bootstyle="warning", width=15)
        scan_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        load_btn = ttk.Button(input_btn_frame, text="📂 Load File", 
                             command=self._load_code_file,
                             bootstyle="info-outline", width=15)
        load_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_btn = ttk.Button(input_btn_frame, text="🗑️ Clear", 
                              command=self._clear_code_input,
                              bootstyle="danger-outline", width=15)
        clear_btn.pack(side=tk.LEFT)
        
        auto_fix_btn = ttk.Button(input_btn_frame, text="🔧 Auto Fix", 
                                 command=self.auto_fix_vulnerabilities,
                                 bootstyle="success-outline", width=15)
        auto_fix_btn.pack(side=tk.RIGHT)
        
        # Results frame
        results_frame = ttk.LabelFrame(main_frame, text="📊 Scan Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Results display
        self.parent.security_results = TtkScrolledText(results_frame, height=10, wrap=tk.WORD,
                                                      font=('Consolas', 10), state='disabled')
        self.parent.security_results.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Results actions
        results_btn_frame = ttk.Frame(results_frame)
        results_btn_frame.pack(fill=tk.X)
        
        export_btn = ttk.Button(results_btn_frame, text="📤 Export Report", 
                               command=self.export_report,
                               bootstyle="primary-outline", width=15)
        export_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_results_btn = ttk.Button(results_btn_frame, text="🗑️ Clear Results", 
                                      command=self._clear_results,
                                      bootstyle="danger-outline", width=15)
        clear_results_btn.pack(side=tk.LEFT)
    
    @ErrorHandler.handle_error("Code Scanning")
    def _scan_code(self):
        """Scan code for security vulnerabilities."""
        code = self.parent.security_code_input.get("1.0", tk.END).strip()
        if not code:
            messagebox.showwarning("No Code", "Please enter code to scan.")
            return
        
        if hasattr(self.parent, 'status_var'):
            self.parent.status_var.set("🔍 Scanning for vulnerabilities...")
        
        # Disable scan button during scanning
        scan_btn = ttk.Button(self.parent.security_tab, text="🔍 Scan Code", 
                             command=self._scan_code,
                             bootstyle="warning", width=15)
        scan_btn.config(state='disabled')
        
        def scan_worker():
            try:
                vulnerabilities = []
                
                # Pattern-based vulnerability detection
                patterns = {
                    "SQL Injection": [
                        r"execute\s*\(\s*[\"'].*?%.*?[\"']\s*%",
                        r"cursor\.execute\s*\(\s*[\"'].*?\+.*?[\"']\s*\)",
                        r"query\s*=.*?\+.*?input"
                    ],
                    "XSS Vulnerability": [
                        r"innerHTML\s*=.*?input",
                        r"document\.write\s*\(.*?input",
                        r"eval\s*\(.*?input"
                    ],
                    "Path Traversal": [
                        r"open\s*\(.*?\.\./",
                        r"file\s*=.*?\.\./",
                        r"path.*?\.\."
                    ],
                    "Command Injection": [
                        r"os\.system\s*\(.*?input",
                        r"subprocess\s*\(.*?input",
                        r"exec\s*\(.*?input"
                    ],
                    "Hardcoded Secrets": [
                        r"password\s*=\s*[\"'][^\"']+[\"']",
                        r"api_key\s*=\s*[\"'][^\"']+[\"']",
                        r"secret\s*=\s*[\"'][^\"']+[\"']"
                    ]
                }
                
                import re
                lines = code.split('\n')
                
                for vuln_type, patterns_list in patterns.items():
                    for pattern in patterns_list:
                        for line_num, line in enumerate(lines, 1):
                            if re.search(pattern, line, re.IGNORECASE):
                                vulnerabilities.append({
                                    'type': vuln_type,
                                    'line': line_num,
                                    'code': line.strip(),
                                    'severity': 'High' if vuln_type in ['SQL Injection', 'Command Injection'] else 'Medium'
                                })
                
                # If AI interface is available, get additional analysis
                if self.parent.ai_interface:
                    try:
                        ai_analysis = self.parent.ai_interface.analyze_security(code)
                        # Parse AI analysis and add to vulnerabilities if needed
                    except Exception as e:
                        logger.warning(f"AI security analysis failed: {e}")
                
                # Update UI on main thread
                self.parent.root.after(0, lambda: self._display_scan_results(vulnerabilities))
                
                if hasattr(self.parent, 'status_var'):
                    status_msg = f"🔍 Scan complete: {len(vulnerabilities)} issues found"
                    self.parent.root.after(0, lambda: self.parent.status_var.set(status_msg))
                
            except Exception as e:
                error_msg = f"Security scan failed: {str(e)}"
                self.parent.root.after(0, lambda: messagebox.showerror("Scan Error", error_msg))
                logger.error(error_msg, exc_info=True)
            finally:
                # Re-enable scan button
                self.parent.root.after(0, lambda: scan_btn.config(state='normal'))
        
        # Run scan in background thread
        import threading
        thread = threading.Thread(target=scan_worker)
        thread.daemon = True
        thread.start()
    
    def _display_scan_results(self, vulnerabilities):
        """Display scan results in the results area."""
        self.parent.security_results.delete("1.0", tk.END)
        
        if not vulnerabilities:
            self.parent.security_results.insert("1.0", "✅ No security vulnerabilities detected!\n\nYour code appears to be secure.")
            return
        
        result_text = f"🚨 Security Scan Results - {len(vulnerabilities)} Issues Found\n"
        result_text += "=" * 60 + "\n\n"
        
        for i, vuln in enumerate(vulnerabilities, 1):
            result_text += f"{i}. {vuln['type']} (Severity: {vuln['severity']})\n"
            result_text += f"   Line {vuln['line']}: {vuln['code']}\n"
            result_text += f"   Recommendation: Review and fix this potential vulnerability\n\n"
        
        self.parent.security_results.insert("1.0", result_text)
        logger.info(f"Security scan completed: {len(vulnerabilities)} vulnerabilities found")
    
    def _perform_security_scan(self, code: str, language: str) -> list:
        """Perform actual security scanning."""
        vulnerabilities = []
        
        # Use the vulnerability scanner if available
        if self.scanner:
            try:
                vulnerabilities = self.scanner.scan_code(code, language)
            except Exception as e:
                logger.warning(f"Scanner failed: {e}")
        
        # Fallback to basic pattern matching
        if not vulnerabilities:
            vulnerabilities = self._basic_vulnerability_scan(code, language)
        
        return vulnerabilities
    
    def _basic_vulnerability_scan(self, code: str, language: str) -> list:
        """Basic vulnerability scanning using pattern matching."""
        vulnerabilities = []
        lines = code.split('\n')
        
        # Common vulnerability patterns
        patterns = {
            "SQL Injection": [
                r"\.execute\s*\(\s*['\"].*%.*['\"]",
                r"SELECT.*\+.*",
                r"INSERT.*\+.*"
            ],
            "Hardcoded Secrets": [
                r"password\s*=\s*['\"][^'\"]+['\"]",
                r"api_key\s*=\s*['\"][^'\"]+['\"]",
                r"secret\s*=\s*['\"][^'\"]+['\"]"
            ],
            "Unsafe Functions": [
                r"eval\s*\(",
                r"exec\s*\(",
                r"system\s*\(",
                r"shell_exec\s*\("
            ]
        }
        
        import re
        
        for i, line in enumerate(lines, 1):
            for vuln_type, pattern_list in patterns.items():
                for pattern in pattern_list:
                    if re.search(pattern, line, re.IGNORECASE):
                        vulnerabilities.append({
                            "type": vuln_type,
                            "line": i,
                            "code": line.strip(),
                            "severity": "Medium",
                            "description": f"Potential {vuln_type.lower()} vulnerability detected"
                        })
        
        return vulnerabilities
    
    def _load_code_file(self):
        """Load code from a file for scanning."""
        file_path = filedialog.askopenfilename(
            title="Load Code File for Security Scan",
            filetypes=[
                ("Python files", "*.py"),
                ("JavaScript files", "*.js"),
                ("Java files", "*.java"),
                ("C++ files", "*.cpp *.cc *.cxx"),
                ("C# files", "*.cs"),
                ("PHP files", "*.php"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.parent.security_code_input.delete("1.0", tk.END)
                self.parent.security_code_input.insert("1.0", content)
                
                if hasattr(self.parent, 'status_var'):
                    self.parent.status_var.set(f"📂 Loaded for scanning: {file_path}")
                
                logger.info(f"Loaded file for security scan: {file_path}")
                
            except Exception as e:
                messagebox.showerror("File Error", f"Failed to load file: {str(e)}")
    
    def _clear_code_input(self):
        """Clear the code input area."""
        self.parent.security_code_input.delete("1.0", tk.END)
        
        if hasattr(self.parent, 'status_var'):
            self.parent.status_var.set("🗑️ Security scan input cleared")
    
    def _clear_results(self):
        """Clear the scan results."""
        self.parent.security_results.config(state='normal')
        self.parent.security_results.delete("1.0", tk.END)
        self.parent.security_results.config(state='disabled')
        
        self.scan_results.clear()
        
        if hasattr(self.parent, 'status_var'):
            self.parent.status_var.set("🗑️ Security scan results cleared")
    
    @ErrorHandler.handle_error("Export Report")
    def export_report(self):
        """Export security scan report."""
        if not self.scan_results:
            messagebox.showinfo("No Results", "No scan results to export.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export Security Report",
            defaultextension=".txt",
            filetypes=[
                ("Text files", "*.txt"),
                ("JSON files", "*.json"),
                ("HTML files", "*.html"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                if file_path.endswith('.json'):
                    import json
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(self.scan_results, f, indent=2)
                elif file_path.endswith('.html'):
                    self._export_html_report(file_path)
                else:
                    self._export_text_report(file_path)
                
                messagebox.showinfo("Export Complete", f"Security report exported to: {file_path}")
                
                if hasattr(self.parent, 'status_var'):
                    self.parent.status_var.set(f"📤 Security report exported: {file_path}")
                
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export report: {str(e)}")
    
    def _export_text_report(self, file_path: str):
        """Export security report as text."""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("CodedSwitch Security Scan Report\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Total vulnerabilities found: {len(self.scan_results)}\n\n")
            
            for i, vuln in enumerate(self.scan_results, 1):
                f.write(f"{i}. {vuln['type']} (Line {vuln['line']})\n")
                f.write(f"   Severity: {vuln['severity']}\n")
                f.write(f"   Code: {vuln['code']}\n")
                f.write(f"   Description: {vuln['description']}\n\n")
    
    def _export_html_report(self, file_path: str):
        """Export security report as HTML."""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>CodedSwitch Security Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .vulnerability {{ border: 1px solid #ddd; margin: 10px 0; padding: 10px; }}
                .high {{ border-left: 5px solid #ff4444; }}
                .medium {{ border-left: 5px solid #ffaa00; }}
                .low {{ border-left: 5px solid #44ff44; }}
                .code {{ background: #f5f5f5; padding: 5px; font-family: monospace; }}
            </style>
        </head>
        <body>
            <h1>CodedSwitch Security Scan Report</h1>
            <p>Total vulnerabilities found: {len(self.scan_results)}</p>
        """
        
        for i, vuln in enumerate(self.scan_results, 1):
            severity_class = vuln['severity'].lower()
            html_content += f"""
            <div class="vulnerability {severity_class}">
                <h3>{i}. {vuln['type']} (Line {vuln['line']})</h3>
                <p><strong>Severity:</strong> {vuln['severity']}</p>
                <p><strong>Code:</strong></p>
                <div class="code">{vuln['code']}</div>
                <p><strong>Description:</strong> {vuln['description']}</p>
            </div>
            """
        
        html_content += """
        </body>
        </html>
        """
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    @ErrorHandler.handle_error("Auto Fix Vulnerabilities")
    def auto_fix_vulnerabilities(self):
        """Auto-fix detected vulnerabilities."""
        logger.info("'auto_fix_vulnerabilities' called.")
        messagebox.showinfo("Auto Fix", "Auto-fix vulnerabilities feature is not yet implemented.")
