import tkinter as tk
from tkinter import ttk, filedialog
import os


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
        
        # API Key
        ttk.Label(self, text="API Key:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.api_key_var = tk.StringVar(value=default_api_key)
        ttk.Entry(self, textvariable=self.api_key_var, width=50, show="*").grid(row=2, column=1, sticky=tk.EW, pady=5)
        
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
        
        # Status Label
        self.status_var = tk.StringVar()
        ttk.Label(self, textvariable=self.status_var, foreground="blue").grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Configure grid
        self.columnconfigure(1, weight=1)
        
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
            self.status_var.set("Error: All fields are required")
            return
        
        try:
            # Import TestRailClient only when needed to avoid circular imports
            from api.testrail_client import TestRailClient
            client = TestRailClient(url, username, api_key)
            projects = client.get_projects()
            self.status_var.set(f"Connection successful! Found {len(projects)} projects.")
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
    
    def _save_settings(self):
        """Save the current settings."""
        # In a real application, you might save these to a config file
        self.status_var.set("Settings saved!")
        
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