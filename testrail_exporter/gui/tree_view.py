import tkinter as tk
from tkinter import ttk
import os
from PIL import Image, ImageTk, ImageDraw


class CheckableTreeview(ttk.Treeview):
    """Custom Treeview with checkboxes for items."""

    def __init__(self, parent, *args, **kwargs):
        """
        Initialize the checkable treeview.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent, *args, **kwargs)
        
        # Define check states
        self._checked = set()
        self._partial = set()
        
        # Bind events
        self.bind("<Button-1>", self._on_click)
        
        # Create the checkbox images
        self._create_checkbox_images()
        
    def _create_checkbox_images(self):
        """Create better-looking checkbox images."""
        size = 16
        
        # Checked icon - green checkmark
        checked = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(checked)
        
        # Outer square
        draw.rectangle([0, 0, size-1, size-1], outline='#BBBBBB', width=1)
        
        # Fill square with light green
        draw.rectangle([1, 1, size-2, size-2], fill='#C0E8C0')
        
        # Draw checkmark
        checkmark_coords = [(3, 8), (7, 12), (13, 4)]
        draw.line(checkmark_coords, fill='#008800', width=2)
        
        self.image_checked = ImageTk.PhotoImage(checked)
        
        # Partial icon - blue square with dash
        partial = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(partial)
        
        # Outer square
        draw.rectangle([0, 0, size-1, size-1], outline='#BBBBBB', width=1)
        
        # Fill square with light blue
        draw.rectangle([1, 1, size-2, size-2], fill='#C0D8E8')
        
        # Draw dash
        draw.rectangle([3, 7, size-4, 9], fill='#0000AA')
        
        self.image_partial = ImageTk.PhotoImage(partial)
        
        # Unchecked icon - empty square
        unchecked = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(unchecked)
        
        # Outer square with white fill
        draw.rectangle([0, 0, size-1, size-1], outline='#BBBBBB', width=1, fill='#FFFFFF')
        
        self.image_unchecked = ImageTk.PhotoImage(unchecked)
        
    def _on_click(self, event):
        """
        Handle mouse clicks on the treeview.
        
        Args:
            event: Click event
        """
        # Get the item that was clicked
        region = self.identify_region(event.x, event.y)
        item = self.identify_row(event.y)
        
        if not item:
            return
        
        # Handle clicks based on region
        if region == "image" or region == "tree":
            # Toggle checkbox when clicked on icon/image
            self._toggle_check(item)
            return "break"  # Prevent default behavior
        elif region == "cell":
            # For cell clicks, allow default behavior (selecting)
            pass
        else:
            # For other areas like the row background, toggle checkbox
            # but allow default action for the carat
            self._toggle_check(item)
            
        # Allow tree expansion/collapse to work normally
        
    def _toggle_check(self, item):
        """
        Toggle the check state of an item.
        
        Args:
            item: Item ID
        """
        if item in self._checked:
            self._uncheck_item(item)
        else:
            self._check_item(item)
            
        self._update_parent_states(self.parent(item))
            
    def _check_item(self, item):
        """
        Check an item and all its children.
        
        Args:
            item: Item ID
        """
        self._checked.add(item)
        self._partial.discard(item)
        
        # Update image
        self.item(item, image=self._get_check_image(item))
        
        # Check all children
        for child in self.get_children(item):
            self._check_item(child)
    
    def _uncheck_item(self, item):
        """
        Uncheck an item and all its children.
        
        Args:
            item: Item ID
        """
        self._checked.discard(item)
        self._partial.discard(item)
        
        # Update image
        self.item(item, image=self._get_check_image(item))
        
        # Uncheck all children
        for child in self.get_children(item):
            self._uncheck_item(child)
    
    def _update_parent_states(self, parent):
        """
        Update the state of a parent item based on its children.
        
        Args:
            parent: Parent item ID
        """
        if not parent:
            return
            
        children = self.get_children(parent)
        if not children:
            return
            
        # Count checked and partial children
        checked_children = sum(1 for child in children if child in self._checked)
        partial_children = sum(1 for child in children if child in self._partial)
        
        # Update parent state
        if checked_children == len(children):
            # All children checked
            self._checked.add(parent)
            self._partial.discard(parent)
        elif checked_children > 0 or partial_children > 0:
            # Some children checked
            self._checked.discard(parent)
            self._partial.add(parent)
        else:
            # No children checked
            self._checked.discard(parent)
            self._partial.discard(parent)
            
        # Update image
        self.item(parent, image=self._get_check_image(parent))
        
        # Update parent's parent
        self._update_parent_states(self.parent(parent))
    
    def _get_check_image(self, item):
        """
        Get the appropriate check image for an item.
        
        Args:
            item: Item ID
            
        Returns:
            PhotoImage: Image object
        """
        if item in self._checked:
            return self.image_checked
        elif item in self._partial:
            return self.image_partial
        else:
            return self.image_unchecked
    
    def check_all(self):
        """Check all items in the treeview."""
        for item in self.get_children():
            self._check_item(item)
    
    def uncheck_all(self):
        """Uncheck all items in the treeview."""
        for item in self.get_children():
            self._uncheck_item(item)
            
    def expand_all(self):
        """Expand all items in the treeview."""
        def _expand_all(item):
            self.item(item, open=True)
            for child in self.get_children(item):
                _expand_all(child)
                
        for item in self.get_children():
            _expand_all(item)
            
    def collapse_all(self):
        """Collapse all items in the treeview."""
        def _collapse_all(item):
            self.item(item, open=False)
            for child in self.get_children(item):
                _collapse_all(child)
                
        for item in self.get_children():
            _collapse_all(item)
            
    def get_checked_items(self):
        """
        Get all checked items.
        
        Returns:
            list: List of checked item IDs
        """
        return list(self._checked)
        
    def configure_icons(self, checked_icon=None, partial_icon=None, unchecked_icon=None):
        """
        Configure the check icons.
        
        Args:
            checked_icon: Image for checked state
            partial_icon: Image for partial state
            unchecked_icon: Image for unchecked state
        """
        if checked_icon:
            self.image_checked = checked_icon
        if partial_icon:
            self.image_partial = partial_icon
        if unchecked_icon:
            self.image_unchecked = unchecked_icon