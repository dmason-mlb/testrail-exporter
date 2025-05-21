import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import json
import os
import time
from PIL import Image, ImageTk
from testrail_exporter.utils.exporter import Exporter

from testrail_exporter.gui.settings import SettingsFrame
from testrail_exporter.gui.tree_view import CheckableTreeview
from testrail_exporter.api.testrail_client import TestRailClient
from testrail_exporter.models.project import Project
from testrail_exporter.models.suite import Suite
from testrail_exporter.models.section import Section
from testrail_exporter.models.case import Case
from testrail_exporter.utils.config import Config


class Application(tk.Tk):
    """Main application window."""

    def __init__(self):
        """Initialize the application."""
        super().__init__()
        
        # Load configuration
        self.config = Config()
        
        # Set window title and size
        self.title("TestRail Exporter")
        window_width = self.config.get_setting('ui', 'window_width', 1200)
        window_height = self.config.get_setting('ui', 'window_height', 800)
        self.geometry(f"{window_width}x{window_height}")
        self.minsize(1000, 700)
        
        # Save window size when closing the application
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Create main frame
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Settings frame
        self.settings_frame = SettingsFrame(main_frame, config=self.config)
        self.settings_frame.pack(fill=tk.X, pady=10)
        
        # Project selection
        project_frame = ttk.Frame(main_frame)
        project_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(project_frame, text="Project:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.project_var = tk.StringVar()
        self.project_combo = ttk.Combobox(project_frame, textvariable=self.project_var, state="readonly", width=50)
        self.project_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.project_combo.bind("<<ComboboxSelected>>", self._on_project_selected)
        
        ttk.Button(project_frame, text="Load Projects", command=self._load_projects).pack(side=tk.LEFT, padx=(10, 0))
        
        # Create treeview frame with scrollbars
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Treeview for suites and sections
        self.tree = CheckableTreeview(tree_frame, columns=("name",), show="tree")
        self.tree.column("#0", width=50, minwidth=50, stretch=False)
        self.tree.column("name", width=200, minwidth=200)
        self.tree.heading("name", text="Suites and Sections")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=vsb.set)
        
        # Tree control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Expand All", command=self.tree.expand_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Collapse All", command=self.tree.collapse_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Check All", command=self.tree.check_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Uncheck All", command=self.tree.uncheck_all).pack(side=tk.LEFT, padx=5)
        
        # Export buttons
        export_frame = ttk.Frame(button_frame)
        export_frame.pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(export_frame, text="Export JSON", command=lambda: self._export_cases(format='json')).pack(side=tk.RIGHT, padx=2)
        ttk.Button(export_frame, text="Export CSV", command=lambda: self._export_cases(format='csv')).pack(side=tk.RIGHT, padx=2)
        
        # Progress bar and status
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=15)
        
        self.status_var = tk.StringVar()
        ttk.Label(status_frame, textvariable=self.status_var).pack(side=tk.LEFT)
        
        self.progress_frame = ttk.Frame(status_frame)
        self.progress_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(20, 0))
        
        self.progress_var = tk.IntVar()
        self.progress = ttk.Progressbar(
            self.progress_frame, 
            orient=tk.HORIZONTAL, 
            length=100, 
            mode='determinate',
            variable=self.progress_var
        )
        self.progress.pack(fill=tk.X, expand=True)
        
        # Add more padding and make the progress label larger
        self.progress_label = ttk.Label(self.progress_frame, text="", font=("", 10))
        self.progress_label.pack(pady=(5, 5))
        
        # Initialize instance variables
        self.client = None
        self.projects = []
        self.current_project = None
        self.api_calls_total = 0
        self.api_calls_done = 0
        
        # Thread control flag
        self.loading_cancelled = False
        self.active_thread = None
    
    def _on_close(self):
        """Save settings and close the application."""
        # Cancel any ongoing operations
        self.loading_cancelled = True
        
        # Save current window size
        width = self.winfo_width()
        height = self.winfo_height()
        
        if width > 100 and height > 100:  # Avoid saving minimized size
            self.config.set_setting('ui', 'window_width', width)
            self.config.set_setting('ui', 'window_height', height)
            
        # Destroy the window
        self.destroy()
    
    def _update_progress(self, step_text="", reset=False):
        """
        Update the progress bar.
        
        Args:
            step_text (str): Text to display for current step
            reset (bool): Whether to reset the progress counter
        """
        if reset:
            self.api_calls_done = 0
            self.api_calls_total = 0
            self.progress_var.set(0)
        
        if self.api_calls_total > 0:
            progress_pct = int((self.api_calls_done / self.api_calls_total) * 100)
            self.progress_var.set(progress_pct)
            progress_text = f"{step_text} [{progress_pct}%]"
        else:
            self.progress_var.set(0)
            progress_text = step_text
            
        self.progress_label.config(text=progress_text)
        self.update_idletasks()
    
    def _register_api_call(self):
        """Register that an API call has been completed."""
        self.api_calls_done += 1
        self._update_progress()
        
    def _create_client(self):
        """Create a TestRail API client from the current settings."""
        settings = self.settings_frame.get_settings()
        
        # Save credentials to config
        self.config.set_setting('testrail', 'url', settings['url'])
        self.config.set_setting('testrail', 'username', settings['username'])
        self.config.set_setting('testrail', 'api_key', settings['api_key'])
        
        self.client = TestRailClient(settings['url'], settings['username'], settings['api_key'])
    
    def _load_projects(self):
        """Load projects from TestRail."""
        try:
            self._create_client()
            
            # Cancel any ongoing loading operations
            self.loading_cancelled = True
            
            # Wait a moment to ensure any running thread notices the cancellation flag
            self.after(100, self._start_load_projects)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create client: {str(e)}")
            self._update_progress("", reset=True)
            self.status_var.set("")
    
    def _start_load_projects(self):
        """Start loading projects after ensuring previous operations are cancelled."""
        # Reset cancellation flag
        self.loading_cancelled = False
        
        # Reset and start progress tracking
        self._update_progress("Loading projects...", reset=True)
        
        # We'll have at least 1 API call (for projects)
        self.api_calls_total = 1
        
        # Load projects in a separate thread
        self.active_thread = threading.Thread(target=self._load_projects_thread)
        self.active_thread.start()
    
    def _load_projects_thread(self):
        """Load projects in a background thread."""
        try:
            # Check if operation has been cancelled
            if self.loading_cancelled:
                return
                
            # Get projects from API
            project_data = self.client.get_projects()
            
            # Check if operation has been cancelled before processing
            if self.loading_cancelled:
                return
                
            self.projects = [Project(p) for p in project_data]
            self._register_api_call()
            
            # Update UI in the main thread
            if not self.loading_cancelled:
                self.after(0, self._update_projects_ui)
        except Exception as e:
            if not self.loading_cancelled:
                self.after(0, lambda: self._show_error(f"Failed to load projects: {str(e)}"))
    
    def _update_projects_ui(self):
        """Update the projects dropdown after loading projects."""
        # Sort projects alphabetically by name
        self.projects.sort(key=lambda p: p.name.lower())
        
        # Update projects dropdown
        project_names = [p.name for p in self.projects]
        self.project_combo['values'] = project_names
        
        # Check if we should select a previously saved project
        last_project = self.config.get_setting('ui', 'last_project')
        
        if project_names:
            if last_project and last_project in project_names:
                index = project_names.index(last_project)
                self.project_combo.current(index)
            else:
                self.project_combo.current(0)
                
            self.status_var.set(f"Loaded {len(project_names)} projects")
            self._update_progress("")
            
            # Trigger project selection
            self._on_project_selected(None)
        else:
            self.status_var.set("No projects found")
            self._update_progress("")
    
    def _on_project_selected(self, event):
        """Handle project selection changes."""
        selected_index = self.project_combo.current()
        if selected_index == -1 or not self.projects:
            return
            
        # Cancel any ongoing loading operations
        self.loading_cancelled = True
        
        # Wait a moment to ensure any running thread notices the cancellation flag
        self.after(100, lambda: self._start_load_project(selected_index))
    
    def _start_load_project(self, selected_index):
        """Start loading the selected project after cancellation of previous operations."""
        # Reset cancellation flag
        self.loading_cancelled = False
        
        self.current_project = self.projects[selected_index]
        
        # Save current project to config
        self.config.set_setting('ui', 'last_project', self.current_project.name)
        
        # Reset and start progress tracking
        self._update_progress("Loading suites...", reset=True)
        
        # Calculate API calls: 1 for suites + 1 for each suite's sections
        self.api_calls_total = 1  # Start with 1 for the suites call
        
        # Clear treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Load suites in a separate thread
        self.active_thread = threading.Thread(target=self._load_suites_thread)
        self.active_thread.start()
    
    def _load_suites_thread(self):
        """Load suites for the selected project in a background thread."""
        try:
            # Check if operation has been cancelled
            if self.loading_cancelled:
                return
                
            # Get suites from API
            suites_data = self.client.get_suites(self.current_project.id)
            
            # Check if operation has been cancelled
            if self.loading_cancelled:
                return
                
            suites = [Suite(s) for s in suites_data]
            
            # Sort suites alphabetically by name
            suites.sort(key=lambda s: s.name.lower())
            
            self.current_project.suites = suites
            self._register_api_call()
            
            # Now we know how many suites we have, update total API calls
            self.api_calls_total += len(suites)  # Add sections calls (1 per suite)
            self._update_progress("Loading sections...")
            
            # Load sections for each suite
            for suite in suites:
                # Check if operation has been cancelled
                if self.loading_cancelled:
                    return
                    
                sections_data = self.client.get_sections(self.current_project.id, suite.id)
                
                # Check if operation has been cancelled
                if self.loading_cancelled:
                    return
                    
                sections = [Section(s) for s in sections_data]
                
                # Sort sections alphabetically by name
                sections.sort(key=lambda s: s.name.lower())
                
                suite.sections = sections
                self._register_api_call()
            
            # Update UI in the main thread
            if not self.loading_cancelled:
                self.after(0, self._update_suites_ui)
        except Exception as e:
            if not self.loading_cancelled:
                self.after(0, lambda: self._show_error(f"Failed to load suites: {str(e)}"))
    
    def _update_suites_ui(self):
        """Update the treeview after loading suites and sections."""
        # Add suites and sections to the treeview
        for suite in self.current_project.suites:
            # Add suite
            suite_id = self.tree.insert("", "end", text="", values=(suite.name,), image=self.tree.image_unchecked)
            
            # Add sections if any
            if suite.has_sections():
                for section in suite.sections:
                    # Add section
                    section_id = self.tree.insert(suite_id, "end", text="", values=(section.name,), image=self.tree.image_unchecked)
            
        self.status_var.set(f"Loaded {len(self.current_project.suites)} suites")
        self._update_progress("")
    
    def _export_cases(self, format='json'):
        """
        Export selected test cases.
        
        Args:
            format (str): Export format ('json' or 'csv')
        """
        if not self.current_project or not self.client:
            messagebox.showwarning("Warning", "Please select a project first")
            return
            
        # Get checked items
        checked_items = self.tree.get_checked_items()
        if not checked_items:
            messagebox.showwarning("Warning", "Please select at least one suite or section to export")
            return
        
        # Cancel any ongoing operations
        self.loading_cancelled = True
        
        # Wait a moment for cancellation to take effect
        self.after(100, lambda: self._start_export(checked_items, format))
        
    def _start_export(self, checked_items, format):
        """Start the export process after cancellation of any previous operations."""
        # Reset cancellation flag
        self.loading_cancelled = False
        
        # Calculate needed API calls for progress tracking
        # One call per suite and one per section that has been selected
        suite_count = sum(1 for item in checked_items if not self.tree.parent(item))
        section_count = sum(1 for item in checked_items if self.tree.parent(item))
        
        # Reset and start progress tracking
        self._update_progress("Preparing export...", reset=True)
        self.api_calls_total = suite_count + section_count
        
        # Export in a separate thread
        self.active_thread = threading.Thread(target=lambda: self._export_cases_thread(checked_items, format))
        self.active_thread.start()
    
    def _export_cases_thread(self, checked_items, format='json'):
        """
        Export test cases in a background thread.
        
        Args:
            checked_items: List of checked tree items
            format (str): Export format ('json' or 'csv')
        """
        try:
            cases = []
            
            # Check if operation has been cancelled
            if self.loading_cancelled:
                return
                
            # Get cases for each checked suite and section
            for item_id in checked_items:
                # Check if operation has been cancelled
                if self.loading_cancelled:
                    return
                    
                item_values = self.tree.item(item_id, "values")
                parent_id = self.tree.parent(item_id)
                
                if not parent_id:
                    # This is a suite
                    suite_name = item_values[0]
                    suite = next((s for s in self.current_project.suites if s.name == suite_name), None)
                    if suite:
                        # Update progress
                        self._update_progress(f"Exporting suite: {suite_name}")
                        
                        # Check if operation has been cancelled
                        if self.loading_cancelled:
                            return
                            
                        # Get cases for the entire suite
                        cases_data = self.client.get_cases(self.current_project.id, suite.id)
                        
                        # Check if operation has been cancelled
                        if self.loading_cancelled:
                            return
                            
                        cases.extend([Case(c) for c in cases_data])
                        self._register_api_call()
                else:
                    # This is a section
                    section_name = item_values[0]
                    suite_name = self.tree.item(parent_id, "values")[0]
                    suite = next((s for s in self.current_project.suites if s.name == suite_name), None)
                    if suite:
                        section = next((s for s in suite.sections if s.name == section_name), None)
                        if section:
                            # Update progress
                            self._update_progress(f"Exporting section: {section_name}")
                            
                            # Check if operation has been cancelled
                            if self.loading_cancelled:
                                return
                                
                            # Get cases for the section
                            cases_data = self.client.get_cases(self.current_project.id, suite.id, section.id)
                            
                            # Check if operation has been cancelled
                            if self.loading_cancelled:
                                return
                                
                            cases.extend([Case(c) for c in cases_data])
                            self._register_api_call()
            
            # Check if operation has been cancelled
            if self.loading_cancelled:
                return
                
            # Prepare export data
            export_data = {
                'project': {
                    'id': self.current_project.id,
                    'name': self.current_project.name
                },
                'cases': [case.to_dict() for case in cases]
            }
            
            # Update UI in the main thread
            if not self.loading_cancelled:
                self.after(0, lambda: self._save_export_file(export_data, format))
        except Exception as e:
            if not self.loading_cancelled:
                self.after(0, lambda: self._show_error(f"Failed to export test cases: {str(e)}"))
    
    def _save_export_file(self, export_data, format='json'):
        """
        Prompt user to save export file.
        
        Args:
            export_data (dict): Data to export
            format (str): Export format ('json' or 'csv')
        """
        # Get export directory from settings
        settings = self.settings_frame.get_settings()
        export_dir = settings['export_dir']
        
        # Save export directory to config
        self.config.set_setting('export', 'directory', export_dir)
        
        # Set file extension and types based on format
        if format == 'csv':
            extension = ".csv"
            file_types = [("CSV Files", "*.csv"), ("All Files", "*.*")]
            default_filename = f"{self.current_project.name}_export.csv"
        else:  # Default to json
            extension = ".json"
            file_types = [("JSON Files", "*.json"), ("All Files", "*.*")]
            default_filename = f"{self.current_project.name}_export.json"
        
        # Prompt for save location
        filepath = filedialog.asksaveasfilename(
            initialdir=export_dir,
            initialfile=default_filename,
            defaultextension=extension,
            filetypes=file_types
        )
        
        if not filepath:
            self.status_var.set("Export cancelled")
            self._update_progress("")
            return
            
        try:
            # Update progress
            self._update_progress("Saving export file...")
            
            # Save the file
            success = False
            if format == 'csv':
                success = Exporter.export_to_csv(export_data, filepath)
            else:  # Default to json
                success = Exporter.export_to_json(export_data, filepath)
                
            if success:
                self.status_var.set(f"Exported {len(export_data['cases'])} test cases to {os.path.basename(filepath)}")
                messagebox.showinfo("Success", f"Successfully exported {len(export_data['cases'])} test cases to {format.upper()} format")
            else:
                self._show_error(f"Failed to export to {format.upper()}")
                
            self._update_progress("")
        except Exception as e:
            self._show_error(f"Failed to save export file: {str(e)}")
    
    def _show_error(self, message):
        """Show an error message and update the status."""
        messagebox.showerror("Error", message)
        self.status_var.set("Error occurred")
        self._update_progress("")