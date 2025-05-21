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
        
        # Use our custom expand all method with progress tracking
        ttk.Button(button_frame, text="Expand All", command=self._expand_all_with_progress).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Collapse All", command=self.tree.collapse_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Check All", command=self.tree.check_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Uncheck All", command=self.tree.uncheck_all).pack(side=tk.LEFT, padx=5)
        
        # Bind tree events for progress tracking
        self.tree.bind("<<ExpandAllStarted>>", self._on_expand_all_started)
        self.tree.bind("<<TreeItemExpanded>>", self._on_tree_item_expanded_progress)
        self.tree.bind("<<ExpandAllCompleted>>", self._on_expand_all_completed)
        
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
        
        # Create a cache for storing API data
        self.cache = {
            'projects': None,
            'suites': {},  # Project ID -> Suites
            'sections': {},  # Suite ID -> Sections
            'cases': {},  # Suite ID+Section ID -> Cases
            'loading_state': {}  # Track loading completion state for projects
        }
        
        # Create a reference to the load projects button
        self.load_projects_button = None
        
        # Store project frame reference for updating UI
        for child in project_frame.winfo_children():
            if isinstance(child, ttk.Button) and child.cget('text') == "Load Projects":
                self.load_projects_button = child
                break
        
        # Auto-load projects if settings are populated
        self.after(500, self._auto_load_projects)
    
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
        
    def _auto_load_projects(self):
        """Automatically load projects if settings are populated."""
        try:
            settings = self.settings_frame.get_settings()
            
            # Check if all required settings are present
            if settings['url'] and settings['username'] and settings['api_key'] and settings['export_dir']:
                # Auto-load projects
                self._load_projects()
        except Exception:
            # Just fail silently if auto-load fails
            pass
            
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
            
            # Check if this is a refresh (button text is "Refresh Projects")
            is_refresh = self.load_projects_button and self.load_projects_button.cget('text') == "Refresh Projects"
            
            # If refreshing, clear the cache
            if is_refresh:
                self.cache = {
                    'projects': None,
                    'suites': {},
                    'sections': {},
                    'cases': {},
                    'loading_state': {}
                }
            
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
        # Check if there's still an active thread running
        if (hasattr(self, 'active_thread') and self.active_thread and 
            self.active_thread.is_alive()):
            # Thread is still running, wait a bit more
            self.after(50, lambda: self._start_load_projects())
            return
            
        # Reset cancellation flag
        self.loading_cancelled = False
        
        # Reset and start progress tracking
        self._update_progress("Loading projects...", reset=True)
        
        # Check if we have cached projects
        if self.cache['projects'] is not None:
            # Use cached data
            self.projects = self.cache['projects']
            self._update_progress("Loading from cache...", reset=True)
            self.after(0, self._update_projects_ui)
            return
        
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
            
            # Cache the projects
            self.cache['projects'] = self.projects
            
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
            
            # Change the load button text to "Refresh Projects"
            if self.load_projects_button:
                self.load_projects_button.config(text="Refresh Projects")
            
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
        # Check if there's still an active thread running
        if (hasattr(self, 'active_thread') and self.active_thread and 
            self.active_thread.is_alive()):
            # Thread is still running, wait a bit more
            self.after(50, lambda: self._start_load_project(selected_index))
            return
            
        # Reset cancellation flag
        self.loading_cancelled = False
        
        self.current_project = self.projects[selected_index]
        
        # Save current project to config
        self.config.set_setting('ui', 'last_project', self.current_project.name)
        
        # Clear treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Check if we have fully loaded data for this project
        project_loading_state = self.cache['loading_state'].get(self.current_project.id, 'not_started')
        
        if (self.current_project.id in self.cache['suites'] and 
            project_loading_state == 'completed'):
            # Use cached data only if loading was completed
            self.current_project.suites = self.cache['suites'][self.current_project.id]
            self._update_progress("Loading from cache...", reset=True)
            self.after(0, self._update_suites_ui)
            return
        
        # Mark project as loading
        self.cache['loading_state'][self.current_project.id] = 'loading'
        
        # Reset and start progress tracking
        self._update_progress("Loading suites...", reset=True)
        
        # Calculate API calls: 1 for suites + 1 for each suite's sections
        self.api_calls_total = 1  # Start with 1 for the suites call
        
        # Load suites in a separate thread
        self.active_thread = threading.Thread(target=self._load_suites_thread)
        self.active_thread.start()
    
    def _load_suites_thread(self):
        """Load suites for the selected project in a background thread."""
        try:
            # Check if operation has been cancelled
            if self.loading_cancelled:
                # Mark as incomplete if cancelled
                if hasattr(self, 'current_project') and self.current_project:
                    self.cache['loading_state'][self.current_project.id] = 'incomplete'
                return
                
            # Get suites from API
            suites_data = self.client.get_suites(self.current_project.id)
            
            # Check if operation has been cancelled
            if self.loading_cancelled:
                # Mark as incomplete if cancelled
                if hasattr(self, 'current_project') and self.current_project:
                    self.cache['loading_state'][self.current_project.id] = 'incomplete'
                return
                
            suites = [Suite(s) for s in suites_data]
            
            # Sort suites alphabetically by name
            suites.sort(key=lambda s: s.name.lower())
            
            self.current_project.suites = suites
            
            # Cache the suites
            self.cache['suites'][self.current_project.id] = suites
            
            self._register_api_call()
            
            # Now we know how many suites we have, update total API calls
            # We'll only need 1 API call per suite to get sections
            self.api_calls_total += len(suites)
            self._update_progress("Loading sections...")
            
            # Load sections for each suite
            for suite in suites:
                # Check if operation has been cancelled
                if self.loading_cancelled:
                    # Mark as incomplete if cancelled
                    if hasattr(self, 'current_project') and self.current_project:
                        self.cache['loading_state'][self.current_project.id] = 'incomplete'
                    return
                
                # Check if we have cached sections for this suite
                if suite.id in self.cache['sections']:
                    suite.sections = self.cache['sections'][suite.id]
                    self._register_api_call()
                else:
                    sections_data = self.client.get_sections(self.current_project.id, suite.id)
                    
                    # Check if operation has been cancelled
                    if self.loading_cancelled:
                        # Mark as incomplete if cancelled
                        if hasattr(self, 'current_project') and self.current_project:
                            self.cache['loading_state'][self.current_project.id] = 'incomplete'
                        return
                        
                    sections = [Section(s) for s in sections_data]
                    
                    # Sort sections alphabetically by name
                    sections.sort(key=lambda s: s.name.lower())
                    
                    suite.sections = sections
                    
                    # Cache the sections
                    self.cache['sections'][suite.id] = sections
                    
                    self._register_api_call()
                
                # We'll no longer preload case counts during initial load to save time
                # The caching will happen on-demand when exporting
            
            # Update UI in the main thread
            if not self.loading_cancelled:
                self.after(0, self._update_suites_ui)
        except Exception as e:
            if not self.loading_cancelled:
                self.after(0, lambda: self._show_error(f"Failed to load suites: {str(e)}"))
    
    def _get_case_count_for_suite(self, suite_id, load_data=False):
        """
        Get the number of test cases in a suite.
        
        Args:
            suite_id: The ID of the suite
            load_data: Whether to load and cache the actual case data
            
        Returns:
            int: Number of test cases in the suite
        """
        # Check if we have cases cached for this suite
        cache_key = f"{self.current_project.id}_{suite_id}_None"
        if cache_key in self.cache['cases']:
            return len(self.cache['cases'][cache_key])
            
        if load_data:
            # Load actual cases data
            try:
                cases_data = self.client.get_cases(self.current_project.id, suite_id)
                cases = [Case(c) for c in cases_data]
                
                # Cache the cases
                self.cache['cases'][cache_key] = cases
                
                return len(cases)
            except Exception:
                # If we fail to get the count, just return 0
                return 0
        else:
            # We're not loading data, just return 0 for now
            return 0
            
    def _get_case_count_for_section(self, suite_id, section_id, load_data=False):
        """
        Get the number of test cases in a section.
        
        Args:
            suite_id: The ID of the suite
            section_id: The ID of the section
            load_data: Whether to load and cache the actual case data
            
        Returns:
            int: Number of test cases in the section
        """
        # Check if we have cases cached for this section
        cache_key = f"{self.current_project.id}_{suite_id}_{section_id}"
        if cache_key in self.cache['cases']:
            return len(self.cache['cases'][cache_key])
            
        if load_data:
            # Load actual cases data
            try:
                cases_data = self.client.get_cases(self.current_project.id, suite_id, section_id)
                cases = [Case(c) for c in cases_data]
                
                # Cache the cases
                self.cache['cases'][cache_key] = cases
                
                return len(cases)
            except Exception:
                # If we fail to get the count, just return 0
                return 0
        else:
            # We're not loading data, just return 0 for now
            return 0
    
    def _expand_all_with_progress(self):
        """Perform expand all operation with progress tracking."""
        # Cancel any ongoing operations
        self.loading_cancelled = True
        
        # Wait a moment to ensure any running thread notices the cancellation flag
        self.after(100, self._start_expand_all)
        
    def _start_expand_all(self):
        """Start the expand all operation in a separate thread."""
        # Reset cancellation flag
        self.loading_cancelled = False
        
        # Start the expand all operation
        self.tree.expand_all()
        
    def _on_expand_all_started(self, event):
        """Handle the start of an expand all operation."""
        # Count total items to expand
        total_items = self.tree.count_all_items()
        
        # Reset progress tracking
        self.api_calls_total = total_items
        self.api_calls_done = 0
        self._update_progress("Expanding all items...", reset=True)
        
    def _on_tree_item_expanded_progress(self, event):
        """Handle progress updates during expand all."""
        self.api_calls_done += 1
        self._update_progress("Expanding items...")
        
    def _on_expand_all_completed(self, event):
        """Handle the completion of an expand all operation."""
        self._update_progress("")
        self.status_var.set("Expanded all items")
    
    def _preload_section_case_counts(self, suite):
        """
        Preload case counts for all sections in a suite.
        
        Args:
            suite: The suite to load section case counts for
        """
        if not suite.has_sections():
            return
            
        # Load case counts for all sections in parallel
        for section in suite.sections:
            # Check if we already have cached case count
            cache_key = f"{self.current_project.id}_{suite.id}_{section.id}"
            if cache_key not in self.cache['cases']:
                try:
                    # Get cases for this section
                    cases_data = self.client.get_cases(self.current_project.id, suite.id, section.id)
                    cases = [Case(c) for c in cases_data]
                    
                    # Cache the cases
                    self.cache['cases'][cache_key] = cases
                except Exception:
                    # If we fail to get the count, just create an empty cache
                    self.cache['cases'][cache_key] = []
    
    def _update_suites_ui(self):
        """Update the treeview after loading suites and sections."""
        # Add suites and sections to the treeview
        for suite in self.current_project.suites:
            # Add suite without case count
            suite_id = self.tree.insert("", "end", text="", values=(suite.name,), image=self.tree.image_unchecked)
            
            # Add sections if any
            if suite.has_sections():
                # Add all sections without case counts or filtering
                for section in suite.sections:
                    section_id = self.tree.insert(suite_id, "end", text="", values=(section.name,), image=self.tree.image_unchecked)
            
        # Add event handler for tree item open (expand) event
        self.tree.bind("<<TreeviewOpen>>", self._on_tree_item_expanded)
            
        # Mark project loading as completed
        if hasattr(self, 'current_project') and self.current_project:
            self.cache['loading_state'][self.current_project.id] = 'completed'
        
        self.status_var.set(f"Loaded {len(self.current_project.suites)} suites")
        self._update_progress("")
        
    def _on_tree_item_expanded(self, event):
        """Handle when a tree item is expanded."""
        # We're not updating the UI with case counts anymore,
        # but we'll keep the event handler for future extensibility
        pass
    
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
        
        # Validate that all checked items still exist in the tree
        # This prevents TclError when switching projects
        valid_checked_items = []
        for item in checked_items:
            try:
                # Try to access the item to see if it still exists
                self.tree.item(item, "values")
                valid_checked_items.append(item)
            except Exception:
                # Item no longer exists, skip it
                continue
            
        # If no valid items remain, show a warning and return
        if not valid_checked_items:
            messagebox.showwarning("Warning", "No valid items selected for export. Please select items again.")
            self._update_progress("", reset=True)
            return
        
        # Calculate needed API calls for progress tracking
        # One call per suite and one per section that has been selected
        try:
            suite_count = sum(1 for item in valid_checked_items if not self.tree.parent(item))
            section_count = sum(1 for item in valid_checked_items if self.tree.parent(item))
        except Exception:
            # If we can't determine parents, show warning and return
            messagebox.showwarning("Warning", "Unable to process selected items. Please select items again.")
            self._update_progress("", reset=True)
            return
        
        # Reset and start progress tracking
        self._update_progress("Preparing export...", reset=True)
        self.api_calls_total = suite_count + section_count
        
        # Export in a separate thread
        self.active_thread = threading.Thread(target=lambda: self._export_cases_thread(valid_checked_items, format))
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
            processed_cases = set()  # Track processed case IDs to avoid duplicates
            
            # Check if operation has been cancelled
            if self.loading_cancelled:
                return
            
            # Separate suites and sections to avoid duplicates
            # If a suite is checked, don't process its individual sections
            suites_to_process = []
            sections_to_process = []
            
            for item_id in checked_items:
                parent_id = self.tree.parent(item_id)
                if not parent_id:
                    # This is a suite
                    suites_to_process.append(item_id)
                else:
                    # This is a section - only add if its parent suite is not also selected
                    if parent_id not in checked_items:
                        sections_to_process.append(item_id)
                
            # Process suites first
            for item_id in suites_to_process:
                # Check if operation has been cancelled
                if self.loading_cancelled:
                    return
                    
                item_values = self.tree.item(item_id, "values")
                suite_display_name = item_values[0]
                # Extract name without count
                if " (" in suite_display_name:
                    suite_name = suite_display_name.split(" (")[0]
                else:
                    suite_name = suite_display_name
                    
                suite = next((s for s in self.current_project.suites if s.name == suite_name), None)
                if suite:
                    # Update progress
                    self._update_progress(f"Exporting suite: {suite_name}")
                    
                    # Check if operation has been cancelled
                    if self.loading_cancelled:
                        return
                        
                    # Check if we have cached cases for this suite
                    cache_key = f"{self.current_project.id}_{suite.id}_None"
                    if cache_key in self.cache['cases']:
                        # Use cached data
                        suite_cases = self.cache['cases'][cache_key]
                    else:
                        # Get cases for the entire suite from API
                        cases_data = self.client.get_cases(self.current_project.id, suite.id)
                        
                        # Check if operation has been cancelled
                        if self.loading_cancelled:
                            return
                        
                        suite_cases = [Case(c) for c in cases_data]
                        
                        # Cache the cases
                        self.cache['cases'][cache_key] = suite_cases
                    
                    # Add cases, avoiding duplicates
                    for case in suite_cases:
                        if case.id not in processed_cases:
                            cases.append(case)
                            processed_cases.add(case.id)
                            
                    self._register_api_call()
            
            # Process individual sections (only if their parent suite wasn't processed)
            for item_id in sections_to_process:
                # Check if operation has been cancelled
                if self.loading_cancelled:
                    return
                    
                item_values = self.tree.item(item_id, "values")
                parent_id = self.tree.parent(item_id)
                
                section_display_name = item_values[0]
                # Extract section name without count
                if " (" in section_display_name:
                    section_name = section_display_name.split(" (")[0]
                else:
                    section_name = section_display_name
                    
                suite_display_name = self.tree.item(parent_id, "values")[0]
                # Extract suite name without count
                if " (" in suite_display_name:
                    suite_name = suite_display_name.split(" (")[0]
                else:
                    suite_name = suite_display_name
                    
                suite = next((s for s in self.current_project.suites if s.name == suite_name), None)
                if suite:
                    section = next((s for s in suite.sections if s.name == section_name), None)
                    if section:
                        # Update progress
                        self._update_progress(f"Exporting section: {section_name}")
                        
                        # Check if operation has been cancelled
                        if self.loading_cancelled:
                            return
                            
                        # Check if we have cached cases for this section
                        cache_key = f"{self.current_project.id}_{suite.id}_{section.id}"
                        if cache_key in self.cache['cases']:
                            # Use cached data
                            section_cases = self.cache['cases'][cache_key]
                        else:
                            # Get cases for the section from API
                            cases_data = self.client.get_cases(self.current_project.id, suite.id, section.id)
                            
                            # Check if operation has been cancelled
                            if self.loading_cancelled:
                                return
                            
                            section_cases = [Case(c) for c in cases_data]
                            
                            # Cache the cases
                            self.cache['cases'][cache_key] = section_cases
                        
                        # Add cases, avoiding duplicates
                        for case in section_cases:
                            if case.id not in processed_cases:
                                cases.append(case)
                                processed_cases.add(case.id)
                                
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