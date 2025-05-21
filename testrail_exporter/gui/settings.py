import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import os
import sys


class SettingsFrame(ttk.LabelFrame):
    """Frame for TestRail connection settings."""

    def __init__(self, parent, *args, **kwargs):
        """
        Initialize the settings frame.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent, text="Settings", padding=10, *args, **kwargs)
        self.parent = parent
        
        # Default values
        default_url = "https://testrail.testeng.mlbinfra.net"
        default_username = os.environ.get("TESTRAIL_USER", "")
        default_api_key = os.environ.get("TESTRAIL_KEY", "")
        default_export_dir = os.path.expanduser("~/Documents")
        
        # URL
        ttk.Label(self, text="TestRail URL:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.url_var = tk.StringVar(value=default_url)
        ttk.Entry(self, textvariable=self.url_var, width=50).grid(row=0, column=1, sticky=tk.EW, pady=5)
        
        # Username
        ttk.Label(self, text="Username:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.username_var = tk.StringVar(value=default_username)
        ttk.Entry(self, textvariable=self.username_var, width=50).grid(row=1, column=1, sticky=tk.EW, pady=5)
        
        # API Key with show/hide toggle
        ttk.Label(self, text="API Key:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.api_key_var = tk.StringVar(value=default_api_key)
        
        # Frame for API key entry and toggle button
        api_key_frame = ttk.Frame(self)
        api_key_frame.grid(row=2, column=1, sticky=tk.EW, pady=5)
        
        # API Key entry
        self.api_key_entry = ttk.Entry(api_key_frame, textvariable=self.api_key_var, width=45, show="*")
        self.api_key_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Toggle button for showing/hiding the API key
        self.show_key = tk.BooleanVar(value=False)
        ttk.Checkbutton(api_key_frame, text="Show", variable=self.show_key, 
                        command=self._toggle_api_key_visibility).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Export Directory
        ttk.Label(self, text="Export Directory:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.export_dir_var = tk.StringVar(value=default_export_dir)
        export_frame = ttk.Frame(self)
        export_frame.grid(row=3, column=1, sticky=tk.EW, pady=5)
        ttk.Entry(export_frame, textvariable=self.export_dir_var, width=42).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(export_frame, text="Browse...", command=self._browse_export_dir).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Test Connection Button
        ttk.Button(self, text="Test Connection", command=self._test_connection).grid(row=4, column=0, pady=10, padx=5)
        
        # Save Settings Button
        ttk.Button(self, text="Save Settings", command=self._save_settings).grid(row=4, column=1, pady=10, padx=5, sticky=tk.E)
        
        # Status Message - Replaced label with text widget for better visibility and copy-paste
        ttk.Label(self, text="Status:").grid(row=5, column=0, sticky=tk.NW, pady=5)
        
        # Create a scrolled text widget for status messages
        self.status_text = scrolledtext.ScrolledText(self, height=4, width=10, wrap=tk.WORD)
        self.status_text.grid(row=5, column=1, sticky=tk.EW, pady=5)
        self.status_text.config(state=tk.DISABLED)  # Make it read-only by default
        
        # Detect if we're in dark mode
        self._configure_status_colors()
        
        # Configure grid
        self.columnconfigure(1, weight=1)
        
    def _configure_status_colors(self):
        """Configure colors based on dark/light mode"""
        # Try to detect dark mode - this is a simple heuristic
        # A more robust method would use platform-specific APIs
        try:
            bg_color = self.tk_getPalette()["background"]
            is_dark_mode = self._is_dark_color(bg_color)
        except:
            # Default to light mode if detection fails
            is_dark_mode = False
            
        if is_dark_mode:
            # Dark mode colors (light text on dark background)
            text_bg = "#2e2e2e"
            text_fg = "#e0e0e0"  # Light gray text
            success_color = "#5cb85c"  # Green
            error_color = "#ff7f7f"  # Light red
        else:
            # Light mode colors (dark text on light background)
            text_bg = "#f0f0f0"
            text_fg = "#000000"  # Black text
            success_color = "#28a745"  # Green
            error_color = "#dc3545"  # Red
            
        self.status_text.config(bg=text_bg, fg=text_fg)
        self.success_color = success_color
        self.error_color = error_color
    
    def _is_dark_color(self, color):
        """Determine if a color is dark based on its hex value"""
        if color.startswith("#"):
            # Convert hex to RGB
            r = int(color[1:3], 16) if len(color) >= 3 else 0
            g = int(color[3:5], 16) if len(color) >= 5 else 0
            b = int(color[5:7], 16) if len(color) >= 7 else 0
            
            # Calculate perceived brightness using weighted average
            brightness = (r * 299 + g * 587 + b * 114) / 1000
            
            # Return True if the color is dark (brightness < 128)
            return brightness < 128
        return False
    
    def _toggle_api_key_visibility(self):
        """Toggle the visibility of the API key."""
        if self.show_key.get():
            self.api_key_entry.config(show="")
        else:
            self.api_key_entry.config(show="*")
        
    def _browse_export_dir(self):
        """Open a directory dialog to select the export directory."""
        directory = filedialog.askdirectory(
            initialdir=self.export_dir_var.get(),
            title="Select Export Directory"
        )
        if directory:
            self.export_dir_var.set(directory)
            
    def _test_connection(self):
        """Test the connection to TestRail."""
        url = self.url_var.get()
        username = self.username_var.get()
        api_key = self.api_key_var.get()
        
        if not url or not username or not api_key:
            self._set_status_text("Error: All fields are required", is_error=True)
            return
        
        try:
            # Import TestRailClient only when needed to avoid circular imports
            from testrail_exporter.api.testrail_client import TestRailClient
            client = TestRailClient(url, username, api_key)
            projects = client.get_projects()
            self._set_status_text(f"Connection successful! Found {len(projects)} projects.", is_error=False)
        except Exception as e:
            self._set_status_text(f"Error: {str(e)}", is_error=True)
    
    def _set_status_text(self, message, is_error=False):
        """Set the status text with appropriate styling."""
        # Enable editing
        self.status_text.config(state=tk.NORMAL)
        
        # Clear previous content
        self.status_text.delete(1.0, tk.END)
        
        # Insert new message with color based on error status
        color = self.error_color if is_error else self.success_color
        self.status_text.insert(tk.END, message)
        self.status_text.tag_configure("colored", foreground=color)
        self.status_text.tag_add("colored", 1.0, tk.END)
        
        # Make selectable but not editable
        self.status_text.config(state=tk.DISABLED)
    
    def _save_settings(self):
        """Save the current settings."""
        # In a real application, you might save these to a config file
        self._set_status_text("Settings saved!", is_error=False)
        
    def get_settings(self):
        """
        Get the current settings.
        
        Returns:
            dict: Current settings
        """
        return {
            'url': self.url_var.get(),
            'username': self.username_var.get(),
            'api_key': self.api_key_var.get(),
            'export_dir': self.export_dir_var.get()
        }