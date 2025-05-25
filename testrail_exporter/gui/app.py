import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
import threading
import json
import os
import time
import tempfile
from datetime import datetime
from PIL import Image, ImageTk
from testrail_exporter.utils.exporter import Exporter, ExportError
from testrail_exporter.utils.testrail2xray import convert_xml_to_xray_csv, XrayConversionError
from testrail_exporter.utils.logger import ExportLogger

from testrail_exporter.gui.settings import SettingsFrame
from testrail_exporter.gui.tree_view import CheckableTreeview
from testrail_exporter.api.testrail_client import TestRailClient
from testrail_exporter.models.project import Project
from testrail_exporter.models.suite import Suite
from testrail_exporter.models.section import Section
from testrail_exporter.models.case import Case
from testrail_exporter.utils.config import Config


class Application(ctk.CTk):
    """Main application window."""

    def __init__(self):
        """Initialize the application."""
        super().__init__()
        
        # Load configuration
        self.config = Config()
        
        # Set window title and size
        self.title("TestRail Exporter")
        window_width = self.config.get_setting('ui', 'window_width', 1200)
        window_height = self.config.get_setting('ui', 'window_height', 850)
        self.geometry(f"{window_width}x{window_height}")
        self.minsize(1000, 750)
        
        # Set window icon
        try:
            icon_path = os.path.join(os.path.dirname(__file__), '..', '..', 'docs', 'images', 'icon.png')
            if os.path.exists(icon_path):
                icon_image = Image.open(icon_path)
                # Convert to PhotoImage for tkinter
                icon_photo = ImageTk.PhotoImage(icon_image)
                self.iconphoto(True, icon_photo)
        except Exception as e:
            # If icon loading fails, just continue without it
            print(f"Could not load icon: {e}")
        
        # Save window size when closing the application
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Create main frame
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Settings frame
        self.settings_frame = SettingsFrame(main_frame, config=self.config)
        self.settings_frame.pack(fill=tk.X, pady=10)
        
        # Toggles container frame
        toggles_container = ctk.CTkFrame(main_frame, fg_color="transparent")
        toggles_container.pack(fill=tk.X, pady=(5, 0), padx=10)
        
        # Load sections toggle
        load_sections_frame = ctk.CTkFrame(toggles_container, fg_color="transparent")
        load_sections_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.load_sections_var = tk.BooleanVar(value=False)  # Default to off
        
        # Create CTkSwitch for Load Sections
        self.load_sections_switch = ctk.CTkSwitch(
            load_sections_frame, 
            text="Load Sections?", 
            command=self._on_load_sections_changed,
            variable=self.load_sections_var,
            onvalue=True,
            offvalue=False,
            width=200
        )
        self.load_sections_switch.pack(side=tk.LEFT)
        
        # Multi-Project Selection toggle
        multi_project_frame = ctk.CTkFrame(toggles_container, fg_color="transparent")
        multi_project_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.multi_project_var = tk.BooleanVar(value=False)  # Default to off
        
        # Create CTkSwitch for Multi-Project Selection
        self.multi_project_switch = ctk.CTkSwitch(
            multi_project_frame,
            text="Multi-Project Selection",
            command=self._on_multi_project_changed,
            variable=self.multi_project_var,
            onvalue=True,
            offvalue=False,
            width=200
        )
        self.multi_project_switch.pack(side=tk.LEFT)
        
        # Add Refresh Projects button to the same line
        self.load_projects_button = ctk.CTkButton(
            multi_project_frame, 
            text="Load Projects", 
            command=self._load_projects,
            width=120
        )
        self.load_projects_button.pack(side=tk.LEFT, padx=(20, 0))
        
        # Project selection frame (for single project mode)
        self.project_selection_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        self.project_selection_frame.pack(fill=tk.X, pady=10, padx=10)
        
        # Create project selection widgets
        self.project_label = ctk.CTkLabel(self.project_selection_frame, text="Project:")
        self.project_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.project_var = tk.StringVar()
        self.project_combo = ctk.CTkComboBox(
            self.project_selection_frame, 
            variable=self.project_var, 
            state="readonly",
            width=400,
            command=self._on_project_selected
        )
        self.project_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Create treeview frame with scrollbars
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Treeview for suites and sections
        self.tree = CheckableTreeview(tree_frame, columns=("name",), show="tree headings")
        self.tree.column("#0", width=50, minwidth=50, stretch=False)
        self.tree.column("name", width=400, minwidth=200, stretch=True)
        self.tree.heading("name", text="Suites and Sections")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=vsb.set)
        
        # Tree control buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill=tk.X, pady=10, padx=10)
        
        # Use our custom expand all method with progress tracking
        self.expand_all_button = ctk.CTkButton(
            button_frame, 
            text="Expand All", 
            command=self._expand_all_with_progress, 
            state="disabled",
            width=100
        )
        self.expand_all_button.pack(side=tk.LEFT, padx=5)
        
        self.collapse_all_button = ctk.CTkButton(
            button_frame, 
            text="Collapse All", 
            command=self.tree.collapse_all, 
            state="disabled",
            width=100
        )
        self.collapse_all_button.pack(side=tk.LEFT, padx=5)
        
        ctk.CTkButton(
            button_frame, 
            text="Check All", 
            command=self.tree.check_all,
            width=100
        ).pack(side=tk.LEFT, padx=5)
        
        ctk.CTkButton(
            button_frame, 
            text="Uncheck All", 
            command=self.tree.uncheck_all,
            width=100
        ).pack(side=tk.LEFT, padx=5)
        
        # Bind tree events for progress tracking
        self.tree.bind("<<ExpandAllStarted>>", self._on_expand_all_started)
        self.tree.bind("<<TreeItemExpanded>>", self._on_tree_item_expanded_progress)
        self.tree.bind("<<ExpandAllCompleted>>", self._on_expand_all_completed)
        
        # Export buttons
        export_frame = ctk.CTkFrame(button_frame, fg_color="transparent")
        export_frame.pack(side=tk.RIGHT, padx=5)
        
        ctk.CTkButton(
            export_frame, 
            text="Export to XML", 
            command=lambda: self._export_cases(format='xml'),
            width=110
        ).pack(side=tk.RIGHT, padx=2)
        
        ctk.CTkButton(
            export_frame, 
            text="Export to CSV", 
            command=lambda: self._export_cases(format='xray_csv'),
            width=110
        ).pack(side=tk.RIGHT, padx=2)
        
        ctk.CTkButton(
            export_frame, 
            text="Export Both", 
            command=lambda: self._export_cases(format='both'),
            width=110
        ).pack(side=tk.RIGHT, padx=2)
        
        # Progress bar and status
        status_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        status_frame.pack(fill=tk.X, pady=(10, 20), padx=10)
        
        self.status_var = tk.StringVar()
        self.status_label = ctk.CTkLabel(status_frame, textvariable=self.status_var)
        self.status_label.pack(side=tk.LEFT)
        
        self.progress_frame = ctk.CTkFrame(status_frame, fg_color="transparent")
        self.progress_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(20, 0))
        
        self.progress_var = tk.DoubleVar()
        self.progress = ctk.CTkProgressBar(
            self.progress_frame,
            variable=self.progress_var,
            mode='determinate'
        )
        self.progress.pack(fill=tk.X, expand=True)
        
        # Add more padding and make the progress label larger
        self.progress_label = ctk.CTkLabel(self.progress_frame, text="", font=("", 12))
        self.progress_label.pack(pady=(5, 5))
        
        # Initialize instance variables
        self.client = None
        self.projects = []
        self.current_project = None
        self.last_selected_project_name = None  # Store project name before MPS toggle
        self.api_calls_total = 0
        self.api_calls_done = 0
        self.current_step_text = ""  # Track current operation for progress display
        
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
            'priorities': None,  # Cache priorities (not project-specific)
            'case_types': None,  # Cache case types (not project-specific)
            'template': {},  # Project ID -> Templates
            'milestone': {}  # Project ID -> Milestones
        }
        
        
        # Auto-load projects if settings are populated
        self.after(500, self._auto_load_projects)
    
    def _on_load_sections_changed(self):
        """Handle when the Load Sections checkbox is toggled."""
        # Update button states based on Load Sections state
        self._update_expand_collapse_buttons()
        
        # Trigger a refresh if projects are already loaded
        if self.projects and self.load_projects_button:
            # Check if the button text is "Refresh Projects" (indicates projects are loaded)
            if self.load_projects_button.cget('text') == "Refresh Projects":
                self._load_projects()
    
    def _on_multi_project_changed(self):
        """Handle when the Multi-Project Selection toggle is changed."""
        # Cancel any ongoing loading operations
        self.loading_cancelled = True
        
        if self.multi_project_var.get():
            # Store the current project selection before clearing
            current_selection = self.project_var.get()
            if current_selection:
                self.last_selected_project_name = current_selection
            
            # Multi-project mode: disable project selection dropdown (but keep it visible)
            self.project_combo.configure(state="disabled")
            self.project_var.set("")  # Clear the selection
            
            # Automatically disable Load Sections when Multi-Project is enabled
            if self.load_sections_var.get():
                self.load_sections_var.set(False)
            self.load_sections_switch.configure(state="disabled")
            
            # Clear the tree
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Reset progress
            self._update_progress("", reset=True)
            
            # Update tree heading for projects mode
            self.tree.heading("name", text="Projects")
            
            # Show projects immediately if they're loaded
            if self.projects:
                # Use after to ensure UI is ready
                self.after(10, self._show_projects_in_tree)
            else:
                self.status_var.set("No projects loaded. Click 'Load Projects' or 'Refresh Projects' to load.")
        else:
            # Single project mode: enable project selection dropdown
            self.project_combo.configure(state="readonly")
            
            # Re-enable Load Sections switch
            self.load_sections_switch.configure(state="normal")
            
            # Clear tree
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Restore the tree heading for suites mode
            self.tree.heading("name", text="Suites and Sections")
            
            # Restore the previous project selection if available
            if self.last_selected_project_name and self.projects:
                project_names = [p.name for p in self.projects]
                if self.last_selected_project_name in project_names:
                    self.project_var.set(self.last_selected_project_name)
            
            # Trigger a refresh of projects when switching back to single-project mode
            if self.projects and self.load_projects_button:
                # Check if the button text is "Refresh Projects" (indicates projects are loaded)
                if self.load_projects_button.cget('text') == "Refresh Projects":
                    self._load_projects()
            
            # Reload current project if one is selected
            if self.current_project and hasattr(self.current_project, 'suites'):
                self._update_suites_ui()
            else:
                self.status_var.set("Select a project from the dropdown")
        
        # Update expand/collapse button states
        self._update_expand_collapse_buttons()
    
    def _update_expand_collapse_buttons(self):
        """Update the state of expand/collapse buttons based on current settings."""
        # Enable buttons only if Load Sections is ON and Multi-Project is OFF
        if self.load_sections_var.get() and not self.multi_project_var.get():
            self.expand_all_button.configure(state="normal")
            self.collapse_all_button.configure(state="normal")
        else:
            self.expand_all_button.configure(state="disabled")
            self.collapse_all_button.configure(state="disabled")
    
    def _show_projects_in_tree(self):
        """Show all projects in the tree view for multi-project selection."""
        # Clear the tree first
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Sort projects alphabetically
        sorted_projects = sorted(self.projects, key=lambda p: p.name.lower())
        
        # Add all projects to the tree
        for project in sorted_projects:
            # Add project to tree with checkbox, using tags to store project ID
            tree_item_id = self.tree.insert("", "end", text="", values=(project.name,), 
                                          image=self.tree.image_unchecked, 
                                          tags=(f"project_{project.id}",))
            
        # Update the tree heading for projects mode
        self.tree.heading("name", text="Projects")
        
        # Update status
        self.status_var.set(f"Showing {len(sorted_projects)} projects for selection")
        
        # Force the tree to refresh
        self.tree.update()
        self.update_idletasks()
        
        # Ensure scrollbar is updated
        self.tree.yview_moveto(0)  # Scroll to top
    
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
            self.current_step_text = ""
        
        # Update current step text if provided
        if step_text:
            self.current_step_text = step_text
        
        if self.api_calls_total > 0:
            progress_fraction = self.api_calls_done / self.api_calls_total
            progress_pct = int(progress_fraction * 100)
            self.progress_var.set(progress_fraction)  # CTkProgressBar expects 0.0 to 1.0
            
            # Check if tasks are complete
            if progress_pct >= 100:
                # Show 100% and Tasks Complete
                self.progress_label.configure(text="100%")
                self.status_var.set("Tasks Complete")
            else:
                # Show percentage beneath progress bar
                self.progress_label.configure(text=f"{progress_pct}%")
                # Show current operation in status label
                self.status_var.set(self.current_step_text)
        else:
            self.progress_var.set(0)
            self.progress_label.configure(text="")
            if self.current_step_text:
                self.status_var.set(self.current_step_text)
            
        self.update_idletasks()
    
    def _register_api_call(self):
        """Register that an API call has been completed."""
        self.api_calls_done += 1
        self._update_progress()  # This will use the stored current_step_text
        
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
                    'priorities': None,
                    'case_types': None,
                    'template': {},
                    'milestone': {}
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
        self.project_combo.configure(values=project_names)
        
        # Check if we should select a previously saved project
        last_project = self.config.get_setting('ui', 'last_project')
        
        if project_names:
            # Determine which project to select
            project_to_select = None
            
            # Priority: last_selected_project_name > last_project > first project
            if self.last_selected_project_name and self.last_selected_project_name in project_names:
                project_to_select = self.last_selected_project_name
            elif last_project and last_project in project_names:
                project_to_select = last_project
            else:
                project_to_select = project_names[0]
            
            # Set the project selection
            self.project_combo.set(project_to_select)
                
            self.status_var.set(f"Loaded {len(project_names)} projects")
            self._update_progress("")
            
            # Change the load button text to "Refresh Projects"
            if self.load_projects_button:
                self.load_projects_button.configure(text="Refresh Projects")
            
            # Check if we're in multi-project mode
            if self.multi_project_var.get():
                # Show projects in tree for multi-project selection  
                # Use after to ensure UI is ready
                self.after(10, self._show_projects_in_tree)
            else:
                # Trigger project selection for single project mode
                # Pass the selected project name to ensure it gets loaded
                if project_to_select:
                    self._on_project_selected(project_to_select)
        else:
            self.status_var.set("No projects found")
            self._update_progress("")
    
    def _on_project_selected(self, choice):
        """Handle project selection changes."""
        if not choice or not self.projects:
            return
            
        # Find the selected project by name
        selected_project = next((p for p in self.projects if p.name == choice), None)
        if not selected_project:
            return
            
        # Cancel any ongoing loading operations
        self.loading_cancelled = True
        
        # Wait a moment to ensure any running thread notices the cancellation flag
        self.after(100, lambda: self._start_load_project(selected_project))
    
    def _start_load_project(self, selected_project):
        """Start loading the selected project after cancellation of previous operations."""
        # Check if there's still an active thread running
        if (hasattr(self, 'active_thread') and self.active_thread and 
            self.active_thread.is_alive()):
            # Thread is still running, wait a bit more
            self.after(50, lambda: self._start_load_project(selected_project))
            return
            
        # Reset cancellation flag
        self.loading_cancelled = False
        
        self.current_project = selected_project
        
        # Save current project to config
        self.config.set_setting('ui', 'last_project', self.current_project.name)
        
        # Clear treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Check if we have fully loaded data for this project
        project_loading_state = self.cache['loading_state'].get(self.current_project.id, 'not_started')
        
        # Check if we have cached suites and if the loading state matches the current checkbox state
        cached_with_sections = project_loading_state == 'completed_with_sections'
        cached_without_sections = project_loading_state == 'completed_without_sections'
        current_wants_sections = self.load_sections_var.get()
        
        if (self.current_project.id in self.cache['suites'] and 
            ((cached_with_sections and current_wants_sections) or 
             (cached_without_sections and not current_wants_sections))):
            # Use cached data only if loading state matches current checkbox state
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
            
            # Only load sections if the checkbox is checked
            if self.load_sections_var.get():
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
            else:
                # When sections are not loaded upfront, initialize empty sections for each suite
                for suite in suites:
                    suite.sections = []
            
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
        # Check if we should stop due to mode change
        if self.loading_cancelled or self.multi_project_var.get():
            return
            
        # Add suites and sections to the treeview
        for suite in self.current_project.suites:
            # Check again before each suite
            if self.loading_cancelled or self.multi_project_var.get():
                return
                
            # Add suite without case count
            suite_id = self.tree.insert("", "end", text="", values=(suite.name,), image=self.tree.image_unchecked)
            
            # Add sections if any and if they were loaded
            if self.load_sections_var.get() and suite.has_sections():
                # Add all sections without case counts or filtering
                for section in suite.sections:
                    section_id = self.tree.insert(suite_id, "end", text="", values=(section.name,), image=self.tree.image_unchecked)
            
        # Add event handler for tree item open (expand) event
        self.tree.bind("<<TreeviewOpen>>", self._on_tree_item_expanded)
            
        # Mark project loading as completed with appropriate state
        if hasattr(self, 'current_project') and self.current_project:
            if self.load_sections_var.get():
                self.cache['loading_state'][self.current_project.id] = 'completed_with_sections'
            else:
                self.cache['loading_state'][self.current_project.id] = 'completed_without_sections'
        
        # Update status message based on whether sections were loaded
        if self.load_sections_var.get():
            self.status_var.set(f"Loaded {len(self.current_project.suites)} suites with sections")
        else:
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
            format (str): Export format ('json', 'csv', or 'xml')
        """
        # Check if multi-project mode is enabled
        if self.multi_project_var.get():
            # Multi-project mode
            if not self.projects or not self.client:
                messagebox.showwarning("Warning", "Please load projects first")
                return
                
            # Get checked items (projects)
            checked_items = self.tree.get_checked_items()
            if not checked_items:
                messagebox.showwarning("Warning", "Please select at least one project to export")
                return
                
            # For Xray CSV format, show column selection dialog first
            if format == 'xray_csv':
                self._show_column_selection_dialog(checked_items, format)
                return
                
            # Cancel any ongoing operations
            self.loading_cancelled = True
            
            # Wait a moment for cancellation to take effect
            self.after(100, lambda: self._start_multi_project_export(checked_items, format))
        else:
            # Single project mode (original behavior)
            if not self.current_project or not self.client:
                messagebox.showwarning("Warning", "Please select a project first")
                return
                
            # Check if the project has loaded suites
            if not hasattr(self.current_project, 'suites') or not self.current_project.suites:
                messagebox.showwarning("Warning", "Project suites not loaded. Please refresh the project and try again.")
                return
                
            # Get checked items
            checked_items = self.tree.get_checked_items()
            if not checked_items:
                messagebox.showwarning("Warning", "Please select at least one suite or section to export")
                return
            
            # For Xray CSV format, show column selection dialog first
            if format == 'xray_csv':
                self._show_column_selection_dialog(checked_items, format)
                return
            
            # Cancel any ongoing operations
            self.loading_cancelled = True
            
            # Wait a moment for cancellation to take effect
            self.after(100, lambda: self._start_export(checked_items, format))
        
    def _start_export(self, checked_items, format, selected_columns=None):
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
        self.active_thread = threading.Thread(target=lambda: self._export_cases_thread(valid_checked_items, format, selected_columns))
        self.active_thread.start()
    
    def _export_cases_thread(self, checked_items, format='json', selected_columns=None):
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
                    
                item_values = self.tree.item(item_id, "values")
                suite_display_name = item_values[0]
                # Don't extract name - use the full display name since it should match exactly
                suite_name = suite_display_name
                    
                # Debug logging
                print(f"DEBUG: Looking for suite with display name: '{suite_display_name}'")
                print(f"DEBUG: Using suite name: '{suite_name}'")
                    
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
                else:
                    # Suite not found - log for debugging
                    print(f"DEBUG: Suite '{suite_name}' not found in current project")
                    print(f"DEBUG: Available suites: {[s.name for s in self.current_project.suites]}")
            
            # Process individual sections (only if their parent suite wasn't processed)
            for item_id in sections_to_process:
                # Check if operation has been cancelled
                if self.loading_cancelled:
                    return
                    
                item_values = self.tree.item(item_id, "values")
                parent_id = self.tree.parent(item_id)
                
                section_display_name = item_values[0]
                # Don't extract name - use the full display name
                section_name = section_display_name
                    
                suite_display_name = self.tree.item(parent_id, "values")[0]
                # Don't extract name - use the full display name
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
                
            # Determine which suites are involved in the export
            suite_ids_in_export = set()
            for case in cases:
                if case.suite_id:
                    suite_ids_in_export.add(case.suite_id)
            
            # Only include suites that have test cases in the export
            suites_for_export = []
            for suite in self.current_project.suites:
                if suite.id in suite_ids_in_export:
                    # If sections were not loaded during initial load, load them now for export
                    if not self.load_sections_var.get() and (not hasattr(suite, 'sections') or not suite.sections):
                        # Check if we have cached sections for this suite
                        if suite.id in self.cache['sections']:
                            suite.sections = self.cache['sections'][suite.id]
                        else:
                            # Load sections for this suite
                            try:
                                self._update_progress(f"Loading sections for suite: {suite.name}")
                                sections_data = self.client.get_sections(self.current_project.id, suite.id)
                                sections = [Section(s) for s in sections_data]
                                
                                # Sort sections alphabetically by name
                                sections.sort(key=lambda s: s.name.lower())
                                
                                suite.sections = sections
                                
                                # Cache the sections
                                self.cache['sections'][suite.id] = sections
                            except Exception as e:
                                # If we fail to load sections, continue with empty sections
                                print(f"Failed to load sections for suite {suite.name}: {e}")
                                suite.sections = []
                    
                    suites_for_export.append(suite)
            
            # Check if we found any test cases
            if not cases:
                # Show error in the main thread
                if not self.loading_cancelled:
                    self.after(0, lambda: messagebox.showwarning(
                        "No Test Cases Found", 
                        "No test cases were found in the selected suites/sections.\n\n"
                        "Possible reasons:\n"
                        "• The selected suite/section has no test cases\n"
                        "• The suite/section was not loaded properly\n"
                        "• There was an issue retrieving the test cases\n\n"
                        "Please try refreshing the project and selecting again."
                    ))
                    self.after(0, lambda: self._update_progress("", reset=True))
                return
            
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
                self.after(0, lambda: self._save_export_file(export_data, format, selected_columns))
        except Exception as e:
            if not self.loading_cancelled:
                self.after(0, lambda: self._show_error(f"Failed to export test cases: {str(e)}"))
    
    def _convert_case_ids_to_names_for_project(self, case, project):
        """
        Convert case IDs to human-readable names for a specific project.
        
        Args:
            case (Case): Case object with IDs
            project: The project object to use for lookups
            
        Returns:
            dict: Case data with names instead of IDs
        """
        # Store old current project temporarily
        old_project = self.current_project
        self.current_project = project
        
        try:
            # Call the original method
            return self._convert_case_ids_to_names(case)
        finally:
            # Restore old current project
            self.current_project = old_project
    
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
        
        # Convert template_id to template name (keep both for XML export)
        if hasattr(case, 'template_id') and case.template_id:
            project_id = self.current_project.id
            # Load templates for this project if not cached
            if project_id not in self.cache['template']:
                try:
                    templates_data = self.client.get_templates(project_id)
                    self.cache['template'][project_id] = templates_data
                except Exception as e:
                    print(f"Failed to load templates: {e}")
                    self.cache['template'][project_id] = []
            
            # Find the template name
            if project_id in self.cache['template']:
                template = next((t for t in self.cache['template'][project_id] if t['id'] == case.template_id), None)
                if template:
                    case_dict['template_name'] = template['name']
        
        # Convert milestone_id to milestone name (keep both for XML export)
        if hasattr(case, 'milestone_id') and case.milestone_id:
            project_id = self.current_project.id
            # Load milestones for this project if not cached
            if project_id not in self.cache['milestone']:
                try:
                    milestones_response = self.client.get_milestones(project_id)
                    # API returns a dict with 'milestones' array
                    self.cache['milestone'][project_id] = milestones_response.get('milestone', [])
                except Exception as e:
                    print(f"Failed to load milestone: {e}")
                    self.cache['milestone'][project_id] = []
            
            # Find the milestone name
            if project_id in self.cache['milestone']:
                milestone = next((m for m in self.cache['milestone'][project_id] if m['id'] == case.milestone_id), None)
                if milestone:
                    case_dict['milestone_name'] = milestone['name']
        
        return case_dict
    
    def _save_export_file(self, export_data, format='xml', selected_columns=None):
        """
        Automatically save export file with timestamped filename.
        
        Args:
            export_data (dict): Data to export
            format (str): Export format ('xml', 'xray_csv', or 'both')
            selected_columns (list): Optional list of columns to include in CSV export
        """
        # Get export directory from settings
        settings = self.settings_frame.get_settings()
        export_dir = settings['export_dir']
        
        # Save export directory to config
        self.config.set_setting('export', 'directory', export_dir)
        
        # Create logger instance
        logger = ExportLogger(export_dir)
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        
        # Sanitize project name for use in filename
        sanitized_project_name = self._sanitize_filename(self.current_project.name)
        
        # Handle different formats
        if format == 'both':
            # Export both XML and CSV
            try:
                # Update progress
                self._update_progress("Exporting to XML and CSV...")
                logger.info(f"Starting export to both XML and CSV formats")
                logger.info(f"Export directory: {export_dir}")
                logger.info(f"Total test cases to export: {len(export_data.get('cases', []))}")
                
                # Export XML
                xml_filename = f"{sanitized_project_name}_export_{timestamp}.xml"
                xml_filepath = os.path.join(export_dir, xml_filename)
                Exporter.export_to_xml(export_data, xml_filepath, logger)
                
                # Export CSV using direct method
                csv_filename = f"{sanitized_project_name}_xray_export_{timestamp}.csv"
                csv_filepath = os.path.join(export_dir, csv_filename)
                
                # Get TestRail endpoint for link handling
                testrail_endpoint = settings.get('url', '')
                Exporter.export_to_xray_csv(export_data, csv_filepath, testrail_endpoint, logger, selected_columns)
                
                self.status_var.set(f"Exported {len(export_data['cases'])} test cases to both formats")
                messagebox.showinfo("Export Complete", 
                    f"Successfully exported {len(export_data['cases'])} test cases!\n\n"
                    f"Files created:\n"
                    f"• XML: {xml_filename}\n"
                    f"• CSV: {csv_filename}")
                    
                self._update_progress("")
                
            except ExportError as e:
                error_msg = str(e)
                logger.error(f"Export failed: {error_msg}")
                log_file = logger.get_log_file_path()
                self._show_export_error(error_msg, log_file, format)
                
        else:
            # Single format export
            if format == 'xray_csv':
                extension = ".csv"
                base_filename = f"{sanitized_project_name}_xray_export"
            else:  # xml
                extension = ".xml"
                base_filename = f"{sanitized_project_name}_export"
            
            # Create timestamped filename
            filename = f"{base_filename}_{timestamp}{extension}"
            filepath = os.path.join(export_dir, filename)
            
            try:
                # Update progress
                self._update_progress("Saving export file...")
                logger.info(f"Starting export to {format.upper()} format")
                logger.info(f"Export directory: {export_dir}")
                logger.info(f"Export filename: {filename}")
                logger.info(f"Total test cases to export: {len(export_data.get('cases', []))}")
                
                # Save the file
                if format == 'xray_csv':
                    # Use direct CSV export
                    testrail_endpoint = settings.get('url', '')
                    Exporter.export_to_xray_csv(export_data, filepath, testrail_endpoint, logger, selected_columns)
                    self.status_var.set(f"Exported {len(export_data['cases'])} test cases to {filename}")
                    messagebox.showinfo("Success", f"Successfully exported {len(export_data['cases'])} test cases to CSV format\n\nSaved as: {filename}")
                else:  # xml
                    Exporter.export_to_xml(export_data, filepath, logger)
                    self.status_var.set(f"Exported {len(export_data['cases'])} test cases to {filename}")
                    messagebox.showinfo("Success", f"Successfully exported {len(export_data['cases'])} test cases to XML format\n\nSaved as: {filename}")
                    
                self._update_progress("")
                
            except ExportError as e:
                error_msg = str(e)
                logger.error(f"Export failed: {error_msg}")
                
                # Show detailed error with log file reference
                log_file = logger.get_log_file_path()
                self._show_export_error(error_msg, log_file, format)
                
            except Exception as e:
                error_msg = f"Unexpected error during {format.upper()} export: {str(e)}"
                logger.error(error_msg, exc_info=True)
                
                # Show detailed error with log file reference
                log_file = logger.get_log_file_path()
                self._show_export_error(error_msg, log_file, format)
    
    
    def _show_column_selection_dialog(self, checked_items, format):
        """Show dialog for selecting CSV columns to export."""
        # Create dialog window
        dialog = tk.Toplevel(self)
        dialog.title("Select Columns for Export")
        dialog.geometry("400x500")
        dialog.transient(self)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Create main frame
        main_frame = ttk.Frame(dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Instructions
        ttk.Label(main_frame, text="Select columns to include in the Xray CSV export:", 
                 wraplength=350).pack(pady=(0, 10))
        
        # Column list frame with scrollbar
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Frame for checkboxes
        checkbox_frame = ttk.Frame(list_frame)
        checkbox_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Available columns from testrail2xray.py
        all_columns = ["Suite Name", "Section Name", "Issue ID", "Test Type", "Test Title", 
                      "Test Priority", "Preconditions", "Action", "Data", "Result", 
                      "Test Repo", "Labels"]
        
        # Mandatory columns that cannot be unchecked
        mandatory_columns = ["Suite Name", "Section Name", "Issue ID", "Test Title"]
        
        # Store checkbox variables
        column_vars = {}
        
        # Create checkboxes for each column
        for i, column in enumerate(all_columns):
            var = tk.BooleanVar(value=True)  # All checked by default
            column_vars[column] = var
            
            # Create checkbox
            if column in mandatory_columns:
                # Mandatory column - disabled checkbox
                cb = ttk.Checkbutton(checkbox_frame, text=column, variable=var, state='disabled')
                cb.pack(anchor=tk.W, pady=2)
            else:
                # Optional column
                cb = ttk.Checkbutton(checkbox_frame, text=column, variable=var)
                cb.pack(anchor=tk.W, pady=2)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Result variable
        dialog.result = None
        
        def on_export():
            # Get selected columns
            selected_columns = [col for col, var in column_vars.items() if var.get()]
            dialog.result = selected_columns
            dialog.destroy()
            
            # Continue with export
            if self.multi_project_var.get():
                self.loading_cancelled = True
                self.after(100, lambda: self._start_multi_project_export(checked_items, format, selected_columns))
            else:
                self.loading_cancelled = True
                self.after(100, lambda: self._start_export(checked_items, format, selected_columns))
        
        def on_cancel():
            dialog.result = None
            dialog.destroy()
        
        # Buttons
        ttk.Button(button_frame, text="Export", command=on_export).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=on_cancel).pack(side=tk.RIGHT)
        
        # Make dialog modal
        dialog.wait_window()
    
    def _start_multi_project_export(self, checked_items, format, selected_columns=None):
        """Start multi-project export process."""
        # Reset cancellation flag
        self.loading_cancelled = False
        
        # Get selected projects
        selected_projects = []
        for item in checked_items:
            try:
                # Get tags from tree item
                tags = self.tree.item(item, 'tags')
                
                # Extract project ID from tag
                project_id = None
                for tag in tags:
                    if tag.startswith('project_'):
                        project_id = int(tag.replace('project_', ''))
                        break
                
                if project_id:
                    # Find project object
                    project = next((p for p in self.projects if p.id == project_id), None)
                    if project:
                        selected_projects.append(project)
            except Exception as e:
                print(f"Error getting project from tree item: {e}")
                continue
        
        if not selected_projects:
            messagebox.showwarning("Warning", "No valid projects selected for export.")
            self._update_progress("", reset=True)
            return
        
        print(f"Starting export of {len(selected_projects)} projects")
        
        # Calculate total API calls for progress tracking
        total_projects = len(selected_projects)
        self._update_progress(f"Preparing to export {total_projects} projects...", reset=True)
        
        # Export in a separate thread
        self.active_thread = threading.Thread(
            target=lambda: self._export_multiple_projects_thread(selected_projects, format, selected_columns)
        )
        self.active_thread.start()
    
    def _export_multiple_projects_thread(self, projects, format, selected_columns=None):
        """Export multiple projects in a background thread."""
        try:
            total_projects = len(projects)
            completed_projects = 0
            
            # Calculate estimated total API calls
            # For each project: 1 for suites + ~5 for sections + ~5 for cases
            estimated_calls_per_project = 11
            self.api_calls_total = total_projects * estimated_calls_per_project
            self.api_calls_done = 0
            
            for project in projects:
                # Check if operation has been cancelled
                if self.loading_cancelled:
                    return
                
                # Update progress in main thread
                progress_text = f"Loading project {completed_projects + 1}/{total_projects}: {project.name}"
                self.after(0, lambda pt=progress_text: self._update_progress(pt))
                
                # Load project data
                try:
                    # Get suites for project
                    suites_data = self.client.get_suites(project.id)
                    suites = [Suite(s) for s in suites_data]
                    suites.sort(key=lambda s: s.name.lower())
                    project.suites = suites
                    self._register_api_call()
                    
                    # Load sections for each suite
                    for suite in suites:
                        if self.loading_cancelled:
                            return
                            
                        sections_data = self.client.get_sections(project.id, suite.id)
                        sections = [Section(s) for s in sections_data]
                        sections.sort(key=lambda s: s.name.lower())
                        suite.sections = sections
                        self._register_api_call()
                    
                    # Load all test cases for the project
                    all_cases = []
                    for suite in suites:
                        if self.loading_cancelled:
                            return
                            
                        # Get all cases for the suite
                        cases_data = self.client.get_cases(project.id, suite.id)
                        cases = [Case(c) for c in cases_data]
                        all_cases.extend(cases)
                        self._register_api_call()
                    
                    # Prepare export data
                    export_data = {
                        'project': {
                            'id': project.id,
                            'name': project.name
                        },
                        'cases': [self._convert_case_ids_to_names_for_project(case, project) for case in all_cases],
                        'suites': suites
                    }
                    
                    # Export project data
                    if not self.loading_cancelled:
                        # Capture project name in closure
                        project_name = project.name
                        self.after(0, lambda ed=export_data, pn=project_name: self._save_project_export_file(
                            ed, format, pn, selected_columns
                        ))
                    
                    completed_projects += 1
                    
                    # Update status to show saving
                    save_text = f"Saved {project.name} ({completed_projects}/{total_projects})"
                    self.after(0, lambda st=save_text: self.status_var.set(st))
                    
                except Exception as e:
                    error_msg = f"Failed to export project '{project.name}': {str(e)}"
                    if not self.loading_cancelled:
                        self.after(0, lambda msg=error_msg: messagebox.showerror("Export Error", msg))
                    continue
            
            # Update final status
            if not self.loading_cancelled:
                self.after(0, lambda: self.status_var.set(f"Exported {completed_projects} projects"))
                self.after(0, lambda: self._update_progress(""))
                
                # Show completion dialog
                export_dir = self.settings_frame.get_settings()['export_dir']
                self.after(0, lambda: self._show_multi_export_complete_dialog(completed_projects, total_projects, export_dir))
                
        except Exception as e:
            if not self.loading_cancelled:
                self.after(0, lambda: self._show_error(f"Failed to export projects: {str(e)}"))
    
    def _save_project_export_file(self, export_data, format, project_name, selected_columns=None):
        """Save export file for a single project."""
        # Get export directory from settings
        settings = self.settings_frame.get_settings()
        export_dir = settings['export_dir']
        
        # Create logger instance
        logger = ExportLogger(export_dir)
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        
        # Sanitize project name for use in filename
        sanitized_project_name = self._sanitize_filename(project_name)
        
        # Handle different formats
        if format == 'both':
            # Export both XML and CSV
            try:
                # Export XML
                xml_filename = f"{sanitized_project_name}_export_{timestamp}.xml"
                xml_filepath = os.path.join(export_dir, xml_filename)
                Exporter.export_to_xml(export_data, xml_filepath, logger)
                
                # Export CSV using direct method
                csv_filename = f"{sanitized_project_name}_xray_export_{timestamp}.csv"
                csv_filepath = os.path.join(export_dir, csv_filename)
                
                # Get TestRail endpoint
                settings = self.settings_frame.get_settings()
                testrail_endpoint = settings.get('url', '')
                Exporter.export_to_xray_csv(export_data, csv_filepath, testrail_endpoint, logger, selected_columns)
                
                logger.info(f"Successfully exported project '{project_name}' to both XML and CSV")
                
            except Exception as e:
                error_msg = f"Failed to export both formats for project '{project_name}': {str(e)}"
                logger.error(error_msg, exc_info=True)
                messagebox.showerror("Export Error", error_msg)
        else:
            # Single format export
            if format == 'xray_csv':
                extension = ".csv"
                base_filename = f"{sanitized_project_name}_xray_export"
            else:  # xml
                extension = ".xml"
                base_filename = f"{sanitized_project_name}_export"
            
            # Create timestamped filename
            filename = f"{base_filename}_{timestamp}{extension}"
            filepath = os.path.join(export_dir, filename)
            
            try:
                # Save the file
                if format == 'xray_csv':
                    # Use direct CSV export
                    settings = self.settings_frame.get_settings()
                    testrail_endpoint = settings.get('url', '')
                    Exporter.export_to_xray_csv(export_data, filepath, testrail_endpoint, logger, selected_columns)
                else:  # xml
                    Exporter.export_to_xml(export_data, filepath, logger)
                
                logger.info(f"Successfully exported project '{project_name}' to {filename}")
            
            except Exception as e:
                error_msg = f"Failed to save export for project '{project_name}': {str(e)}"
                logger.error(error_msg, exc_info=True)
                messagebox.showerror("Export Error", error_msg)
    
    
    def _show_multi_export_complete_dialog(self, completed_count, total_count, export_dir):
        """Show completion dialog for multi-project export."""
        if completed_count == total_count:
            title = "Export Complete"
            message = f"Successfully exported {completed_count} project{'s' if completed_count != 1 else ''} to:\n\n{export_dir}"
        else:
            title = "Export Partially Complete"
            message = f"Exported {completed_count} of {total_count} projects to:\n\n{export_dir}\n\nCheck the log files for any errors."
        
        messagebox.showinfo(title, message)
    
    def _show_error(self, message):
        """Show an error message and update the status."""
        messagebox.showerror("Error", message)
        self.status_var.set("Error occurred")
        self._update_progress("")
    
    def _show_export_error(self, error_message, log_file_path, format):
        """Show a detailed export error message with log file information."""
        # Create detailed error message
        detail_msg = (
            f"Failed to export to {format.upper()} format\n\n"
            f"Error: {error_message}\n\n"
            f"A detailed log file has been created at:\n"
            f"{log_file_path}\n\n"
            f"Please check the log file for more information."
        )
        
        messagebox.showerror("Export Error", detail_msg)
        self.status_var.set(f"Export failed - see log file")
        self._update_progress("")
    
    def _sanitize_filename(self, filename):
        """
        Sanitize a filename by replacing problematic characters.
        
        Args:
            filename (str): The filename to sanitize
            
        Returns:
            str: Sanitized filename safe for filesystem use
        """
        # Replace slashes with dashes
        filename = filename.replace('/', '-')
        filename = filename.replace('\\', '-')
        
        # Replace other problematic characters
        # These characters are generally problematic across different filesystems
        problematic_chars = '<>:"|?*'
        for char in problematic_chars:
            filename = filename.replace(char, '_')
        
        # Remove any leading/trailing dots or spaces
        filename = filename.strip('. ')
        
        # Ensure filename is not empty after sanitization
        if not filename:
            filename = 'unnamed_project'
        
        return filename