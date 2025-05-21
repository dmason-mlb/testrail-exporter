import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import json
import os
from PIL import Image, ImageTk

from gui.settings import SettingsFrame
from gui.tree_view import CheckableTreeview
from api.testrail_client import TestRailClient
from models.project import Project
from models.suite import Suite
from models.section import Section
from models.case import Case


class Application(tk.Tk):
    """Main application window."""

    def __init__(self):
        """Initialize the application."""
        super().__init__()
        
        self.title("TestRail Exporter")
        self.geometry("1000x700")
        self.minsize(800, 600)
        
        # Load icons
        self._load_icons()
        
        # Create main frame
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Settings frame
        self.settings_frame = SettingsFrame(main_frame)
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
        self.tree.configure_icons(self.checked_icon, self.partial_icon, self.unchecked_icon)
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
        
        # Export button
        ttk.Button(button_frame, text="Export", command=self._export_cases).pack(side=tk.RIGHT, padx=5)
        
        # Progress bar and status
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=10)
        
        self.status_var = tk.StringVar()
        ttk.Label(status_frame, textvariable=self.status_var).pack(side=tk.LEFT)
        
        self.progress = ttk.Progressbar(status_frame, orient=tk.HORIZONTAL, length=100, mode='indeterminate')
        self.progress.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
        
        # Initialize instance variables
        self.client = None
        self.projects = []
        self.current_project = None
        
    def _load_icons(self):
        """Load checkbox icons."""
        # Create simple icons since we don't have image files
        size = 20
        
        # Checked icon (green checkmark)
        checked = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        for i in range(size):
            for j in range(size):
                # Draw a checkmark
                if (i == j and i > size/2) or (i + j == size - 1 and i < size/2):
                    checked.putpixel((i, j), (0, 150, 0, 255))
        self.checked_icon = ImageTk.PhotoImage(checked)
        
        # Partial icon (blue square)
        partial = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        for i in range(size//4, 3*size//4):
            for j in range(size//4, 3*size//4):
                partial.putpixel((i, j), (0, 0, 150, 255))
        self.partial_icon = ImageTk.PhotoImage(partial)
        
        # Unchecked icon (empty square)
        unchecked = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        for i in range(size):
            for j in range(size):
                # Draw square border
                if i == 0 or i == size-1 or j == 0 or j == size-1:
                    unchecked.putpixel((i, j), (100, 100, 100, 255))
        self.unchecked_icon = ImageTk.PhotoImage(unchecked)
        
    def _create_client(self):
        """Create a TestRail API client from the current settings."""
        settings = self.settings_frame.get_settings()
        self.client = TestRailClient(settings['url'], settings['username'], settings['api_key'])
    
    def _load_projects(self):
        """Load projects from TestRail."""
        try:
            self._create_client()
            
            # Show progress
            self.progress.start()
            self.status_var.set("Loading projects...")
            
            # Load projects in a separate thread
            threading.Thread(target=self._load_projects_thread).start()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create client: {str(e)}")
            self.progress.stop()
            self.status_var.set("")
    
    def _load_projects_thread(self):
        """Load projects in a background thread."""
        try:
            # Get projects from API
            project_data = self.client.get_projects()
            self.projects = [Project(p) for p in project_data]
            
            # Update UI in the main thread
            self.after(0, self._update_projects_ui)
        except Exception as e:
            self.after(0, lambda: self._show_error(f"Failed to load projects: {str(e)}"))
    
    def _update_projects_ui(self):
        """Update the projects dropdown after loading projects."""
        # Stop progress
        self.progress.stop()
        
        # Update projects dropdown
        project_names = [p.name for p in self.projects]
        self.project_combo['values'] = project_names
        
        if project_names:
            self.project_combo.current(0)
            self.status_var.set(f"Loaded {len(project_names)} projects")
            # Trigger project selection
            self._on_project_selected(None)
        else:
            self.status_var.set("No projects found")
    
    def _on_project_selected(self, event):
        """Handle project selection changes."""
        selected_index = self.project_combo.current()
        if selected_index == -1 or not self.projects:
            return
            
        self.current_project = self.projects[selected_index]
        
        # Show progress
        self.progress.start()
        self.status_var.set(f"Loading suites for project {self.current_project.name}...")
        
        # Clear treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Load suites in a separate thread
        threading.Thread(target=self._load_suites_thread).start()
    
    def _load_suites_thread(self):
        """Load suites for the selected project in a background thread."""
        try:
            # Get suites from API
            suites_data = self.client.get_suites(self.current_project.id)
            suites = [Suite(s) for s in suites_data]
            self.current_project.suites = suites
            
            # Load sections for each suite
            for suite in suites:
                sections_data = self.client.get_sections(self.current_project.id, suite.id)
                sections = [Section(s) for s in sections_data]
                suite.sections = sections
            
            # Update UI in the main thread
            self.after(0, self._update_suites_ui)
        except Exception as e:
            self.after(0, lambda: self._show_error(f"Failed to load suites: {str(e)}"))
    
    def _update_suites_ui(self):
        """Update the treeview after loading suites and sections."""
        # Stop progress
        self.progress.stop()
        
        # Add suites and sections to the treeview
        for suite in self.current_project.suites:
            suite_id = self.tree.insert("", "end", text="", values=(suite.name,), image="unchecked")
            
            # Add sections if any
            if suite.has_sections():
                for section in suite.sections:
                    section_id = self.tree.insert(suite_id, "end", text="", values=(section.name,), image="unchecked")
            
        self.status_var.set(f"Loaded {len(self.current_project.suites)} suites")
    
    def _export_cases(self):
        """Export selected test cases."""
        if not self.current_project or not self.client:
            messagebox.showwarning("Warning", "Please select a project first")
            return
            
        # Get checked items
        checked_items = self.tree.get_checked_items()
        if not checked_items:
            messagebox.showwarning("Warning", "Please select at least one suite or section to export")
            return
        
        # Show progress
        self.progress.start()
        self.status_var.set("Exporting test cases...")
        
        # Export in a separate thread
        threading.Thread(target=lambda: self._export_cases_thread(checked_items)).start()
    
    def _export_cases_thread(self, checked_items):
        """Export test cases in a background thread."""
        try:
            cases = []
            
            # Get cases for each checked suite and section
            for item_id in checked_items:
                item_values = self.tree.item(item_id, "values")
                parent_id = self.tree.parent(item_id)
                
                if not parent_id:
                    # This is a suite
                    suite_name = item_values[0]
                    suite = next((s for s in self.current_project.suites if s.name == suite_name), None)
                    if suite:
                        # Get cases for the entire suite
                        cases_data = self.client.get_cases(self.current_project.id, suite.id)
                        cases.extend([Case(c) for c in cases_data])
                else:
                    # This is a section
                    section_name = item_values[0]
                    suite_name = self.tree.item(parent_id, "values")[0]
                    suite = next((s for s in self.current_project.suites if s.name == suite_name), None)
                    if suite:
                        section = next((s for s in suite.sections if s.name == section_name), None)
                        if section:
                            # Get cases for the section
                            cases_data = self.client.get_cases(self.current_project.id, suite.id, section.id)
                            cases.extend([Case(c) for c in cases_data])
            
            # Prepare export data
            export_data = {
                'project': {
                    'id': self.current_project.id,
                    'name': self.current_project.name
                },
                'cases': [case.to_dict() for case in cases]
            }
            
            # Update UI in the main thread
            self.after(0, lambda: self._save_export_file(export_data))
        except Exception as e:
            self.after(0, lambda: self._show_error(f"Failed to export test cases: {str(e)}"))
    
    def _save_export_file(self, export_data):
        """Prompt user to save export file."""
        # Stop progress
        self.progress.stop()
        
        # Get export directory from settings
        settings = self.settings_frame.get_settings()
        export_dir = settings['export_dir']
        
        # Default filename
        default_filename = f"{self.current_project.name}_export.json"
        
        # Prompt for save location
        filepath = filedialog.asksaveasfilename(
            initialdir=export_dir,
            initialfile=default_filename,
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        
        if not filepath:
            self.status_var.set("Export cancelled")
            return
            
        try:
            # Save the file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2)
                
            self.status_var.set(f"Exported {len(export_data['cases'])} test cases to {os.path.basename(filepath)}")
            messagebox.showinfo("Success", f"Successfully exported {len(export_data['cases'])} test cases")
        except Exception as e:
            self._show_error(f"Failed to save export file: {str(e)}")
    
    def _show_error(self, message):
        """Show an error message and update the status."""
        messagebox.showerror("Error", message)
        self.progress.stop()
        self.status_var.set("Error occurred")