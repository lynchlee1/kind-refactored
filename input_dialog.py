import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import threading
import sys

class InputDialog:
    def __init__(self):
        self.result = None
        self.root = None
        
    def show_dialog(self):
        """Show the input dialog and return the result"""
        self.root = tk.Tk()
        self.root.title("KIND Project - Configuration")
        self.root.geometry("450x600")
        self.root.resizable(False, False)
        
        # Center the window
        self.root.eval('tk::PlaceWindow . center')
        
        # Configure style
        self.setup_style()
        
        # Create main frame
        main_frame = tk.Frame(self.root, bg='#f8f9fa', padx=30, pady=30)
        main_frame.pack(fill='both', expand=True)
        
        # Header
        self.create_header(main_frame)
        
        # Input fields
        self.create_input_fields(main_frame)
        
        # Action buttons
        self.create_buttons(main_frame)
        
        # Make window modal
        self.root.transient()
        self.root.grab_set()
        
        # Start the dialog
        self.root.mainloop()
        
        return self.result
    
    def setup_style(self):
        """Configure the visual style"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure button styles
        style.configure('Blue.TButton',
                       background='#007bff',
                       foreground='white',
                       font=('SF Pro Display', 12, 'bold'),
                       padding=(20, 12))
        
        style.configure('Gray.TButton',
                       background='#6c757d',
                       foreground='white',
                       font=('SF Pro Display', 12),
                       padding=(20, 12))
        
        # Configure entry styles
        style.configure('Custom.TEntry',
                       fieldbackground='white',
                       borderwidth=2,
                       relief='solid',
                       font=('SF Pro Display', 11))
    
    def create_header(self, parent):
        """Create the header section"""
        header_frame = tk.Frame(parent, bg='#f8f9fa')
        header_frame.pack(fill='x', pady=(0, 30))
        
        # Title
        title_label = tk.Label(header_frame,
                              text="KIND Project",
                              font=('SF Pro Display', 24, 'bold'),
                              fg='#2c3e50',
                              bg='#f8f9fa')
        title_label.pack(anchor='w')
        
        # Subtitle
        subtitle_label = tk.Label(header_frame,
                                 text="Configure your web scraping parameters",
                                 font=('SF Pro Display', 14),
                                 fg='#6c757d',
                                 bg='#f8f9fa')
        subtitle_label.pack(anchor='w', pady=(5, 0))
    
    def create_input_fields(self, parent):
        """Create input fields"""
        fields_frame = tk.Frame(parent, bg='#f8f9fa')
        fields_frame.pack(fill='both', expand=True)
        
        # Company Name
        company_frame = tk.Frame(fields_frame, bg='#f8f9fa')
        company_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(company_frame,
                text="Company Name",
                font=('SF Pro Display', 12, 'bold'),
                fg='#2c3e50',
                bg='#f8f9fa').pack(anchor='w')
        
        self.company_entry = tk.Entry(company_frame,
                                    font=('SF Pro Display', 11),
                                    relief='solid',
                                    borderwidth=2,
                                    bg='white',
                                    fg='#2c3e50')
        self.company_entry.pack(fill='x', pady=(8, 0), ipady=8)
        self.company_entry.insert(0, "에스티팜")
        
        # Date Range
        date_frame = tk.Frame(fields_frame, bg='#f8f9fa')
        date_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(date_frame,
                text="Date Range",
                font=('SF Pro Display', 12, 'bold'),
                fg='#2c3e50',
                bg='#f8f9fa').pack(anchor='w')
        
        # From Date
        from_frame = tk.Frame(date_frame, bg='#f8f9fa')
        from_frame.pack(fill='x', pady=(8, 10))
        
        tk.Label(from_frame,
                text="From Date",
                font=('SF Pro Display', 10),
                fg='#6c757d',
                bg='#f8f9fa').pack(anchor='w')
        
        self.from_entry = tk.Entry(from_frame,
                                 font=('SF Pro Display', 11),
                                 relief='solid',
                                 borderwidth=2,
                                 bg='white',
                                 fg='#2c3e50')
        self.from_entry.pack(fill='x', pady=(5, 0), ipady=6)
        self.from_entry.insert(0, "2024-09-20")
        
        # To Date
        to_frame = tk.Frame(date_frame, bg='#f8f9fa')
        to_frame.pack(fill='x')
        
        tk.Label(to_frame,
                text="To Date",
                font=('SF Pro Display', 10),
                fg='#6c757d',
                bg='#f8f9fa').pack(anchor='w')
        
        self.to_entry = tk.Entry(to_frame,
                               font=('SF Pro Display', 11),
                               relief='solid',
                               borderwidth=2,
                               bg='white',
                               fg='#2c3e50')
        self.to_entry.pack(fill='x', pady=(5, 0), ipady=6)
        self.to_entry.insert(0, "2025-09-30")
        
        # Max Rows
        rows_frame = tk.Frame(fields_frame, bg='#f8f9fa')
        rows_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(rows_frame,
                text="Maximum Rows per Page",
                font=('SF Pro Display', 12, 'bold'),
                fg='#2c3e50',
                bg='#f8f9fa').pack(anchor='w')
        
        self.rows_entry = tk.Entry(rows_frame,
                                 font=('SF Pro Display', 11),
                                 relief='solid',
                                 borderwidth=2,
                                 bg='white',
                                 fg='#2c3e50')
        self.rows_entry.pack(fill='x', pady=(8, 0), ipady=8)
        self.rows_entry.insert(0, "200")
        
        # Headless Mode
        self.headless_var = tk.BooleanVar()
        headless_check = tk.Checkbutton(fields_frame,
                                      text="Run in background (headless mode)",
                                      font=('SF Pro Display', 11),
                                      fg='#2c3e50',
                                      bg='#f8f9fa',
                                      selectcolor='#007bff',
                                      variable=self.headless_var)
        headless_check.pack(anchor='w', pady=(0, 20))
    
    def create_buttons(self, parent):
        """Create action buttons"""
        buttons_frame = tk.Frame(parent, bg='#f8f9fa')
        buttons_frame.pack(fill='x', pady=(20, 0))
        
        # Start Button
        start_btn = tk.Button(buttons_frame,
                            text="Start Scraping",
                            font=('SF Pro Display', 12, 'bold'),
                            bg='#007bff',
                            fg='white',
                            relief='flat',
                            cursor='hand2',
                            command=self.start_scraping)
        start_btn.pack(side='right', padx=(10, 0), ipady=8, ipadx=20)
        
        # Cancel Button
        cancel_btn = tk.Button(buttons_frame,
                             text="Cancel",
                             font=('SF Pro Display', 12),
                             bg='#6c757d',
                             fg='white',
                             relief='flat',
                             cursor='hand2',
                             command=self.cancel)
        cancel_btn.pack(side='right', ipady=8, ipadx=20)
    
    def validate_inputs(self):
        """Validate user inputs"""
        try:
            # Validate dates
            from_date = datetime.strptime(self.from_entry.get(), '%Y-%m-%d')
            to_date = datetime.strptime(self.to_entry.get(), '%Y-%m-%d')
            
            if from_date > to_date:
                messagebox.showerror("Invalid Date Range", "From date cannot be after To date")
                return False
            
            # Validate max rows
            max_rows = int(self.rows_entry.get())
            if max_rows <= 0:
                messagebox.showerror("Invalid Input", "Maximum rows must be greater than 0")
                return False
            
            # Validate company name
            if not self.company_entry.get().strip():
                messagebox.showerror("Invalid Input", "Company name cannot be empty")
                return False
            
            return True
            
        except ValueError as e:
            messagebox.showerror("Invalid Input", "Please check your date format (YYYY-MM-DD) and ensure max rows is a number")
            return False
    
    def start_scraping(self):
        """Handle start button click"""
        if self.validate_inputs():
            self.result = {
                'company_name': self.company_entry.get().strip(),
                'from_date': self.from_entry.get().strip(),
                'to_date': self.to_entry.get().strip(),
                'max_rows': int(self.rows_entry.get()),
                'headless': self.headless_var.get()
            }
            self.root.destroy()
    
    def cancel(self):
        """Handle cancel button click"""
        self.result = None
        self.root.destroy()

def get_user_input():
    """Main function to show the input dialog"""
    dialog = InputDialog()
    return dialog.show_dialog()

if __name__ == "__main__":
    result = get_user_input()
    if result:
        print("User input:", result)
    else:
        print("User cancelled")
