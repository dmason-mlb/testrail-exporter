import sys
import os
import locale

# Ensure UTF-8 encoding for all file operations
if sys.platform.startswith('win'):
    # Windows often uses cp1252 as default
    os.environ['PYTHONIOENCODING'] = 'utf-8'
else:
    # Set UTF-8 as default for other platforms too
    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except locale.Error:
        pass

# Add the parent directory to sys.path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the application
from testrail_exporter.gui.app import Application


def main():
    """Run the TestRail Exporter application."""
    app = Application()
    app.mainloop()


if __name__ == "__main__":
    main()