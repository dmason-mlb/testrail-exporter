import sys
import os

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