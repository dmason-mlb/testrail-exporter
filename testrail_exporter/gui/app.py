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
        self.tree = CheckableTreeview(tree_frame, columns=("name", "suite_id", "section_id", "section_parent_id", "is_placeholder"), show="tree")
        self.tree.column("#0", width=50, minwidth=50, stretch=False)
        self.tree.column("name", width=200, minwidth=200)
        self.tree.column("suite_id", width=0, minwidth=0, stretch=False)  # Hidden column for metadata
        self.tree.column("section_id", width=0, minwidth=0, stretch=False)  # Hidden column for metadata
        self.tree.column("section_parent_id", width=0, minwidth=0, stretch=False)  # Hidden column for metadata
        self.tree.column("is_placeholder", width=0, minwidth=0, stretch=False)  # Hidden column for placeholder detection
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
        ttk.Button(export_frame, text="Export XML", command=lambda: self._export_cases(format='xml')).pack(side=tk.RIGHT, padx=2)
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
            'loading_state': {},  # Track loading completion state for projects
            'sections_loaded': set(),  # Track which suites have sections loaded
            'priorities': None,  # Cache priorities (not project-specific)
            'case_types': None  # Cache case types (not project-specific)
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
                    'loading_state': {},
                    'sections_loaded': set(),
                    'priorities': None,
                    'case_types': None
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
        
        # We'll have 3 API calls (for projects, priorities, and case types)
        self.api_calls_total = 3
        
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
            
            # Load priorities if not cached yet
            if self.cache['priorities'] is None:
                # Check if operation has been cancelled before priorities call
                if self.loading_cancelled:
                    return
                    
                priorities_data = self.client.get_priorities()
                
                # Check if operation has been cancelled before processing
                if self.loading_cancelled:
                    return
                    
                # Cache the priorities
                self.cache['priorities'] = priorities_data
                
                self._register_api_call()
            else:
                # Priorities already cached, skip API call
                self._register_api_call()
            
            # Load case types if not cached yet
            if self.cache['case_types'] is None:
                # Check if operation has been cancelled before case types call
                if self.loading_cancelled:
                    return
                    
                case_types_data = self.client.get_case_types()
                
                # Check if operation has been cancelled before processing
                if self.loading_cancelled:
                    return
                    
                # Cache the case types
                self.cache['case_types'] = case_types_data
                
                self._register_api_call()
            else:
                # Case types already cached, skip API call
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
        
        # Only need 1 API call for suites (sections will be loaded lazily)
        self.api_calls_total = 1
        
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
            
            # Don't load sections now - they'll be loaded lazily when needed
            
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
        
        # First, we need to load sections for all suites that haven't been loaded yet
        # then expand all items
        self._expand_all_with_lazy_loading()
        
    def _expand_all_with_lazy_loading(self):
        """Expand all items, loading sections as needed."""
        if not self.current_project or not self.current_project.suites:
            return
            
        # Count total suites that need loading for progress tracking
        suites_to_load = []
        for suite in self.current_project.suites:
            if suite.id not in self.cache['sections_loaded']:
                suites_to_load.append(suite)
        
        if suites_to_load:
            # Reset progress tracking
            self.api_calls_total = len(suites_to_load)
            self.api_calls_done = 0
            self._update_progress("Loading sections for expand all...", reset=True)
            
            # Load sections for all suites in a background thread
            self.active_thread = threading.Thread(target=lambda: self._load_all_sections_then_expand(suites_to_load))
            self.active_thread.start()
        else:
            # All sections already loaded, just expand
            self._update_progress("Expanding all items...", reset=True)
            self.tree.expand_all()
            self._update_progress("")
            
    def _load_all_sections_then_expand(self, suites_to_load):
        """Load sections for all suites then expand all items."""
        try:
            for suite in suites_to_load:
                if self.loading_cancelled:
                    return
                    
                # Load sections for this suite
                if suite.id not in self.cache['sections_loaded']:
                    try:
                        sections_data = self.client.get_sections(self.current_project.id, suite.id)
                        sections = [Section(s) for s in sections_data]
                        self.cache['sections'][suite.id] = sections
                        self.cache['sections_loaded'].add(suite.id)
                        
                        # Update suite object
                        suite.sections = sections
                        
                    except Exception:
                        # If we can't load, mark as loaded with empty sections to avoid retry
                        self.cache['sections'][suite.id] = []
                        self.cache['sections_loaded'].add(suite.id)
                        suite.sections = []
                
                self._register_api_call()
            
            # Now expand all in the main thread
            if not self.loading_cancelled:
                self.after(0, self._finish_expand_all)
                
        except Exception as e:
            if not self.loading_cancelled:
                self.after(0, lambda: self._show_error(f"Failed to load sections for expand all: {str(e)}"))
                
    def _finish_expand_all(self):
        """Finish the expand all operation by updating UI and expanding."""
        try:
            # Remove all placeholders and add real sections to tree
            for suite_item_id in self.tree.get_children():
                suite_id = self._get_suite_id_from_item(suite_item_id)
                if suite_id and suite_id in self.cache['sections_loaded']:
                    # Remove placeholder children
                    children = self.tree.get_children(suite_item_id)
                    for child in children:
                        if self.tree.set(child, "is_placeholder") == "true":
                            self.tree.delete(child)
                    
                    # Add real sections if any exist
                    sections = self.cache['sections'].get(suite_id, [])
                    if sections:
                        self._add_sections_to_tree(sections, suite_item_id)
            
            # Now expand all items
            self._update_progress("Expanding all items...")
            self.tree.expand_all()
            self._update_progress("")
            self.status_var.set("Expanded all items")
            
        except Exception as e:
            self._show_error(f"Failed to expand all: {str(e)}")
        
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
        """Update the treeview after loading suites."""
        # Add suites to the treeview (sections will be loaded on demand)
        for suite in self.current_project.suites:
            # Add suite without loading sections yet
            suite_item_id = self.tree.insert("", "end", text="", values=(suite.name,), image=self.tree.image_unchecked)
            
            # Store suite ID in hidden column for later reference
            self.tree.set(suite_item_id, "suite_id", str(suite.id))
            print(f"DEBUG: Created suite item {suite_item_id} for suite '{suite.name}' (id: {suite.id})")
            
            # Add a placeholder child to show the expansion caret
            # This will be replaced with actual sections when expanded
            placeholder_id = self.tree.insert(suite_item_id, "end", text="", values=("Loading...",), image=self.tree.image_unchecked)
            self.tree.set(placeholder_id, "is_placeholder", "true")
            
        # Add event handler for tree item open (expand) event
        self.tree.bind("<<TreeviewOpen>>", self._on_tree_item_expanded)
            
        # Mark project loading as completed
        if hasattr(self, 'current_project') and self.current_project:
            self.cache['loading_state'][self.current_project.id] = 'completed'
        
        self.status_var.set(f"Loaded {len(self.current_project.suites)} suites")
        self._update_progress("")
        
    def _on_tree_item_expanded(self, event):
        """Handle when a tree item is expanded - lazy load sections if needed."""
        # Simple approach: check all open items and load sections if needed
        self.after(50, self._check_all_expanded_items)
    
    def _check_all_expanded_items(self):
        """Check all expanded items and load sections if needed."""
        # Simple check: look for any open suites with placeholder children
        for item_id in self.tree.get_children():
            if self.tree.item(item_id, "open"):
                # This suite is expanded, check if it needs sections loaded
                children = self.tree.get_children(item_id)
                if children and len(children) == 1:
                    child_id = children[0]
                    if self.tree.set(child_id, "is_placeholder") == "true":
                        # This suite has a placeholder - load sections
                        suite_id = self._get_suite_id_from_item(item_id)
                        print(f"DEBUG: Got suite_id {suite_id} for item {item_id}")
                        
                        # Also get suite name for verification
                        item_values = self.tree.item(item_id, "values")
                        suite_name = item_values[0] if item_values else "Unknown"
                        print(f"DEBUG: Suite name from tree: {suite_name}")
                        
                        if suite_id and suite_id not in self.cache['sections_loaded']:
                            self._load_sections_sync(suite_id, item_id)
    
    def _load_sections_sync(self, suite_id, suite_item_id):
        """Load sections synchronously and immediately update the tree."""
        print(f"DEBUG: _load_sections_sync called for suite {suite_id}")
        if not self.client or not self.current_project:
            print("DEBUG: No client or project")
            return
            
        try:
            self.status_var.set("Loading sections...")
            
            # Load sections from API if not cached
            if suite_id not in self.cache['sections']:
                print(f"DEBUG: Loading sections from API for suite {suite_id}")
                sections_data = self.client.get_sections(self.current_project.id, suite_id)
                print(f"DEBUG: Got {len(sections_data)} sections from API")
                sections = [Section(s) for s in sections_data]
                for i, section in enumerate(sections):
                    print(f"DEBUG: API Section {i}: {section.name} (id: {section.id}, parent: {section.parent_id})")
                self.cache['sections'][suite_id] = sections
            else:
                print(f"DEBUG: Using cached sections for suite {suite_id}")
                sections = self.cache['sections'][suite_id]
            
            # Mark as loaded
            self.cache['sections_loaded'].add(suite_id)
            
            # Remove placeholder children
            children = self.tree.get_children(suite_item_id)
            print(f"DEBUG: Removing {len(children)} placeholder children")
            for child in children:
                self.tree.delete(child)
            
            if sections:
                print(f"DEBUG: Adding {len(sections)} sections to tree")
                # Add sections to tree with proper hierarchy
                self._add_sections_to_tree(sections, suite_item_id)
                self.status_var.set(f"Loaded {len(sections)} sections")
            else:
                print("DEBUG: No sections to add")
                self.status_var.set("No sections returned")
                
        except Exception as e:
            self._show_error(f"Failed to load sections: {str(e)}")
    
    def _export_cases(self, format='json'):
        """
        Export selected test cases.
        
        Args:
            format (str): Export format ('json', 'csv', or 'xml')
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
            format (str): Export format ('json', 'csv', or 'xml')
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
                    
                # Get suite ID from tree item
                suite_id = self._get_suite_id_from_item(item_id)
                suite = next((s for s in self.current_project.suites if s.id == suite_id), None) if suite_id else None
                
                if suite:
                    # Update progress
                    self._update_progress(f"Exporting suite: {suite.name}")
                    
                    # Check if operation has been cancelled
                    if self.loading_cancelled:
                        return
                        
                    # Make sure sections are loaded for this suite before exporting
                    if suite.id not in self.cache['sections_loaded']:
                        self._ensure_sections_loaded_for_export(suite.id)
                        
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
                    
                # Get section info from tree
                section_id = self._get_section_id_from_item(item_id)
                suite_id = self._get_suite_id_from_item(item_id)
                
                if not section_id or not suite_id:
                    continue
                    
                item_values = self.tree.item(item_id, "values")
                section_name = item_values[0] if item_values else "Unknown Section"
                
                # Update progress
                self._update_progress(f"Exporting section: {section_name}")
                
                # Check if operation has been cancelled
                if self.loading_cancelled:
                    return
                    
                # Check if we have cached cases for this section
                cache_key = f"{self.current_project.id}_{suite_id}_{section_id}"
                if cache_key in self.cache['cases']:
                    # Use cached data
                    section_cases = self.cache['cases'][cache_key]
                else:
                    # Get cases for the section from API
                    cases_data = self.client.get_cases(self.current_project.id, suite_id, section_id)
                    
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
                
            # Determine which suites are involved in the export
            suite_ids_in_export = set()
            for case in cases:
                if case.suite_id:
                    suite_ids_in_export.add(case.suite_id)
            
            # Only include suites that have test cases in the export
            suites_for_export = [suite for suite in self.current_project.suites if suite.id in suite_ids_in_export]
            
            # Prepare export data with names instead of IDs
            export_data = {
                'project': {
                    'id': self.current_project.id,
                    'name': self.current_project.name
                },
                'cases': [self._convert_case_ids_to_names(case) for case in cases],
                'suites': suites_for_export  # Include only suites with exported test cases
            }
            
            # Update UI in the main thread
            if not self.loading_cancelled:
                self.after(0, lambda: self._save_export_file(export_data, format))
        except Exception as e:
            if not self.loading_cancelled:
                self.after(0, lambda: self._show_error(f"Failed to export test cases: {str(e)}"))
    
    def _convert_case_ids_to_names(self, case):
        """
        Convert a test case's IDs to names for export.
        
        Args:
            case (Case): Test case object
            
        Returns:
            dict: Case dictionary with names instead of IDs where possible
        """
        case_dict = case.to_dict()
        
        # Convert suite_id to suite name (keep both for XML export)
        if case.suite_id:
            suite = next((s for s in self.current_project.suites if s.id == case.suite_id), None)
            if suite:
                case_dict['suite_name'] = suite.name
                # Keep suite_id for XML export
        
        # Convert section_id to section name and add hierarchy info (keep all for XML export)
        if case.section_id:
            suite = next((s for s in self.current_project.suites if s.id == case.suite_id), None)
            if suite:
                section = next((sec for sec in suite.sections if sec.id == case.section_id), None)
                if section:
                    case_dict['section_name'] = section.name
                    case_dict['section_parent_id'] = section.parent_id
                    case_dict['section_depth'] = section.depth
                    # Keep section_id for XML export
        
        # Convert priority_id to priority name (keep both for XML export)
        if case.priority_id and self.cache['priorities']:
            priority = next((p for p in self.cache['priorities'] if p['id'] == case.priority_id), None)
            if priority:
                case_dict['priority_name'] = priority['name']
                # Keep priority_id for XML export
        
        # Convert type_id to type name (keep both for XML export)
        if case.type_id and self.cache['case_types']:
            case_type = next((t for t in self.cache['case_types'] if t['id'] == case.type_id), None)
            if case_type:
                case_dict['type_name'] = case_type['name']
                # Keep type_id for XML export
        
        return case_dict
    
    def _save_export_file(self, export_data, format='json'):
        """
        Prompt user to save export file.
        
        Args:
            export_data (dict): Data to export
            format (str): Export format ('json', 'csv', or 'xml')
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
        elif format == 'xml':
            extension = ".xml"
            file_types = [("XML Files", "*.xml"), ("All Files", "*.*")]
            default_filename = f"{self.current_project.name}_export.xml"
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
            elif format == 'xml':
                success = Exporter.export_to_xml(export_data, filepath)
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
    
    def _get_suite_id_from_item(self, item_id):
        """Get suite ID from a tree item."""
        print(f"DEBUG: _get_suite_id_from_item called for item {item_id}")
        
        # First try to get from stored column
        try:
            suite_id = self.tree.set(item_id, "suite_id")
            print(f"DEBUG: suite_id from column: '{suite_id}'")
            if suite_id and suite_id != "":
                result = int(suite_id)
                print(f"DEBUG: Converted to int: {result}")
                return result
        except (ValueError, tk.TclError) as e:
            print(f"DEBUG: Error getting suite_id from column: {e}")
            pass
            
        # If this is a section, get suite ID from its parent
        parent_id = self.tree.parent(item_id)
        print(f"DEBUG: parent_id: {parent_id}")
        if parent_id:
            return self._get_suite_id_from_item(parent_id)
            
        # Fallback: get from suite name
        item_values = self.tree.item(item_id, "values")
        print(f"DEBUG: item_values: {item_values}")
        if item_values:
            suite_name = item_values[0]
            print(f"DEBUG: suite_name: {suite_name}")
            suite = next((s for s in self.current_project.suites if s.name == suite_name), None)
            if suite:
                print(f"DEBUG: Found suite by name: {suite.name} (id: {suite.id})")
                return suite.id
            else:
                print(f"DEBUG: No suite found with name '{suite_name}'")
        print("DEBUG: Returning None")
        return None
        
    
    
    
            
    def _add_sections_to_tree(self, sections, parent_item_id):
        """Add sections to tree view with proper hierarchical nesting."""
        print(f"DEBUG: Adding {len(sections)} sections to tree")
        
        # Create a mapping of parent_id -> children for hierarchy building
        children_by_parent = {}
        root_sections = []
        
        for section in sections:
            print(f"DEBUG: Section {section.name} - parent_id: {section.parent_id}")
            if section.parent_id is None:
                root_sections.append(section)
                print(f"DEBUG: Added as root section: {section.name}")
            else:
                if section.parent_id not in children_by_parent:
                    children_by_parent[section.parent_id] = []
                children_by_parent[section.parent_id].append(section)
                print(f"DEBUG: Added as child of {section.parent_id}: {section.name}")
        
        # Sort root sections alphabetically
        root_sections.sort(key=lambda s: s.name.lower())
        
        print(f"DEBUG: Found {len(root_sections)} root sections, {len(children_by_parent)} parent groups")
        
        # Add root sections and their children recursively
        for section in root_sections:
            print(f"DEBUG: Processing root section: {section.name}")
            self._add_section_with_children(section, parent_item_id, children_by_parent)
            
    def _add_section_with_children(self, section, parent_item_id, children_by_parent):
        """Recursively add a section and its children to the tree."""
        print(f"DEBUG: Adding section {section.name} to tree under parent {parent_item_id}")
        
        # Add this section
        section_item_id = self.tree.insert(
            parent_item_id, "end", 
            text="", 
            values=(section.name,), 
            image=self.tree.image_unchecked
        )
        
        print(f"DEBUG: Created tree item {section_item_id} for section {section.name}")
        
        # Store section info in hidden columns for later reference
        self.tree.set(section_item_id, "section_id", str(section.id))
        self.tree.set(section_item_id, "section_parent_id", str(section.parent_id or ""))
        
        # Also store the suite_id for sections so we can find their parent suite
        parent_suite_id = self._get_suite_id_from_item(parent_item_id)
        if parent_suite_id:
            self.tree.set(section_item_id, "suite_id", str(parent_suite_id))
        
        # Add children if any exist
        if section.id in children_by_parent:
            children = children_by_parent[section.id]
            print(f"DEBUG: Section {section.name} has {len(children)} children")
            # Sort children alphabetically
            children.sort(key=lambda s: s.name.lower())
            
            for child_section in children:
                print(f"DEBUG: Adding child {child_section.name} under {section.name}")
                self._add_section_with_children(child_section, section_item_id, children_by_parent)
        else:
            print(f"DEBUG: Section {section.name} has no children")
                
    def _get_section_id_from_item(self, item_id):
        """Get section ID from a tree item."""
        try:
            section_id = self.tree.set(item_id, "section_id")
            if section_id and section_id != "":
                return int(section_id)
        except (ValueError, tk.TclError):
            pass
        return None
        
    def _ensure_sections_loaded_for_export(self, suite_id):
        """Ensure sections are loaded for a suite before export."""
        if suite_id not in self.cache['sections_loaded']:
            try:
                # Load sections from API if not cached
                if suite_id not in self.cache['sections']:
                    sections_data = self.client.get_sections(self.current_project.id, suite_id)
                    sections = [Section(s) for s in sections_data]
                    self.cache['sections'][suite_id] = sections
                
                # Update the suite object with loaded sections
                suite = next((s for s in self.current_project.suites if s.id == suite_id), None)
                if suite:
                    suite.sections = self.cache['sections'][suite_id]
                
                # Mark as loaded
                self.cache['sections_loaded'].add(suite_id)
                
            except Exception as e:
                # If we can't load sections, continue with empty sections
                pass
                
    def _lazy_load_child_sections(self, section_item_id):
        """Check if a section should have children and load them if needed."""
        # This method is for future extensibility if we need to load
        # sections on demand at deeper levels
        pass
    
    def _show_error(self, message):
        """Show an error message and update the status."""
        messagebox.showerror("Error", message)
        self.status_var.set("Error occurred")
        self._update_progress("")