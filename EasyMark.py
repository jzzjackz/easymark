import re
import os
import sys
import argparse
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

def markup_cvrt(text):
    # Process line-based commands first (order matters)
    text = re.sub(r'^\@header (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    text = re.sub(r'^\$mark (.+)$', r'<b>\1</b>', text, flags=re.MULTILINE)
    text = re.sub(r'^\$url\((.*?)\)\[(.*?)\]$', r'<a href="\1">\2</a>', text, flags=re.MULTILINE)
    text = re.sub(r'^@small (.+)$', r'<h6>\1</h6>', text, flags=re.MULTILINE)
    text = re.sub(r'^\$cb (.+)$', r'<code>\1</code>', text, flags=re.MULTILINE)
    
    # Process list items before inline formatting
    text = re.sub(r'(?m)^- (.+)$', r'<li>\1</li>', text)
    text = re.sub(r'((?:<li>.*?</li>\n?)+)', r'<ul>\1</ul>', text)
    
    # Process inline formatting (bold text in parentheses)
    # More permissive pattern - matches any text in parentheses (allows numbers, more punctuation, etc.)
    # Avoid matching if already inside HTML tags by checking the context
    def replace_parentheses(match):
        content = match.group(1)
        # Skip if content contains HTML tags (already processed)
        if '<' in content or '>' in content:
            return match.group(0)
        return f'<b>{content}</b>'
    
    # Match parentheses with any characters except parentheses and angle brackets
    # This allows numbers, all punctuation, and any other characters
    text = re.sub(r'\(([^()<>]+)\)', replace_parentheses, text)
    
    # Process italic text (between ampersands)
    text = re.sub(r'&([^&]+)&', r'<i>\1</i>', text)
    return text

def markup_to_markdown(text):
    """Convert EasyMark syntax to Markdown"""
    # Process line-based commands first
    text = re.sub(r'^\@header (.+)$', r'# \1', text, flags=re.MULTILINE)
    text = re.sub(r'^\$mark (.+)$', r'**\1**', text, flags=re.MULTILINE)
    text = re.sub(r'^\$url\((.*?)\)\[(.*?)\]$', r'[\2](\1)', text, flags=re.MULTILINE)
    text = re.sub(r'^@small (.+)$', r'###### \1', text, flags=re.MULTILINE)
    text = re.sub(r'^\$cb (.+)$', r'```\n\1\n```', text, flags=re.MULTILINE)
    
    # List items stay the same
    # Process inline bold (parentheses)
    text = re.sub(r'\(([^()<>]+)\)', r'**\1**', text)
    
    # Process italic
    text = re.sub(r'&([^&]+)&', r'*\1*', text)
    
    return text

def html_to_easymark(html_text):
    """Convert HTML back to EasyMark syntax"""
    # Remove html/body tags
    html_text = re.sub(r'<html>.*?<body>', '', html_text, flags=re.DOTALL | re.IGNORECASE)
    html_text = re.sub(r'</body>.*?</html>', '', html_text, flags=re.DOTALL | re.IGNORECASE)
    
    # Convert HTML tags back to EasyMark
    # Headers
    html_text = re.sub(r'<h1>(.+?)</h1>', r'@header \1', html_text, flags=re.IGNORECASE)
    html_text = re.sub(r'<h6>(.+?)</h6>', r'@small \1', html_text, flags=re.IGNORECASE)
    
    # Code blocks
    html_text = re.sub(r'<code>(.+?)</code>', r'$cb \1', html_text, flags=re.IGNORECASE | re.DOTALL)
    
    # Links
    html_text = re.sub(r'<a href="([^"]+?)">(.+?)</a>', r'$url(\1)[\2]', html_text, flags=re.IGNORECASE)
    
    # Lists - convert <ul><li>...</li></ul> back to - ...
    def process_list(match):
        list_content = match.group(1)
        # Extract all list items
        items = re.findall(r'<li>(.+?)</li>', list_content, flags=re.IGNORECASE | re.DOTALL)
        return '\n'.join(f'- {item.strip()}' for item in items) + '\n'
    
    html_text = re.sub(r'<ul>(.*?)</ul>', process_list, html_text, flags=re.IGNORECASE | re.DOTALL)
    
    # Bold - try to determine if it's line-based or inline
    # First handle line-based bold (whole line)
    html_text = re.sub(r'^<b>(.+?)</b>$', r'$mark \1', html_text, flags=re.MULTILINE | re.IGNORECASE)
    # Then inline bold
    html_text = re.sub(r'<b>(.+?)</b>', r'(\1)', html_text, flags=re.IGNORECASE)
    
    # Italic
    html_text = re.sub(r'<i>(.+?)</i>', r'&\1&', html_text, flags=re.IGNORECASE)
    
    return html_text.strip()

def convert_em_to_html(filename):
    """Convert .em file to .html"""
    if not filename.endswith(".em"):
        print("Error: File must have .em extension")
        return False
    
    if not os.path.exists(filename):
        print(f"Error: File not found: {filename}")
        return False
    
    try:
        with open(filename, "r", encoding="utf-8") as f:
            source = f.read()
        
        html = markup_cvrt(source)
        output_name = filename.rsplit(".", 1)[0] + ".html"
        
        with open(output_name, "w", encoding="utf-8") as f:
            f.write(f"<html><body>{html}</body></html>")
        
        print(f"Successfully converted {filename} → {output_name}")
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def convert_em_to_md(filename):
    """Convert .em file to .md (Markdown)"""
    if not filename.endswith(".em"):
        print("Error: File must have .em extension")
        return False
    
    if not os.path.exists(filename):
        print(f"Error: File not found: {filename}")
        return False
    
    try:
        with open(filename, "r", encoding="utf-8") as f:
            source = f.read()
        
        markdown = markup_to_markdown(source)
        output_name = filename.rsplit(".", 1)[0] + ".md"
        
        with open(output_name, "w", encoding="utf-8") as f:
            f.write(markdown)
        
        print(f"Successfully converted {filename} → {output_name}")
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def convert_html_to_em(filename):
    """Convert .html file back to .em"""
    if not filename.endswith(".html"):
        print("Error: File must have .html extension")
        return False
    
    if not os.path.exists(filename):
        print(f"Error: File not found: {filename}")
        return False
    
    try:
        with open(filename, "r", encoding="utf-8") as f:
            html_content = f.read()
        
        easymark = html_to_easymark(html_content)
        output_name = filename.rsplit(".", 1)[0] + ".em"
        
        with open(output_name, "w", encoding="utf-8") as f:
            f.write(easymark)
        
        print(f"Successfully converted {filename} → {output_name}")
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def show_info():
    """Show version information"""
    print("Command line-based interpreter protocol for EasyMark.")
    print("")
    print("Compatible versions: v1.1.0+")

def show_help():
    """Show all available commands"""
    print("EasyMark Interpreter (eminterp) - Command Line Interface")
    print("")
    print("Usage: eminterp [OPTION] [FILENAME]")
    print("")
    print("Options:")
    print("  -c FILENAME      Convert .em file to .html")
    print("  -cmd FILENAME    Convert .em file to .md (Markdown)")
    print("  -dc FILENAME     Convert .html file back to .em")
    print("  -info            Show version information")
    print("  -help            Show this help message")
    print("")
    print("Examples:")
    print("  eminterp -c document.em")
    print("  eminterp -cmd document.em")
    print("  eminterp -dc document.html")

def handle_command_line():
    """Handle command-line arguments"""
    # Check if any arguments were provided
    # sys.argv[0] is the script name, so if len is 1, only script name is present
    if len(sys.argv) <= 1:
        return None  # No arguments - launch GUI
    
    # Create parser with proper error handling
    # Use parse_known_args to avoid SystemExit on unknown args
    parser_kwargs = {
        'description': 'EasyMark Interpreter - Command line converter',
        'add_help': False
    }
    # exit_on_error is only available in Python 3.9+
    if sys.version_info >= (3, 9):
        parser_kwargs['exit_on_error'] = False
    
    parser = argparse.ArgumentParser(**parser_kwargs)
    
    parser.add_argument('-c', '--convert', type=str, metavar='FILENAME',
                       help='Convert .em file to .html')
    parser.add_argument('-cmd', type=str, metavar='FILENAME',
                       help='Convert .em file to .md (Markdown)')
    parser.add_argument('-dc', '--deconvert', type=str, metavar='FILENAME',
                       help='Convert .html file back to .em')
    parser.add_argument('-info', action='store_true',
                       help='Show version information')
    parser.add_argument('-help', action='store_true',
                       help='Show help message')
    
    try:
        args, unknown = parser.parse_known_args()
    except (argparse.ArgumentError, SystemExit) as e:
        # Handle parsing errors
        print(f"Error parsing arguments: {str(e)}", file=sys.stderr)
        print("Use -help to see available options.", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return False
    
    # Check for unknown arguments
    if unknown:
        print(f"Error: Unknown argument(s): {' '.join(unknown)}", file=sys.stderr)
        print("Use -help to see available options.", file=sys.stderr)
        return False
    
    # Handle different commands - check in order
    if args.help:
        show_help()
        return True
    elif args.info:
        show_info()
        return True
    elif args.convert:
        return convert_em_to_html(args.convert)
    elif args.cmd:
        return convert_em_to_md(args.cmd)
    elif args.deconvert:
        return convert_html_to_em(args.deconvert)
    else:
        # Arguments were provided but no valid command found
        # This can happen if user provides invalid arguments
        print("Error: No valid command specified.", file=sys.stderr)
        print("Use -help to see available options.", file=sys.stderr)
        return False

class EasyMarkConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("EasyMark Reader")
        self.root.geometry("600x320")
        self.root.resizable(False, False)
        
        # Modern color scheme
        self.bg_color = "#2b2b2b"
        self.secondary_bg = "#3c3c3c"
        self.accent_color = "#4a9eff"
        self.accent_hover = "#5dadff"
        self.text_color = "#ffffff"
        self.text_secondary = "#b0b0b0"
        self.success_color = "#4caf50"
        self.error_color = "#f44336"
        
        # Configure root
        self.root.configure(bg=self.bg_color)
        
        # Style configuration
        self.setup_styles()
        
        # Header frame
        header_frame = tk.Frame(root, bg=self.secondary_bg, height=80)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="EasyMark Converter",
            font=("Segoe UI", 24, "bold"),
            bg=self.secondary_bg,
            fg=self.text_color
        )
        title_label.pack(pady=20)
        
        subtitle_label = tk.Label(
            header_frame,
            text="Convert .em files to HTML",
            font=("Segoe UI", 10),
            bg=self.secondary_bg,
            fg=self.text_secondary
        )
        subtitle_label.pack()
        
        # Main content frame
        main_frame = tk.Frame(root, bg=self.bg_color, padx=30, pady=25)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # File selection section
        file_label = tk.Label(
            main_frame,
            text="Select EasyMark File",
            font=("Segoe UI", 11, "bold"),
            bg=self.bg_color,
            fg=self.text_color,
            anchor="w"
        )
        file_label.pack(fill=tk.X, pady=(0, 10))
        
        file_frame = tk.Frame(main_frame, bg=self.bg_color)
        file_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.filename_var = tk.StringVar()
        entry_style = {
            "font": ("Segoe UI", 10),
            "bg": self.secondary_bg,
            "fg": self.text_color,
            "insertbackground": self.text_color,
            "relief": tk.FLAT,
            "borderwidth": 0,
            "highlightthickness": 1,
            "highlightbackground": "#555555",
            "highlightcolor": self.accent_color
        }
        self.filename_entry = tk.Entry(
            file_frame,
            textvariable=self.filename_var,
            width=45,
            **entry_style
        )
        self.filename_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10), ipady=8)
        
        browse_btn = tk.Button(
            file_frame,
            text="File Browser",
            command=self.browse_file,
            font=("Segoe UI", 10, "bold"),
            bg=self.secondary_bg,
            fg=self.text_color,
            activebackground="#4a4a4a",
            activeforeground=self.text_color,
            relief=tk.FLAT,
            borderwidth=0,
            padx=20,
            pady=8,
            cursor="hand2"
        )
        browse_btn.pack(side=tk.LEFT)
        self.setup_hover_effect(browse_btn, self.secondary_bg, "#4a4a4a")
        
        # Convert button
        convert_btn = tk.Button(
            main_frame,
            text="Convert to HTML",
            command=self.convert_file,
            font=("Segoe UI", 12, "bold"),
            bg=self.accent_color,
            fg="white",
            activebackground=self.accent_hover,
            activeforeground="white",
            relief=tk.FLAT,
            borderwidth=0,
            padx=30,
            pady=12,
            cursor="hand2"
        )
        convert_btn.pack(pady=(10, 15))
        self.setup_hover_effect(convert_btn, self.accent_color, self.accent_hover)
        
        # Status frame with better styling
        status_frame = tk.Frame(main_frame, bg=self.secondary_bg, relief=tk.FLAT, bd=0)
        status_frame.pack(fill=tk.X, pady=(5, 0), ipady=12)
        
        self.status_label = tk.Label(
            status_frame,
            text="Ready to convert",
            font=("Segoe UI", 10),
            bg=self.secondary_bg,
            fg=self.text_secondary,
            anchor="center"
        )
        self.status_label.pack()
    
    def setup_styles(self):
        """Configure ttk styles for better appearance"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure entry style
        style.configure(
            "Modern.TEntry",
            fieldbackground=self.secondary_bg,
            borderwidth=0,
            relief=tk.FLAT
        )
    
    def setup_hover_effect(self, widget, normal_color, hover_color):
        """Add hover effect to buttons"""
        def on_enter(e):
            widget.config(bg=hover_color)
        
        def on_leave(e):
            widget.config(bg=normal_color)
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select EasyMark file",
            filetypes=[("EasyMark files", "*.em"), ("All files", "*.*")]
        )
        if filename:
            self.filename_var.set(filename)
            self.status_label.config(text="File selected - Ready to convert", fg=self.text_secondary)
    
    def convert_file(self):
        filename = self.filename_var.get().strip()
        
        if not filename:
            self.status_label.config(text="File Error: No File Selected", fg=self.error_color)
            messagebox.showerror("Error", "Please select a file first.")
            return
        
        if not filename.endswith(".em"):
            self.status_label.config(text="Error reading file: Unsupported FileType", fg=self.error_color)
            messagebox.showerror("Error", "Unsupported FileType. Please select a .em file.")
            return
        
        if not os.path.exists(filename):
            self.status_label.config(text="Reading Error: File Not Found", fg=self.error_color)
            messagebox.showerror("Error", "File Not Found (FNF)")
            return
        
        try:
            # Update status to show conversion in progress
            self.status_label.config(text= "Converting...", fg=self.accent_color)
            self.root.update()
            
            with open(filename, "r", encoding="utf-8") as f:
                source = f.read()
            
            html = markup_cvrt(source)
            
            output_name = filename.rsplit(".", 1)[0] + ".html"
            with open(output_name, "w", encoding="utf-8") as f:
                f.write(f"<html><body>{html}</body></html>")
            
            success_msg = f" Successfully converted {os.path.basename(filename)} → {os.path.basename(output_name)}"
            self.status_label.config(text=success_msg, fg=self.success_color)
            messagebox.showinfo("Success", f"Converted {os.path.basename(filename)} to {os.path.basename(output_name)}")
        except Exception as e:
            error_msg = f"Conversion failed: {str(e)}"
            self.status_label.config(text=error_msg, fg=self.error_color)
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

if __name__ == "__main__":
    # Check for command-line arguments FIRST, before any GUI initialization
    # This ensures commands are executed without opening the GUI
    try:
        result = handle_command_line()
        
        # If result is None, no arguments were provided - launch GUI
        if result is None:
            root = tk.Tk()
            app = EasyMarkConverter(root)
            root.mainloop()
        # If result is False, there was an error - exit with error code
        elif result is False:
            sys.exit(1)
        # If result is True, command executed successfully - exit normally
        else:
            sys.exit(0)
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        sys.exit(130)
    except Exception as e:
        # If there's an unexpected error and we have arguments, don't show GUI
        if len(sys.argv) > 1:
            print(f"Error: {str(e)}", file=sys.stderr)
            sys.exit(1)
        else:
            # No arguments, show GUI anyway
            root = tk.Tk()
            app = EasyMarkConverter(root)
            root.mainloop()
